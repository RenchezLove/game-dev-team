// gen-flame.js — генератор стилизованной текстуры ПЛАМЕНИ (alpha) для дешёвого VFX костра ContrarySurvivor.
// Приём «огонь на скрещённых плашках»: язык пламени с прозрачным фоном и мягкими краями.
// Форма: широкое горячее основание → органичные «языки» кверху (НЕ симметричный треугольник).
// Цвет снизу вверх: бело-жёлтое ядро → оранжевый → красный к верхушкам; верх с частичной прозрачностью.
// Выход: standalone HTML c инлайн-SVG. Рендер: Edge --default-background-color=00000000 --screenshot.
//   flame-01/02 — 512×1024 (два разных языка). flame-flipbook — 1024×1024, сетка 4×2 = 8 фаз мерцания.
'use strict';
const fs = require('fs');
const path = require('path');

// ---- seeded RNG (mulberry32) ----
function rng(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const fmt = (n) => Math.round(n * 100) / 100;

// ---- Catmull-Rom (замкнутый) → кубический безье. Гладкий органический контур. ----
function closedSmoothPath(pts, tension = 1) {
  const n = pts.length;
  let d = `M ${fmt(pts[0].x)} ${fmt(pts[0].y)} `;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const c1x = p1.x + ((p2.x - p0.x) / 6) * tension, c1y = p1.y + ((p2.y - p0.y) / 6) * tension;
    const c2x = p2.x - ((p3.x - p1.x) / 6) * tension, c2y = p2.y - ((p3.y - p1.y) / 6) * tension;
    d += `C ${fmt(c1x)} ${fmt(c1y)} ${fmt(c2x)} ${fmt(c2y)} ${fmt(p2.x)} ${fmt(p2.y)} `;
  }
  return d + 'Z';
}

// Контур языка пламени: узкая «нога» → пузо (широкое горячее тело) → плечо → языки-лобы.
// P — параметры в долях W/H; t — фаза мерцания [0..1).
function flamePath(rand, W, H, P, t) {
  const baseY = H * 0.94;
  const cx = W * 0.5 + (P.baseLean || 0) * W;
  const footHalf = W * P.footHalf;
  const bulgeHalf = W * P.bulgeHalf;
  const shoulderHalf = W * P.shoulderHalf;
  const bulgeY = baseY - H * P.bulgeYf;
  const shoulderY = baseY - H * P.shoulderYf;
  const topYmin = H * 0.04;
  const lean = ((P.lean || 0) + (P.swayAmp || 0) * Math.sin(2 * Math.PI * t)) * W;
  const leanAt = (y) => lean * ((baseY - y) / (baseY - topYmin));

  const bottomLeft = { x: cx - footHalf, y: baseY };
  const bottomMid = { x: cx, y: baseY + H * 0.012 };
  const bottomRight = { x: cx + footHalf, y: baseY };
  const rBulge = { x: cx + bulgeHalf + leanAt(bulgeY), y: bulgeY };
  const rShoulder = { x: cx + shoulderHalf + leanAt(shoulderY), y: shoulderY };
  const lShoulder = { x: cx - shoulderHalf + leanAt(shoulderY), y: shoulderY };
  const lBulge = { x: cx - bulgeHalf + leanAt(bulgeY), y: bulgeY };

  // пики-«языки» справа налево; высота от плеча (один центральный выше = асимметрия)
  const nT = P.nTongues;
  const span = shoulderHalf * 2 * 1.04;
  const peaks = [];
  for (let k = 0; k < nT; k++) {
    const frac = (k + 0.5) / nT;
    let px = cx + span * 0.5 - span * frac;
    const centerBoost = (1 - Math.abs(0.5 - frac) * 2) * H * (P.centerTall ?? 0.16);
    const sway = (P.tongueSway || 0) * Math.sin(2 * Math.PI * t + k * 1.9 + (P.seedPhase || 0)) * H;
    let tongueH = H * (P.tongueMin + rand() * P.tongueVar) + centerBoost + sway;
    let py = clamp(shoulderY - tongueH, topYmin, shoulderY - H * 0.05);
    px += leanAt(py) + (rand() - 0.5) * W * 0.03;
    peaks.push({ x: px, y: py });
  }

  // долины между пиками — у самого плеча (мелкие), чтобы языки были толстыми лобами, не иглами
  const top = [];
  let prev = rShoulder;
  for (let k = 0; k < peaks.length; k++) {
    const p = peaks[k];
    const vx = (prev.x + p.x) / 2 + (rand() - 0.5) * W * 0.03;
    const vy = shoulderY - H * (0.015 + rand() * 0.05);
    top.push({ x: vx, y: vy });
    top.push(p);
    prev = p;
  }
  {
    const vx = (prev.x + lShoulder.x) / 2 + (rand() - 0.5) * W * 0.02;
    const vy = shoulderY - H * (0.01 + rand() * 0.04);
    top.push({ x: vx, y: vy });
  }

  const pts = [bottomLeft, bottomMid, bottomRight, rBulge, rShoulder, ...top, lShoulder, lBulge];
  return { d: closedSmoothPath(pts, 1), baseY, topY: Math.min(...peaks.map(p => p.y)), cx };
}

// SVG-группа одной ячейки пламени (тело + горячее ядро + ореол) с уникальными id.
function flameCell(rand, W, H, P, t, uid) {
  const body = flamePath(rand, W, H, P, t);
  // ядро: короче и уже, центрированное, почти без наклона (горячий хребет у основания)
  const coreP = Object.assign({}, P, {
    footHalf: P.footHalf * 0.6, bulgeHalf: P.bulgeHalf * 0.5, shoulderHalf: P.shoulderHalf * 0.55,
    bulgeYf: P.bulgeYf * 0.7, shoulderYf: P.shoulderYf * 0.66,
    nTongues: Math.max(2, P.nTongues - 1),
    lean: (P.lean || 0) * 0.4, swayAmp: (P.swayAmp || 0) * 0.4, baseLean: (P.baseLean || 0) * 0.5,
    centerTall: 0.07, tongueMin: 0.04, tongueVar: 0.08
  });
  const core = flamePath(rand, W, H, coreP, t);

  const bodyTop = clamp(body.topY, H * 0.03, H);
  const coreTop = clamp(core.topY, H * 0.30, H);
  const blurBody = H * 0.006, blurCore = H * 0.013, blurGlow = H * 0.026;

  return `
  <defs>
    <linearGradient id="bg${uid}" gradientUnits="userSpaceOnUse" x1="0" y1="${fmt(bodyTop)}" x2="0" y2="${fmt(body.baseY)}">
      <stop offset="0%"   stop-color="#b81a10" stop-opacity="0.75"/>
      <stop offset="11%"  stop-color="#e23a14"/>
      <stop offset="30%"  stop-color="#ff5e16"/>
      <stop offset="52%"  stop-color="#ff8a18"/>
      <stop offset="73%"  stop-color="#ffb733"/>
      <stop offset="89%"  stop-color="#ffdc66"/>
      <stop offset="100%" stop-color="#fff2c2"/>
    </linearGradient>
    <linearGradient id="cg${uid}" gradientUnits="userSpaceOnUse" x1="0" y1="${fmt(coreTop)}" x2="0" y2="${fmt(core.baseY)}">
      <stop offset="0%"   stop-color="#ff7e1a" stop-opacity="0.85"/>
      <stop offset="42%"  stop-color="#ffd45c"/>
      <stop offset="100%" stop-color="#fffaf0"/>
    </linearGradient>
    <filter id="fb${uid}" x="-30%" y="-20%" width="160%" height="140%"><feGaussianBlur stdDeviation="${fmt(blurBody)}"/></filter>
    <filter id="fc${uid}" x="-40%" y="-30%" width="180%" height="160%"><feGaussianBlur stdDeviation="${fmt(blurCore)}"/></filter>
    <filter id="fg${uid}" x="-60%" y="-40%" width="220%" height="180%"><feGaussianBlur stdDeviation="${fmt(blurGlow)}"/></filter>
  </defs>
  <path d="${body.d}" fill="#ff7a22" opacity="0.16" filter="url(#fg${uid})"/>
  <path d="${body.d}" fill="url(#bg${uid})" filter="url(#fb${uid})"/>
  <path d="${core.d}" fill="url(#cg${uid})" filter="url(#fc${uid})"/>`;
}

function htmlWrap(W, H, inner) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0;width:${W}px;height:${H}px;overflow:hidden;background:transparent}
  svg{display:block}
  </style></head><body><svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${inner}</svg></body></html>`;
}

const outDir = __dirname;

// ---- два одиночных языка 512×1024 (разные формы) ----
const single = [
  { tag: '01', seed: 50231, W: 512, H: 1024,
    P: { footHalf: 0.12, bulgeHalf: 0.33, shoulderHalf: 0.20, bulgeYf: 0.24, shoulderYf: 0.46,
         nTongues: 4, tongueMin: 0.08, tongueVar: 0.16, centerTall: 0.22,
         lean: 0.05, baseLean: -0.01, seedPhase: 0.4 } },
  { tag: '02', seed: 778113, W: 512, H: 1024,
    P: { footHalf: 0.13, bulgeHalf: 0.35, shoulderHalf: 0.22, bulgeYf: 0.22, shoulderYf: 0.48,
         nTongues: 3, tongueMin: 0.10, tongueVar: 0.20, centerTall: 0.14,
         lean: -0.07, baseLean: 0.015, seedPhase: 1.9 } },
];
single.forEach((s) => {
  const inner = flameCell(rng(s.seed), s.W, s.H, s.P, 0, 'S' + s.tag);
  const file = path.join(outDir, `flame-${s.tag}.html`);
  fs.writeFileSync(file, htmlWrap(s.W, s.H, inner));
  console.log('wrote', file, fs.statSync(file).size, 'bytes');
});

// ---- флипбук 4×2 = 8 фаз мерцания, ячейка 256×512, лист 1024×1024 ----
(function flipbook() {
  const cols = 4, rows = 2, cw = 256, ch = 512, W = cols * cw, H = rows * ch;
  const baseP = { footHalf: 0.12, bulgeHalf: 0.33, shoulderHalf: 0.20, bulgeYf: 0.24, shoulderYf: 0.46,
                  nTongues: 4, tongueMin: 0.08, tongueVar: 0.14, centerTall: 0.20,
                  lean: 0.0, swayAmp: 0.06, tongueSway: 0.05, seedPhase: 0.7 };
  let cells = '';
  let defsClip = `<clipPath id="cellclip"><rect x="0" y="0" width="${cw}" height="${ch}"/></clipPath>`;
  for (let i = 0; i < cols * rows; i++) {
    const col = i % cols, row = Math.floor(i / cols);
    const t = i / (cols * rows); // фаза цикла 0..7/8
    // у каждого кадра свой rng-сид, но плавность даёт фаза t в sin (sway/tongueSway)
    const inner = flameCell(rng(424242), cw, ch, baseP, t, 'F' + i);
    cells += `<g transform="translate(${col * cw},${row * ch})" clip-path="url(#cellclip)">${inner}</g>`;
  }
  const svgInner = `<defs>${defsClip}</defs>${cells}`;
  const file = path.join(outDir, 'flame-flipbook.html');
  fs.writeFileSync(file, htmlWrap(W, H, svgInner));
  console.log('wrote', file, fs.statSync(file).size, 'bytes');
})();

console.log('done');

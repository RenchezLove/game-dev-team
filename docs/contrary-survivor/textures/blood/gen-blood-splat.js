// gen-blood-splat.js — генератор органических пятен крови (top-down декаль) для ContrarySurvivor.
// Стиль: тёмно-багровая засохшая лужа, лоуполи пост-апок (LDoE/STALKER), палитра Muted Blood #8A2F2A.
// Выход: standalone HTML c инлайн-SVG, viewBox 1024×1024, ПРОЗРАЧНЫЙ фон (без background).
// Рендер: Edge --headless=new --default-background-color=00000000 --window-size=1024,1024 --screenshot.
// Форма строго НЕ круг/НЕ прямоугольник: неправильный замкнутый безье-контур (Catmull-Rom→Bezier)
//   + пальцевые выступы + капли-брызги по периметру + потёки.
'use strict';
const fs = require('fs');
const path = require('path');

const SIZE = 1024;
const CX = SIZE / 2, CY = SIZE / 2;

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
const fmt = (n) => Math.round(n * 100) / 100;

// ---- Catmull-Rom (замкнутый) → кубический безье path. Даёт гладкий органический контур. ----
function closedSmoothPath(pts, tension = 1) {
  const n = pts.length;
  let d = `M ${fmt(pts[0].x)} ${fmt(pts[0].y)} `;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n];
    const p1 = pts[i];
    const p2 = pts[(i + 1) % n];
    const p3 = pts[(i + 2) % n];
    const c1x = p1.x + ((p2.x - p0.x) / 6) * tension;
    const c1y = p1.y + ((p2.y - p0.y) / 6) * tension;
    const c2x = p2.x - ((p3.x - p1.x) / 6) * tension;
    const c2y = p2.y - ((p3.y - p1.y) / 6) * tension;
    d += `C ${fmt(c1x)} ${fmt(c1y)} ${fmt(c2x)} ${fmt(c2y)} ${fmt(p2.x)} ${fmt(p2.y)} `;
  }
  return d + 'Z';
}

// Неправильный блоб вокруг (cx,cy): N точек, радиус с шумом + редкие «пальцы» (выступы).
function blobPoints(rand, cx, cy, baseR, opts = {}) {
  const n = opts.n || (10 + Math.floor(rand() * 5));
  const irregular = opts.irregular ?? 0.34;   // доля вариации радиуса
  const fingerChance = opts.fingerChance ?? 0.22;
  const fingerBoost = opts.fingerBoost ?? 0.55;
  const squashX = opts.squashX ?? 1;          // вытянутость (направленный сплэт)
  const squashY = opts.squashY ?? 1;
  const rot = opts.rot ?? 0;
  const pts = [];
  for (let i = 0; i < n; i++) {
    const baseA = (i / n) * Math.PI * 2;
    const a = baseA + (rand() - 0.5) * (Math.PI / n) * 0.9; // лёгкий джиттер угла
    let r = baseR * (1 + (rand() - 0.5) * 2 * irregular);
    if (rand() < fingerChance) r *= 1 + rand() * fingerBoost; // палец/растёк
    let x = Math.cos(a) * r * squashX;
    let y = Math.sin(a) * r * squashY;
    // поворот для направленного пятна
    const xr = x * Math.cos(rot) - y * Math.sin(rot);
    const yr = x * Math.sin(rot) + y * Math.cos(rot);
    pts.push({ x: cx + xr, y: cy + yr });
  }
  return pts;
}

// Капля-брызг (teardrop): круглое тело + хвост в сторону angle. Возврат — path.
function dropletPath(rand, x, y, r, angle, tail = 1.6) {
  // тело
  const pts = blobPoints(rand, 0, 0, r, { n: 8, irregular: 0.18, fingerChance: 0.1, fingerBoost: 0.3 });
  // хвост: вытянуть 1-2 точки в сторону angle
  const tx = Math.cos(angle), ty = Math.sin(angle);
  const ti = pts.reduce((best, p, idx) => {
    const dot = (p.x * tx + p.y * ty);
    return dot > best.dot ? { dot, idx } : best;
  }, { dot: -1e9, idx: 0 }).idx;
  pts[ti].x = tx * r * tail;
  pts[ti].y = ty * r * tail;
  const d = closedSmoothPath(pts, 1);
  return d.replace(/M ([\-\d.]+) ([\-\d.]+)/, (m, mx, my) => `M ${fmt(+mx + x)} ${fmt(+my + y)}`)
    .replace(/C ([^Z]+)/g, (seg) => {
      // сдвиг всех координат внутри C на (x,y)
      const nums = seg.slice(2).trim().split(/\s+/).map(Number);
      let out = 'C ';
      for (let k = 0; k < nums.length; k += 2) out += `${fmt(nums[k] + x)} ${fmt(nums[k + 1] + y)} `;
      return out;
    });
}

// Палитра засохшей крови (тёмный густой центр → подсохший край, оттенок к Muted Blood #8A2F2A).
function bloodGradient(id, rand) {
  // лёгкая вариация тона между вариантами
  const c0 = '#360b08';
  const c1 = '#561511';
  const c2 = '#6e1f18';
  const c3 = '#7c2a1f';
  const c4 = '#6f2a20';
  return `
  <radialGradient id="${id}" cx="46%" cy="44%" r="62%">
    <stop offset="0%"  stop-color="${c0}"/>
    <stop offset="32%" stop-color="${c1}"/>
    <stop offset="62%" stop-color="${c2}"/>
    <stop offset="88%" stop-color="${c3}"/>
    <stop offset="100%" stop-color="${c4}" stop-opacity="0.92"/>
  </radialGradient>`;
}

function buildSVG(seed, cfg) {
  const rand = rng(seed);
  const gid = `bg${seed}`;
  const mainR = cfg.mainR;
  const mainPts = blobPoints(rand, CX, CY, mainR, {
    n: cfg.n, irregular: cfg.irregular, fingerChance: cfg.fingerChance,
    fingerBoost: cfg.fingerBoost, squashX: cfg.squashX, squashY: cfg.squashY, rot: cfg.rot
  });
  const mainPath = closedSmoothPath(mainPts, 1);

  // внутренние тёмные сгустки (густой центр, вариация плотности)
  let mottle = '';
  const nMot = cfg.mottle || 3;
  for (let i = 0; i < nMot; i++) {
    const a = rand() * Math.PI * 2;
    const rr = rand() * mainR * 0.4;
    const mx = CX + Math.cos(a) * rr, my = CY + Math.sin(a) * rr;
    const mr = mainR * (0.16 + rand() * 0.2);
    const pts = blobPoints(rand, mx, my, mr, { n: 7, irregular: 0.3, fingerChance: 0.15, fingerBoost: 0.4 });
    mottle += `<path d="${closedSmoothPath(pts, 1)}" fill="#2c0907" opacity="${fmt(0.28 + rand() * 0.22)}"/>`;
  }

  // потёки (drips) — вытянутые капли от тела наружу
  let drips = '';
  const nDrip = cfg.drips;
  for (let i = 0; i < nDrip; i++) {
    const a = cfg.dripBias != null
      ? cfg.dripBias + (rand() - 0.5) * cfg.dripSpread
      : rand() * Math.PI * 2;
    const edge = mainR * (0.82 + rand() * 0.2);
    const dx = CX + Math.cos(a) * edge, dy = CY + Math.sin(a) * edge;
    const dr = mainR * (0.07 + rand() * 0.07);
    drips += `<path d="${dropletPath(rand, dx, dy, dr, a, 2.0 + rand() * 1.6)}" fill="url(#${gid})"/>`;
  }

  // брызги/капли по периметру (spatter) — разлёт от центра, дальше = реже и мельче
  let spatter = '';
  const nSpat = cfg.spatter;
  for (let i = 0; i < nSpat; i++) {
    const a = cfg.spatBias != null
      ? cfg.spatBias + (rand() - 0.5) * cfg.spatSpread
      : rand() * Math.PI * 2;
    const t = Math.pow(rand(), 0.6); // концентрация ближе к телу
    const dist = mainR * (1.0 + t * cfg.spatReach);
    const sx = CX + Math.cos(a) * dist * cfg.squashX;
    const sy = CY + Math.sin(a) * dist * cfg.squashY;
    if (sx < 24 || sx > SIZE - 24 || sy < 24 || sy > SIZE - 24) continue; // держим прозрачные поля
    const sr = lerp(mainR * 0.11, mainR * 0.028, t) * (0.75 + rand() * 0.65);
    if (rand() < 0.5) {
      // вытянутая капля по направлению разлёта (хвост умеренный — капля, не «волосок»)
      spatter += `<path d="${dropletPath(rand, sx, sy, sr, a, 1.2 + rand() * 0.9)}" fill="#5e1812" opacity="${fmt(0.8 + rand() * 0.2)}"/>`;
    } else {
      spatter += `<ellipse cx="${fmt(sx)}" cy="${fmt(sy)}" rx="${fmt(sr)}" ry="${fmt(sr * (0.7 + rand() * 0.5))}" fill="#62160f" opacity="${fmt(0.78 + rand() * 0.22)}"/>`;
    }
  }

  // halo-«впитывание» (диффузный край, мягкая частичная прозрачность)
  const haloPts = blobPoints(rand, CX, CY, mainR * 1.1, {
    n: cfg.n, irregular: cfg.irregular * 0.8, fingerChance: 0.15, fingerBoost: 0.3,
    squashX: cfg.squashX, squashY: cfg.squashY, rot: cfg.rot
  });
  const haloPath = closedSmoothPath(haloPts, 1);

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${SIZE}" height="${SIZE}" viewBox="0 0 ${SIZE} ${SIZE}">
  <defs>
    ${bloodGradient(gid, rand)}
    <filter id="soft${seed}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.4"/>
    </filter>
    <filter id="halo${seed}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="12"/>
    </filter>
    <filter id="mot${seed}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="9"/>
    </filter>
  </defs>
  <!-- 1. halo: диффузное впитывание в землю (тёплый багровый, не серый) -->
  <path d="${haloPath}" fill="#5a1611" opacity="0.34" filter="url(#halo${seed})"/>
  <!-- 2. основное пятно: неправильный безье-контур, градиент густой центр→подсохший край -->
  <path d="${mainPath}" fill="url(#${gid})" filter="url(#soft${seed})"/>
  <!-- 3. внутренние сгустки (плотность) -->
  <g filter="url(#mot${seed})">${mottle}</g>
  <!-- 4. потёки -->
  ${drips}
  <!-- 5. брызги/капли по периметру -->
  ${spatter}
</svg>`;
}

function htmlWrap(svg) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0;width:${SIZE}px;height:${SIZE}px;overflow:hidden;background:transparent}
  svg{display:block}
  </style></head><body>${svg}</body></html>`;
}

// ---- 3 варианта формы ----
const variants = [
  // 1: компактная осевшая лужа (под телом), пара потёков вбок
  { seed: 73101, mainR: 300, n: 13, irregular: 0.36, fingerChance: 0.24, fingerBoost: 0.5,
    squashX: 1.06, squashY: 0.96, rot: 0.3, mottle: 4, drips: 3, dripBias: 0.6, dripSpread: 1.8,
    spatter: 16, spatReach: 0.45, spatBias: null, spatSpread: 0 },
  // 2: направленный сплэт (импакт): вытянут, веер брызг в одну сторону
  { seed: 920455, mainR: 285, n: 14, irregular: 0.42, fingerChance: 0.3, fingerBoost: 0.7,
    squashX: 1.32, squashY: 0.82, rot: -0.5, mottle: 3, drips: 4, dripBias: -0.5, dripSpread: 1.2,
    spatter: 26, spatReach: 0.7, spatBias: -0.5, spatSpread: 1.5 },
  // 3: большая разлитая лужа, много пальцев и брызг кругом
  { seed: 11377, mainR: 330, n: 16, irregular: 0.4, fingerChance: 0.32, fingerBoost: 0.6,
    squashX: 0.98, squashY: 1.04, rot: 1.1, mottle: 5, drips: 5, dripBias: null, dripSpread: 6.28,
    spatter: 30, spatReach: 0.42, spatBias: null, spatSpread: 0 },
];

const outDir = __dirname;
variants.forEach((cfg, i) => {
  const svg = buildSVG(cfg.seed, cfg);
  const file = path.join(outDir, `blood-splat-${String(i + 1).padStart(2, '0')}.html`);
  fs.writeFileSync(file, htmlWrap(svg));
  console.log('wrote', file, fs.statSync(file).size, 'bytes');
});
console.log('done');

// gen-autumn-ground.js — осенние бесшовные текстуры земли для ContrarySurvivor (26.09).
// Эталон: утверждённые скрины village/road (замер — measure-palette.js -> palette-measured.json).
// Замер снят с кадра, уже освещённого закатным солнцем. Текстура = собственный цвет поверхности,
// поэтому каждый замеренный цвет переводится функцией albedo(): светлота (HSL L) x0.7, насыщенность
// x0.55, тон сдвигается от оранжевого: земля и сухая трава +6°, зелень +18° (тёплый закатный свет
// сильнее всего «желтит» именно зелень, без этого сдвига трава выходит бурой, а не оливковой).
// Бесшовность: весь рисунок строится из периодического шума, период которого делит размер плитки
// нацело, а камешки рисуются с учётом переноса через край -> плитка стыкуется сама с собой.
// Запуск: NODE_PATH=<папка с node_modules, где есть sharp> node gen-autumn-ground.js
const sharp = require('sharp');
const fs = require('fs'), path = require('path');
const OUT = __dirname;
const measured = JSON.parse(fs.readFileSync(path.join(OUT, 'palette-measured.json'), 'utf8'));

// --- цвет ---
const H2R = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const R2H = c => '#' + c.map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('').toUpperCase();
function rgb2hsl([r, g, b]) {
  r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); let h = 0; const l = (mx + mn) / 2, d = mx - mn;
  if (d) { if (mx == r) h = ((g - b) / d) % 6; else if (mx == g) h = (b - r) / d + 2; else h = (r - g) / d + 4; h *= 60; if (h < 0) h += 360 }
  return [h, d ? d / (1 - Math.abs(2 * l - 1)) : 0, l];
}
function hsl2rgb([h, s, l]) {
  const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs((h / 60) % 2 - 1)), m = l - c / 2;
  const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return [(r + m) * 255, (g + m) * 255, (b + m) * 255];
}
const SHIFT = { hue: 6, hueGreen: 18, sat: 0.55, light: 0.7 };
const albedo = (hex, hue = SHIFT.hue) => { const [h, s, l] = rgb2hsl(H2R(hex)); return hsl2rgb([(h + hue) % 360, s * SHIFT.sat, l * SHIFT.light]); };
const mix = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const scale = (a, k) => a.map(v => v * k);
const clamp01 = t => Math.max(0, Math.min(1, t));
const smooth = (e0, e1, x) => { const t = clamp01((x - e0) / (e1 - e0)); return t * t * (3 - 2 * t); };

const P = {
  olive: albedo(measured.grassOliveLitTop, SHIFT.hueGreen),
  oliveDeep: albedo(measured.grassOliveLit, SHIFT.hueGreen),
  gold: albedo(measured.grassGoldLit),
  dirt: albedo(measured.dirtLit),
  dirtDark: albedo(measured.dirtShade),
  pebDark: albedo(measured.pebbleDark),
  pebLight: albedo(measured.pebbleLight),
};

// --- детерминированный ГСЧ и периодический шум ---
function rng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
function lattice(n, r) { const g = new Float32Array(n * n); for (let i = 0; i < g.length; i++) g[i] = r(); return g; }
// шум в точке (u,v) из [0,1): решётка n x n с переносом через край, квинтическая интерполяция (без «ступенек» по решётке)
function vnoise(g, n, u, v) {
  const x = u * n, y = v * n; const x0 = Math.floor(x), y0 = Math.floor(y); const fx = x - x0, fy = y - y0;
  const q = t => t * t * t * (t * (t * 6 - 15) + 10); const sx = q(fx), sy = q(fy);
  const i0 = ((x0 % n) + n) % n, j0 = ((y0 % n) + n) % n, i1 = (i0 + 1) % n, j1 = (j0 + 1) % n;
  const a = g[j0 * n + i0], b = g[j0 * n + i1], c = g[j1 * n + i0], d = g[j1 * n + i1];
  const top = a + (b - a) * sx, bot = c + (d - c) * sx;
  return top + (bot - top) * sy;
}
function makeFbm(seed, base, oct, gain = 0.5) {
  const r = rng(seed); const L = [];
  // случайный сдвиг каждой октавы: узлы решёток не совпадают с краем плитки (иначе на стыке
  // шум «замирает» и шов читается как ровная полоса); период при этом сохраняется
  for (let k = 0; k < oct; k++) { const n = base << k; L.push([lattice(n, r), n, r(), r()]); }
  let norm = 0, a = 1; for (let k = 0; k < oct; k++) { norm += a; a *= gain; }
  return (u, v) => { let s = 0, amp = 1; for (const [g, n, ox, oy] of L) { s += vnoise(g, n, u + ox, v + oy) * amp; amp *= gain; } return s / norm; };
}
const wrap01 = t => t - Math.floor(t);

// растянуть значения по перцентилям в 0..1
function normalize(arr, lo = 0.02, hi = 0.98) {
  const s = Float32Array.from(arr).sort(); const a = s[Math.floor(s.length * lo)], b = s[Math.floor(s.length * hi)];
  for (let i = 0; i < arr.length; i++) arr[i] = clamp01((arr[i] - a) / (b - a));
  return arr;
}
const put = (img, i, c) => { for (let k = 0; k < 3; k++) img[i * 3 + k] = Math.max(0, Math.min(255, Math.round(c[k]))); };

// --- ТРАВА ---
function grass(S) {
  const warp = makeFbm(11, 4, 3), patch = makeFbm(12, 9, 4, 0.55), tone = makeFbm(13, 3, 3), clump = makeFbm(14, 28, 2), deep = makeFbm(15, 14, 3);
  const m = new Float32Array(S * S);
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const u = x / S, v = y / S;
    const wu = wrap01(u + (warp(u, v) - 0.5) * 0.10), wv = wrap01(v + (warp(wrap01(u + 0.37), wrap01(v + 0.61)) - 0.5) * 0.10);
    m[y * S + x] = patch(wu, wv) * 0.8 + tone(u, v) * 0.2;   // крупная волна слегка сдвигает баланс сухое/зелёное
  }
  normalize(m);
  const mid = mix(P.olive, P.gold, 0.5);
  const img = Buffer.alloc(S * S * 3);
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const u = x / S, v = y / S, i = y * S + x;
    // на эталоне сухой травы примерно вдвое больше, чем зелёной -> порог смещён в сторону олив
    const t = m[i];
    let c = t < 0.4 ? mix(P.olive, mid, smooth(0.1, 0.4, t)) : mix(mid, P.gold, smooth(0.4, 0.7, t));
    c = mix(c, P.oliveDeep, smooth(0.6, 0.85, deep(u, v)) * (1 - smooth(0.25, 0.5, t)) * 0.3); // густые тёмные куртинки в зелени
    c = scale(c, 1 + (tone(wrap01(u + 0.5), v) - 0.5) * 0.14 + (clump(u, v) - 0.5) * 0.12);   // мягкая пятнистость, без мелкого шума
    put(img, i, c);
  }
  return img;
}

// --- ЗЕМЛЯ / ДОРОГА ---
function dirt(S) {
  const mott = makeFbm(21, 10, 4, 0.55), grain = makeFbm(22, 96, 2), warp = makeFbm(23, 4, 2);
  const f = new Float32Array(S * S * 3);
  const darkT = mix(P.dirt, P.dirtDark, 0.18);   // утоптанные тёмные места
  const liteT = mix(P.dirt, P.pebLight, 0.22);   // пыльные светлые места
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const u = x / S, v = y / S, i = y * S + x;
    const t = mott(wrap01(u + (warp(u, v) - 0.5) * 0.12), v);
    let c = t < 0.5 ? mix(darkT, P.dirt, smooth(0.25, 0.5, t)) : mix(P.dirt, liteT, smooth(0.5, 0.75, t));
    c = scale(c, 1 + (grain(u, v) - 0.5) * 0.10);
    f[i * 3] = c[0]; f[i * 3 + 1] = c[1]; f[i * 3 + 2] = c[2];
  }
  // камешки и крап: мягкий диск (+ тень снизу-справа у светлых), с переносом через край
  const r = rng(24);
  const stamp = (cx, cy, rad, col, alpha) => {
    const R = Math.ceil(rad + 1.5), rx = Math.round(cx), ry = Math.round(cy);
    for (let dy = -R; dy <= R; dy++) for (let dx = -R; dx <= R; dx++) {
      const a = alpha * clamp01(rad + 0.5 - Math.hypot(rx + dx - cx, ry + dy - cy)); if (a <= 0) continue;
      const px = ((rx + dx) % S + S) % S, py = ((ry + dy) % S + S) % S, i = (py * S + px) * 3;
      for (let k = 0; k < 3; k++) f[i + k] += (col[k] - f[i + k]) * a;
    }
  };
  for (let n = 0; n < 2400; n++) {
    const cx = r() * S, cy = r() * S, rad = 1.2 + r() * r() * 3.3, light = r() < 0.65;
    const col = light ? mix(P.pebLight, P.dirt, r() * 0.4) : mix(P.pebDark, P.dirtDark, r() * 0.5);
    if (light) stamp(cx + 0.8, cy + 1.1, rad, P.pebDark, 0.35);
    stamp(cx, cy, rad, col, light ? 0.75 : 0.55);
  }
  const img = Buffer.alloc(S * S * 3); for (let i = 0; i < f.length; i++) img[i] = Math.max(0, Math.min(255, Math.round(f[i])));
  return img;
}

// размытие с переносом через край: плитка 3x3 -> размытие -> центральная плитка (шов не появляется)
async function wrapBlurAsync(img, S, sigma) {
  const T = 3 * S, big = Buffer.alloc(T * T);
  for (let y = 0; y < T; y++) for (let x = 0; x < T; x++) big[y * T + x] = img[(y % S) * S + (x % S)];
  // два отдельных прохода: в одном конвейере sharp обрезку делает ДО размытия, и шов возвращается
  const blurred = await sharp(big, { raw: { width: T, height: T, channels: 1 } }).blur(sigma).extractChannel(0).raw().toBuffer();
  const out = Buffer.alloc(S * S);
  for (let y = 0; y < S; y++) blurred.copy(out, y * S, (y + S) * T + S, (y + S) * T + 2 * S);
  return out;
}
const wrapBlur = (img, S, sigma) => wrapBlurAsync(img, S, sigma);

// --- МАКРО-МАСКА (серая) ---
function macro(S) {
  const base = makeFbm(31, 3, 4, 0.5), warp = makeFbm(32, 4, 2);
  const m = new Float32Array(S * S);
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const u = x / S, v = y / S;
    m[y * S + x] = base(wrap01(u + (warp(u, v) - 0.5) * 0.08), wrap01(v + (warp(wrap01(u + 0.5), wrap01(v + 0.5)) - 0.5) * 0.08));
  }
  normalize(m, 0.01, 0.99);
  const img = Buffer.alloc(S * S); for (let i = 0; i < m.length; i++) img[i] = Math.round(m[i] * 255);
  return wrapBlur(img, S, 18);
}

// --- проверка бесшовности по записанному файлу. Для каждой пары соседних столбцов (и строк) внутри
// плитки считается средняя разница пикселей; затем то же для пары «последний -> первый» (стык при
// повторе). Если стык попадает в обычный разброс внутренних пар (перцентиль между 1 и 99) — шва нет.
function seamCheck(buf, S, ch) {
  const at = (x, y, k) => buf[(y * S + x) * ch + k];
  const res = {};
  for (const axis of ['X', 'Y']) {
    const diff = (a, b) => { let d = 0; for (let t = 0; t < S; t++) for (let k = 0; k < ch; k++) d += axis === 'X' ? Math.abs(at(a, t, k) - at(b, t, k)) : Math.abs(at(t, a, k) - at(t, b, k)); return d / (S * ch); };
    const inner = []; for (let q = 0; q < S - 1; q++) inner.push(diff(q + 1, q));
    const seam = diff(0, S - 1); inner.sort((p, q) => p - q);
    const pctl = inner.filter(v => v < seam).length / inner.length * 100;
    res['шов' + axis] = +seam.toFixed(3); res['внутри' + axis] = [+inner[0].toFixed(3), +inner[inner.length - 1].toFixed(3)]; res['перцентиль' + axis] = +pctl.toFixed(1);
  }
  return res;
}
function meanColor(buf, S) { const s = [0, 0, 0]; for (let i = 0; i < S * S; i++) for (let k = 0; k < 3; k++) s[k] += buf[i * 3 + k]; return R2H(s.map(v => v / (S * S))); }

(async () => {
  const jobs = [['T_GroundGrassAutumn', 1024, 3, grass], ['T_GroundDirtAutumn', 1024, 3, dirt], ['T_GroundMacroMask', 512, 1, macro]];
  console.log('Палитра (замер -> собственный цвет):');
  for (const [k, v] of Object.entries(P)) console.log(' ', k.padEnd(10), R2H(v));
  for (const [name, S, ch, fn] of jobs) {
    const buf = await fn(S);
    const raw = { raw: { width: S, height: S, channels: ch } };
    const file = path.join(OUT, name + '.png');
    await (ch === 1 ? sharp(buf, raw).toColourspace('b-w') : sharp(buf, raw)).png().toFile(file);
    // превью 2x2 плитки (стык крестом по центру) и шов 1:1 (512x512 вокруг центра креста)
    const tile = await sharp(buf, raw).png().toBuffer();
    const big = await sharp({ create: { width: S * 2, height: S * 2, channels: 3, background: '#000' } })
      .composite([[0, 0], [S, 0], [0, S], [S, S]].map(([left, top]) => ({ input: tile, left, top }))).png().toBuffer();
    await sharp(big).resize(1024, 1024).png().toFile(path.join(OUT, name + '_preview2x2.png'));
    await sharp(big).extract({ left: S - 256, top: S - 256, width: 512, height: 512 }).png().toFile(path.join(OUT, name + '_seam1to1.png'));
    const meta = await sharp(file).metadata();
    const back = await (ch === 1 ? sharp(file).extractChannel(0) : sharp(file)).raw().toBuffer({ resolveWithObject: true });
    console.log(name, `${meta.width}x${meta.height} каналов в файле ${meta.channels} (${meta.space})`, JSON.stringify(seamCheck(back.data, S, back.info.channels)), ch === 3 ? 'средний ' + meanColor(back.data, S) : '');
  }
})();

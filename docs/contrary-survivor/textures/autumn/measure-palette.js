// measure-palette.js — замер палитры земли/травы с утверждённых эталонных скринов (26.09).
// Запуск: NODE_PATH=<папка с node_modules, где есть sharp> node measure-palette.js
// Выход: таблица в консоль + palette-measured.json (медиана RGB по отфильтрованным пикселям).
const sharp = require('sharp');
const fs = require('fs'), path = require('path');
const D = 'C:/Users/pgr40/Desktop/GamdevAITeam/Скрины в магазин 24.09.2026/2/';
const V = D + 'ContrarySurvivor_village_final(2)_enhanced_1920x1080.png';
const R = D + 'ContrarySurvivor_road_final(2)_enhanced_1920x1080.png';
const hex = c => '#' + c.map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
function hsl([r, g, b]) { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); let h = 0; const l = (mx + mn) / 2, d = mx - mn;
  if (d) { if (mx == r) h = ((g - b) / d) % 6; else if (mx == g) h = (b - r) / d + 2; else h = (r - g) / d + 4; h *= 60; if (h < 0) h += 360 }
  return [h, d ? d / (1 - Math.abs(2 * l - 1)) : 0, l] }
const lum = c => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
const med = px => [0, 1, 2].map(i => { const a = px.map(p => p[i]).sort((x, y) => x - y); return a[a.length >> 1] });
function region(img, [x0, y0, x1, y1]) { const px = []; for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { const i = (y * img.w + x) * 3; px.push([img.data[i], img.data[i + 1], img.data[i + 2]]) } return px }
const pct = (px, lo, hi) => { const s = px.map(lum).sort((a, b) => a - b); const a = s[Math.floor(s.length * lo)], b = s[Math.min(s.length - 1, Math.floor(s.length * hi))]; return p => { const L = lum(p); return L >= a && L <= b } };
// На эталоне «зелень» под закатной грейдинг-заливкой = оливковый тон H40-60; сухая трава = H24-36.
const olive = p => { const [h, , l] = hsl(p); return h >= 40 && h <= 60 && l > 0.08 };
const golden = p => { const [h, s, l] = hsl(p); return h >= 24 && h < 36 && s > 0.35 && l > 0.25 };
(async () => {
  const load = async f => { const { data, info } = await sharp(f).removeAlpha().raw().toBuffer({ resolveWithObject: true }); return { data, w: info.width } };
  const v = await load(V), r = await load(R);
  const GL = [[r, 'road', [600, 180, 760, 320]], [r, 'road', [1350, 450, 1560, 600]], [v, 'village', [700, 380, 860, 480]]];
  const rows = [
    ['grassOliveLit', 'Трава на свету, оливковая (H40-60)', GL, olive],
    ['grassOliveLitTop', 'Трава на свету, оливковая — светлая половина (без теней между травинками)', GL, 'oliveTop'],
    ['grassGoldLit', 'Сухая золотистая трава на свету (H24-36)', GL, golden],
    ['grassShade', 'Трава в тени (тёмная треть яркости)', [[v, 'village', [1000, 900, 1400, 1070]]], 'd33'],
    ['grassShade2', 'Трава в тени (весь участок)', [[r, 'road', [150, 420, 300, 560]]], null],
    ['dirtLit', 'Дорога на свету', [[r, 'road', [1030, 480, 1180, 600]]], null],
    ['dirtLit2', 'Голая земля поляны на свету (светлая половина)', [[v, 'village', [850, 380, 1100, 470]]], 'l50'],
    ['dirtShade', 'Дорога в тени (тёмная треть яркости)', [[r, 'road', [760, 700, 1250, 1060]]], 'd33'],
    ['pebbleDark', 'Камешки/крап тёмный (5% самых тёмных)', [[r, 'road', [760, 700, 1250, 1060]]], 'd5'],
    ['pebbleLight', 'Крап светлый (3% самых светлых)', [[r, 'road', [1030, 480, 1180, 600]]], 'l3']];
  const out = {};
  console.log('| ключ | что | hex | HSL | откуда | пикселей |');
  for (const [key, name, srcs, flt] of rows) {
    let all = [];
    for (const [img, , reg] of srcs) {
      const px = region(img, reg); let fl = flt;
      if (flt === 'd33') fl = pct(px, 0, 0.33); if (flt === 'l50') fl = pct(px, 0.5, 1);
      if (flt === 'd5') fl = pct(px, 0, 0.05); if (flt === 'l3') fl = pct(px, 0.97, 1);
      if (flt === 'oliveTop') { const o = px.filter(olive); const t = pct(o, 0.5, 1); fl = p => olive(p) && t(p) }
      all = all.concat(fl ? px.filter(fl) : px);
    }
    const m = med(all); const [h, s, l] = hsl(m); out[key] = hex(m);
    const where = srcs.map(([, f, g]) => `${f} x${g[0]}-${g[2]} y${g[1]}-${g[3]}`).join('; ');
    console.log(`| ${key} | ${name} | ${hex(m)} | H${h.toFixed(0)} S${(s * 100).toFixed(0)} L${(l * 100).toFixed(0)} | ${where} | ${all.length} |`);
  }
  fs.writeFileSync(path.join(__dirname, 'palette-measured.json'), JSON.stringify(out, null, 2));
})();

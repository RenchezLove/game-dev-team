// gen-ground-tex.js — tileable ground textures (grass / dirt) for ContrarySurvivor
// Stylized low-poly top-down. Palette matched to docs/contrary-survivor/art/village.png.jpg
// Output: standalone HTML files (inline SVG). Render to PNG via headless Edge.
// Seamless trick: every drawn element that may cross a tile edge is rendered 9x
// at offsets {-S,0,+S} on both axes; the SVG viewBox clips to SxS so anything
// leaving one edge re-enters the opposite edge -> perfect wrap.

const fs = require('fs');
const path = require('path');

const S = 1024; // tile size

// --- deterministic PRNG (mulberry32) ---
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
const pick = (r, arr) => arr[Math.floor(r() * arr.length)];
const rr = (r, a, b) => lerp(a, b, r());

// draw an element 9x (wrap) — `make(dx,dy)` returns an SVG string translated by dx,dy
function wrap(make) {
  let out = '';
  for (let ix = -1; ix <= 1; ix++)
    for (let iy = -1; iy <= 1; iy++)
      out += make(ix * S, iy * S);
  return out;
}

// an organic blob: irregular polygon around (cx,cy) radius ~rad
function blob(r, cx, cy, rad, irregularity, points) {
  const irr = irregularity;
  const n = points;
  let pts = [];
  for (let i = 0; i < n; i++) {
    const ang = (i / n) * Math.PI * 2;
    const rad2 = rad * (1 - irr + r() * irr * 2);
    pts.push([cx + Math.cos(ang) * rad2, cy + Math.sin(ang) * rad2]);
  }
  // smooth-ish via quadratic between midpoints
  let d = `M ${(pts[n - 1][0] + pts[0][0]) / 2} ${(pts[n - 1][1] + pts[0][1]) / 2} `;
  for (let i = 0; i < n; i++) {
    const cur = pts[i];
    const nxt = pts[(i + 1) % n];
    const mx = (cur[0] + nxt[0]) / 2, my = (cur[1] + nxt[1]) / 2;
    d += `Q ${cur[0]} ${cur[1]} ${mx} ${my} `;
  }
  d += 'Z';
  return d;
}

// short grass-stroke speck (tiny flat dash)
function speckStroke(cx, cy, len, ang, w, col) {
  const dx = Math.cos(ang) * len / 2, dy = Math.sin(ang) * len / 2;
  return `<line x1="${(cx - dx).toFixed(1)}" y1="${(cy - dy).toFixed(1)}" x2="${(cx + dx).toFixed(1)}" y2="${(cy + dy).toFixed(1)}" stroke="${col}" stroke-width="${w.toFixed(1)}" stroke-linecap="round"/>`;
}

// =================== GRASS ===================
function grass() {
  const r = rng(20260625);
  // palette sampled/matched from reference (muted natural, slightly cool)
  const base = '#52723C';        // mid grass
  const cols = {
    darkA: '#3C5A33', darkB: '#33502E', // shaded clumps (cooler)
    midA: '#557A3E', midB: '#4E6E3A',
    liteA: '#6E8A47', liteB: '#7C924F', // sunlit
    dryA: '#83864C', dryB: '#8E8A55',   // dry/khaki patches
  };
  let g = '';

  // base fill
  g += `<rect x="0" y="0" width="${S}" height="${S}" fill="${base}"/>`;

  // layer 1: gentle large tonal unevenness — small radius, many, low opacity, tones
  // close to base so NO single big shape anchors the tile repeat.
  g += `<g filter="url(#soft)">`;
  const bigN = 64;
  for (let i = 0; i < bigN; i++) {
    const cx = r() * S, cy = r() * S;
    const rad = rr(r, 60, 125);
    let col;
    const t = r();
    if (t < 0.42) col = pick(r, [cols.darkA, cols.darkB, cols.midB]);
    else if (t < 0.80) col = pick(r, [cols.midA, cols.midB]);
    else col = pick(r, [cols.liteA, cols.midA]);
    const d = blob(r, cx, cy, rad, 0.4, 9);
    const op = rr(r, 0.18, 0.4).toFixed(2);
    g += wrap((dx, dy) => `<path transform="translate(${dx} ${dy})" d="${d}" fill="${col}" opacity="${op}"/>`);
  }
  // a few dry/khaki patches (sparse, like worn grass near paths) — kept small & soft
  for (let i = 0; i < 7; i++) {
    const cx = r() * S, cy = r() * S;
    const rad = rr(r, 45, 95);
    const d = blob(r, cx, cy, rad, 0.5, 8);
    g += wrap((dx, dy) => `<path transform="translate(${dx} ${dy})" d="${d}" fill="${pick(r, [cols.dryA, cols.dryB])}" opacity="${rr(r, 0.16, 0.32).toFixed(2)}"/>`);
  }
  g += `</g>`;

  // layer 2: medium clumps (lighter blur) — carries even visual interest (grass tufts)
  g += `<g filter="url(#fine)">`;
  for (let i = 0; i < 150; i++) {
    const cx = r() * S, cy = r() * S;
    const rad = rr(r, 20, 50);
    const t = r();
    const col = t < 0.5 ? pick(r, [cols.darkA, cols.darkB]) : pick(r, [cols.liteA, cols.liteB]);
    const d = blob(r, cx, cy, rad, 0.5, 7);
    g += wrap((dx, dy) => `<path transform="translate(${dx} ${dy})" d="${d}" fill="${col}" opacity="${rr(r, 0.16, 0.36).toFixed(2)}"/>`);
  }
  g += `</g>`;

  // layer 3: fine grass-blade specks (short flat strokes, multi-direction so no anisotropy)
  g += `<g filter="url(#micro)">`;
  const speckCols = [cols.liteA, cols.liteB, cols.darkA, cols.midA, cols.dryA];
  for (let i = 0; i < 2600; i++) {
    const cx = r() * S, cy = r() * S;
    const len = rr(r, 6, 16);
    const ang = r() * Math.PI * 2; // omnidirectional -> repeat not obvious
    const w = rr(r, 1.3, 2.6);
    const col = pick(r, speckCols);
    const op = rr(r, 0.20, 0.5).toFixed(2);
    g += wrap((dx, dy) => `<g transform="translate(${dx} ${dy})" opacity="${op}">${speckStroke(cx, cy, len, ang, w, col)}</g>`);
  }
  g += `</g>`;

  // subtle overall vignette-free grain dots for break-up
  g += `<g filter="url(#micro)">`;
  for (let i = 0; i < 900; i++) {
    const cx = r() * S, cy = r() * S;
    const rad = rr(r, 1.5, 4);
    const col = pick(r, [cols.darkB, cols.liteB]);
    g += wrap((dx, dy) => `<circle cx="${(cx + dx).toFixed(1)}" cy="${(cy + dy).toFixed(1)}" r="${rad.toFixed(1)}" fill="${col}" opacity="${rr(r, 0.1, 0.3).toFixed(2)}"/>`);
  }
  g += `</g>`;

  return g;
}

// =================== DIRT / ROAD ===================
function dirt() {
  const r = rng(770421);
  const base = '#9A7E55';        // mid trodden earth
  const cols = {
    darkA: '#6F5638', darkB: '#7A5F3C', // damp/edge dark
    midA: '#937a52', midB: '#8A7048',
    liteA: '#B49A6E', liteB: '#C0A878', // dusty light (centre wear)
    pebA: '#5E4A30', pebB: '#cab488',   // small stones / dust
  };
  let g = '';
  g += `<rect x="0" y="0" width="${S}" height="${S}" fill="${base}"/>`;

  // layer 1: gentle large tonal unevenness — small radius, many, low opacity so no
  // big light/dark island anchors the tile repeat.
  g += `<g filter="url(#soft)">`;
  for (let i = 0; i < 60; i++) {
    const cx = r() * S, cy = r() * S;
    const rad = rr(r, 55, 115);
    const t = r();
    let col;
    if (t < 0.4) col = pick(r, [cols.darkA, cols.darkB]);
    else if (t < 0.75) col = pick(r, [cols.midA, cols.midB]);
    else col = pick(r, [cols.liteA, cols.midB]);
    const d = blob(r, cx, cy, rad, 0.42, 9);
    g += wrap((dx, dy) => `<path transform="translate(${dx} ${dy})" d="${d}" fill="${col}" opacity="${rr(r, 0.18, 0.4).toFixed(2)}"/>`);
  }
  g += `</g>`;

  // layer 2: medium dirt mottling — denser, carries even interest
  g += `<g filter="url(#fine)">`;
  for (let i = 0; i < 170; i++) {
    const cx = r() * S, cy = r() * S;
    const rad = rr(r, 16, 46);
    const t = r();
    const col = t < 0.5 ? pick(r, [cols.darkA, cols.darkB]) : pick(r, [cols.liteA, cols.liteB]);
    const d = blob(r, cx, cy, rad, 0.5, 7);
    g += wrap((dx, dy) => `<path transform="translate(${dx} ${dy})" d="${d}" fill="${col}" opacity="${rr(r, 0.14, 0.34).toFixed(2)}"/>`);
  }
  g += `</g>`;

  // layer 3: pebbles / grit specks
  g += `<g filter="url(#micro)">`;
  for (let i = 0; i < 1700; i++) {
    const cx = r() * S, cy = r() * S;
    const rad = rr(r, 1.5, 5);
    const col = pick(r, [cols.pebA, cols.pebB, cols.darkA, cols.liteB]);
    const op = rr(r, 0.2, 0.55).toFixed(2);
    g += wrap((dx, dy) => `<circle cx="${(cx + dx).toFixed(1)}" cy="${(cy + dy).toFixed(1)}" r="${rad.toFixed(1)}" fill="${col}" opacity="${op}"/>`);
  }
  g += `</g>`;

  // faint cracks / scuff dashes (short, omnidirectional)
  g += `<g filter="url(#micro)">`;
  for (let i = 0; i < 500; i++) {
    const cx = r() * S, cy = r() * S;
    const len = rr(r, 8, 22);
    const ang = r() * Math.PI * 2;
    const w = rr(r, 1.0, 2.2);
    const col = pick(r, [cols.darkA, cols.pebA]);
    g += wrap((dx, dy) => `<g opacity="${rr(r, 0.12, 0.3).toFixed(2)}">${speckStroke(cx + dx, cy + dy, len, ang, w, col)}</g>`);
  }
  g += `</g>`;

  return g;
}

// SVG filter defs (soft/fine/micro blur) — gives the painterly low-poly softness
const defs = `
<defs>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="22"/></filter>
  <filter id="fine" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="micro" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.1"/></filter>
</defs>`;

function pageSingle(name, body) {
  // single 1024x1024 tile, locked viewport
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0;width:${S}px;height:${S}px;overflow:hidden;background:#000}
  svg{display:block}
  </style></head><body>
  <svg width="${S}" height="${S}" viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg">
  ${defs}
  ${body}
  </svg></body></html>`;
}

function pageQC(name, body) {
  // 3x3 montage of the SAME tile to inspect seams. Each cell 384px (scaled tile).
  const cell = 341; // 1023/3 ~ keep small render
  const grid = 3;
  const total = cell * grid;
  let cells = '';
  for (let gy = 0; gy < grid; gy++)
    for (let gx = 0; gx < grid; gx++)
      cells += `<g transform="translate(${gx * cell} ${gy * cell}) scale(${cell / S})">
        <svg width="${S}" height="${S}" viewBox="0 0 ${S} ${S}">${defs}${body}</svg></g>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0;width:${total}px;height:${total}px;overflow:hidden;background:#000}
  svg{display:block}
  </style></head><body>
  <svg width="${total}" height="${total}" viewBox="0 0 ${total} ${total}" xmlns="http://www.w3.org/2000/svg">
  ${cells}
  </svg></body></html>`;
}

const outDir = __dirname;
const grassBody = grass();
const dirtBody = dirt();

fs.writeFileSync(path.join(outDir, 'grass-tile.html'), pageSingle('grass', grassBody));
fs.writeFileSync(path.join(outDir, 'dirt-tile.html'), pageSingle('dirt', dirtBody));
fs.writeFileSync(path.join(outDir, 'grass-qc3x3.html'), pageQC('grass', grassBody));
fs.writeFileSync(path.join(outDir, 'dirt-qc3x3.html'), pageQC('dirt', dirtBody));

console.log('written: grass-tile.html, dirt-tile.html, grass-qc3x3.html, dirt-qc3x3.html');
console.log('QC montage cell px:', 341, 'total px:', 341 * 3);

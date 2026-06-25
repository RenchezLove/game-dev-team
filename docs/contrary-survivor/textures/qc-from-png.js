// Build a 3x3 montage page from an exported PNG (tests real exported pixels for seams)
const fs = require('fs');
const path = require('path');
function page(imgAbsUrl, cell) {
  const total = cell * 3;
  let imgs = '';
  for (let y = 0; y < 3; y++)
    for (let x = 0; x < 3; x++)
      imgs += `<img src="${imgAbsUrl}" style="position:absolute;left:${x*cell}px;top:${y*cell}px;width:${cell}px;height:${cell}px;display:block">`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0;width:${total}px;height:${total}px;overflow:hidden;background:#000}
  img{image-rendering:auto}
  </style></head><body>${imgs}</body></html>`;
}
const dir = __dirname;
const cell = 340; // 3*340 = 1020
fs.writeFileSync(path.join(dir, 'grass-qc-png.html'),
  page('file:///E:/ForGameLead(Materials)/ground-tex/grass_1024.png', cell));
fs.writeFileSync(path.join(dir, 'dirt-qc-png.html'),
  page('file:///E:/ForGameLead(Materials)/ground-tex/dirt_1024.png', cell));
console.log('written qc-png htmls, total px', cell*3);

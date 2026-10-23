// Redraw a picture from a reference through the OpenAI images edits endpoint.
// Usage: node edit-image.js <reference.png> "<prompt>" <out.png> [model] [size] [quality]
'use strict';
const fs = require('fs'), path = require('path');
const KEY = fs.readFileSync('E:/ContrarySurvior/ContrarySurvivor/Saved/OpenAIKey.txt', 'utf8').trim();
const [ref, prompt, out, model = 'gpt-image-2.5-sunburst', size = '1536x1024', quality = 'high'] = process.argv.slice(2);
(async () => {
  const fd = new FormData();
  fd.append('model', model); fd.append('prompt', prompt); fd.append('size', size); fd.append('quality', quality); fd.append('n', '1');
  fd.append('image', new Blob([fs.readFileSync(ref)], { type: 'image/png' }), path.basename(ref));
  for (let i = 0; ; i++) {
    try {
      const r = await fetch('https://api.openai.com/v1/images/edits', { method: 'POST', headers: { Authorization: 'Bearer ' + KEY }, body: fd });
      const j = await r.json(); if (j.error) { console.log('ОШИБКА', JSON.stringify(j.error)); process.exit(1); }
      fs.writeFileSync(out, Buffer.from(j.data[0].b64_json, 'base64')); console.log('ok', out, JSON.stringify(j.usage)); return;
    } catch (e) { if (i >= 4) throw e; console.log('повтор', i + 1, e.cause && e.cause.code); await new Promise(r => setTimeout(r, 5000)); }
  }
})();

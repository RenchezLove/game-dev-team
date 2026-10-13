// Picture generation through the OpenAI API. No third-party packages.
// The key is read from the file named in OPENAI_KEY_FILE, or from the game folder Saved/OpenAIKey.txt (not in git,
// next to the other keys of the project). The key is never printed.
//   node gen-image.js --check                       -> is the key accepted, which picture models are available
//   node gen-image.js "<prompt>" <out.png> [size] [quality] [model]
//     size: 1024x1024 | 1536x1024 | 1024x1536 (default 1024x1024); quality: low | medium | high (default medium)
// Every generation is appended to apps/team-dashboard/data/openai-usage.json (count and tokens), the dashboard shows it.
'use strict';
const https = require('https'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), KEY_FILE = process.env.OPENAI_KEY_FILE || 'E:/ContrarySurvior/ContrarySurvivor/Saved/OpenAIKey.txt', USAGE = path.join(ROOT, 'apps', 'team-dashboard', 'data', 'openai-usage.json');

function call(method, url, body) {
  let key; try { key = fs.readFileSync(KEY_FILE, 'utf8').trim(); } catch { return Promise.resolve({ status: 0, error: 'Нет файла с ключом: ' + KEY_FILE }); }
  if (!key) return Promise.resolve({ status: 0, error: 'Файл с ключом пуст.' });
  const data = body ? JSON.stringify(body) : null;
  return new Promise(res => {
    const req = https.request(url, { method, headers: Object.assign({ Authorization: 'Bearer ' + key }, data ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } : {}) }, r => {
      const ch = []; r.on('data', d => ch.push(d)); r.on('end', () => { let j = null; try { j = JSON.parse(Buffer.concat(ch).toString('utf8')); } catch { }
        res({ status: r.statusCode, json: j, error: r.statusCode >= 400 ? ((j && j.error && j.error.message) || 'HTTP ' + r.statusCode) : null }); });
    });
    req.setTimeout(300000, () => { req.destroy(); res({ status: 0, error: 'Сервер OpenAI не ответил за 5 минут.' }); });
    req.on('error', e => res({ status: 0, error: 'Нет связи с OpenAI: ' + e.message })); req.end(data || undefined);
  });
}

// Is the key accepted, and which picture models does it see.
async function check() {
  const r = await call('GET', 'https://api.openai.com/v1/models');
  if (r.error) return { ok: false, error: r.error, status: r.status };
  return { ok: true, imageModels: r.json.data.map(m => m.id).filter(id => /image|dall-e/i.test(id)).sort() };
}

async function generate(prompt, out, size = '1024x1024', quality = 'medium', model = 'gpt-image-1') {
  const r = await call('POST', 'https://api.openai.com/v1/images/generations', { model, prompt, size, quality, n: 1 });
  if (r.error) return { ok: false, error: r.error, status: r.status };
  const b64 = r.json.data && r.json.data[0] && r.json.data[0].b64_json; if (!b64) return { ok: false, error: 'В ответе нет картинки.' };
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true }); fs.writeFileSync(out, Buffer.from(b64, 'base64'));
  let u = { images: 0, tokens: 0, log: [] }; try { u = JSON.parse(fs.readFileSync(USAGE, 'utf8')); } catch { }
  const tok = (r.json.usage && r.json.usage.total_tokens) || 0;
  u.images++; u.tokens += tok; u.last = Date.now(); u.log = (u.log || []).concat({ t: Date.now(), model, size, quality, tokens: tok, out: path.resolve(out).replace(/\\/g, '/') }).slice(-200);
  fs.writeFileSync(USAGE, JSON.stringify(u, null, 1));
  return { ok: true, out: path.resolve(out), bytes: fs.statSync(out).size, model, size, quality, usage: r.json.usage || null };
}

module.exports = { check, generate, KEY_FILE, USAGE };
if (require.main === module) (async () => {
  const a = process.argv.slice(2);
  const r = a[0] === '--check' ? await check() : a.length >= 2 ? await generate(a[0], a[1], a[2], a[3], a[4]) : { ok: false, error: 'Использование: node gen-image.js --check | "<описание>" <файл.png> [размер] [качество] [модель]' };
  console.log(JSON.stringify(r, null, 1)); process.exit(r.ok ? 0 : 1);
})();

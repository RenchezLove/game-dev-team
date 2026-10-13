// Picture generation through the OpenAI API. No third-party packages.
// The key is read from the file named in OPENAI_KEY_FILE, or from the game folder Saved/OpenAIKey.txt (not in git,
// next to the other keys of the project). The key is never printed.
//
//   node gen-image.js --check
//       is the key accepted, which picture models are available
//   node gen-image.js "<prompt>" <out.png> [--model=...] [--quality=...] [--size=...] [--transparent]
//
// WHICH MODEL (rule of the team, from the OpenAI model pages and price list read on 2026-10-13):
//   gpt-image-1-mini        rough drafts and many variants: the cheapest one
//   gpt-image-2.5-flare     DEFAULT. Everyday final pictures: icons, interface art, references for the modeller
//   gpt-image-2.5-sunburst  the most capable; take it when the picture needs precise work or must follow a reference closely
// Quality: low for drafts, medium by default, high for final pictures (2.5 models also know xhigh and max).
// Size: 1024x1024 (default), 1536x1024, 1024x1536. --transparent gives a PNG with a transparent background (icons).
//
// Every generation is appended to apps/team-dashboard/data/openai-usage.json (count, tokens, price); the dashboard shows it.
'use strict';
const https = require('https'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), KEY_FILE = process.env.OPENAI_KEY_FILE || 'E:/ContrarySurvior/ContrarySurvivor/Saved/OpenAIKey.txt', USAGE = path.join(ROOT, 'apps', 'team-dashboard', 'data', 'openai-usage.json');
const DEFAULT_MODEL = 'gpt-image-2.5-flare';
// Dollars per million tokens: [text input, image input, image output]. Source: platform.openai.com/docs/pricing, 2026-10-13.
const PRICE = { 'gpt-image-2.5-sunburst': [5, 8, 30], 'gpt-image-2.5-flare': [5, 8, 30], 'gpt-image-2': [5, 8, 30], 'gpt-image-1.5': [5, 8, 32], 'gpt-image-1-mini': [2, 2.5, 8], 'gpt-image-1': [5, 10, 40], 'chatgpt-image-latest': [5, 8, 32] };
function costOf(model, usage) { const p = PRICE[Object.keys(PRICE).find(k => model === k || model.startsWith(k + '-')) || ''], u = usage || {}; if (!p || !usage) return null;
  const d = u.input_tokens_details || {}, text = d.text_tokens != null ? d.text_tokens : (u.input_tokens || 0), img = d.image_tokens || 0;
  return (text * p[0] + img * p[1] + (u.output_tokens || 0) * p[2]) / 1e6; }

function call(method, url, body) {
  let key; try { key = fs.readFileSync(KEY_FILE, 'utf8').trim(); } catch { return Promise.resolve({ status: 0, error: 'Нет файла с ключом: ' + KEY_FILE }); }
  if (!key) return Promise.resolve({ status: 0, error: 'Файл с ключом пуст.' });
  const data = body ? JSON.stringify(body) : null;
  return new Promise(res => {
    const req = https.request(url, { method, headers: Object.assign({ Authorization: 'Bearer ' + key }, data ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } : {}) }, r => {
      const ch = []; r.on('data', d => ch.push(d)); r.on('end', () => { let j = null; try { j = JSON.parse(Buffer.concat(ch).toString('utf8')); } catch { }
        res({ status: r.statusCode, json: j, error: r.statusCode >= 400 ? ((j && j.error && j.error.message) || 'HTTP ' + r.statusCode) : null }); });
    });
    req.setTimeout(600000, () => { req.destroy(); res({ status: 0, error: 'Сервер OpenAI не ответил за 10 минут.' }); });
    req.on('error', e => res({ status: 0, error: 'Нет связи с OpenAI: ' + e.message })); req.end(data || undefined);
  });
}

// Is the key accepted, and which picture models does it see.
async function check() {
  const r = await call('GET', 'https://api.openai.com/v1/models');
  if (r.error) return { ok: false, error: r.error, status: r.status };
  return { ok: true, imageModels: r.json.data.map(m => m.id).filter(id => /image|dall-e/i.test(id)).sort() };
}

// opts: { size, quality, model, transparent }
async function generate(prompt, out, opts = {}) {
  const model = opts.model || DEFAULT_MODEL, size = opts.size || '1024x1024', quality = opts.quality || 'medium';
  const body = { model, prompt, size, quality, n: 1 }; if (opts.transparent) { body.background = 'transparent'; body.output_format = 'png'; }
  const r = await call('POST', 'https://api.openai.com/v1/images/generations', body);
  if (r.error) return { ok: false, error: r.error, status: r.status };
  const b64 = r.json.data && r.json.data[0] && r.json.data[0].b64_json; if (!b64) return { ok: false, error: 'В ответе нет картинки.' };
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true }); fs.writeFileSync(out, Buffer.from(b64, 'base64'));
  let u = { images: 0, tokens: 0, cost: 0, log: [] }; try { u = JSON.parse(fs.readFileSync(USAGE, 'utf8')); } catch { }
  const tok = (r.json.usage && r.json.usage.total_tokens) || 0, cost = costOf(model, r.json.usage);
  u.images = (u.images || 0) + 1; u.tokens = (u.tokens || 0) + tok; u.cost = (u.cost || 0) + (cost || 0); u.last = Date.now();
  u.log = (u.log || []).concat({ t: Date.now(), model, size, quality, tokens: tok, cost, out: path.resolve(out).replace(/\\/g, '/') }).slice(-1000);
  try { fs.mkdirSync(path.dirname(USAGE), { recursive: true }); fs.writeFileSync(USAGE, JSON.stringify(u, null, 1)); } catch { }
  return { ok: true, out: path.resolve(out), bytes: fs.statSync(out).size, model, size, quality, costUsd: cost, usage: r.json.usage || null };
}

module.exports = { check, generate, costOf, KEY_FILE, USAGE, DEFAULT_MODEL, PRICE };
if (require.main === module) (async () => {
  const a = process.argv.slice(2), flags = {}, pos = [];
  for (const x of a) { const m = x.match(/^--([\w-]+)(?:=(.*))?$/); if (m) flags[m[1]] = m[2] === undefined ? true : m[2]; else pos.push(x); }
  const r = flags.check ? await check() : pos.length >= 2 ? await generate(pos[0], pos[1], { size: flags.size || pos[2], quality: flags.quality || pos[3], model: flags.model || pos[4], transparent: !!flags.transparent })
    : { ok: false, error: 'Использование: node gen-image.js --check | "<описание>" <файл.png> [--model=...] [--quality=low|medium|high] [--size=1024x1024] [--transparent]' };
  console.log(JSON.stringify(r, null, 1)); process.exit(r.ok ? 0 : 1);
})();

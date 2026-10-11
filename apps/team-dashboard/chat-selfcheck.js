// Usage: node chat-selfcheck.js <empty folder> <file to create outside it>. Adds a scratch project 'Проба' (remove it from data/projects.json afterwards).
// Self-check of the chat: a message to a plain Claude in a scratch folder, with a permission request answered by "allow".
const http = require('http'); const B = 'http://127.0.0.1:47821';
const post = (p, d) => fetch(B + p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) }).then(r => r.json());
(async () => {
  const teamRoot = process.argv[2], target = process.argv[3];
  const pr = await post('/api/projects', { name: 'Проба', teamRoot }); console.log('project', JSON.stringify(pr));
  const P = '?project=' + pr.id; let done = false;
  http.get(B + '/api/chat/events', res => { res.on('data', async d => { for (const l of String(d).split('\n')) { if (!l.startsWith('data: ')) continue; const e = JSON.parse(l.slice(6));
    if (e.kind === 'text') console.log('TEXT', e.text.slice(0, 200)); if (e.kind === 'activity') console.log('ACT', e.current.lead);
    if (e.kind === 'limits') console.log('LIMITS five', e.limits.five && e.limits.five.utilization, 'seven', e.limits.seven && e.limits.seven.utilization);
    if (e.kind === 'permission') { console.log('PERMISSION', e.request.tool, JSON.stringify(e.request.input).slice(0, 160)); console.log('permit', JSON.stringify(await post('/api/chat/permit' + P, { id: e.request.id, allow: true }))); }
    if (e.kind === 'result') console.log('RESULT denials', JSON.stringify(e.denials).slice(0, 300), 'cost', e.cost);
    if (e.kind === 'status' && !e.running && done) { const h = await (await fetch(B + '/api/chat/history' + P)).json(); console.log('HISTORY', h.messages.map(m => m.role + ': ' + m.text.slice(0, 120)).join(' || ')); process.exit(0); }
    if (e.kind === 'status' && e.running) done = true; } }); });
  await new Promise(r => setTimeout(r, 500));
  console.log('send', JSON.stringify(await post('/api/chat/send' + P, { text: 'Инструментом Write создай файл ' + target + ' с одним словом «проба». Потом ответь одним словом: готово.' })));
  setTimeout(() => { console.log('TIMEOUT'); process.exit(1); }, 170000);
})();

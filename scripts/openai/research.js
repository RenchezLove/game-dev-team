// Web research through the OpenAI Responses API with the web search tool, run in background mode and polled
// (a long research answer outlives an ordinary request). Usage: node research.js <question.txt> <out.md> [model]
'use strict';
const fs = require('fs'), KEY = fs.readFileSync('E:/ContrarySurvior/ContrarySurvivor/Saved/OpenAIKey.txt', 'utf8').trim();
const [q, out, model = 'gpt-5.5'] = process.argv.slice(2), H = { Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' };
const sl = ms => new Promise(r => setTimeout(r, ms));
// The connection to OpenAI sometimes drops (ECONNRESET): retry each request a few times.
async function req(url, opt) { for (let i = 0; ; i++) { try { return await (await fetch(url, opt)).json(); } catch (e) { if (i >= 8) throw e; console.log('связь оборвалась, повтор', i + 1, e.cause && e.cause.code); await sl(5000 * (i + 1)); } } }
(async () => {
  let j = await req('https://api.openai.com/v1/responses', { method: 'POST', headers: H,
    body: JSON.stringify({ model, background: true, input: fs.readFileSync(q, 'utf8'), tools: [{ type: 'web_search' }], reasoning: { effort: 'high' } }) });
  if (j.error) { console.log('ОШИБКА', JSON.stringify(j.error)); process.exit(1); }
  console.log('запрос', j.id, j.status);
  while (['queued', 'in_progress'].includes(j.status)) { await sl(15000); j = await req('https://api.openai.com/v1/responses/' + j.id, { headers: H }); }
  if (j.status !== 'completed') { console.log('СТАТУС', j.status, JSON.stringify(j.error || j.incomplete_details)); process.exit(1); }
  const text = (j.output || []).filter(o => o.type === 'message').flatMap(o => o.content).filter(c => c.type === 'output_text').map(c => c.text).join('\n\n');
  fs.writeFileSync(out, text); console.log('ok', model, 'символов', text.length, 'расход', JSON.stringify(j.usage));
})();

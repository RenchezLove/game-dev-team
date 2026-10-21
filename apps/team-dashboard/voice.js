// Voice mode: a live spoken conversation with an OpenAI Realtime model inside the "Моя команда" window.
// The browser talks to OpenAI directly over WebRTC with a short-lived key minted here; the real key never leaves this server.
// The model hands work to the team lead through three tools that the page executes with the existing chat endpoints
// (/api/chat/send, /api/chat/history, /api/chat/stop) — no second way of running the team.
// Docs read 2026-10-14: developers.openai.com/api/docs/guides/realtime-webrtc, realtime-conversations, realtime-costs,
// api/reference .../realtime/client_secrets/methods/create, models/gpt-realtime-2.1(-mini).
'use strict';
const https = require('https'), fs = require('fs'), path = require('path');

// Dollars per 1M tokens: [text in, cached in, text out, audio in, cached audio in, audio out] — model pages, 2026-10-14.
const PRICE = { 'gpt-realtime-2.1': [4, 0.4, 24, 32, 0.4, 64], 'gpt-realtime-2.1-mini': [0.6, 0.06, 2.4, 10, 0.3, 20] };
const DEFAULTS = { model: 'gpt-realtime-2.1', voice: 'marin', dailyUsd: 3 };

const TOOLS = [
  { type: 'function', name: 'send_task', description: 'Передать готовое подробное техническое задание руководителю команды GameLead. Вызывать только когда задача обсуждена и Ринат согласился её отправить. GameLead выполняет одну задачу за раз.',
    parameters: { type: 'object', properties: { task: { type: 'string', description: 'Полное техническое задание по-русски: цель, что именно сделать, ограничения, как понять, что готово. Пиши так, чтобы его понял исполнитель, не слышавший разговора.' } }, required: ['task'] } },
  { type: 'function', name: 'get_status', description: 'Узнать, работает ли сейчас GameLead, чем занят, ждёт ли разрешения, и получить его последний ответ.', parameters: { type: 'object', properties: {} } },
  { type: 'function', name: 'stop_task', description: 'Остановить текущую работу GameLead. Только после того, как Ринат явно подтвердил остановку.', parameters: { type: 'object', properties: {} } }];

// Owner's decision 2026-10-20: the voice model is only the ears and the voice of GameLead. It does not answer by itself:
// what the owner says goes into the main chat as his message, and the lead's answer is read out aloud.
function voiceOfLead(p) {
  return `Ты — голос руководителя команды GameLead в программе «Моя команда». Ринат делает игру «${p.name}». Сам ты ничего не решаешь и по существу не отвечаешь: всё, что говорит Ринат, программа передаёт GameLead в чат, а ответы GameLead присылает тебе, чтобы ты прочитал их вслух.
Правила:
- Говори по-русски, от первого лица, как будто это говорит сам GameLead, живо и естественно.
- Когда программа просит прочитать ответ, читай его близко к тексту, ничего не добавляя от себя. Пути к файлам, имена файлов, команды и технические строки не читай: вместо них скажи «подробности в чате» или «картинку я показал в чате».
- Когда программа просит коротко подтвердить, что услышал, скажи одну короткую фразу вроде «Понял, сейчас посмотрю». Без вопросов и без обещаний.
- Если Ринат перебивает, сразу замолкай.`;
}

function instructions(p, ctx) {
  const read = f => ctx.readText(f);
  // The lead's "now" block: the first part of his memory file, so the voice knows where the project stands.
  const mem = read(path.join(p.teamRoot, 'context', p.agent || 'game-lead', 'context.md')).split(/\r?\n/).slice(0, 40).join('\n').slice(0, 4000);
  const chat = ctx.readJson(path.join(ctx.DATA, 'chat-' + p.id + '.json'), { messages: [] }).messages.slice(-6)
    .map(m => (m.role === 'user' ? 'Ринат → GameLead: ' : 'GameLead: ') + String(m.text || '').slice(0, 1200)).join('\n');
  const talk = ctx.readJson(voiceFile(p, ctx), { lines: [] }).lines.slice(-30).map(l => (l.role === 'user' ? 'Ринат: ' : 'Ты: ') + l.text).join('\n');
  return `Ты — голосовой помощник Рината в программе «Моя команда». Ринат делает игру «${p.name}» с командой ИИ-разработчиков. Командой руководит GameLead (Claude Code): он распределяет работу между программистом, оператором Unreal Engine, 3D-моделлером, художником и тестировщиком, меняет код и файлы, генерирует картинки через OpenAI и модели через Tripo.
Твоя роль: живой собеседник. Обсуждай идеи, задавай уточняющие вопросы, спорь по делу, помогай додумать. Сам ничего в проекте не делаешь — для работы есть GameLead.
Правила:
- Говори по-русски, живо и коротко, как в обычном разговоре. Без списков и разметки, без английских терминов без нужды.
- Когда задача обсуждена, сформулируй подробное техническое задание и коротко перескажи Ринату суть. Отправляй через send_task, когда Ринат согласился («да», «отправляй» и т. п.). Если он сразу сказал «поручи» или «отправь», переспрашивать не нужно.
- Не выдумывай факты о проекте. Не знаешь — так и скажи или спроси у GameLead через задание.
- Состояние работы узнавай через get_status. Останавливай работу через stop_task только после явного подтверждения Рината.
- Сообщения, начинающиеся с «[Программа]», пишет программа, а не Ринат. Если в нём результат GameLead — перескажи Ринату главное простыми словами в двух-трёх фразах и предложи, что делать дальше.
- Пока GameLead работает, продолжай разговор на любые темы.

Что сейчас известно о проекте (память GameLead, начало):
${mem || '(нет)'}

Последние сообщения в чате с GameLead:
${chat || '(нет)'}

Конец прошлого голосового разговора:
${talk || '(разговора ещё не было)'}`;
}

const voiceFile = (p, ctx) => path.join(ctx.DATA, 'voice-' + p.id + '.json');
const usageFile = ctx => path.join(ctx.DATA, 'voice-usage.json');
const settings = ctx => Object.assign({}, DEFAULTS, ctx.readJson(path.join(ctx.DATA, 'voice-settings.json'), {}));
const today = () => new Date().toLocaleDateString('sv');
function usageState(ctx) { const u = ctx.readJson(usageFile(ctx), { total: 0, days: {}, log: [] }), s = settings(ctx), d = u.days[today()] || 0;
  return { today: d, total: u.total || 0, dailyUsd: s.dailyUsd, over: d >= s.dailyUsd, model: s.model }; }

// Cost of one response from its usage block. Field names as the API returned them (logged raw in the usage file).
function costOf(model, u) { const p = PRICE[model] || PRICE[DEFAULTS.model]; if (!u) return 0;
  const i = u.input_token_details || {}, o = u.output_token_details || {}, c = i.cached_tokens_details || {};
  const cachedText = c.text_tokens || 0, cachedAudio = c.audio_tokens != null ? c.audio_tokens : (i.cached_tokens || 0) - cachedText;
  const inText = Math.max(0, (i.text_tokens != null ? i.text_tokens : 0) - cachedText), inAudio = i.audio_tokens != null ? Math.max(0, i.audio_tokens - cachedAudio) : Math.max(0, (u.input_tokens || 0) - (i.cached_tokens || 0));
  const outText = o.text_tokens || 0, outAudio = o.audio_tokens != null ? o.audio_tokens : (u.output_tokens || 0) - outText;
  return (inText * p[0] + cachedText * p[1] + outText * p[2] + inAudio * p[3] + Math.max(0, cachedAudio) * p[4] + outAudio * p[5]) / 1e6; }

function mint(ctx, session) { return new Promise(res => {
  let key = ''; try { key = fs.readFileSync(ctx.keyFile, 'utf8').trim().split(/\r?\n/)[0].trim(); } catch { }
  if (!key) return res({ error: 'Нет ключа OpenAI (файл ' + ctx.keyFile + ').' });
  const data = JSON.stringify({ expires_after: { anchor: 'created_at', seconds: 120 }, session });
  const r = https.request('https://api.openai.com/v1/realtime/client_secrets', { method: 'POST', timeout: 20000, headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } }, q => {
    let b = ''; q.on('data', d => b += d); q.on('end', () => { let j = null; try { j = JSON.parse(b); } catch { }
      res(j && j.value ? { value: j.value } : { error: 'OpenAI не выдал голосовой пропуск: ' + ((j && j.error && j.error.message) || 'HTTP ' + q.statusCode) }); }); });
  r.on('error', e => res({ error: 'Нет связи с OpenAI: ' + e.message })); r.on('timeout', () => { r.destroy(); res({ error: 'OpenAI не ответил.' }); }); r.end(data); }); }

// Returns true when the request was a voice request and has been answered.
async function handle(u, req, res, p, ctx) {
  if (!u.pathname.startsWith('/api/voice/')) return false;
  const { send, body } = ctx;
  if (u.pathname === '/api/voice/state') { send(res, 200, usageState(ctx)); return true; }
  if (u.pathname === '/api/voice/session' && req.method === 'POST') {
    const st = usageState(ctx), s = settings(ctx);
    if (st.over) { send(res, 200, { error: `Дневной предел расходов на голос ($${s.dailyUsd}) исчерпан. Его можно поднять в файле data/voice-settings.json.` }); return true; }
    // No automatic answers (create_response: false): the page decides when to speak. The owner's speech still
    // interrupts the voice (interrupt_response: true).
    const r = await mint(ctx, { type: 'realtime', model: s.model, instructions: voiceOfLead(p),
      audio: { input: { transcription: { model: 'gpt-4o-mini-transcribe', language: 'ru' }, turn_detection: { type: 'semantic_vad', create_response: false, interrupt_response: true }, noise_reduction: { type: 'near_field' } }, output: { voice: s.voice } } });
    send(res, 200, Object.assign(r, { model: s.model })); return true; }
  if (u.pathname === '/api/voice/log' && req.method === 'POST') { const b = await body(req), text = String(b.text || '').trim().slice(0, 4000);
    if (text && (b.role === 'user' || b.role === 'assistant')) { const f = voiceFile(p, ctx), v = ctx.readJson(f, { lines: [] }); v.lines.push({ t: Date.now(), role: b.role, text }); if (v.lines.length > 500) v.lines.splice(0, v.lines.length - 500); ctx.writeJson(f, v); }
    send(res, 200, { ok: true }); return true; }
  if (u.pathname === '/api/voice/usage' && req.method === 'POST') { const b = await body(req), model = settings(ctx).model, cost = costOf(model, b.usage);
    const f = usageFile(ctx), all = ctx.readJson(f, { total: 0, days: {}, log: [] }); all.total = (all.total || 0) + cost; all.days[today()] = (all.days[today()] || 0) + cost;
    all.log = (all.log || []).concat({ t: Date.now(), model, cost, usage: b.usage || null }).slice(-300); ctx.writeJson(f, all); send(res, 200, usageState(ctx)); return true; }
  if (u.pathname === '/api/voice/history') { send(res, 200, { lines: ctx.readJson(voiceFile(p, ctx), { lines: [] }).lines.slice(-40) }); return true; }
  send(res, 404, { error: 'нет такого адреса' }); return true;
}

module.exports = { handle, costOf, PRICE, TOOLS };

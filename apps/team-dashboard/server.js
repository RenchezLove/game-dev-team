// "Моя команда" — local dashboard over the installed Claude Code. No third-party packages.
// Listens on 127.0.0.1 only. Start: node server.js (or start.cmd). Data lives in ./data and in <teamRoot>/tasks.
'use strict';
const http = require('http'), fs = require('fs'), path = require('path'), { spawn, execFile } = require('child_process');
const PORT = 47821, ROOT = __dirname, DATA = path.join(ROOT, 'data'), PUB = path.join(ROOT, 'public');
fs.mkdirSync(DATA, { recursive: true });

const readJson = (f, d) => { try { return JSON.parse(fs.readFileSync(f, 'utf8').replace(/^\uFEFF/, '')); } catch { return d; } };
const writeJson = (f, v) => { fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, JSON.stringify(v, null, 1), 'utf8'); };
const run = (cmd, args, cwd, ms = 8000) => new Promise(res => execFile(cmd, args, { cwd, timeout: ms, windowsHide: true, maxBuffer: 4e6 }, (e, out) => res(e ? '' : String(out))));
const norm = p => path.resolve(p).replace(/\\/g, '/').toLowerCase();
const inside = (root, p) => { const r = norm(root), q = norm(p); return q === r || q.startsWith(r + '/'); };

// ---------- projects ----------
const PROJ_FILE = path.join(DATA, 'projects.json');
function projects() {
  let p = readJson(PROJ_FILE, null);
  if (!p) {
    p = [{ id: 'marevo', name: 'Марево', teamRoot: 'E:/game-dev-team', gameRoot: 'E:/ContrarySurvior/ContrarySurvivor', agent: 'game-lead',
      contentRoot: 'E:/ContrarySurvior/ContrarySurvivor/Content', adb: 'E:/Android/sdk/platform-tools/adb.exe', editorProcess: 'UnrealEditor.exe',
      docs: [{ title: 'Игра: дизайн, тексты, отчёты', path: 'E:/game-dev-team/docs/contrary-survivor' }, { title: 'Решения и общие документы', path: 'E:/game-dev-team/docs', flat: true },
        { title: 'Память команды', path: 'E:/game-dev-team/context' }] }];
    writeJson(PROJ_FILE, p);
  }
  return p;
}
const proj = id => projects().find(p => p.id === id) || projects()[0];
const tasksFile = p => path.join(p.teamRoot, 'tasks', p.id + '.json');

// ---------- overview ----------
async function overview(p) {
  const [tl, adb, head, log] = await Promise.all([
    run('tasklist', ['/FI', 'IMAGENAME eq ' + (p.editorProcess || 'none.exe'), '/NH'], ROOT),
    p.adb && fs.existsSync(p.adb) ? run(p.adb, ['devices'], ROOT, 5000) : Promise.resolve(''),
    p.gameRoot ? run('git', ['log', '-1', '--pretty=%D|%h|%s'], p.gameRoot) : Promise.resolve(''),
    p.gameRoot ? run('git', ['log', '--since=midnight', '--pretty=%ct|%s', '-n', '15'], p.gameRoot) : Promise.resolve('')]);
  const h = head.trim().split('|');
  const branch = (h[0] || '').replace(/^HEAD -> /, '').split(',')[0];
  const done = log.split('\n').filter(l => l && !/\|Merge /.test(l)).map(l => { const i = l.indexOf('|'); return { t: +l.slice(0, i) * 1000, text: l.slice(i + 1) }; });
  const ts = readJson(tasksFile(p), { tasks: [] }).tasks, day = new Date().toDateString();
  for (const t of ts) if (t.status === 'done' && t.updated && new Date(t.updated).toDateString() === day) done.push({ t: t.updated, text: 'Задача готова: ' + t.title });
  done.sort((a, b) => b.t - a.t);
  const status = readJson(path.join(p.teamRoot, 'tasks', p.id + '-status.json'), {});
  return { editor: tl.toLowerCase().includes((p.editorProcess || '###').toLowerCase()), phone: /\n\S+\s+device\b/.test(adb), branch, head: h[1] || '', headText: h.slice(2).join('|'), done: done.slice(0, 12),
    status, limits: readJson(path.join(DATA, 'limits.json'), null), costs: readJson(path.join(DATA, 'costs.json'), { total: 0, runs: 0 }), ollama: await ollama() };
}
function ollama() {
  return new Promise(res => { const r = http.get({ host: '127.0.0.1', port: 11434, path: '/api/tags', timeout: 1500 }, q => { let b = ''; q.on('data', d => b += d); q.on('end', () => { try { res({ up: true, models: JSON.parse(b).models.map(m => m.name) }); } catch { res({ up: true, models: [] }); } }); });
    r.on('error', () => res({ up: false, models: [] })); r.on('timeout', () => { r.destroy(); res({ up: false, models: [] }); }); });
}

// ---------- documents ----------
const DOC_EXT = ['.md', '.txt', '.svg', '.png', '.jpg', '.json', '.csv'];
function docTree(p) {
  const walk = (dir, depth, flat) => { let out = []; let list = []; try { list = fs.readdirSync(dir, { withFileTypes: true }); } catch { return out; }
    for (const e of list.sort((a, b) => (a.isDirectory() === b.isDirectory() ? a.name.localeCompare(b.name, 'ru') : a.isDirectory() ? -1 : 1))) {
      if (e.name.startsWith('.') || e.name.startsWith('_')) continue; const full = path.join(dir, e.name).replace(/\\/g, '/');
      if (e.isDirectory()) { if (flat || depth > 3) continue; const ch = walk(full, depth + 1, false); if (ch.length) out.push({ name: e.name, dir: true, children: ch }); }
      else if (DOC_EXT.includes(path.extname(e.name).toLowerCase())) out.push({ name: e.name, path: full, size: fs.statSync(full).size });
    } return out; };
  return (p.docs || []).map(g => ({ name: g.title, dir: true, root: true, children: walk(g.path, 0, g.flat) }));
}
const docAllowed = (p, f) => (p.docs || []).some(g => inside(g.path, f));

// ---------- assets ----------
const TYPES = [[/^(SM_|SK_|SKM_)/, 'model', 'Модель'], [/^(T_|TX_)/, 'texture', 'Текстура'], [/^(M_|MI_|MF_|ML_)/, 'material', 'Материал'], [/^WBP_/, 'window', 'Окно и интерфейс'],
  [/^(ABP_|AM_|AS_|A_|Anim|BS_)/, 'anim', 'Анимация'], [/^BP_/, 'object', 'Объект игры'], [/^(DT_|DA_|CT_)/, 'data', 'Данные'], [/^(S_|SW_|SC_|SFX_|weapon_|music_)/i, 'sound', 'Звук']];
function scanAssets(p) {
  const out = []; const root = p.contentRoot; if (!root || !fs.existsSync(root)) return { assets: [], scanned: Date.now(), note: 'Папка содержимого игры не найдена' };
  const walk = dir => { for (const e of fs.readdirSync(dir, { withFileTypes: true })) { const full = path.join(dir, e.name);
    if (e.isDirectory()) { if (!/^(__ExternalActors__|__ExternalObjects__|Collections|Developers)$/.test(e.name)) walk(full); continue; }
    const ext = path.extname(e.name).toLowerCase(); if (ext !== '.uasset' && ext !== '.umap') continue;
    const name = path.basename(e.name, ext), rel = path.relative(root, dir).replace(/\\/g, '/'), st = fs.statSync(full);
    let type = ext === '.umap' ? 'level' : 'other'; if (ext !== '.umap') { for (const [re, t] of TYPES) if (re.test(name)) { type = t; break; } if (type === 'other' && /audio|sound|music/i.test(rel)) type = 'sound'; }
    out.push({ name, type, folder: rel, kb: Math.round(st.size / 1024), m: Math.round(st.mtimeMs) }); } };
  walk(root); const res = { assets: out, scanned: Date.now() }; writeJson(path.join(DATA, 'assets-' + p.id + '.json'), res); return res;
}

// ---------- chat with the team lead ----------
const clients = new Set(); let child = null, current = null;
const chatFile = p => path.join(DATA, 'chat-' + p.id + '.json');
const emit = ev => { const s = 'data: ' + JSON.stringify(ev) + '\n\n'; for (const c of clients) c.write(s); };
function chatSend(p, text, images) {
  if (child) return { error: 'Руководитель ещё отвечает на прошлое сообщение. Дождитесь ответа или нажмите «Остановить».' };
  const chat = readJson(chatFile(p), { session: null, messages: [] });
  chat.messages.push({ role: 'user', text, images: (images || []).length, t: Date.now() }); writeJson(chatFile(p), chat);
  let cmd = 'claude -p --input-format stream-json --output-format stream-json --verbose --permission-prompts host --permission-prompt-tool stdio';
  if (p.agent && /^[\w-]+$/.test(p.agent)) cmd += ' --agent ' + p.agent;
  if (chat.session && /^[\w-]+$/.test(chat.session)) cmd += ' --resume ' + chat.session;
  child = spawn(cmd, { cwd: p.teamRoot, shell: true, windowsHide: true }); const me = child;
  current = { project: p.id, started: Date.now(), agents: {}, lead: 'Читает задачу', pending: {}, answer: '' };
  emit({ kind: 'status', running: true, current });
  let buf = '', errText = '';
  const finish = () => { if (child !== me) return; child = null; const c = readJson(chatFile(p), { session: null, messages: [] });
    if (current.answer.trim()) c.messages.push({ role: 'lead', text: current.answer.trim(), t: Date.now() });
    else if (errText.trim()) c.messages.push({ role: 'error', text: errText.trim().slice(0, 1500), t: Date.now() });
    if (current.session) c.session = current.session; writeJson(chatFile(p), c); current = null; emit({ kind: 'status', running: false }); };
  child.stdout.on('data', d => { buf += d; let i; while ((i = buf.indexOf('\n')) >= 0) { const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1); if (line) { try { onEvent(p, JSON.parse(line), me); } catch (e) { /* not json */ } } } });
  child.stderr.on('data', d => { errText += d; });
  child.on('close', finish); child.on('error', e => { errText += String(e); finish(); });
  const content = [{ type: 'text', text: text || 'Посмотри приложенные картинки.' }];
  for (const im of images || []) content.push({ type: 'image', source: { type: 'base64', media_type: im.media_type, data: im.data } });
  child.stdin.write(JSON.stringify({ type: 'user', message: { role: 'user', content } }) + '\n');
  return { ok: true };
}
function onEvent(p, e, proc) {
  if (!current) return;
  if (e.session_id) current.session = e.session_id;
  if (e.type === 'assistant' && e.message && Array.isArray(e.message.content)) {
    for (const b of e.message.content) {
      if (b.type === 'text' && b.text && !e.parent_tool_use_id) { current.answer += (current.answer ? '\n\n' : '') + b.text; emit({ kind: 'text', text: b.text }); }
      if (b.type === 'tool_use') {
        const what = (b.input && (b.input.description || b.input.summary)) || b.name;
        if (b.name === 'Agent' && !e.parent_tool_use_id) current.agents[b.id] = { name: (b.input && (b.input.name || b.input.subagent_type)) || 'специалист', text: what, state: 'work', t: Date.now() };
        else if (e.parent_tool_use_id && current.agents[e.parent_tool_use_id]) current.agents[e.parent_tool_use_id].text = what;
        else current.lead = what;
        emit({ kind: 'activity', current });
      }
    }
  } else if (e.type === 'user' && e.message && Array.isArray(e.message.content)) {
    for (const b of e.message.content) if (b.type === 'tool_result' && current.agents[b.tool_use_id]) { current.agents[b.tool_use_id].state = 'done'; emit({ kind: 'activity', current }); }
  } else if (e.type === 'rate_limit_event' && e.rate_limit_info) {
    const li = e.rate_limit_info, w = li.unifiedWindows || {}; const lim = { t: Date.now(), status: li.status, five: w.five_hour || null, seven: w.seven_day || null };
    if (!lim.five && !lim.seven && li.rateLimitType) lim[li.rateLimitType === 'five_hour' ? 'five' : 'seven'] = { utilization: li.utilization, resetsAt: li.resetsAt };
    writeJson(path.join(DATA, 'limits.json'), lim); emit({ kind: 'limits', limits: lim });
  } else if (e.type === 'control_request' && e.request && e.request.subtype === 'can_use_tool') {
    current.pending[e.request_id] = { id: e.request_id, tool: e.request.tool_name, input: e.request.input, t: Date.now() }; current.lead = 'Ждёт вашего разрешения';
    emit({ kind: 'permission', request: current.pending[e.request_id], current });
  } else if (e.type === 'result') {
    current.lead = 'Закончил'; const c = readJson(path.join(DATA, 'costs.json'), { total: 0, runs: 0 }); c.total += e.total_cost_usd || 0; c.runs++; writeJson(path.join(DATA, 'costs.json'), c);
    if (e.is_error && e.result) current.answer += (current.answer ? '\n\n' : '') + '⚠ ' + e.result;
    emit({ kind: 'result', denials: e.permission_denials || [], cost: e.total_cost_usd || 0 });
    try { proc.stdin.end(); } catch { }
  }
}
function chatPermit(id, allow) {
  if (!child || !current || !current.pending[id]) return { error: 'Этот запрос уже неактуален.' };
  const rq = current.pending[id]; delete current.pending[id];
  const response = allow ? { behavior: 'allow', updatedInput: rq.input } : { behavior: 'deny', message: 'Владелец проекта отклонил это действие в окне программы.' };
  child.stdin.write(JSON.stringify({ type: 'control_response', response: { subtype: 'success', request_id: id, response } }) + '\n');
  current.lead = allow ? 'Продолжает работу' : 'Получил отказ, ищет другой путь'; emit({ kind: 'activity', current }); return { ok: true };
}
function chatStop() { if (!child) return { ok: true }; const pid = child.pid; execFile('taskkill', ['/PID', String(pid), '/T', '/F'], { windowsHide: true }, () => { }); return { ok: true }; }

// ---------- http ----------
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };
const send = (res, code, body, type = 'application/json; charset=utf-8') => { res.writeHead(code, { 'Content-Type': type, 'Cache-Control': 'no-store' }); res.end(typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body)); };
const body = req => new Promise(res => { const ch = []; req.on('data', d => ch.push(d)); req.on('end', () => { try { res(JSON.parse(Buffer.concat(ch).toString('utf8') || '{}')); } catch { res({}); } }); });

http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, 'http://x'), q = Object.fromEntries(u.searchParams), p = proj(q.project);
    // Only this computer and only this page may call the server.
    if (req.headers.origin && req.headers.origin !== 'http://127.0.0.1:' + PORT) return send(res, 403, { error: 'forbidden' });
    if (u.pathname === '/api/projects' && req.method === 'GET') return send(res, 200, projects());
    if (u.pathname === '/api/projects' && req.method === 'POST') { const b = await body(req); if (!b.name || !b.teamRoot || !fs.existsSync(b.teamRoot)) return send(res, 400, { error: 'Нужны название и существующая папка команды.' });
      const all = projects(); const id = ('p' + Date.now()); all.push({ id, name: String(b.name).slice(0, 60), teamRoot: b.teamRoot, gameRoot: b.gameRoot || '', contentRoot: b.contentRoot || '', agent: b.agent || '', docs: b.docsPath ? [{ title: 'Документы', path: b.docsPath }] : [] }); writeJson(PROJ_FILE, all); return send(res, 200, { ok: true, id }); }
    if (u.pathname === '/api/overview') return send(res, 200, await overview(p));
    if (u.pathname === '/api/tasks' && req.method === 'GET') return send(res, 200, readJson(tasksFile(p), { tasks: [] }));
    if (u.pathname === '/api/tasks' && req.method === 'POST') { const b = await body(req), f = tasksFile(p), d = readJson(f, { tasks: [] });
      if (b.action === 'delete') d.tasks = d.tasks.filter(t => t.id !== b.id);
      else if (b.task) { const t = b.task; t.updated = Date.now(); const i = d.tasks.findIndex(x => x.id === t.id); if (i >= 0) d.tasks[i] = Object.assign(d.tasks[i], t); else { t.id = 't' + Date.now(); t.created = Date.now(); d.tasks.push(t); } }
      writeJson(f, d); return send(res, 200, d); }
    if (u.pathname === '/api/docs/tree') return send(res, 200, docTree(p));
    if (u.pathname === '/api/docs/file' && req.method === 'GET') { if (!q.path || !docAllowed(p, q.path) || !fs.existsSync(q.path)) return send(res, 404, { error: 'нет такого документа' });
      const ext = path.extname(q.path).toLowerCase(); if (['.png', '.jpg', '.svg'].includes(ext)) return send(res, 200, fs.readFileSync(q.path), MIME[ext]);
      const st = fs.statSync(q.path); return send(res, 200, { path: q.path, text: fs.readFileSync(q.path, 'utf8').replace(/^\uFEFF/, '').slice(0, 400000), size: st.size, m: st.mtimeMs }); }
    if (u.pathname === '/api/docs/file' && req.method === 'POST') { const b = await body(req); if (!b.path || !docAllowed(p, b.path) || !/\.(md|txt)$/i.test(b.path) || typeof b.text !== 'string') return send(res, 400, { error: 'Этот файл править нельзя.' });
      if (fs.existsSync(b.path)) fs.copyFileSync(b.path, path.join(DATA, 'backup-' + path.basename(b.path))); fs.writeFileSync(b.path, b.text, 'utf8'); return send(res, 200, { ok: true }); }
    if (u.pathname === '/api/assets') { const f = path.join(DATA, 'assets-' + p.id + '.json'); return send(res, 200, q.refresh || !fs.existsSync(f) ? scanAssets(p) : readJson(f, { assets: [] })); }
    if (u.pathname === '/api/chat/history') { const c = readJson(chatFile(p), { session: null, messages: [] }); return send(res, 200, { messages: c.messages.slice(-60), running: !!child, current }); }
    if (u.pathname === '/api/chat/send' && req.method === 'POST') { const b = await body(req); return send(res, 200, chatSend(p, String(b.text || ''), b.images)); }
    if (u.pathname === '/api/chat/permit' && req.method === 'POST') { const b = await body(req); return send(res, 200, chatPermit(b.id, !!b.allow)); }
    if (u.pathname === '/api/chat/stop' && req.method === 'POST') return send(res, 200, chatStop());
    if (u.pathname === '/api/chat/new' && req.method === 'POST') { if (child) return send(res, 200, { error: 'Сначала дождитесь ответа или остановите работу.' }); const c = readJson(chatFile(p), { messages: [] }); c.session = null; c.messages.push({ role: 'note', text: 'Начат новый разговор: руководитель начнёт с чистого листа и прочитает память команды.', t: Date.now() }); writeJson(chatFile(p), c); return send(res, 200, { ok: true }); }
    if (u.pathname === '/api/chat/events') { res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-store', Connection: 'keep-alive' }); res.write('data: ' + JSON.stringify({ kind: 'status', running: !!child, current }) + '\n\n'); clients.add(res); req.on('close', () => clients.delete(res)); return; }
    // static files
    let f = path.join(PUB, u.pathname === '/' ? 'index.html' : decodeURIComponent(u.pathname)); if (!inside(PUB, f) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) return send(res, 404, 'not found', 'text/plain');
    return send(res, 200, fs.readFileSync(f), MIME[path.extname(f).toLowerCase()] || 'application/octet-stream');
  } catch (e) { send(res, 500, { error: String(e && e.message || e) }); }
}).listen(PORT, '127.0.0.1', () => console.log('Моя команда: http://127.0.0.1:' + PORT));
setInterval(() => { for (const c of clients) c.write(': ping\n\n'); }, 25000);

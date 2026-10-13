// What the dashboard does when the team lead is cut off by the subscription limit:
// 1) snapshots every working copy into a side branch (working tree, index and current branch stay untouched),
// 2) writes a hand-off note for the lead, 3) asks the local model (Ollama) for a short summary.
// The local model also answers in the chat until the limit resets. It has no tools: it cannot change anything.
'use strict';
const fs = require('fs'), path = require('path'), os = require('os'), http = require('http'), { execFile, spawn } = require('child_process');

const git = (cwd, args, env, ms = 60000) => new Promise(res => execFile('git', ['-c', 'core.quotepath=false', ...args], { cwd, env: env || process.env, timeout: ms, windowsHide: true, maxBuffer: 16e6 },
  (e, out, err) => res({ ok: !e, out: String(out || '').replace(/\s+$/, ''), err: String(err || (e && e.message) || '').trim() })));
const pad = n => String(n).padStart(2, '0');
const stampOf = d => `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
const human = t => { const d = new Date(t); return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`; };

// ---------- snapshots ----------
// All working copies of the project: the team folder plus every git worktree of the game, except the excluded ones.
async function copies(p) {
  const out = [];
  if (p.teamRoot && fs.existsSync(p.teamRoot)) out.push(p.teamRoot);
  if (p.gameRoot && fs.existsSync(p.gameRoot)) {
    const w = await git(p.gameRoot, ['worktree', 'list', '--porcelain']);
    const list = w.ok ? w.out.split('\n').filter(l => l.startsWith('worktree ')).map(l => l.slice(9).trim()) : [p.gameRoot];
    for (const d of list) if (!(p.saveSkipCopies || []).includes(path.basename(d)) && fs.existsSync(d)) out.push(d);
  }
  return [...new Set(out.map(d => d.replace(/\\/g, '/')))];
}

// Stores the current state of one working copy as a commit on a side branch "save/limit-<time>-<copy>".
// It works through a temporary index file, so nothing in the copy itself changes.
async function snapshot(dir, stamp, skipFiles) {
  const r = { dir, name: path.basename(dir).replace(/[^\w.-]/g, '_') };
  const head = await git(dir, ['rev-parse', 'HEAD']);
  if (!head.ok) return Object.assign(r, { error: 'не удалось прочитать состояние: ' + head.err.slice(0, 200) });
  r.head = head.out.slice(0, 7);
  r.branch = (await git(dir, ['branch', '--show-current'])).out || 'без ветки';
  r.headText = (await git(dir, ['log', '-1', '--pretty=%s'])).out;
  const st = await git(dir, ['status', '--porcelain']);
  r.changes = st.out ? st.out.split('\n') : [];
  if (!r.changes.length) return Object.assign(r, { clean: true });
  const tmp = path.join(os.tmpdir(), `team-save-${stamp}-${r.name}.idx`), env = Object.assign({}, process.env, { GIT_INDEX_FILE: tmp });
  try {
    const idx = await git(dir, ['rev-parse', '--git-path', 'index']);
    try { fs.copyFileSync(path.resolve(dir, idx.out), tmp); } catch { await git(dir, ['read-tree', 'HEAD'], env); }
    const add = await git(dir, ['add', '-A'], env, 20 * 60000); if (!add.ok) throw new Error(add.err);
    for (const f of skipFiles || []) await git(dir, ['reset', '-q', 'HEAD', '--', f], env); // files with secrets stay out of the snapshot
    const tree = await git(dir, ['write-tree'], env); if (!tree.ok) throw new Error(tree.err);
    if (tree.out === (await git(dir, ['rev-parse', 'HEAD^{tree}'])).out) return Object.assign(r, { clean: true, onlySkipped: true });
    const c = await git(dir, ['commit-tree', tree.out, '-p', head.out, '-m', `Автосохранение при обрыве по лимиту ${human(Date.now())} (ветка ${r.branch})`]); if (!c.ok) throw new Error(c.err);
    r.saved = `save/limit-${stamp}-${r.name}`; r.commit = c.out.slice(0, 7);
    const up = await git(dir, ['update-ref', 'refs/heads/' + r.saved, c.out]); if (!up.ok) throw new Error(up.err);
  } catch (e) { r.error = String(e.message || e).slice(0, 300); delete r.saved; }
  finally { try { fs.unlinkSync(tmp); } catch { } try { fs.unlinkSync(tmp + '.lock'); } catch { } }
  return r;
}

// ---------- local model ----------
const getTags = () => new Promise(res => { const r = http.get({ host: '127.0.0.1', port: 11434, path: '/api/tags', timeout: 2000 }, q => { let b = ''; q.on('data', d => b += d); q.on('end', () => { try { res(JSON.parse(b).models.map(m => m.name)); } catch { res([]); } }); });
  r.on('error', () => res(null)); r.on('timeout', () => { r.destroy(); res(null); }); });
// Returns the list of installed models; starts Ollama if it is not running. null = could not start.
async function ensureOllama() {
  let m = await getTags(); if (m) return m;
  try { spawn('ollama', ['serve'], { detached: true, stdio: 'ignore', windowsHide: true }).on('error', () => { }).unref(); } catch { return null; }
  for (let i = 0; i < 20 && !m; i++) { await new Promise(r => setTimeout(r, 1000)); m = await getTags(); }
  return m;
}
const pickModel = (p, models) => (p.localModel && models.includes(p.localModel)) ? p.localModel : models[0];

// Streams one chat answer. Returns { promise -> { ok, text, error, model }, abort() }.
function localChat(p, messages, onDelta, ms = 10 * 60000) {
  let req = null, stopped = false;
  const promise = (async () => {
    const models = await ensureOllama();
    if (!models) return { ok: false, error: 'Локальная нейросеть не запущена, и запустить её не удалось.' };
    if (!models.length) return { ok: false, error: 'В локальной нейросети не установлено ни одной модели.' };
    if (stopped) return { ok: false, error: 'Остановлено.' };
    const model = pickModel(p, models), payload = JSON.stringify({ model, messages, stream: true, options: { num_ctx: 16384 } });
    return await new Promise(res => {
      let text = '', buf = '', done = false; const end = v => { if (!done) { done = true; res(Object.assign({ model }, v)); } };
      req = http.request({ host: '127.0.0.1', port: 11434, path: '/api/chat', method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) } }, q => {
        q.setEncoding('utf8');
        q.on('data', d => { buf += d; let i; while ((i = buf.indexOf('\n')) >= 0) { const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1); if (!line) continue;
          try { const j = JSON.parse(line); if (j.error) return end({ ok: false, error: String(j.error) }); const t = j.message && j.message.content; if (t) { text += t; if (onDelta) onDelta(t); } } catch { } } });
        q.on('end', () => end(text.trim() ? { ok: true, text: text.trim() } : { ok: false, error: 'Локальная нейросеть вернула пустой ответ.' }));
      });
      req.setTimeout(ms, () => { req.destroy(); end(text.trim() ? { ok: true, text: text.trim() + '\n\n(ответ оборван по времени)' } : { ok: false, error: 'Локальная нейросеть не ответила за отведённое время.' }); });
      req.on('error', e => end(stopped ? { ok: false, error: 'Остановлено.', text: text.trim() } : { ok: false, error: 'Нет связи с локальной нейросетью: ' + e.message }));
      req.end(payload);
    });
  })();
  return { promise, abort: () => { stopped = true; if (req) req.destroy(); } };
}

// ---------- hand-off note ----------
const noteFile = p => { const dir = path.join(p.teamRoot, 'context', p.agent || ''); return path.join(p.agent && fs.existsSync(dir) ? dir : p.teamRoot, 'handoff.md').replace(/\\/g, '/'); };
const readHead = (f, n) => { try { return fs.readFileSync(f, 'utf8').replace(/^﻿/, '').slice(0, n); } catch { return ''; } };
const who = { user: 'Ринат', lead: 'Руководитель', local: 'Локальная нейросеть', error: 'Ошибка', note: 'Программа' };

function buildNote(info, snaps, summary) {
  const cur = info.cur || {}, L = [];
  L.push(`# Работа оборвалась из-за лимита подписки — ${human(info.when)}`, '',
    'Эту запись сделала программа «Моя команда» автоматически. Руководителю: прочитай её перед продолжением и сверь с живым состоянием файлов — запись описывает момент обрыва, а не то, что происходит сейчас.', '',
    `Лимит должен сброситься: ${info.until ? human(info.until) : 'время неизвестно'}.`, '', '## Что делалось в момент обрыва');
  L.push(`- Последнее действие руководителя: ${cur.lead || 'неизвестно'}.`);
  if (cur.started) L.push(`- Работа над последним сообщением шла ${Math.max(1, Math.round((info.when - cur.started) / 60000))} мин.`);
  const ag = Object.values(cur.agents || {});
  for (const a of ag) L.push(`- Специалист «${a.name}» — ${a.state === 'done' ? 'успел сдать работу' : 'НЕ закончил, работа оборвана'}: ${a.text}`);
  if (!ag.length) L.push('- Специалисты в этот момент не работали.');
  L.push('', '## Состояние рабочих копий');
  for (const s of snaps) {
    L.push(`### ${s.dir}`);
    if (s.error && !s.head) { L.push(`- ОШИБКА: ${s.error}`, ''); continue; }
    L.push(`- Ветка \`${s.branch}\`, последняя запись \`${s.head}\` «${s.headText || ''}».`);
    if (s.clean) L.push(s.onlySkipped ? '- Несохранённые изменения есть только в файлах, которые в сохранение не берутся (пароли).' : '- Несохранённых изменений нет.');
    else {
      L.push(s.saved ? `- Несохранённые изменения записаны в отдельную ветку \`${s.saved}\` (запись \`${s.commit}\`). Сами файлы, текущая ветка и подготовленные к записи изменения не тронуты.` : `- СОХРАНИТЬ НЕ УДАЛОСЬ: ${s.error}`);
      L.push('- Изменённые файлы:', ...s.changes.slice(0, 40).map(c => '  - `' + c.trim() + '`'));
      if (s.changes.length > 40) L.push(`  - …и ещё ${s.changes.length - 40}.`);
    }
    L.push('');
  }
  L.push('## Последние сообщения');
  for (const m of (info.messages || []).slice(-6)) L.push(`**${who[m.role] || m.role}** (${human(m.t)}): ${String(m.text || '(картинка)').slice(0, 1500)}`, '');
  L.push('## Заметка локальной нейросети', summary || 'Заметка ещё не написана.', '');
  return L.join('\n');
}

// Runs the whole rescue. onStep(text) reports progress, setAbort(fn) lets the caller cancel the local model.
async function save(p, info, onStep, setAbort) {
  const stamp = stampOf(new Date(info.when)), file = noteFile(p), all = await copies(p), snaps = [];
  const team = (p.teamRoot || '').replace(/\\/g, '/');
  for (const d of all.filter(x => x !== team)) { onStep && onStep('Сохраняет рабочую копию ' + path.basename(d)); snaps.push(await snapshot(d, stamp, p.saveSkipFiles)); }
  const teamStub = { dir: team, name: path.basename(team), branch: (await git(team, ['branch', '--show-current'])).out, head: (await git(team, ['rev-parse', '--short', 'HEAD'])).out, headText: (await git(team, ['log', '-1', '--pretty=%s'])).out,
    saved: `save/limit-${stamp}-${path.basename(team).replace(/[^\w.-]/g, '_')}`, commit: 'эта запись', changes: ((await git(team, ['status', '--porcelain'])).out || '').split('\n').filter(Boolean).concat('?? ' + path.relative(team, file).replace(/\\/g, '/')) };
  fs.writeFileSync(file, buildNote(info, [teamStub, ...snaps], 'Локальная нейросеть ещё пишет заметку.'), 'utf8');
  onStep && onStep('Локальная нейросеть пишет заметку о том, на чём остановились');
  let summary = '';
  if (info.noModel) summary = 'Заметка не запрашивалась.';
  else {
    const job = localChat(p, [{ role: 'system', content: 'Ты — помощник команды разработки игры. Отвечай по-русски, законченными предложениями, простыми словами.' },
      { role: 'user', content: 'Работа руководителя команды оборвалась из-за лимита. Ниже служебная запись о моменте обрыва. Напиши короткую заметку, не больше двенадцати строк: что делалось, что уже сделано, что осталось и с чего начать после возвращения. Пиши только то, что прямо следует из записи. Ничего не выдумывай. Если чего-то из записи не видно — так и скажи.\n\n' + buildNote(info, [teamStub, ...snaps], '—').slice(0, 14000) }], null, 6 * 60000);
    setAbort && setAbort(job.abort);
    const a = await job.promise; setAbort && setAbort(null);
    summary = a.ok ? `Написала модель \`${a.model}\`. Это пересказ записи выше, а не проверенные факты.\n\n${a.text}` : 'Заметку написать не удалось: ' + a.error;
  }
  fs.writeFileSync(file, buildNote(info, [teamStub, ...snaps], summary), 'utf8');
  onStep && onStep('Сохраняет папку команды');
  const ts = await snapshot(team, stamp, p.saveSkipFiles);
  return { file, stamp, snaps: [ts, ...snaps], summaryOk: !/^Заметку написать не удалось/.test(summary) };
}

// Context for the local model when it answers in the chat instead of the lead.
function chatContext(p, history, noteText) {
  const mem = readHead(path.join(p.teamRoot, 'context', p.agent || '', 'context.md'), 9000);
  const sys = 'Ты — резервный помощник команды разработки игры. Основной руководитель команды сейчас недоступен: исчерпан лимит подписки. Отвечай владельцу проекта Ринату по-русски, коротко, законченными предложениями, без жаргона. '
    + 'У тебя нет инструментов: ты не можешь читать и менять файлы, запускать программы и специалистов. Если просят что-то сделать — честно скажи, что это сделает руководитель после сброса лимита, и предложи записать задачу. '
    + 'Отвечай только по сведениям ниже; если ответа в них нет — так и скажи, не выдумывай.'
    + (noteText ? '\n\n=== Запись о моменте обрыва ===\n' + noteText.slice(0, 6000) : '') + (mem ? '\n\n=== Память руководителя (начало файла) ===\n' + mem : '');
  const msgs = [{ role: 'system', content: sys }];
  for (const m of history.filter(m => ['user', 'lead', 'local'].includes(m.role) && m.text).slice(-10)) msgs.push({ role: m.role === 'user' ? 'user' : 'assistant', content: String(m.text).slice(0, 3000) });
  return msgs;
}

module.exports = { save, snapshot, copies, localChat, chatContext, noteFile, human };

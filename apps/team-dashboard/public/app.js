'use strict';
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const S = { project: localStorage.project || '', tab: ['home', 'tasks', 'docs', 'assets', 'team', 'costs'].includes(location.hash.slice(1)) ? location.hash.slice(1) : 'home', tasks: [], assets: [], doc: null, images: [], running: false, current: null, live: '', taskFilter: 'all', assetFilter: 'all', assetShown: 120, asset: null, q: '' };
const api = async (url, data) => { const sep = url.includes('?') ? '&' : '?'; const r = await fetch(url + sep + 'project=' + encodeURIComponent(S.project), data ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) } : undefined); return r.json(); };
const time = t => new Date(t).toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' });
const TYPE = { feature: 'фича', bug: 'ошибка', change: 'правка', idea: 'идея' };
const COLS = [['idea', 'Идеи'], ['queue', 'В очереди'], ['work', 'В работе'], ['check', 'Проверить вам'], ['done', 'Готово']];
const ATYPE = { all: ['Все', '🧱'], tools: ['Инструменты разработки', '🛠'], model: ['Модели', '🧊'], texture: ['Текстуры', '🖼'], material: ['Материалы', '🎨'], window: ['Окна и интерфейс', '🪟'], object: ['Объекты игры', '⚙'], anim: ['Анимации', '🏃'], sound: ['Звуки', '🔊'], data: ['Данные', '📊'], level: ['Уровни', '🗺'], other: ['Прочее', '📦'] };

// ---------- tabs ----------
function show(tab) { S.tab = tab; $$('.page').forEach(p => p.classList.toggle('hidden', p.id !== tab)); $$('.nav[data-tab]').forEach(n => n.classList.toggle('on', n.dataset.tab === tab));
  if (tab === 'tasks') drawTasks(); if (tab === 'docs' && !$('#docTree').dataset.ready) loadDocs(); if (tab === 'assets') loadAssets(); if (tab === 'costs') drawCosts(); if (tab === 'team') loadTeam(); }
$$('.nav[data-tab]').forEach(n => n.onclick = () => show(n.dataset.tab));
$('#search').oninput = e => { S.q = e.target.value.trim().toLowerCase(); if (S.tab === 'home' && S.q) show('tasks'); else if (S.tab === 'tasks') drawTasks(); else if (S.tab === 'assets') { S.assetShown = 120; drawAssets(); } else if (S.tab === 'docs') filterDocs(); };

// ---------- projects ----------
async function loadProjects() { const ps = await (await fetch('/api/projects')).json(); if (!ps.find(p => p.id === S.project)) S.project = ps[0].id;
  $('#project').innerHTML = ps.map(p => `<option value="${esc(p.id)}"${p.id === S.project ? ' selected' : ''}>Проект: ${esc(p.name)}</option>`).join(''); }
$('#project').onchange = e => { S.project = localStorage.project = e.target.value; $('#docTree').dataset.ready = ''; S.assets = []; S.doc = null; boot(); };
$('#addProject').onclick = () => modal(`<h2>Новый проект</h2><label>Название</label><input id="pn"><label>Папка команды (там память, документы и задачи)</label><input id="pt" placeholder="E:/my-team"><label>Папка игры (необязательно)</label><input id="pg"><label>Папка содержимого игры для банка ассетов (необязательно)</label><input id="pc"><label>Папка документов (необязательно)</label><input id="pd"><label>Имя руководителя-агента (необязательно)</label><input id="pa" placeholder="game-lead">
  <div class="acts"><div class="btn s g" id="mNo">Отмена</div><div class="btn s" id="mOk">Добавить</div></div>`, async () => { const r = await api('/api/projects', { name: $('#pn').value, teamRoot: $('#pt').value, gameRoot: $('#pg').value, contentRoot: $('#pc').value, docsPath: $('#pd').value, agent: $('#pa').value }); if (r.error) return alertBox(r.error); S.project = localStorage.project = r.id; closeModal(); boot(); });

// ---------- modal ----------
function modal(html, onOk) { $('#modalBody').innerHTML = html; $('#modal').classList.remove('hidden'); const no = $('#mNo'), ok = $('#mOk'); if (no) no.onclick = closeModal; if (ok) ok.onclick = onOk; }
function closeModal() { $('#modal').classList.add('hidden'); $('#modalBody').style.width = ''; }
function alertBox(text) { modal(`<p>${esc(text)}</p><div class="acts"><div class="btn s" id="mNo">Понятно</div></div>`); }
$('#modal').onclick = e => { if (e.target.id === 'modal') closeModal(); };

// ---------- overview and right column ----------
async function loadOverview() { const o = await api('/api/overview'); S.over = o; drawRight(); drawHome(); if (S.tab === 'costs') drawCosts(); }
function limitBar(title, w) { if (!w) return ''; const pc = Math.round((w.utilization || 0) * 100); const cls = pc >= 90 ? 'r' : pc >= 70 ? 'w' : ''; const d = new Date(w.resetsAt * 1000);
  const when = d.toDateString() === new Date().toDateString() ? 'сегодня в ' + time(d) : d.toLocaleDateString('ru', { weekday: 'long', day: 'numeric', month: 'long' }) + ' в ' + time(d);
  return `<div class="bar"><u class="${cls}" style="width:${pc}%"></u></div><small>${title}: израсходовано ${pc} %, сброс ${when}</small>`; }
const money = v => '$ ' + (+v).toFixed(2), day = t => new Date(t).toLocaleDateString('ru');
// What is known about the money at OpenAI, in plain words.
function oaText() { const oa = (S.over && S.over.openai) || {}, sp = oa.spend || {}, b = sp.budget;
  if (!oa.key) return 'Ключ не подключён.'; if (!oa.ok) return 'Ключ есть, но OpenAI его не принял: ' + esc(oa.error);
  let t = `Ключ работает. Картинок сделано командой: ${oa.images}. `;
  if (!sp.admin) return t + 'Сколько денег осталось, OpenAI обычному ключу не сообщает. Программа может считать остаток сама, если дать ей второй ключ. <span class="lnk2" data-oaset>Как это включить</span>';
  if (sp.error) return t + 'Сведения о тратах получить не удалось: ' + esc(sp.error) + ' <span class="lnk2" data-oaset>Настройка</span>';
  if (b) return t + `С ${day(b.since)} потрачено ${money(sp.spent)}. Осталось примерно ${money(Math.max(0, b.amount - sp.spent))} из ${money(b.amount)}. <span class="lnk2" data-oaset>Изменить</span>`;
  return t + `За последние 30 дней потрачено ${money(sp.spent)}. Чтобы видеть остаток, <span class="lnk2" data-oaset>укажите, сколько вы положили на счёт</span>.`; }
function trText() { const tr = (S.over && S.over.tripo) || {}; if (!tr.key) return 'Ключ не подключён.'; if (!tr.ok) return 'Ключ есть, но Tripo не ответил: ' + esc(tr.error || '');
  return `Осталось кредитов: ${tr.balance}.${tr.frozen ? ' Заморожено под текущие заказы: ' + tr.frozen + '.' : ''} Проверено в ${time(tr.checked)}.`; }
function oaSetup() { const b = ((S.over && S.over.openai && S.over.openai.spend) || {}).budget || {};
  modal(`<h2>Остаток денег на счёте OpenAI</h2><p>OpenAI не отдаёт программам сам остаток, но отдаёт сумму трат. Поэтому программа считает так: сколько вы положили на счёт минус сколько потрачено с того дня.</p>
   <p style="margin-top:8px"><b>Шаг 1.</b> Создайте второй ключ — «ключ администратора» — на странице <a href="https://platform.openai.com/settings/organization/admin-keys" target="_blank" style="color:#8fc7ff">Admin keys</a>. Обычный ключ траты читать не может.</p>
   <p style="margin-top:8px"><b>Шаг 2.</b> Сохраните его одной строкой в файл <code>E:\\ContrarySurvior\\ContrarySurvivor\\Saved\\OpenAIAdminKey.txt</code>. В чат ключ не вставляйте.</p>
   <p style="margin-top:8px"><b>Шаг 3.</b> Укажите здесь, сколько денег вы положили и когда, и нажмите «Сохранить».</p>
   <label>Сколько долларов положили на счёт</label><input id="oaAmount" type="number" step="0.01" value="${b.amount || ''}"><label>Когда положили</label><input id="oaSince" type="date" value="${b.since ? new Date(b.since).toISOString().slice(0, 10) : new Date().toISOString().slice(0, 10)}">
   <div class="acts"><div class="btn s g" id="mNo">Закрыть</div><div class="btn s" id="mOk">Сохранить</div></div>`, async () => { const r = await api('/api/openai/budget', { amount: $('#oaAmount').value, since: $('#oaSince').value }); if (r.error) return alertBox(r.error); closeModal(); await api('/api/resources/refresh?what=openai', {}); loadOverview(); }); }
function drawRight() { const o = S.over || {}, l = o.limits, ol = o.ollama || {}, oa = o.openai || {}, tr = o.tripo || {};
  const rf = k => `<i class="rf ${S.refreshing === k ? 'spin' : ''}" data-rf="${k}" title="Обновить сведения">⟳</i>`;
  $('#resources').innerHTML = `<div class="res"><b><span>Claude · подписка</span><span>лимит ${rf('claude')}</span></b>${l ? limitBar('Сессия (5 часов)', l.five) + limitBar('Неделя', l.seven) + `<small class="dim">Замер от ${time(l.t)}.</small>` : '<small>Проценты появятся после первого ответа руководителя или по значку обновления.</small>'}</div>
   <div class="res"><b><span>OpenAI · картинки</span><span>${oa.key && oa.ok ? 'подключён' : 'нет связи'} ${rf('openai')}</span></b><small>${oaText()}</small></div>
   <div class="res"><b><span>Tripo · 3D-модели</span><span>${tr.key && tr.ok ? 'подключён' : 'нет связи'} ${rf('tripo')}</span></b><small>${trText()}</small></div>
   <div class="res"><b><span>Локальная модель</span><span>бесплатно ${rf('ollama')}</span></b><small>${ol.up ? 'Работает на этом компьютере. Модели: ' + esc(ol.models.join(', ') || 'не загружены') : 'Сейчас не запущена.'}</small></div>`;
  $$('[data-rf]').forEach(b => b.onclick = async () => { if (S.refreshing) return; S.refreshing = b.dataset.rf; drawRight(); const r = await api('/api/resources/refresh?what=' + b.dataset.rf, {}); S.refreshing = ''; await loadOverview(); if (r.error) alertBox(r.error); });
  $$('[data-oaset]').forEach(b => b.onclick = oaSetup);
  const st = o.status || {};
  $('#state').innerHTML = [['Редактор игры', o.editor ? 'открыт' : 'закрыт'], ['Телефон', o.phone ? 'подключён' : 'не подключён'], ['Ветка игры', o.branch || '—'], ['Последняя запись', o.head || '—'], ['Автопроверки', st.tests || '—'], ['На телефоне', st.onPhone || '—'], ['В магазине', st.inStore || '—']]
    .map(r => `<div class="kv"><span>${r[0]}</span><b>${esc(r[1])}</b></div>`).join('');
  $('#pillStore').textContent = st.inStore ? 'в магазине ' + st.inStore : ''; $('#pillPhone').textContent = o.phone ? '📱 телефон подключён' : ''; }
function drawHome() { const o = S.over || {}, c = S.current;
  const rows = []; rows.push(`<div class="ag"><span class="dot ${S.running ? '' : 'x'}"></span><b>Руководитель</b><span class="t">${esc(S.running ? (c && c.lead) || 'Работает' : 'Свободен')}</span><i>${S.running && c ? Math.max(1, Math.round((Date.now() - c.started) / 60000)) + ' мин' : ''}</i></div>`);
  if (c) for (const a of Object.values(c.agents || {})) rows.push(`<div class="ag"><span class="dot ${a.state === 'done' ? 'x' : 'y'}"></span><b>${esc(a.name)}</b><span class="t">${esc(a.text)}</span><i>${a.state === 'done' ? 'сдал' : 'работает'}</i></div>`);
  $('#workList').innerHTML = rows.join('');
  $('#doneList').innerHTML = (o.done || []).map(d => `<div class="ag"><span class="dot"></span><span class="t" title="${esc(d.text)}">${esc(d.text)}</span><i>${time(d.t)}</i></div>`).join('') || '<p class="dim">Сегодня записей пока нет.</p>';
  const chk = S.tasks.filter(t => t.status === 'check'), nx = S.tasks.filter(t => t.status === 'queue').slice(0, 6);
  $('#waitN').textContent = chk.length ? '— ' + chk.length : '';
  $('#waitList').innerHTML = chk.map(t => `<div class="ag click" data-task="${t.id}"><span class="tag ${t.type}">${TYPE[t.type] || ''}</span><span class="t">${esc(t.title)}</span><i>открыть</i></div>`).join('') || '<p class="dim">Сейчас от вас ничего не требуется.</p>';
  $('#nextList').innerHTML = nx.map(t => `<div class="ag click" data-task="${t.id}"><span class="tag ${t.type}">${TYPE[t.type] || ''}</span><span class="t">${esc(t.title)}</span><i>в очереди</i></div>`).join('') || '<p class="dim">Очередь пуста.</p>';
  $$('[data-task]').forEach(e => e.onclick = () => editTask(S.tasks.find(t => t.id === e.dataset.task))); }

// ---------- chat ----------
const IMG_RE = /(?:[A-Za-z]:[\\/])[^\s"'<>|*?`()\[\]]+\.(?:png|jpe?g|webp|gif)/gi;
// Pictures whose full paths are mentioned in a message are shown under it.
function pics(text) { const seen = new Set(); return [...String(text || '').matchAll(IMG_RE)].map(m => m[0]).filter(f => !seen.has(f.toLowerCase()) && seen.add(f.toLowerCase())).slice(0, 12)
  .map(f => `<img class="cpic" loading="lazy" src="/api/file?project=${encodeURIComponent(S.project)}&path=${encodeURIComponent(f)}" title="${esc(f)}" onerror="this.remove()">`).join(''); }
document.addEventListener('click', e => { if (e.target.classList && e.target.classList.contains('cpic')) { modal(`<img class="bigpic" src="${e.target.src}"><div class="acts"><div class="btn s g" id="mNo">Закрыть</div></div>`); $('#modalBody').style.width = 'auto'; } });
function bubble(m) { const who = { user: m.to ? 'Вы → специалисту ' + (ROLE[m.to] || m.to) : 'Вы', lead: 'Руководитель', local: 'Локальная нейросеть (резерв)', error: 'Ошибка' }[m.role]; return `<div class="m ${m.role}">${who ? `<small>${esc(who)}${m.t ? ' · ' + time(m.t) : ''}${m.images ? ' · картинок: ' + m.images : ''}</small>` : ''}${esc(m.text)}${m.role === 'lead' ? pics(m.text) : ''}</div>`; }
async function loadChat() { const h = await api('/api/chat/history'); S.msgs = h.messages; S.running = h.running; S.current = h.current; S.fallback = h.fallback; drawChat(); }
function drawChat() { const c = $('#chat'); c.classList.toggle('hidden', !S.msgs.length && !S.running);
  c.innerHTML = S.msgs.map(bubble).join('') + (S.fallback && S.fallback.active ? `<div class="m fb">Лимит подписки исчерпан до ${time(S.fallback.until)}. Сейчас отвечает локальная нейросеть: она ничего не меняет в проекте. <span class="btn s" id="fbOff">Вернуться к руководителю сейчас</span></div>` : '')
    + (S.running ? `<div class="m ${S.current && S.current.local ? 'local' : 'lead'} live"><small>${S.current && S.current.local ? esc(S.current.title || 'Локальная нейросеть отвечает…') : 'Руководитель работает…'}</small>${esc(S.live) || '<span class="dim">' + esc((S.current && S.current.lead) || '') + '</span>'}${pics(S.live)}</div>` : '');
  c.scrollTop = c.scrollHeight; $('#sendBtn').classList.toggle('hidden', S.running); $('#stopBtn').classList.toggle('hidden', !S.running); drawPerm();
  const off = $('#fbOff'); if (off) off.onclick = async () => { await api('/api/chat/fallback-off', {}); loadChat(); }; }
function drawPerm() { const p = (S.current && S.current.pending) || {};
  $('#perm').innerHTML = Object.values(p).map(r => `<div class="permit"><b>Руководитель просит разрешение: ${esc(r.tool)}</b><pre>${esc(JSON.stringify(r.input, null, 1).slice(0, 1200))}</pre><span class="btn s" data-ok="${esc(r.id)}">Разрешить</span><span class="btn s bad" data-no="${esc(r.id)}">Отклонить</span></div>`).join('');
  $$('[data-ok]').forEach(b => b.onclick = () => api('/api/chat/permit', { id: b.dataset.ok, allow: true })); $$('[data-no]').forEach(b => b.onclick = () => api('/api/chat/permit', { id: b.dataset.no, allow: false })); }
async function sendMsg(preset) { const text = (preset || $('#msg').value).trim(); if (!text && !S.images.length) return; if (S.running) return alertBox('Прошлое сообщение ещё в работе. Дождитесь ответа или нажмите «Остановить».');
  const r = await api('/api/chat/send', { text, images: S.images.map(i => ({ media_type: i.type, data: i.data })) }); if (r.error) return alertBox(r.error);
  S.msgs.push({ role: 'user', text, images: S.images.length, t: Date.now() }); S.images = []; drawThumbs(); $('#msg').value = ''; S.live = ''; S.running = true; show('home'); drawChat(); }
$('#sendBtn').onclick = () => sendMsg(); $('#stopBtn').onclick = () => api('/api/chat/stop', {});
$('#newChat').onclick = async () => { const r = await api('/api/chat/new', {}); if (r.error) return alertBox(r.error); loadChat(); };
// Enter sends, Shift+Enter makes a new line.
$('#msg').onkeydown = e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); sendMsg(); } };
function addImage(file) { if (!file || !/^image\/(png|jpeg|webp|gif)$/.test(file.type)) return; if (file.size > 4.5e6) return alertBox('Картинка больше 4,5 МБ — уменьшите её.'); const fr = new FileReader(); fr.onload = () => { S.images.push({ type: file.type, data: fr.result.split(',')[1], url: fr.result }); drawThumbs(); }; fr.readAsDataURL(file); }
function drawThumbs() { $('#thumbs').innerHTML = S.images.map((i, n) => `<div><img src="${i.url}"><b data-rm="${n}">×</b></div>`).join(''); $$('[data-rm]').forEach(b => b.onclick = () => { S.images.splice(+b.dataset.rm, 1); drawThumbs(); }); }
document.addEventListener('paste', e => { for (const it of e.clipboardData.items) if (it.kind === 'file') addImage(it.getAsFile()); });
const card = $('#chatCard'); card.ondragover = e => { e.preventDefault(); $('#msg').classList.add('drop'); }; card.ondragleave = () => $('#msg').classList.remove('drop');
card.ondrop = e => { e.preventDefault(); $('#msg').classList.remove('drop'); for (const f of e.dataTransfer.files) addImage(f); };
function listen() { const es = new EventSource('/api/chat/events'); es.onmessage = m => { const e = JSON.parse(m.data);
  if (e.kind === 'status') { const was = S.running; S.running = e.running; S.current = e.current || null; if (was && !e.running) { loadChat(); loadTasks(); loadOverview(); } else drawChat(); drawHome(); }
  if (e.kind === 'text') { S.live += (S.live ? '\n\n' : '') + e.text; drawChat(); }
  if (e.kind === 'delta') { S.live += e.text; drawChat(); }
  if (e.kind === 'fallback') { S.fallback = e.fallback; drawChat(); }
  if (e.kind === 'team' && S.tab === 'team') { clearTimeout(S.teamTimer); S.teamTimer = setTimeout(loadTeam, 500); }
  if (e.kind === 'activity' || e.kind === 'permission') { S.current = e.current; drawHome(); drawChat(); }
  if (e.kind === 'limits') { if (S.over) S.over.limits = e.limits; drawRight(); }
  if (e.kind === 'result' && e.denials && e.denials.length) S.msgs.push({ role: 'note', text: 'Часть действий защита не разрешила: ' + e.denials.map(d => d.tool_name).join(', ') + '.' }); }; }

// ---------- tasks ----------
async function loadTasks() { S.tasks = (await api('/api/tasks')).tasks || []; const n = S.tasks.filter(t => t.status !== 'done' && t.status !== 'idea').length; $('#taskBadge').textContent = n || ''; if (S.tab === 'tasks') drawTasks(); drawHome(); }
function drawTasks() { const f = [['all', 'Все'], ['feature', '🟢 Фичи'], ['bug', '🔴 Ошибки'], ['change', '🔵 Правки'], ['idea', '🟡 Идеи']];
  $('#taskFilter').innerHTML = f.map(x => `<span class="${S.taskFilter === x[0] ? 'on' : ''}" data-f="${x[0]}">${x[1]}</span>`).join('') + '<span class="add" id="taskAdd">+ Новая задача</span>';
  $$('#taskFilter [data-f]').forEach(e => e.onclick = () => { S.taskFilter = e.dataset.f; drawTasks(); }); $('#taskAdd').onclick = () => editTask({ type: 'feature', status: 'queue', title: '', note: '', docs: '', assets: '' });
  const ok = t => (S.taskFilter === 'all' || t.type === S.taskFilter) && (!S.q || (t.title + ' ' + (t.note || '')).toLowerCase().includes(S.q));
  $('#kanban').innerHTML = COLS.map(([id, name]) => { const ts = S.tasks.filter(t => t.status === id && ok(t)).sort((a, b) => (b.updated || 0) - (a.updated || 0));
    return `<div class="kcol" data-col="${id}"><h2>${name} — ${ts.length}</h2>${ts.slice(0, id === 'done' ? 30 : 200).map(t => `<div class="kc ${t.status === 'check' ? 'check' : ''}" draggable="true" data-id="${t.id}"><span class="tag ${t.type}">${TYPE[t.type] || ''}</span>${esc(t.title)}${t.note ? `<small>${esc(t.note.slice(0, 90))}</small>` : ''}${t.docs || t.assets ? `<small>${t.docs ? '📚 документ ' : ''}${t.assets ? '🧱 ' + esc(t.assets) : ''}</small>` : ''}</div>`).join('')}</div>`; }).join('');
  $$('.kc').forEach(k => { k.onclick = () => editTask(S.tasks.find(t => t.id === k.dataset.id)); k.ondragstart = e => e.dataTransfer.setData('text/plain', k.dataset.id); });
  $$('.kcol').forEach(c => { c.ondragover = e => { e.preventDefault(); c.classList.add('over'); }; c.ondragleave = () => c.classList.remove('over');
    c.ondrop = async e => { e.preventDefault(); c.classList.remove('over'); const t = S.tasks.find(x => x.id === e.dataTransfer.getData('text/plain')); if (t && t.status !== c.dataset.col) { t.status = c.dataset.col; S.tasks = (await api('/api/tasks', { task: t })).tasks; loadTasks(); } }; }); }
function editTask(t) { if (!t) return; const opt = (o, v) => Object.entries(o).map(([k, n]) => `<option value="${k}"${k === v ? ' selected' : ''}>${n}</option>`).join('');
  modal(`<h2>${t.id ? 'Задача' : 'Новая задача'}</h2><label>Что нужно сделать</label><input id="tt" value="${esc(t.title)}"><div class="row"><div class="col"><label>Вид</label><select id="ty">${opt(TYPE, t.type)}</select></div><div class="col"><label>Состояние</label><select id="ts">${opt(Object.fromEntries(COLS), t.status)}</select></div></div>
   <label>Подробности, как проверить, где смотреть</label><textarea id="tn" rows="4">${esc(t.note || '')}</textarea><label>Связанный документ (путь к файлу)</label><input id="td" value="${esc(t.docs || '')}"><label>Связанные ассеты (имена через запятую)</label><input id="ta" value="${esc(t.assets || '')}">
   <div class="acts">${t.id ? '<div class="btn s bad" id="mDel">Удалить</div><div class="btn s g" id="mAsk">Поручить команде</div>' : ''}<div class="btn s g" id="mNo">Отмена</div><div class="btn s" id="mOk">Сохранить</div></div>`, async () => {
    const n = Object.assign({}, t, { title: $('#tt').value.trim(), type: $('#ty').value, status: $('#ts').value, note: $('#tn').value.trim(), docs: $('#td').value.trim(), assets: $('#ta').value.trim() }); if (!n.title) return; await api('/api/tasks', { task: n }); closeModal(); loadTasks(); });
  if (t.id) { $('#mDel').onclick = async () => { await api('/api/tasks', { action: 'delete', id: t.id }); closeModal(); loadTasks(); };
    $('#mAsk').onclick = () => { closeModal(); $('#msg').value = `Возьми в работу задачу из списка задач: «${t.title}».${t.note ? ' Подробности: ' + t.note : ''}`; show('home'); $('#msg').focus(); }; } }

// ---------- documents ----------
async function loadDocs() { const tree = await api('/api/docs/tree'); const draw = (n, d) => n.dir ? `<div class="n ${n.root ? 'root' : ''}" data-fold>${n.root ? '' : '📁 '}${esc(n.name)}</div><div class="kids ${d > 0 ? 'hidden' : ''}">${n.children.map(c => draw(c, d + 1)).join('')}</div>` : `<div class="n file" data-path="${esc(n.path)}" title="${esc(n.name)}">${esc(n.name)}</div>`;
  $('#docTree').innerHTML = '<h2>Документы проекта</h2>' + tree.map(n => draw(n, 0)).join(''); $('#docTree').dataset.ready = '1';
  $$('#docTree [data-fold]').forEach(f => f.onclick = () => f.nextElementSibling.classList.toggle('hidden')); $$('#docTree .file').forEach(f => f.onclick = () => openDoc(f.dataset.path)); filterDocs(); }
function filterDocs() { if (!S.q) return $$('#docTree .file').forEach(f => f.classList.remove('hidden')); $$('#docTree .kids').forEach(k => k.classList.remove('hidden')); $$('#docTree .file').forEach(f => f.classList.toggle('hidden', !f.textContent.toLowerCase().includes(S.q))); }
function md(t) { const out = []; let inCode = false, table = [];
  const inline = s => esc(s).replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/&lt;br&gt;/g, '<br>');
  const flush = () => { if (table.length) { out.push('<table>' + table.filter(r => !/^\|?[\s:|-]+\|?$/.test(r)).map((r, i) => '<tr>' + r.replace(/^\||\|$/g, '').split('|').map(c => `<${i ? 'td' : 'th'}>${inline(c.trim())}</${i ? 'td' : 'th'}>`).join('') + '</tr>').join('') + '</table>'); table = []; } };
  for (const l of t.split(/\r?\n/)) { if (l.startsWith('```')) { flush(); inCode = !inCode; out.push(inCode ? '<pre class="text"><code>' : '</code></pre>'); continue; } if (inCode) { out.push(esc(l) + '\n'); continue; }
    if (/^\s*\|.*\|\s*$/.test(l)) { table.push(l.trim()); continue; } flush();
    const h = l.match(/^(#{1,4})\s+(.*)/); if (h) out.push(`<h${h[1].length < 3 ? 3 : 4}>${inline(h[2])}</h${h[1].length < 3 ? 3 : 4}>`); else if (/^\s*([-*]|\d+\.)\s+/.test(l)) out.push('<li>' + inline(l.replace(/^\s*([-*]|\d+\.)\s+/, '')) + '</li>'); else if (l.trim()) out.push('<p>' + inline(l) + '</p>'); } flush(); return out.join(''); }
async function openDoc(p) { $$('#docTree .file').forEach(f => f.classList.toggle('on', f.dataset.path === p)); const name = p.split('/').pop(), v = $('#docView');
  if (/\.(png|jpg|svg)$/i.test(p)) { S.doc = { path: p }; v.innerHTML = `<h2>${esc(name)}</h2><img src="/api/docs/file?project=${encodeURIComponent(S.project)}&path=${encodeURIComponent(p)}">`; }
  else { const d = await api('/api/docs/file?path=' + encodeURIComponent(p)); if (d.error) return; S.doc = d; const can = /\.(md|txt)$/i.test(p);
    v.innerHTML = `<h2>${esc(name)} <span class="lnk dim">изменён ${new Date(d.m).toLocaleDateString('ru')}</span></h2><p>${can ? '<span class="btn s" id="dEdit">Править</span>' : ''}<span class="btn s g" id="dAsk">Попросить команду обновить</span></p><div id="dBody">${/\.md$/i.test(p) ? md(d.text) : `<pre class="text">${esc(d.text)}</pre>`}</div>`;
    if (can) $('#dEdit').onclick = () => { $('#dBody').innerHTML = `<textarea id="dText"></textarea><p><span class="btn s" id="dSave">Сохранить</span><span class="btn s g" id="dCancel">Отмена</span></p>`; $('#dText').value = d.text; $('#dCancel').onclick = () => openDoc(p);
      $('#dSave').onclick = async () => { const r = await api('/api/docs/file', { path: p, text: $('#dText').value }); if (r.error) return alertBox(r.error); openDoc(p); }; };
    $('#dAsk').onclick = () => { $('#msg').value = `Обнови документ ${p}: `; show('home'); $('#msg').focus(); }; }
  const rel = S.tasks.filter(t => t.docs && p.toLowerCase().includes(t.docs.toLowerCase().replace(/\\/g, '/')));
  $('#docLinks').innerHTML = '<h2>Связано с документом</h2>' + (rel.map(t => `<div class="kc" data-task="${t.id}"><span class="tag ${t.type}">${TYPE[t.type]}</span>${esc(t.title)}<small>${Object.fromEntries(COLS)[t.status]}</small></div>`).join('') || '<p class="dim">Задач, связанных с этим документом, нет. Связь задаётся в карточке задачи.</p>') + `<div class="kv" style="margin-top:10px"><span>Файл</span><b>${esc(p)}</b></div>`;
  $$('#docLinks [data-task]').forEach(e => e.onclick = () => editTask(S.tasks.find(t => t.id === e.dataset.task))); }

// ---------- assets ----------
async function loadAssets(refresh) { if (!S.assets.length || refresh) { $('#assetGrid').innerHTML = '<p class="dim">Просматриваю папку игры…</p>'; const r = await api('/api/assets' + (refresh ? '?refresh=1' : '')); S.assets = (r.assets || []).sort((a, b) => b.m - a.m); S.tools = r.tools || []; S.assetScan = r.scanned; S.assetNote = r.note; } drawAssets(); }
const toolOf = a => (S.tools || []).find(t => t.asset === a.name);
function drawAssets() { const cnt = {}; for (const a of S.assets) cnt[a.type] = (cnt[a.type] || 0) + 1;
  const toolList = (S.tools || []).map(t => S.assets.find(a => a.name === t.asset)).filter(Boolean); cnt.tools = toolList.length;
  $('#assetFilter').innerHTML = Object.entries(ATYPE).filter(([k]) => k === 'all' || cnt[k]).map(([k, v]) => `<span class="${S.assetFilter === k ? 'on' : ''}" data-f="${k}">${v[1]} ${v[0]} ${k === 'all' ? S.assets.length : cnt[k]}</span>`).join('') + `<span class="add" id="assetScan">Обновить список</span>`;
  $$('#assetFilter [data-f]').forEach(e => e.onclick = () => { S.assetFilter = e.dataset.f; S.assetShown = 120; drawAssets(); }); $('#assetScan').onclick = () => loadAssets(true);
  const list = (S.assetFilter === 'tools' ? toolList : S.assets).filter(a => (S.assetFilter === 'all' || S.assetFilter === 'tools' || a.type === S.assetFilter) && (!S.q || (a.name + ' ' + a.folder).toLowerCase().includes(S.q)));
  $('#assetGrid').innerHTML = list.slice(0, S.assetShown).map(a => `<div class="as ${S.asset === a ? 'sel' : ''}" data-n="${esc(a.folder + '/' + a.name)}"><div class="pic">${ATYPE[a.type][1]}</div><div class="nm">${S.assetFilter === 'tools' ? `<b>${esc(toolOf(a).title)}</b>` : ''}${esc(a.name)}<small>${esc(ATYPE[a.type][0])} · ${a.kb > 1024 ? (a.kb / 1024).toFixed(1) + ' МБ' : a.kb + ' КБ'}</small></div></div>`).join('') || `<p class="dim">${esc(S.assetNote || 'Ничего не найдено.')}</p>`;
  $('#assetMore').textContent = list.length > S.assetShown ? `Показать ещё (осталось ${list.length - S.assetShown})` : ''; $('#assetMore').onclick = () => { S.assetShown += 240; drawAssets(); };
  $$('#assetGrid .as').forEach(e => e.onclick = () => { S.asset = S.assets.find(a => a.folder + '/' + a.name === e.dataset.n); drawAssets(); drawAsset(); }); }
function drawAsset() { const a = S.asset; if (!a) return; const rel = S.tasks.filter(t => t.assets && t.assets.toLowerCase().split(',').some(n => n.trim() && a.name.toLowerCase().includes(n.trim())));
  const tool = toolOf(a);
  $('#assetInfo').innerHTML = `<h2>${esc(tool ? tool.title : a.name)}</h2>${tool ? `<p class="toolwhat">${esc(tool.what)}</p><div class="kv"><span>Файл в игре</span><b>${esc(a.name)}</b></div>` : ''}<div class="as"><div class="pic" style="height:110px;font-size:48px">${ATYPE[a.type][1]}</div></div><div class="kv" style="margin-top:8px"><span>Вид</span><b>${esc(ATYPE[a.type][0])}</b></div><div class="kv"><span>Папка</span><b>${esc(a.folder)}</b></div><div class="kv"><span>Размер файла</span><b>${a.kb} КБ</b></div><div class="kv"><span>Изменён</span><b>${new Date(a.m).toLocaleDateString('ru')}</b></div>
   <h2 style="margin-top:12px">Связанные задачи</h2>${rel.map(t => `<div class="kc" data-task="${t.id}"><span class="tag ${t.type}">${TYPE[t.type]}</span>${esc(t.title)}</div>`).join('') || '<p class="dim">Нет.</p>'}<p style="margin-top:8px"><span class="btn s" id="aAsk">Попросить изменить</span><span class="btn s g" id="aTask">Завести задачу</span></p>`;
  $('#aAsk').onclick = () => { $('#msg').value = `По ассету ${a.name} (папка ${a.folder}): `; show('home'); $('#msg').focus(); }; $('#aTask').onclick = () => editTask({ type: 'change', status: 'queue', title: '', note: '', docs: '', assets: a.name });
  $$('#assetInfo [data-task]').forEach(e => e.onclick = () => editTask(S.tasks.find(t => t.id === e.dataset.task))); }

// ---------- costs ----------
function drawCosts() { const o = S.over || {}, c = o.costs || { total: 0, runs: 0 }, l = o.limits, pc = w => w ? Math.round((w.utilization || 0) * 100) + ' %' : 'нет данных';
  $('#costBox').innerHTML = `<div class="cost"><b>Claude — руководитель и специалисты</b><p>Вы платите за подписку раз в месяц, отдельно за каждое сообщение деньги не списываются. Ограничение здесь не деньги, а лимит: сколько работы можно сделать за пять часов и за неделю. Сейчас израсходовано: за пять часов — ${pc(l && l.five)}, за неделю — ${pc(l && l.seven)}.</p>
    <p style="margin-top:6px">Из этой программы руководителю отправлено сообщений: ${c.runs}. Если бы подписки не было и Anthropic брала деньги за каждое обращение, эта работа стоила бы около ${money(c.total)}. Это справочное число, чтобы видеть, какие задачи самые тяжёлые; с вас эти деньги не списываются.</p></div>
   <div class="cost"><b>OpenAI — картинки</b><p>Здесь деньги списываются с вашего счёта OpenAI за каждую картинку. ${oaText()}</p></div>
   <div class="cost"><b>Tripo — 3D-модели</b><p>Здесь тратятся кредиты Tripo: каждая заказанная модель стоит несколько кредитов. ${trText()}</p></div>
   <div class="cost"><b>Локальная нейросеть</b><p>Работает на вашем компьютере и ничего не стоит. Она подменяет руководителя в чате, когда лимит Claude исчерпан.</p></div>`;
  $$('#costBox [data-oaset]').forEach(b => b.onclick = oaSetup); }

// ---------- specialists ----------
const ROLE = { 'cpp-dev': 'Программист', 'unreal-operator': 'Оператор движка', 'modeler-3d': '3D-моделлер', 'concept-artist': 'Художник', qa: 'Проверяющий', 'game-designer': 'Геймдизайнер', 'tech-artist': 'Технический художник', sound: 'Звукорежиссёр', 'level-designer': 'Дизайнер уровней', 'ui-ux-designer': 'Дизайнер интерфейса' };
const ROLE_WHAT = { 'cpp-dev': 'Пишет и правит программный код игры.', 'unreal-operator': 'Работает в редакторе игры: расставляет объекты на уровне, настраивает заготовки, собирает игру для компьютера и телефона.', 'modeler-3d': 'Делает трёхмерные модели в Blender и готовит их для игры.', 'concept-artist': 'Готовит палитры, макеты экранов и описания внешнего вида для моделей.', qa: 'Запускает сборку и автопроверки и решает, можно ли принимать работу.' };
async function loadTeam() { const t = await api('/api/team'); S.team = t.agents || []; S.teamQueue = t.queue || 0; if (!S.spec || !S.team.find(a => a.id === S.spec)) S.spec = (S.team[0] || {}).id; drawTeam(); if (S.spec) loadThread(); }
function drawTeam() { $('#teamList').innerHTML = '<h2>Специалисты</h2>' + (S.team.map(a => `<div class="n sp ${a.id === S.spec ? 'on' : ''}" data-sp="${esc(a.id)}"><span class="dot ${a.busy ? 'y' : 'x'}"></span><b>${esc(ROLE[a.id] || a.id)}</b><small>${a.busy ? 'работает сейчас' : a.last ? 'последняя запись ' + day(a.last) + ' в ' + time(a.last) : 'переписки пока нет'}</small></div>`).join('') || '<p class="dim">В папке команды специалисты не описаны.</p>')
    + (S.teamQueue ? `<p class="dim" style="margin-top:10px">Ждут отправки сообщений: ${S.teamQueue}.</p>` : '');
  $$('[data-sp]').forEach(e => e.onclick = () => { S.spec = e.dataset.sp; drawTeam(); loadThread(); }); }
async function loadThread() { const id = S.spec, r = await api('/api/team/thread?id=' + encodeURIComponent(id)); if (id !== S.spec) return; const a = S.team.find(x => x.id === id) || {}, nm = ROLE[id] || id;
  $('#teamTitle').textContent = nm + ' и руководитель'; $('#teamDesc').textContent = ROLE_WHAT[id] || a.desc || '';
  const who = { lead: 'Руководитель → ' + nm, spec: nm + ' → руководителю', user: 'Вы → ' + nm }, c = $('#teamThread'), stick = c.scrollHeight - c.scrollTop - c.clientHeight < 80 || S.threadOf !== id; S.threadOf = id;
  c.innerHTML = (r.thread || []).map(m => m.from === 'act' ? `<div class="m note act">${time(m.t)} · ${esc(nm)}: ${esc(m.text)}</div>` : `<div class="m ${m.from === 'user' ? 'user' : m.from === 'lead' ? 'lead' : 'local'}"><small>${esc(who[m.from] || '')} · ${day(m.t)} ${time(m.t)}</small>${esc(m.text)}${m.from === 'user' ? '' : pics(m.text)}</div>`).join('')
    || '<p class="dim">Переписки пока нет. Она появится, когда руководитель поручит этому специалисту работу из этой программы. Можно написать специалисту первым — поле ниже.</p>';
  if (stick) c.scrollTop = c.scrollHeight; $('#teamMsg').placeholder = `Напишите специалисту «${nm}»… Отправка — Enter, новая строка — Shift+Enter.`; }
async function teamSend() { const text = $('#teamMsg').value.trim(); if (!text || !S.spec) return; const r = await api('/api/team/send', { id: S.spec, text }); if (r.error) return alertBox(r.error); $('#teamMsg').value = ''; await loadTeam(); if (r.queued) alertBox('Руководитель сейчас занят. Сообщение уйдёт специалисту, как только он освободится.'); else loadChat(); }
$('#teamSendBtn').onclick = teamSend; $('#teamMsg').onkeydown = e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); teamSend(); } };

async function boot() { await loadProjects(); await loadTasks(); await Promise.all([loadOverview(), loadChat()]); show(S.tab); }
const SHOT = location.search.includes('shot=1'); // shot=1: a still frame for checks, without the live connection
boot().then(() => { if (!SHOT) { listen(); setInterval(loadOverview, 60000); setInterval(() => { if (S.running) drawHome(); }, 30000); } });

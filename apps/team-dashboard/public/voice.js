'use strict';
// Voice mode: live conversation with an OpenAI Realtime model over WebRTC (developers.openai.com/api/docs/guides/realtime-webrtc).
// The server mints a short-lived key (/api/voice/session); the page connects to OpenAI directly with it.
// Tools the model calls are executed here through the existing chat endpoints of this program.
const V = { on: false, pc: null, dc: null, ms: null, audio: null, es: null, inResp: false, notes: [], leadRunning: false };
const vset = (state, cls) => { $('#voiceState').textContent = state; $('#voiceDot').className = 'vdot ' + (cls || ''); };
const vline = (cls, text) => { const box = $('#voiceLines'), d = document.createElement('div'); d.className = cls; d.textContent = text; box.appendChild(d); while (box.children.length > 60) box.firstChild.remove(); box.scrollTop = box.scrollHeight; };
const vsend = ev => { if (V.dc && V.dc.readyState === 'open') V.dc.send(JSON.stringify(ev)); };
const money = x => '$' + (x || 0).toFixed(2);

async function voiceStart() {
  if (V.on) return; V.on = true; $('#voiceBar').classList.remove('hidden'); $('#voiceBtn').classList.add('on'); $('#voiceBtn').textContent = '🎙 Идёт разговор'; vset('Подключаюсь…', 'think');
  try {
    const s = await api('/api/voice/session', {}); if (s.error) throw new Error(s.error);
    const h = await api('/api/chat/history'); V.leadRunning = !!h.running;
    const pc = V.pc = new RTCPeerConnection();
    V.audio = new Audio(); V.audio.autoplay = true; pc.ontrack = e => { V.audio.srcObject = e.streams[0]; };
    V.ms = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
    pc.addTrack(V.ms.getTracks()[0]);
    const dc = V.dc = pc.createDataChannel('oai-events');
    dc.onmessage = e => { try { onVoiceEvent(JSON.parse(e.data)); } catch (err) { console.error(err); } };
    dc.onopen = () => { vset('Слушаю', 'listen'); note('[Программа] Ринат включил голосовой режим. Поздоровайся одной короткой фразой.', true); };
    dc.onclose = () => { if (V.on) voiceEnd('Связь с голосовым помощником прервалась. Нажмите «Голосом», чтобы продолжить: помощник вспомнит конец разговора.'); };
    pc.onconnectionstatechange = () => { if (['failed', 'disconnected'].includes(pc.connectionState) && V.on) voiceEnd('Связь оборвалась. Нажмите «Голосом», чтобы продолжить.'); };
    const offer = await pc.createOffer(); await pc.setLocalDescription(offer);
    const r = await fetch('https://api.openai.com/v1/realtime/calls', { method: 'POST', body: offer.sdp, headers: { Authorization: 'Bearer ' + s.value, 'Content-Type': 'application/sdp' } });
    if (!r.ok) throw new Error('OpenAI не принял соединение: HTTP ' + r.status + ' ' + (await r.text()).slice(0, 300));
    await pc.setRemoteDescription({ type: 'answer', sdp: await r.text() });
    // Lead events: tell the voice when the lead finishes or asks for permission.
    V.es = new EventSource('/api/chat/events'); V.es.onmessage = m => { const e = JSON.parse(m.data); if (e.kind === 'status') leadStatus(!!e.running);
      if (e.kind === 'permission' && e.request) note(`[Программа] GameLead ждёт разрешения на действие «${e.request.tool}». Кнопки «Разрешить» и «Отклонить» — на экране программы. Скажи об этом Ринату одной фразой.`); };
    const st = await api('/api/voice/state'); $('#voiceCost').textContent = 'сегодня ' + money(st.today) + ' из ' + money(st.dailyUsd);
  } catch (e) { voiceEnd('Не удалось начать разговор: ' + (e && e.message || e)); }
}
function voiceEnd(why) {
  if (!V.on) return; V.on = false;
  try { V.dc && V.dc.close(); } catch { } try { V.pc && V.pc.close(); } catch { } try { V.ms && V.ms.getTracks().forEach(t => t.stop()); } catch { } try { V.es && V.es.close(); } catch { }
  if (V.audio) V.audio.srcObject = null; Object.assign(V, { pc: null, dc: null, ms: null, es: null, inResp: false, notes: [] });
  $('#voiceBtn').classList.remove('on'); $('#voiceBtn').textContent = '🎙 Голосом'; vset(why ? 'Разговор завершён' : 'Разговор завершён', why ? 'err' : ''); if (why) vline('n', why);
}
// A program message into the conversation; spoken right away, or after the current answer finishes.
function note(text, now) { if (!V.on) return; if (V.inResp && !now) { V.notes.push(text); return; }
  vsend({ type: 'conversation.item.create', item: { type: 'message', role: 'user', content: [{ type: 'input_text', text }] } }); vsend({ type: 'response.create' }); V.inResp = true; }
async function leadStatus(running) {
  const was = V.leadRunning; V.leadRunning = running; if (!was || running) return;
  const h = await api('/api/chat/history'), last = [...h.messages].reverse().find(m => m.role !== 'user');
  vline('n', 'Руководитель закончил работу.');
  note('[Программа] GameLead закончил работу. Его ответ:\n' + (last ? String(last.text).slice(0, 6000) : '(ответа нет)'));
}
async function runTool(name, args) {
  if (name === 'send_task') { const task = String(args.task || '').trim(); if (!task) return { error: 'Пустое задание.' };
    const r = await api('/api/chat/send', { text: '[Задание от Рината из голосового разговора]\n\n' + task }); if (r.error) return { error: r.error };
    V.leadRunning = true; vline('n', 'Задание отправлено руководителю.'); if (typeof loadChat === 'function') loadChat(); return { ok: true, note: 'GameLead принял задание. Когда закончит, программа сама пришлёт его ответ.' }; }
  if (name === 'get_status') { const h = await api('/api/chat/history'), c = h.current || {}, last = [...h.messages].reverse().find(m => m.role !== 'user');
    return { running: !!h.running, activity: c.lead || null, specialists_at_work: Object.values(c.agents || {}).filter(a => a.state === 'work').map(a => a.name + ': ' + a.text),
      waiting_permission: Object.values(c.pending || {}).map(x => x.tool), current_partial_answer: h.running ? String(c.answer || '').slice(-1500) : undefined,
      last_answer: last ? String(last.text).slice(0, 6000) : null }; }
  if (name === 'stop_task') { const r = await api('/api/chat/stop', {}); vline('n', 'Работа руководителя остановлена.'); return r; }
  return { error: 'Нет такого инструмента.' };
}
async function onVoiceEvent(e) {
  switch (e.type) {
    case 'input_audio_buffer.speech_started': vset('Слушаю вас', 'listen'); break;
    case 'response.created': V.inResp = true; vset('Думает', 'think'); break;
    case 'output_audio_buffer.started': vset('Говорит', 'speak'); break;
    case 'output_audio_buffer.stopped': case 'output_audio_buffer.cleared': vset('Слушаю', 'listen'); break;
    case 'conversation.item.input_audio_transcription.completed': if (e.transcript && e.transcript.trim()) { vline('u', 'Вы: ' + e.transcript.trim()); api('/api/voice/log', { role: 'user', text: e.transcript }); } break;
    case 'response.output_audio_transcript.done': case 'response.audio_transcript.done': if (e.transcript) { vline('a', e.transcript); api('/api/voice/log', { role: 'assistant', text: e.transcript }); } break;
    case 'error': vline('n', 'Ошибка голосового помощника: ' + ((e.error && e.error.message) || JSON.stringify(e).slice(0, 200))); break;
    case 'response.done': {
      V.inResp = false; const resp = e.response || {};
      if (resp.usage) api('/api/voice/usage', { usage: resp.usage }).then(st => { $('#voiceCost').textContent = 'сегодня ' + money(st.today) + ' из ' + money(st.dailyUsd);
        if (st.over) voiceEnd('Дневной предел расходов на голос исчерпан.'); });
      const calls = (resp.output || []).filter(o => o.type === 'function_call');
      if (calls.length) { vset('Работает с командой', 'think');
        for (const c of calls) { let args = {}; try { args = JSON.parse(c.arguments || '{}'); } catch { }
          let out; try { out = await runTool(c.name, args); } catch (err) { out = { error: String(err && err.message || err) }; }
          vsend({ type: 'conversation.item.create', item: { type: 'function_call_output', call_id: c.call_id, output: JSON.stringify(out) } }); }
        vsend({ type: 'response.create' }); V.inResp = true; break; }
      if (V.notes.length) note(V.notes.shift());
      break; }
  }
}
$('#voiceBtn').onclick = () => V.on ? voiceEnd() : voiceStart();
$('#voiceEnd').onclick = () => voiceEnd();

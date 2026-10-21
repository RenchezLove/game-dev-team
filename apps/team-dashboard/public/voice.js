'use strict';
// Voice mode (owner's decision 2026-10-20): the OpenAI Realtime model over WebRTC is only the ears and the voice of GameLead.
// What the owner says becomes his message in the main chat (queued if the lead is busy); every answer the lead finishes
// while the voice mode is on is read out aloud. The owner may interrupt the voice by speaking.
// Docs: developers.openai.com/api/docs/guides/realtime-webrtc, realtime-conversations (read 2026-10-14).
const V = { on: false, pc: null, dc: null, ms: null, audio: null, es: null, inResp: false, notes: [], leadRunning: false, acked: false };
const vset = (state, cls) => { $('#voiceState').textContent = state; $('#voiceDot').className = 'vdot ' + (cls || ''); };
const vline = (cls, text) => { const box = $('#voiceLines'), d = document.createElement('div'); d.className = cls; d.textContent = text; box.appendChild(d); while (box.children.length > 8) box.firstChild.remove(); box.scrollTop = box.scrollHeight; };
const vsend = ev => { if (V.dc && V.dc.readyState === 'open') V.dc.send(JSON.stringify(ev)); };
const vmoney = x => '$' + (x || 0).toFixed(2);

async function voiceStart() {
  if (V.on) return; V.on = true; $('#voiceLines').innerHTML = ''; $('#voiceBar').classList.remove('hidden'); $('#voiceBtn').classList.add('on'); $('#voiceBtn').textContent = '🎙 Идёт разговор'; vset('Подключаюсь…', 'think');
  try {
    const s = await api('/api/voice/session', {}); if (s.error) throw new Error(s.error);
    const h = await api('/api/chat/history'); V.leadRunning = !!h.running; V.acked = V.leadRunning;
    const pc = V.pc = new RTCPeerConnection();
    V.audio = new Audio(); V.audio.autoplay = true; pc.ontrack = e => { V.audio.srcObject = e.streams[0]; };
    V.ms = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
    pc.addTrack(V.ms.getTracks()[0]);
    const dc = V.dc = pc.createDataChannel('oai-events');
    dc.onmessage = e => { try { onVoiceEvent(JSON.parse(e.data)); } catch (err) { console.error(err); } };
    dc.onopen = () => { vset('Слушаю', 'listen'); note('[Программа] Ринат включил голосовой режим. Скажи одну короткую фразу, что слушаешь.', true); };
    dc.onclose = () => { if (V.on) voiceEnd('Связь с голосовым движком прервалась. Нажмите «Голосом», чтобы продолжить.'); };
    pc.onconnectionstatechange = () => { if (['failed', 'disconnected'].includes(pc.connectionState) && V.on) voiceEnd('Связь оборвалась. Нажмите «Голосом», чтобы продолжить.'); };
    const offer = await pc.createOffer(); await pc.setLocalDescription(offer);
    const r = await fetch('https://api.openai.com/v1/realtime/calls', { method: 'POST', body: offer.sdp, headers: { Authorization: 'Bearer ' + s.value, 'Content-Type': 'application/sdp' } });
    if (!r.ok) throw new Error('OpenAI не принял соединение: HTTP ' + r.status + ' ' + (await r.text()).slice(0, 300));
    await pc.setRemoteDescription({ type: 'answer', sdp: await r.text() });
    V.es = new EventSource('/api/chat/events'); V.es.onmessage = m => { const e = JSON.parse(m.data); if (e.kind === 'status') leadStatus(!!e.running);
      if (e.kind === 'permission' && e.request) note('[Программа] Скажи Ринату одной фразой: ты ждёшь его разрешения на действие, кнопки «Разрешить» и «Отклонить» на экране.'); };
    const st = await api('/api/voice/state'); $('#voiceCost').textContent = 'сегодня ' + vmoney(st.today) + ' из ' + vmoney(st.dailyUsd);
  } catch (e) { voiceEnd('Не удалось начать разговор: ' + (e && e.message || e)); }
}
// End the conversation and close the panel. A reason (an error) is shown in the chat area as an alert.
function voiceEnd(why) {
  if (!V.on) return; V.on = false;
  try { V.dc && V.dc.close(); } catch { } try { V.pc && V.pc.close(); } catch { } try { V.ms && V.ms.getTracks().forEach(t => t.stop()); } catch { } try { V.es && V.es.close(); } catch { }
  if (V.audio) V.audio.srcObject = null; Object.assign(V, { pc: null, dc: null, ms: null, es: null, inResp: false, notes: [] });
  $('#voiceBtn').classList.remove('on'); $('#voiceBtn').textContent = '🎙 Голосом'; $('#voiceBar').classList.add('hidden');
  if (why && typeof alertBox === 'function') alertBox(why);
}
// A program instruction to the voice; spoken right away, or after the current phrase is finished.
function note(text, now) { if (!V.on) return; if (V.inResp && !now) { V.notes.push(text); return; }
  vsend({ type: 'conversation.item.create', item: { type: 'message', role: 'user', content: [{ type: 'input_text', text }] } }); vsend({ type: 'response.create' }); V.inResp = true; }
// The lead finished: read his last answer aloud.
async function leadStatus(running) {
  const was = V.leadRunning; V.leadRunning = running; if (running) return; if (!was) return;
  V.acked = false;
  const h = await api('/api/chat/history'), last = [...h.messages].reverse().find(m => m.role === 'lead' || m.role === 'local' || m.role === 'error');
  if (!last) return;
  note('[Программа] Прочитай Ринату вслух свой ответ, близко к тексту:\n\n' + String(last.text).slice(0, 5000));
}
// What the owner said goes to the lead as his chat message.
async function toLead(text) {
  const r = await api('/api/chat/send', { text, via: 'voice' }); if (r.error) { vline('n', r.error); return; }
  if (typeof loadChat === 'function') loadChat();
  if (!V.acked) { V.acked = true; note(r.queued ? '[Программа] Ты сейчас занят прошлой работой. Скажи одной фразой, что услышал и займёшься этим, как освободишься.' : '[Программа] Скажи одной короткой фразой, что услышал и смотришь.'); }
}
async function onVoiceEvent(e) {
  switch (e.type) {
    case 'input_audio_buffer.speech_started': vset('Слушаю вас', 'listen'); break;
    case 'response.created': V.inResp = true; vset('Говорит', 'speak'); break;
    case 'output_audio_buffer.stopped': case 'output_audio_buffer.cleared': vset(V.leadRunning ? 'Руководитель работает' : 'Слушаю', V.leadRunning ? 'think' : 'listen'); break;
    case 'conversation.item.input_audio_transcription.completed': { const t = (e.transcript || '').trim(); if (t) { api('/api/voice/log', { role: 'user', text: t }); toLead(t); } break; }
    case 'error': vline('n', 'Ошибка голосового движка: ' + ((e.error && e.error.message) || JSON.stringify(e).slice(0, 200))); break;
    case 'response.done': {
      V.inResp = false; const resp = e.response || {};
      if (resp.usage) api('/api/voice/usage', { usage: resp.usage }).then(st => { $('#voiceCost').textContent = 'сегодня ' + vmoney(st.today) + ' из ' + vmoney(st.dailyUsd);
        if (st.over) voiceEnd('Дневной предел расходов на голос исчерпан.'); });
      if (V.notes.length) note(V.notes.shift());
      break; }
  }
}
$('#voiceBtn').onclick = () => V.on ? voiceEnd() : voiceStart();
$('#voiceEnd').onclick = () => voiceEnd();

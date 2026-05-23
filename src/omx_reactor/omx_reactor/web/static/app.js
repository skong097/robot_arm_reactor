// WS 연결 + 패널 갱신.

const $ = (id) => document.getElementById(id);

const vaCanvas = document.getElementById('va_canvas');
const vaQuadrant = new window.VAQuadrant(vaCanvas);

const timeline = document.getElementById('timeline');
const eventsEl = document.getElementById('events');

function setStatus({ v, a, confidence, source, track_id,
                     current_motion, queued_motion }) {
  if (v !== null && v !== undefined) $('v').textContent = v.toFixed(2);
  if (a !== null && a !== undefined) $('a').textContent = a.toFixed(2);
  if (confidence !== undefined) $('conf').textContent = confidence.toFixed(2);
  if (source) $('source').textContent = source;
  if (current_motion !== undefined) $('current_motion').textContent = current_motion || '-';
  if (queued_motion !== undefined) $('queued_motion').textContent = queued_motion || '-';
  if (track_id !== undefined) $('track').textContent = track_id >= 0 ? track_id : '-';
}

function pushEvent(kind, text) {
  const li = document.createElement('li');
  li.className = kind;
  const ts = new Date().toLocaleTimeString();
  li.textContent = `${ts}  ${text}`;
  eventsEl.prepend(li);
  while (eventsEl.children.length > 20) eventsEl.lastChild.remove();
}

function handle(msg) {
  if (msg.type === 'snapshot') {
    if (msg.payload.reactor) {
      setStatus(msg.payload.reactor);
      if (msg.payload.reactor.v !== null) vaQuadrant.push(msg.payload.reactor.v, msg.payload.reactor.a);
    }
  } else if (msg.type === 'reactor') {
    setStatus(msg.payload);
    if (msg.payload.v !== null) vaQuadrant.push(msg.payload.v, msg.payload.a);
    if (msg.payload.current_motion) {
      // engagement-timeline 의 marker 표시는 timeline 컴포넌트에 위임
      if (timeline && typeof timeline.addMarker === 'function') {
        timeline.addMarker(msg.payload.current_motion);
      }
    }
  } else if (msg.type === 'rapport') {
    pushEvent('rapport',
      `${msg.payload.event_type}  w=${msg.payload.weight.toFixed(2)}  ${msg.payload.reason}`);
    if (timeline && typeof timeline.addPoint === 'function') {
      timeline.addPoint(msg.payload);
    }
  } else if (msg.type === 'emotion') {
    // raw V·A — quadrant 표시는 reactor 가 합산 후 다시 함
  }
}

function connect() {
  const ws = new WebSocket(`ws://${location.host}/ws/stream`);
  ws.onmessage = (ev) => {
    try { handle(JSON.parse(ev.data)); } catch (e) { console.error(e); }
  };
  ws.onclose = () => setTimeout(connect, 5_000);  // auto-reconnect
  // keep-alive
  setInterval(() => { if (ws.readyState === 1) ws.send('ping'); }, 25_000);
}
connect();

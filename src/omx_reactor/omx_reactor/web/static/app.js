/* app.js — omx_reactor 고유 dashboard (omx 토픽만 처리).
 *
 * vendored engaging-analytics.js 가 자체적으로 /ws/v1/engaging 직접 구독 —
 * 본 app.js 와 독립. dashboard_node 의 /ws/v1/engaging 가 doby opserver 와
 * 동일 payload shape 발행하므로 engaging-analytics.js 0-modification 작동.
 *
 * 본 app.js 는 /ws/stream (omx 고유 — reactor 모션 + 이벤트) 만 처리해서
 * 상단 status bar (현 모션 / 큐 / track) + 우측 events 영역 갱신.
 *
 * Step B 의 이벤트 타임라인 시각화도 본 채널의 데이터로 추후 추가.
 */
(function () {
  const $ = (id) => document.getElementById(id);
  const eventsEl = $('events');

  function setStatus(p) {
    if (!p) return;
    if (p.current_motion !== undefined) {
      const el = $('current_motion');
      if (el) el.textContent = p.current_motion || '-';
    }
    if (p.queued_motion !== undefined) {
      const el = $('queued_motion');
      if (el) el.textContent = p.queued_motion || '-';
    }
    if (p.track_id !== undefined) {
      const el = $('track');
      if (el) el.textContent = (p.track_id >= 0 ? p.track_id : '-');
    }
  }

  function pushEvent(kind, text) {
    if (!eventsEl) return;
    const li = document.createElement('li');
    li.className = kind;
    const ts = new Date().toLocaleTimeString();
    li.textContent = `${ts}  ${text}`;
    eventsEl.prepend(li);
    while (eventsEl.children.length > 20) eventsEl.lastChild.remove();
  }

  function handle(msg) {
    if (msg.type === 'snapshot') {
      const pay = msg.payload || {};
      if (pay.reactor) setStatus(pay.reactor);
    } else if (msg.type === 'reactor') {
      const p = msg.payload;
      setStatus(p);
      if (p.current_motion) {
        const tag = p.session_event ? ` (${p.session_event})` : '';
        pushEvent('motion', `▶ ${p.current_motion}${tag}`);
      }
    } else if (msg.type === 'rapport') {
      const p = msg.payload;
      pushEvent('rapport', `${p.event_type}  w=${p.weight.toFixed(2)}  ${p.reason}`);
    }
    // 'emotion' 은 engaging-analytics 가 처리 — 본 app 는 무시
  }

  function connect() {
    const ws = new WebSocket(`ws://${location.host}/ws/stream`);
    ws.onmessage = (ev) => {
      try { handle(JSON.parse(ev.data)); } catch (e) { console.error('[omx-ws]', e); }
    };
    ws.onclose = () => setTimeout(connect, 5_000);
    // keep-alive (dashboard_node 의 await ws.receive_text())
    setInterval(() => { if (ws.readyState === 1) ws.send('ping'); }, 25_000);
  }
  connect();
})();

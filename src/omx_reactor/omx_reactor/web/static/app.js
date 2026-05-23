/* app.js — omx_reactor adapter
 *
 * omx_reactor 의 /ws/stream payload 를 vendored engaging-analytics.js 가
 * 기대하는 doby shape 으로 변환해서 동일한 UI 를 구동한다.
 *
 * vendored engaging-analytics.js (0 modification) 는 /ws/v1/engaging 로
 * WebSocket 을 여는데 omx_reactor 에는 해당 endpoint 가 없다. 따라서
 * window.WebSocket 을 hijack — engaging-analytics.js 의 connect 호출은
 * FakeWS 로 가로채고, 실제 데이터는 /ws/stream 의 omx payload 를 변환해서
 * FakeWS.onmessage 로 주입한다.
 *
 * 또한 engaging-analytics.js 는 window.store 가 없으면 항상 visible 유지하고
 * (init() 의 if-guard), bindUtter 의 click handler 는 omx_reactor 에 dialog
 * endpoint 가 없어 NET 에러로 떨어진다 — 기능 제한, UX 동일성 우선.
 */
(function () {
  // ─── doby shape buffer (client-side accumulator) ─────
  const TRAJ_MAX = 30;
  const RECENT_MAX = 8;
  const nowSec = () => Date.now() / 1000;

  const state = {
    emotion: {
      latest: null,              // {v, a, conf, source, track_id, group_id, flags}
      trajectory: [],            // [{v, a, t}]
    },
    rapport: {
      counters: {
        engagement_up: 0,
        engagement_down: 0,
        abort_trigger: 0,
        neutral_continue: 0,
      },
      recent: [],                // [{type, weight, reason, ts, v, a, track_id}]
    },
    minigame: { latest: null, recent: [] },   // P0 — 항상 빈
    mode: { current: 'engaging', entered_at: 0 },
  };

  // ─── status bar (omx_reactor 고유) ────────────────────
  const $ = (id) => document.getElementById(id);
  function setStatus(p) {
    if (!p) return;
    if (p.current_motion !== undefined) $('current_motion').textContent = p.current_motion || '-';
    if (p.queued_motion !== undefined) $('queued_motion').textContent = p.queued_motion || '-';
    if (p.track_id !== undefined) $('track').textContent = (p.track_id >= 0 ? p.track_id : '-');
    if (p.source !== undefined && p.source !== null) $('source').textContent = p.source || '-';
  }

  // ─── 이벤트 로그 (omx_reactor 고유) ──────────────────
  const eventsEl = $('events');
  function pushEvent(kind, text) {
    if (!eventsEl) return;
    const li = document.createElement('li');
    li.className = kind;
    const ts = new Date().toLocaleTimeString();
    li.textContent = `${ts}  ${text}`;
    eventsEl.prepend(li);
    while (eventsEl.children.length > 20) eventsEl.lastChild.remove();
  }

  // ─── omx → doby shape 변환 ────────────────────────────
  function buildPayload() {
    return {
      ts: nowSec(),
      emotion: {
        latest: state.emotion.latest,
        trajectory: state.emotion.trajectory.slice(),
      },
      rapport: {
        counters: { ...state.rapport.counters },
        recent: state.rapport.recent.slice(),
      },
      minigame: state.minigame,
      mode: state.mode,
    };
  }

  function ingestEmotion(p) {
    // p: {v, a, confidence, source, track_id, [group_id]}
    if (p === null || p === undefined) return;
    if (p.v === null || p.v === undefined) return;
    const latest = {
      v: p.v,
      a: p.a,
      conf: (p.confidence !== undefined && p.confidence !== null) ? p.confidence : 0,
      source: p.source || '',
      track_id: (p.track_id !== undefined && p.track_id !== null) ? p.track_id : -1,
      // dashboard_node 는 group_id 를 노출하지 않음 — Solo 로 표시
      group_id: -1,
      flags: p.flags || [],
    };
    state.emotion.latest = latest;
    state.emotion.trajectory.push({ v: p.v, a: p.a, t: nowSec() });
    while (state.emotion.trajectory.length > TRAJ_MAX) state.emotion.trajectory.shift();
  }

  function ingestRapport(p) {
    // p: {event_type, weight, reason, v, a, [track_id]}
    if (!p || !p.event_type) return;
    const t = p.event_type;
    if (state.rapport.counters[t] !== undefined) {
      state.rapport.counters[t] += 1;
    }
    state.rapport.recent.push({
      type: t,
      weight: (p.weight !== undefined && p.weight !== null) ? p.weight : 0,
      reason: p.reason || '',
      ts: nowSec(),
      v: (p.v !== undefined && p.v !== null) ? p.v : 0,
      a: (p.a !== undefined && p.a !== null) ? p.a : 0,
      track_id: (p.track_id !== undefined && p.track_id !== null) ? p.track_id : -1,
    });
    while (state.rapport.recent.length > RECENT_MAX) state.rapport.recent.shift();
  }

  // ─── FakeWebSocket — engaging-analytics.js 가 /ws/v1/engaging 로
  //     접속 시 진짜 socket 대신 본 객체를 돌려준다 ─────────
  class FakeEngagingWS {
    constructor(url) {
      this.url = url;
      this.readyState = 0; // CONNECTING
      this.onopen = null;
      this.onmessage = null;
      this.onclose = null;
      this.onerror = null;
      FakeEngagingWS._instances.push(this);
      // 다음 tick 에 'open' 발사 — engaging-analytics.js 가 핸들러 부착 후 호출되도록
      setTimeout(() => {
        this.readyState = 1; // OPEN
        if (this.onopen) try { this.onopen({}); } catch (e) {}
      }, 0);
    }
    close() {
      this.readyState = 3;
      if (this.onclose) try { this.onclose({}); } catch (e) {}
      const i = FakeEngagingWS._instances.indexOf(this);
      if (i >= 0) FakeEngagingWS._instances.splice(i, 1);
    }
    send() { /* no-op */ }
    static broadcast(payload) {
      const text = JSON.stringify(payload);
      for (const ws of FakeEngagingWS._instances.slice()) {
        if (ws.readyState === 1 && ws.onmessage) {
          try { ws.onmessage({ data: text }); } catch (e) { /* ignore */ }
        }
      }
    }
  }
  FakeEngagingWS._instances = [];

  // window.WebSocket hijack — /ws/v1/engaging 만 가로채고 나머지는 원본 사용
  const _RealWebSocket = window.WebSocket;
  window.WebSocket = function (url, protocols) {
    if (typeof url === 'string' && url.indexOf('/ws/v1/engaging') >= 0) {
      return new FakeEngagingWS(url);
    }
    return protocols !== undefined ? new _RealWebSocket(url, protocols) : new _RealWebSocket(url);
  };
  // prototype/static 보존 (구식 코드 호환)
  for (const k of Object.keys(_RealWebSocket)) {
    try { window.WebSocket[k] = _RealWebSocket[k]; } catch (e) {}
  }
  window.WebSocket.prototype = _RealWebSocket.prototype;

  // ─── omx /ws/stream 핸들러 ────────────────────────────
  function handle(msg) {
    if (msg.type === 'snapshot') {
      const pay = msg.payload || {};
      if (pay.emotion) ingestEmotion(pay.emotion);
      if (pay.rapport) ingestRapport(pay.rapport);
      if (pay.reactor) {
        setStatus(pay.reactor);
        // reactor 는 smoothed v/a — emotion 으로 흡수
        ingestEmotion(pay.reactor);
      }
      FakeEngagingWS.broadcast(buildPayload());
    } else if (msg.type === 'emotion') {
      ingestEmotion(msg.payload);
      FakeEngagingWS.broadcast(buildPayload());
    } else if (msg.type === 'reactor') {
      const p = msg.payload;
      setStatus(p);
      ingestEmotion(p);   // reactor.v/a 는 smoothed 결과 — trajectory 의 SoT
      if (p.current_motion) {
        pushEvent('motion', `▶ ${p.current_motion}` + (p.session_event ? ` (${p.session_event})` : ''));
      }
      FakeEngagingWS.broadcast(buildPayload());
    } else if (msg.type === 'rapport') {
      const p = msg.payload;
      ingestRapport(p);
      pushEvent('rapport', `${p.event_type}  w=${p.weight.toFixed(2)}  ${p.reason}`);
      FakeEngagingWS.broadcast(buildPayload());
    }
  }

  function connect() {
    const ws = new _RealWebSocket(`ws://${location.host}/ws/stream`);
    ws.onmessage = (ev) => {
      try { handle(JSON.parse(ev.data)); } catch (e) { console.error('[omx-ws]', e); }
    };
    ws.onclose = () => setTimeout(connect, 5_000);
    // keep-alive (dashboard_node 의 await ws.receive_text())
    setInterval(() => { if (ws.readyState === 1) ws.send('ping'); }, 25_000);
  }
  connect();

  // engaging-analytics.js 는 init() 에서 window.store 가 없으면 mode 분기를
  // 건너뛴다 — section.hidden 은 initial HTML(hidden 속성 제거됨) 상태 유지.
})();

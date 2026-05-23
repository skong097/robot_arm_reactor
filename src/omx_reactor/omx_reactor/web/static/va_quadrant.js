// V·A 4분면 산점도 + 30초 trail.
// state.va 가 갱신될 때마다 redraw.

const W = 360, H = 360;
const PAD = 30;
const QUAD_LABELS = { Q1: 'DANCE', Q2: 'FREEZE', Q3: 'CONSOLE', Q4: 'IDLE' };

class VAQuadrant {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.trail = [];   // { v, a, t }
    this.current = null;
    this._draw();
  }
  push(v, a) {
    const t = performance.now();
    this.trail.push({ v, a, t });
    this.current = { v, a };
    // 30s trail 만 유지
    const cutoff = t - 30_000;
    this.trail = this.trail.filter(p => p.t > cutoff);
    this._draw();
  }
  _toCanvas(v, a) {
    // v: -1..+1 → x: PAD..W-PAD
    // a: -1..+1 → y: H-PAD..PAD (위가 +)
    const x = PAD + (v + 1) * 0.5 * (W - 2 * PAD);
    const y = (H - PAD) - (a + 1) * 0.5 * (H - 2 * PAD);
    return [x, y];
  }
  _draw() {
    const c = this.ctx;
    c.clearRect(0, 0, W, H);

    // 그리드
    c.strokeStyle = '#2a2e38';
    c.lineWidth = 1;
    c.beginPath();
    c.moveTo(W / 2, PAD); c.lineTo(W / 2, H - PAD);
    c.moveTo(PAD, H / 2); c.lineTo(W - PAD, H / 2);
    c.stroke();

    // 축 라벨
    c.fillStyle = '#6b7280';
    c.font = '11px monospace';
    c.fillText('V+', W - 22, H / 2 + 14);
    c.fillText('V-', 6, H / 2 + 14);
    c.fillText('A+', W / 2 + 4, 14);
    c.fillText('A-', W / 2 + 4, H - 6);

    // 분면별 모션 라벨
    c.fillStyle = '#62a9ff';
    c.font = 'bold 14px monospace';
    c.fillText(QUAD_LABELS.Q2, PAD + 24, PAD + 30);
    c.fillText(QUAD_LABELS.Q1, W - PAD - 80, PAD + 30);
    c.fillText(QUAD_LABELS.Q3, PAD + 24, H - PAD - 18);
    c.fillText(QUAD_LABELS.Q4, W - PAD - 60, H - PAD - 18);

    // trail (옅게)
    for (const p of this.trail) {
      const [x, y] = this._toCanvas(p.v, p.a);
      c.fillStyle = 'rgba(98, 169, 255, 0.20)';
      c.beginPath(); c.arc(x, y, 3, 0, Math.PI * 2); c.fill();
    }
    // current (강조)
    if (this.current) {
      const [x, y] = this._toCanvas(this.current.v, this.current.a);
      c.fillStyle = '#ff8b62';
      c.beginPath(); c.arc(x, y, 6, 0, Math.PI * 2); c.fill();
    }
  }
}

window.VAQuadrant = VAQuadrant;

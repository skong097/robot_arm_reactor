"""motion_scheduler — cooldown + priority interrupt + queue(depth=1) 정책."""
from __future__ import annotations

from enum import Enum

from omx_reactor.motions import Motion


class SchedulerAction(Enum):
    IGNORE = 'ignore'
    START = 'start'
    QUEUE = 'queue'
    INTERRUPT = 'interrupt'


class MotionScheduler:
    """단일 모션 진행 + 큐 깊이 1 + 같은 id cooldown."""

    def __init__(self, cooldown_default_sec: float = 5.0):
        # NOTE: 현재 미사용 — Motion.cooldown_sec 는 float (None 불가) + 기본값 없음 →
        # 호출자가 항상 명시. 향후 Motion 에 cooldown_sec 옵셔널화될 때 fallback 으로 활용.
        self._default_cooldown = cooldown_default_sec
        self._current: Motion | None = None
        self._queued: Motion | None = None
        # id -> 다음 실행 가능 시각
        self._available_at: dict[str, float] = {}

    # ── submit ─────────────────────────────────────────────
    def submit(self, motion: Motion, t_now: float) -> SchedulerAction:
        # 같은 id cooldown 검사
        avail = self._available_at.get(motion.id, 0.0)
        if t_now < avail:
            return SchedulerAction.IGNORE

        # 진행 중 없음 → 즉시 시작
        if self._current is None:
            self._current = motion
            return SchedulerAction.START

        # 진행 중 모션과 같은 id 재요청 → 무시 (cooldown 과 무관)
        if motion.id == self._current.id:
            return SchedulerAction.IGNORE

        # priority 높음 → interrupt
        if motion.priority > self._current.priority:
            self._current = motion
            self._queued = None       # 큐는 비움
            return SchedulerAction.INTERRUPT

        # 같은 priority 거나 낮음 → 큐 depth 1 (덮어쓰기)
        self._queued = motion
        return SchedulerAction.QUEUE

    # ── on_finish ──────────────────────────────────────────
    def on_finish(self, t_now: float) -> Motion | None:
        """현 모션이 끝났음을 통보. 큐에 있으면 다음 모션 반환 + current 로 promote."""
        if self._current is not None:
            cd = self._current.cooldown_sec
            self._available_at[self._current.id] = t_now + cd
        self._current = self._queued
        self._queued = None
        return self._current

    # ── 조회 ───────────────────────────────────────────────
    @property
    def current(self) -> Motion | None:
        return self._current

    @property
    def queued(self) -> Motion | None:
        return self._queued

    def cooldown_remaining(self, motion_id: str, t_now: float) -> float:
        return max(0.0, self._available_at.get(motion_id, 0.0) - t_now)

"""session_tracker — track_id 시퀀스 관찰로 'new_track' / 'track_gone' 이벤트 발행.

V·A 와 직교한 세션 경계 트리거. HELLO/BYE 모션의 입력.
"""
from __future__ import annotations


class SessionTracker:
    """track_id 시퀀스 → 'new_track' | 'track_gone' | None.

    P0 단순화: track_id 변경 (N -> M) 도 'new_track' 으로 처리.
    단, 같은 track_id 가 grace 안에 복귀하면 (-1 깜빡임/occlusion) 재인사 X.
    """

    def __init__(self, bye_grace_sec: float = 3.0):
        self._grace = bye_grace_sec
        self._last_track_id: int = -1
        self._last_valid_id: int = -1              # 마지막으로 본 valid track_id (>=0)
        self._lost_at: float | None = None         # -1 로 떨어진 시점
        self._gone_emitted: bool = False           # 이번 lost 세션에 track_gone 이미 발행했나

    def update(self, current_track_id: int, t_now: float) -> str | None:
        prev = self._last_track_id
        self._last_track_id = current_track_id

        # ── valid -> valid (또는 first valid, 또는 lost 후 복귀)
        if current_track_id != -1:
            # 같은 track_id 가 grace 안에 복귀 + 아직 gone 미발행 → 재인사 X
            returning_same_within_grace = (
                prev == -1
                and current_track_id == self._last_valid_id
                and not self._gone_emitted
            )

            self._lost_at = None
            self._gone_emitted = False
            prev_valid = self._last_valid_id
            self._last_valid_id = current_track_id

            if returning_same_within_grace:
                return None
            if prev_valid == -1:
                # 한 번도 valid id 를 본 적 없음 — 첫 인사
                return 'new_track'
            if prev_valid != current_track_id:
                # 다른 track_id — 새 사람으로 간주
                return 'new_track'
            # prev_valid == current_track_id, 연속 관측 (prev 도 valid 였음)
            return None

        # ── current == -1
        if prev != -1:
            # 막 잃음 — grace 시작
            self._lost_at = t_now
            self._gone_emitted = False
            return None

        # ── 이미 잃은 상태 (prev == -1)
        if self._lost_at is not None and not self._gone_emitted:
            if (t_now - self._lost_at) > self._grace:
                self._gone_emitted = True
                return 'track_gone'
        return None

"""gesture_detection — pure logic for hand visibility + cooldown.

mediapipe / ROS 무의존. mediapipe HandLandmarker 결과 (landmarks 존재 여부)
를 받아 'hand_visible' event emit + cooldown 관리. 단위 테스트 친화 (시간 주입).
"""
from __future__ import annotations


class HandVisibilityDetector:
    """손 visibility 감지기 + cooldown.

    Caller 가 매 frame 마다 update(visible, t_now) 호출.
    - visible = mediapipe 가 손 detect 했나
    - cooldown 안의 추가 visible 은 emit X (motion spam 방지)
    - 손이 없어졌다 다시 보여도 cooldown 안이면 emit X
    """

    def __init__(self, cooldown_sec: float = 5.0):
        self._cooldown = cooldown_sec
        self._last_emit_t: float | None = None

    def update(self, visible: bool, t_now: float) -> str | None:
        if not visible:
            return None
        # 첫 emit
        if self._last_emit_t is None:
            self._last_emit_t = t_now
            return 'hand_visible'
        # cooldown 검사
        if (t_now - self._last_emit_t) > self._cooldown:
            self._last_emit_t = t_now
            return 'hand_visible'
        return None

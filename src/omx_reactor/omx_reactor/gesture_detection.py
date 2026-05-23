"""gesture_detection — pure logic for hand visibility + cooldown + wave detection.

mediapipe / ROS 무의존. mediapipe GestureRecognizer 결과 (recognized gesture name +
hand landmark wrist position) 를 받아 event_type 결정 + cooldown + wave 시계열 분석.
모두 단위 테스트 친화 (시간 주입, frame 주입).
"""
from __future__ import annotations

from collections import deque


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


def classify_hand_state(
    gesture: str | None,
    wrist_y_normalized: float,
    is_waving: bool,
    up_threshold: float = 0.4,
) -> str | None:
    """recognized gesture + wrist 위치 + wave 결합 → event_type.

    - gesture != 'Open_Palm' → None (다른 gesture 는 별 매핑 없음 — 추후 확장)
    - Open_Palm + wrist y < up_threshold + wave → 'hands_up_wave'
    - Open_Palm + wrist y < up_threshold + no wave → 'hands_up'
    - Open_Palm + wrist 중간 → 'hand_visible'

    wrist_y_normalized: 0.0 (이미지 상단) ~ 1.0 (하단). mediapipe HandLandmarker 의
    landmark 0 (wrist) y 좌표 정규화 값.
    """
    if gesture != 'Open_Palm':
        return None
    if wrist_y_normalized < up_threshold:
        return 'hands_up_wave' if is_waving else 'hands_up'
    return 'hand_visible'


class WaveDetector:
    """wrist x 시계열 좌우 진동 감지.

    매 frame 마다 update(wrist_x_normalized) — 0.0 (좌측) ~ 1.0 (우측).
    최근 window_size 점들의 peak-to-peak > oscillation_threshold 면 wave.
    초기 window 충분 안 채워지면 False (false positive 방지).
    """

    def __init__(self, window_size: int = 10, oscillation_threshold: float = 0.2):
        self._window: deque[float] = deque(maxlen=window_size)
        self._window_size = window_size
        self._threshold = oscillation_threshold

    def update(self, wrist_x_normalized: float) -> None:
        self._window.append(wrist_x_normalized)

    def is_waving(self) -> bool:
        if len(self._window) < self._window_size:
            return False
        return (max(self._window) - min(self._window)) > self._threshold

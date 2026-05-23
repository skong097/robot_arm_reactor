"""context — reactor 가 매 tick 합성하는 입력 신호 통합."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmotionSignal:
    """rapport_tracker EMA 출력 + 분면 라벨."""
    v: float          # smoothed valence (-1.0 ~ +1.0)
    a: float          # smoothed arousal (-1.0 ~ +1.0)
    quadrant: str | None   # 'Q1'|'Q2'|'Q3'|'Q4', None = 데드밴드
    in_deadband: bool
    confidence: float
    source: str       # 'face' | 'voice' | 'fused'


@dataclass
class GestureSignal:
    """gesture_detector_node 의 /gesture/event 출력 — 1 tick 만 살아있음."""
    event: str          # 'hand_visible' | ... (확장 시 추가)
    confidence: float   # 0.0 ~ 1.0
    source: str         # 'mediapipe.HandLandmarker'


# P2+ 자리 (지금은 정의만 없음 — 추가 시 여기에 dataclass 추가)
# @dataclass
# class PoseSignal: ...


@dataclass
class Context:
    """매 tick reactor 가 합성하는 입력."""
    emotion: EmotionSignal | None     # P0 source
    session_event: str | None         # 'new_track' | 'track_gone' | None (한 tick 만)
    t_now: float                      # 시계 (테스트 주입 용이)
    gesture: GestureSignal | None = None   # P1 — 1 tick 만 (default None, 후방 호환)
    # pose: PoseSignal | None         # P2


def make_emotion_signal(v: float, a: float, confidence: float = 1.0,
                        source: str = 'face',
                        deadband: float = 0.10) -> EmotionSignal:
    """V·A 로부터 quadrant 라벨링까지 한번에."""
    in_db = abs(v) < deadband and abs(a) < deadband
    if in_db:
        q = None
    elif v >= 0 and a >= 0:   q = 'Q1'
    elif v <  0 and a >= 0:   q = 'Q2'
    elif v <  0 and a <  0:   q = 'Q3'
    else:                      q = 'Q4'
    return EmotionSignal(v=v, a=a, quadrant=q, in_deadband=in_db,
                         confidence=confidence, source=source)

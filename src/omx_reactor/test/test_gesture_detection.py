"""TDD — hand visibility detection + cooldown.

gesture_detection.py 는 mediapipe / ROS 무의존 pure logic.
mediapipe HandLandmarker 결과 (landmarks 존재 여부 bool) 를 받아
'hand_visible' 이벤트 emit + cooldown 관리.
"""
import pytest

from omx_reactor.gesture_detection import HandVisibilityDetector


def test_first_visible_emits():
    det = HandVisibilityDetector(cooldown_sec=5.0)
    assert det.update(visible=True, t_now=0.0) == 'hand_visible'


def test_visible_continuous_within_cooldown_no_emit():
    det = HandVisibilityDetector(cooldown_sec=5.0)
    det.update(visible=True, t_now=0.0)
    assert det.update(visible=True, t_now=1.0) is None
    assert det.update(visible=True, t_now=4.9) is None


def test_visible_after_cooldown_emits_again():
    det = HandVisibilityDetector(cooldown_sec=5.0)
    det.update(visible=True, t_now=0.0)
    assert det.update(visible=True, t_now=5.01) == 'hand_visible'


def test_not_visible_no_emit():
    det = HandVisibilityDetector(cooldown_sec=5.0)
    assert det.update(visible=False, t_now=0.0) is None
    assert det.update(visible=False, t_now=1.0) is None


def test_visible_lost_then_visible_again_within_cooldown_no_emit():
    """grace 안 손 깜빡임 + 복귀 — cooldown 안이라 emit X (spam 방지)."""
    det = HandVisibilityDetector(cooldown_sec=5.0)
    det.update(visible=True, t_now=0.0)
    det.update(visible=False, t_now=1.0)
    assert det.update(visible=True, t_now=2.0) is None


def test_visible_lost_then_visible_after_cooldown_emits():
    """오래 떠난 후 손 다시 보임 — emit."""
    det = HandVisibilityDetector(cooldown_sec=5.0)
    det.update(visible=True, t_now=0.0)
    det.update(visible=False, t_now=1.0)
    assert det.update(visible=True, t_now=6.0) == 'hand_visible'


def test_cooldown_zero_emits_every_transition():
    """cooldown=0 시 매 visibility=True 마다 emit (테스트 친화)."""
    det = HandVisibilityDetector(cooldown_sec=0.0)
    assert det.update(visible=True, t_now=0.0) == 'hand_visible'
    assert det.update(visible=True, t_now=0.1) == 'hand_visible'

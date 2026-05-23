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


# ─── classify_hand_state — Open_Palm + wrist 위치 + wave 결합 ───
from omx_reactor.gesture_detection import classify_hand_state, WaveDetector


def test_classify_open_palm_middle_no_wave_is_hand_visible():
    assert classify_hand_state('Open_Palm', wrist_y_normalized=0.5, is_waving=False) == 'hand_visible'


def test_classify_open_palm_up_no_wave_is_hands_up():
    assert classify_hand_state('Open_Palm', wrist_y_normalized=0.3, is_waving=False) == 'hands_up'


def test_classify_open_palm_up_wave_is_hands_up_wave():
    assert classify_hand_state('Open_Palm', wrist_y_normalized=0.3, is_waving=True) == 'hands_up_wave'


def test_classify_open_palm_up_threshold_boundary():
    # default up_threshold=0.4 — exclusive
    assert classify_hand_state('Open_Palm', wrist_y_normalized=0.39, is_waving=False) == 'hands_up'
    assert classify_hand_state('Open_Palm', wrist_y_normalized=0.41, is_waving=False) == 'hand_visible'


def test_classify_other_gesture_returns_none():
    assert classify_hand_state('Closed_Fist', wrist_y_normalized=0.3, is_waving=False) is None
    assert classify_hand_state('Thumb_Up', wrist_y_normalized=0.5, is_waving=False) is None
    assert classify_hand_state('Victory', wrist_y_normalized=0.3, is_waving=True) is None


def test_classify_none_gesture_returns_none():
    assert classify_hand_state(None, wrist_y_normalized=0.5, is_waving=False) is None
    assert classify_hand_state('', wrist_y_normalized=0.3, is_waving=False) is None


# ─── WaveDetector — wrist x 시계열 진동 감지 ───

def test_wave_constant_no_oscillation():
    wd = WaveDetector(window_size=10, oscillation_threshold=0.2)
    for _ in range(10):
        wd.update(wrist_x_normalized=0.5)
    assert wd.is_waving() is False


def test_wave_strong_oscillation_detected():
    wd = WaveDetector(window_size=10, oscillation_threshold=0.2)
    for x in [0.3, 0.7, 0.3, 0.7, 0.3, 0.7, 0.3, 0.7, 0.3, 0.7]:
        wd.update(wrist_x_normalized=x)
    assert wd.is_waving() is True


def test_wave_below_threshold_no_detect():
    wd = WaveDetector(window_size=10, oscillation_threshold=0.3)
    # peak-to-peak = 0.2 < threshold 0.3
    for x in [0.4, 0.6, 0.4, 0.6]:
        wd.update(wrist_x_normalized=x)
    assert wd.is_waving() is False


def test_wave_window_drops_old_samples():
    wd = WaveDetector(window_size=4, oscillation_threshold=0.2)
    # 초기 진동 → window 가 새 정적 값으로 채워지면 wave 해제
    for x in [0.3, 0.7, 0.3, 0.7]:
        wd.update(wrist_x_normalized=x)
    assert wd.is_waving() is True
    for _ in range(5):   # window=4 보다 더 — 옛 진동 다 빠짐
        wd.update(wrist_x_normalized=0.5)
    assert wd.is_waving() is False


def test_wave_insufficient_samples_no_detect():
    """window_size 채우기 전엔 wave X (단조롭다 판정 어려움 — false positive 방지)."""
    wd = WaveDetector(window_size=10, oscillation_threshold=0.2)
    wd.update(wrist_x_normalized=0.3)
    wd.update(wrist_x_normalized=0.7)
    assert wd.is_waving() is False

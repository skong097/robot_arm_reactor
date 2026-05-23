"""Backward-compat shim — gesture_detection 은 arm_reactor_core.gesture_detection 로 이동."""
from arm_reactor_core.gesture_detection import (   # noqa: F401
    HandVisibilityDetector,
    classify_hand_state,
    WaveDetector,
)

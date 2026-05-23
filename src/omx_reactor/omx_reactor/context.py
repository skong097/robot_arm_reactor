"""Backward-compat shim — context 는 arm_reactor_core.context 로 이동했음.

신규 코드는 `from arm_reactor_core.context import ...` 직접 사용 권장.
본 shim 은 omx_reactor 내부 모듈 (motions.py / motion_mapper.py / reactor_node.py)
의 기존 import 경로 호환성을 위해 유지.
"""
from arm_reactor_core.context import (   # noqa: F401
    EmotionSignal,
    GestureSignal,
    Context,
    make_emotion_signal,
)

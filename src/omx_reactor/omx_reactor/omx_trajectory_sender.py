"""Backward-compat shim — TrajectorySender 는 arm_reactor_core.trajectory_sender 로 이동.

OmxTrajectorySender 라는 OMX-specific 이름은 의미상 맞지 않아 generic
TrajectorySender 로 rename 했음. 본 shim 은 외부 import 호환용.
"""
from arm_reactor_core.trajectory_sender import TrajectorySender as OmxTrajectorySender  # noqa: F401

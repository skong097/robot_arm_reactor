"""Backward-compat shim — motions 는 omx_motion_pack.motions 로 이동."""
from omx_motion_pack.motions import MOTIONS   # noqa: F401
from arm_reactor_core.motion import Motion    # noqa: F401  (외부 import 호환)

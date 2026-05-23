"""Backward-compat shim — trajectories 는 omx_motion_pack.trajectories 로 이동."""
from omx_motion_pack.trajectories import (   # noqa: F401
    Dispatch, ARM_ACT, GRIPPER_ACT,
    JOINT_NAMES, HOME,
    GRIPPER_JOINT_NAMES, GRIPPER_OPEN_ANGLE, GRIPPER_CLOSE_ANGLE,
    traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
    traj_hand_out, traj_hands_up, traj_hands_up_wave,
    traj_point_back, traj_nod, traj_cheer, traj_heart, traj_strong, traj_sad,
    traj_twinkle, traj_gripper_open, traj_gripper_close,
)

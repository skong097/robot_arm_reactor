"""motions — OMX MOTIONS 리스트 (arm-specific). Motion dataclass 는 arm_reactor_core 로 이동."""
from __future__ import annotations

from arm_reactor_core.motion import Motion   # noqa: F401  (재export — 기존 import 호환)


# trajectories import 는 함수 정의 후에 한다 (순환 방지 필요 없음 — trajectories.py 는 motions 안 참조)
from omx_motion_pack.trajectories import (
    traj_dance, traj_freeze, traj_console, traj_idle, traj_hello, traj_bye,
    traj_hand_out, traj_hands_up, traj_hands_up_wave,
    traj_point_back, traj_nod, traj_cheer, traj_heart, traj_strong, traj_sad, traj_twinkle,
    traj_gripper_open, traj_gripper_close,
)

MOTIONS: list[Motion] = [
    # 감정 4분면 (priority 10)
    Motion('DANCE',
           trigger=lambda c: bool(c.emotion and c.emotion.quadrant == 'Q1'),
           priority=10, cooldown_sec=1.0, trajectory=traj_dance),
    Motion('FREEZE',
           trigger=lambda c: bool(c.emotion and c.emotion.quadrant == 'Q2'),
           priority=10, cooldown_sec=5.0, trajectory=traj_freeze),
    Motion('CONSOLE',
           trigger=lambda c: bool(c.emotion and c.emotion.quadrant == 'Q3'),
           priority=10, cooldown_sec=5.0, trajectory=traj_console),
    Motion('IDLE',
           trigger=lambda c: bool(c.emotion and
                                  (c.emotion.quadrant == 'Q4' or c.emotion.in_deadband)),
           priority=0,  cooldown_sec=0.0, trajectory=traj_idle),

    # 세션 경계 (priority 100 — 분면 모션 interrupt)
    Motion('HELLO',
           trigger=lambda c: c.session_event == 'new_track',
           priority=100, cooldown_sec=0.0, trajectory=traj_hello),
    Motion('BYE',
           trigger=lambda c: c.session_event == 'track_gone',
           priority=100, cooldown_sec=0.0, trajectory=traj_bye),

    # Gesture mimic (HELLO/BYE 보다 낮지만 분면 모션 interrupt) — priority 80~95
    Motion('HAND_OUT',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'hand_visible'),
           priority=80, cooldown_sec=5.0, trajectory=traj_hand_out),
    Motion('TWINKLE',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'twinkle'),
           priority=82, cooldown_sec=5.0, trajectory=traj_twinkle),
    Motion('HANDS_UP',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'hands_up'),
           priority=85, cooldown_sec=5.0, trajectory=traj_hands_up),
    Motion('HANDS_UP_WAVE',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'hands_up_wave'),
           priority=90, cooldown_sec=5.0, trajectory=traj_hands_up_wave),
    Motion('POINT_BACK',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'pointing_up'),
           priority=82, cooldown_sec=5.0, trajectory=traj_point_back),
    Motion('NOD',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'thumb_up'),
           priority=82, cooldown_sec=5.0, trajectory=traj_nod),
    Motion('SAD',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'thumb_down'),
           priority=82, cooldown_sec=5.0, trajectory=traj_sad),
    Motion('CHEER',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'victory'),
           priority=85, cooldown_sec=5.0, trajectory=traj_cheer),
    Motion('HEART',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'ilove_you'),
           priority=82, cooldown_sec=5.0, trajectory=traj_heart),
    Motion('STRONG',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'closed_fist'),
           priority=82, cooldown_sec=5.0, trajectory=traj_strong),
    # Gripper — 별 controller (reactor 가 trajectory.joint_names 으로 dispatch 분기)
    Motion('GRIPPER_OPEN',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'gripper_open'),
           priority=95, cooldown_sec=3.0, trajectory=traj_gripper_open),
    Motion('GRIPPER_CLOSE',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'gripper_close'),
           priority=95, cooldown_sec=3.0, trajectory=traj_gripper_close),
]

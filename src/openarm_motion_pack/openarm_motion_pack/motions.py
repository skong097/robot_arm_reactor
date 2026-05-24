"""motions — OpenArm v10 bimanual MOTIONS 등록부 (18 Motion).

trigger set 은 OMX 와 동일 (14 trigger 의 motion 이름 동일, 4 trigger 는 양손 특화
대체 motion 이름).
"""
from __future__ import annotations

from arm_reactor_core.motion import Motion   # noqa: F401  (외부 import 호환)

from openarm_motion_pack.trajectories import (
    traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
    traj_handshake, traj_hands_up, traj_hands_up_wave,
    traj_nod, traj_sad, traj_strong, traj_twinkle, traj_gripper_open,
    traj_bimanual_clap, traj_bimanual_hug, traj_asymmetric_point, traj_bimanual_grip_clap,
)


MOTIONS: list[Motion] = [
    # 감정 4분면 (priority 10)
    Motion('DANCE',
           trigger=lambda c: bool(c.emotion and c.emotion.quadrant == 'Q1'),
           priority=10, cooldown_sec=5.0, trajectory=traj_dance),
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

    # 세션 (priority 100)
    Motion('HELLO',
           trigger=lambda c: c.session_event == 'new_track',
           priority=100, cooldown_sec=0.0, trajectory=traj_hello),
    Motion('BYE',
           trigger=lambda c: c.session_event == 'track_gone',
           priority=100, cooldown_sec=0.0, trajectory=traj_bye),

    # Gesture mimic — OMX 와 동일 trigger 14 + 4 가 양손 특화 대체
    Motion('HANDSHAKE',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'hand_visible'),
           priority=80, cooldown_sec=5.0, trajectory=traj_handshake),
    Motion('TWINKLE',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'twinkle'),
           priority=82, cooldown_sec=5.0, trajectory=traj_twinkle),
    Motion('HANDS_UP',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'hands_up'),
           priority=85, cooldown_sec=5.0, trajectory=traj_hands_up),
    Motion('HANDS_UP_WAVE',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'hands_up_wave'),
           priority=90, cooldown_sec=5.0, trajectory=traj_hands_up_wave),
    Motion('NOD',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'thumb_up'),
           priority=82, cooldown_sec=5.0, trajectory=traj_nod),
    Motion('SAD',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'thumb_down'),
           priority=82, cooldown_sec=5.0, trajectory=traj_sad),
    Motion('STRONG',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'closed_fist'),
           priority=82, cooldown_sec=5.0, trajectory=traj_strong),

    # 양손 특화 대체 4 (같은 trigger, 새 ID)
    Motion('BIMANUAL_CLAP',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'victory'),
           priority=85, cooldown_sec=5.0, trajectory=traj_bimanual_clap),
    Motion('BIMANUAL_HUG',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'ilove_you'),
           priority=82, cooldown_sec=5.0, trajectory=traj_bimanual_hug),
    Motion('ASYMMETRIC_POINT',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'pointing_up'),
           priority=82, cooldown_sec=5.0, trajectory=traj_asymmetric_point),

    # 그리퍼 — GRIPPER_OPEN (gripper_open trigger) + BIMANUAL_GRIP_CLAP (gripper_close trigger)
    Motion('GRIPPER_OPEN',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'gripper_open'),
           priority=95, cooldown_sec=3.0, trajectory=traj_gripper_open),
    Motion('BIMANUAL_GRIP_CLAP',
           trigger=lambda c: bool(c.gesture and c.gesture.event == 'gripper_close'),
           priority=95, cooldown_sec=3.0, trajectory=traj_bimanual_grip_clap),
]

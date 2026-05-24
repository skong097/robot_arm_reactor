"""trajectories — OpenArm v10 bimanual 의 18 trajectory factory.

각 factory 는 list[Dispatch] 반환 (양손 atomic 모션).

joint 매핑 (OpenArm v10):
  joint1: base yaw (±200°)        joint2: 어깨 (±100°)
  joint3: upper arm yaw (±90°)    joint4: 엘보 (0~140°)
  joint5: forearm yaw (±90°)      joint6: 손목 pitch (±45°)
  joint7: 손목 yaw (±90°)
  finger_joint1: 그리퍼 (0~0.043)

안전 제약:
  - safe range: joint_limits.yaml lower/upper 의 90% 이내 (액추에이터 limit 여유)
  - velocity: ≤ 2.5 rad/s (expressive motion, OMX 와 동일 게이트)
"""
from __future__ import annotations

from builtin_interfaces.msg import Duration
from control_msgs.action import GripperCommand
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from arm_reactor_core.dispatch import Dispatch

# ─── action 이름 상수 (OpenArm bimanual controller 4종) ─────────────────────
LEFT_ARM_ACT   = '/left_joint_trajectory_controller/follow_joint_trajectory'
RIGHT_ARM_ACT  = '/right_joint_trajectory_controller/follow_joint_trajectory'
LEFT_GRIP_ACT  = '/left_gripper_controller/gripper_cmd'
RIGHT_GRIP_ACT = '/right_gripper_controller/gripper_cmd'

# ─── joint 이름 ────────────────────────────────────────────────────────────
LEFT_JOINTS  = [f'openarm_left_joint{i}'  for i in range(1, 8)]
RIGHT_JOINTS = [f'openarm_right_joint{i}' for i in range(1, 8)]

# ─── 자세 상수 ──────────────────────────────────────────────────────────────
# HOME: OpenArm v10 bimanual 의 default 'zero pose' — 양손 정자로 똑바로
# (URDF default 와 일치, 사용자 시각 검증: OpenArm bringup 단독 시 default 자세).
HOME = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
# 만세 — 양팔 북쪽 (world +Z, 위) 으로 끝까지 뻗기.
# OpenArm URDF: joint2 axis=(-1,0,0), left base rpy=(-π/2,0,0) / right rpy=(+π/2,0,0)
# → joint2 양수 = left 위로, right 아래로 (mirror). 만세 = left/right 별 부호 반전.
# joint2 = ±1.57 (limit ±1.745 의 90%), joint4=0 (엘보 펴기 — 끝까지).
UP_LEFT  = [0.0,  1.57, 0.0, 0.0, 0.0, 0.0, 0.0]
UP_RIGHT = [0.0, -1.57, 0.0, 0.0, 0.0, 0.0, 0.0]
# UP (legacy — 단일 arm 자세 미사용. 양손 motion 은 UP_LEFT/UP_RIGHT 사용)
UP   = [0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0]
# 가리킴 (joint2 살짝 위, joint4 0 — 정면 reach)
PT   = [0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0]
# 안기 (양손 안쪽으로 joint1 ±0.4)
HUG_L = [-0.4, -0.5, 0.0, 0.5, 0.0, 0.0, 0.0]
HUG_R = [ 0.4, -0.5, 0.0, 0.5, 0.0, 0.0, 0.0]
# 박수 (양손 link7 모음 — 안쪽 joint1 ±0.5)
CLAP_L = [-0.5, -0.6, 0.0, 0.6, 0.0, 0.0, 0.0]
CLAP_R = [ 0.5, -0.6, 0.0, 0.6, 0.0, 0.0, 0.0]

GRIPPER_OPEN_POS   = 0.04   # OpenArm finger range 0~0.043
GRIPPER_CLOSE_POS  = 0.0
GRIPPER_MAX_EFFORT = 5.0


# ─── 헬퍼 ───────────────────────────────────────────────────────────────────
def _point(positions: list[float], t_sec: float) -> JointTrajectoryPoint:
    p = JointTrajectoryPoint()
    p.positions = list(positions)
    p.time_from_start = Duration(sec=int(t_sec),
                                 nanosec=int((t_sec - int(t_sec)) * 1e9))
    return p


def _traj(joint_names: list[str], points: list[JointTrajectoryPoint]) -> JointTrajectory:
    t = JointTrajectory()
    t.joint_names = list(joint_names)
    t.points = points
    return t


def _build_gripper(position: float) -> GripperCommand.Goal:
    g = GripperCommand.Goal()
    g.command.position = float(position)
    g.command.max_effort = GRIPPER_MAX_EFFORT
    return g


def _both_arms(left_points: list[JointTrajectoryPoint],
               right_points: list[JointTrajectoryPoint]) -> list[Dispatch]:
    """양손 sym/asym dispatch list (left/right arm 2 개)."""
    return [
        Dispatch(LEFT_ARM_ACT,  _traj(LEFT_JOINTS,  left_points),  'trajectory'),
        Dispatch(RIGHT_ARM_ACT, _traj(RIGHT_JOINTS, right_points), 'trajectory'),
    ]


# ─── 14 OMX 직역 모션 (양손 sym) ───────────────────────────────────────────

def traj_idle() -> list[Dispatch]:
    pts = [_point(HOME, 0.5)]
    return _both_arms(pts, pts)


def traj_hello() -> list[Dispatch]:
    """양손 sym wave — joint4 ±1.0 ×2, 3s."""
    pts = [
        _point(HOME,                          0.5),
        _point([0.0, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0], 1.0),
        _point([0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0], 1.5),
        _point([0.0, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0], 2.0),
        _point([0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0], 2.5),
        _point(HOME,                          3.0),
    ]
    return _both_arms(pts, pts)


def traj_bye() -> list[Dispatch]:
    """HELLO 슬로우 (1.5×), 4.5s."""
    pts = [
        _point(HOME,                          0.75),
        _point([0.0, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0], 1.5),
        _point([0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0], 2.25),
        _point([0.0, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0], 3.0),
        _point([0.0, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0], 3.75),
        _point(HOME,                          4.5),
    ]
    return _both_arms(pts, pts)


def traj_dance() -> list[Dispatch]:
    """양손 joint1 ±0.7 sym swing ×3, 4s. peak velocity ~1.75 rad/s."""
    pts = [
        _point(HOME,                          0.4),
        _point([ 0.7, -0.3, 0.0, 0.5, 0.0, 0.0, 0.0], 1.2),
        _point([-0.7, -0.3, 0.0, 0.5, 0.0, 0.0, 0.0], 2.0),
        _point([ 0.7, -0.3, 0.0, 0.5, 0.0, 0.0, 0.0], 2.8),
        _point([-0.7, -0.3, 0.0, 0.5, 0.0, 0.0, 0.0], 3.6),
        _point(HOME,                          4.4),
    ]
    return _both_arms(pts, pts)


def traj_freeze() -> list[Dispatch]:
    """양손 joint2 살짝 down 0.05, 1s."""
    pts = [_point([0.0, -0.35, 0.0, 0.5, 0.0, 0.0, 0.0], 1.0)]
    return _both_arms(pts, pts)


def traj_console() -> list[Dispatch]:
    """양손 joint7 부드러운 좌우 ±0.4 ×4, 4s."""
    pts = [
        _point(HOME,                          0.4),
        _point([0.0, -0.3, 0.0, 0.5, 0.0, 0.0,  0.4], 1.0),
        _point([0.0, -0.3, 0.0, 0.5, 0.0, 0.0, -0.4], 1.6),
        _point([0.0, -0.3, 0.0, 0.5, 0.0, 0.0,  0.4], 2.2),
        _point([0.0, -0.3, 0.0, 0.5, 0.0, 0.0, -0.4], 2.8),
        _point([0.0, -0.3, 0.0, 0.5, 0.0, 0.0,  0.4], 3.4),
        _point(HOME,                          4.0),
    ]
    return _both_arms(pts, pts)


def traj_hand_out() -> list[Dispatch]:
    """양손 정면 reach (PT) + hold + home, 3.5s."""
    pts = [
        _point(HOME, 0.4),
        _point(PT,   1.5),
        _point(PT,   2.5),
        _point(HOME, 3.5),
    ]
    return _both_arms(pts, pts)


def traj_hands_up() -> list[Dispatch]:
    """양손 만세 (북쪽 위로 끝까지 뻗기, UP_LEFT/UP_RIGHT mirror 보정) + hold + home, 3.6s."""
    pts_l = [_point(HOME,     0.4), _point(UP_LEFT,  1.8), _point(UP_LEFT,  2.6), _point(HOME, 3.6)]
    pts_r = [_point(HOME,     0.4), _point(UP_RIGHT, 1.8), _point(UP_RIGHT, 2.6), _point(HOME, 3.6)]
    return _both_arms(pts_l, pts_r)


def traj_hands_up_wave() -> list[Dispatch]:
    """양손 만세 (UP_LEFT/UP_RIGHT mirror 보정) + joint1 ±0.5 swing ×2, 6.0s."""
    # 양손 위 자세 hold + joint1 양손 같이 ±0.5 swing
    UP_L_R  = [ 0.5,  1.57, 0.0, 0.0, 0.0, 0.0, 0.0]   # left arm, joint1 +0.5
    UP_L_L  = [-0.5,  1.57, 0.0, 0.0, 0.0, 0.0, 0.0]   # left arm, joint1 -0.5
    UP_R_R  = [ 0.5, -1.57, 0.0, 0.0, 0.0, 0.0, 0.0]   # right arm, joint1 +0.5
    UP_R_L  = [-0.5, -1.57, 0.0, 0.0, 0.0, 0.0, 0.0]   # right arm, joint1 -0.5
    pts_l = [
        _point(HOME,    0.4),
        _point(UP_LEFT, 1.8),
        _point(UP_L_R,  2.4),
        _point(UP_L_L,  3.0),
        _point(UP_L_R,  3.6),
        _point(UP_L_L,  4.2),
        _point(UP_LEFT, 4.8),
        _point(HOME,    6.0),
    ]
    pts_r = [
        _point(HOME,     0.4),
        _point(UP_RIGHT, 1.8),
        _point(UP_R_R,   2.4),
        _point(UP_R_L,   3.0),
        _point(UP_R_R,   3.6),
        _point(UP_R_L,   4.2),
        _point(UP_RIGHT, 4.8),
        _point(HOME,     6.0),
    ]
    return _both_arms(pts_l, pts_r)


def traj_nod() -> list[Dispatch]:
    """양손 joint7 끄덕 ±0.5 ×3, 3.3s."""
    NOD_DN = [0.0, -0.3, 0.0, 0.5, 0.0, 0.0,  0.5]
    NOD_UP = [0.0, -0.3, 0.0, 0.5, 0.0, 0.0, -0.5]
    pts = [
        _point(HOME,   0.4),
        _point(NOD_DN, 0.9),
        _point(NOD_UP, 1.4),
        _point(NOD_DN, 1.9),
        _point(NOD_UP, 2.4),
        _point(HOME,   3.3),
    ]
    return _both_arms(pts, pts)


def traj_sad() -> list[Dispatch]:
    """양손 joint2 down + joint4 굽힘 + joint7 살짝 down (머리 숙임), 3s."""
    SD = [0.0, -0.15, 0.0, 1.0, 0.0, 0.0, 0.5]
    pts = [
        _point(HOME, 0.5),
        _point(SD,   1.5),
        _point(SD,   2.3),
        _point(HOME, 3.0),
    ]
    return _both_arms(pts, pts)


def traj_strong() -> list[Dispatch]:
    """양손 위 (UP_LEFT/UP_RIGHT mirror 보정) + hold, 3.6s. arm only."""
    pts_l = [_point(HOME, 0.4), _point(UP_LEFT,  1.8), _point(UP_LEFT,  2.6), _point(HOME, 3.6)]
    pts_r = [_point(HOME, 0.4), _point(UP_RIGHT, 1.8), _point(UP_RIGHT, 2.6), _point(HOME, 3.6)]
    return _both_arms(pts_l, pts_r)


def traj_twinkle() -> list[Dispatch]:
    """양손 joint1 ±0.4 sym ×4, 3.6s."""
    TW_R = [ 0.4, -0.3, 0.0, 0.5, 0.0, 0.0, 0.0]
    TW_L = [-0.4, -0.3, 0.0, 0.5, 0.0, 0.0, 0.0]
    pts = [
        _point(HOME, 0.4),
        _point(TW_R, 0.8),
        _point(TW_L, 1.2),
        _point(TW_R, 1.6),
        _point(TW_L, 2.0),
        _point(TW_R, 2.4),
        _point(TW_L, 2.8),
        _point(TW_R, 3.2),
        _point(HOME, 3.6),
    ]
    return _both_arms(pts, pts)


def traj_gripper_open() -> list[Dispatch]:
    """양 그리퍼 동시 open (0.04)."""
    g = _build_gripper(GRIPPER_OPEN_POS)
    return [
        Dispatch(LEFT_GRIP_ACT,  g, 'gripper'),
        Dispatch(RIGHT_GRIP_ACT, g, 'gripper'),
    ]


# ─── 4 양손 특화 신규 (OMX 의 CHEER/HEART/POINT_BACK/GRIPPER_CLOSE 대체) ────

def traj_bimanual_clap() -> list[Dispatch]:
    """박수 — 양손 link7 모음 (CLAP_L/R 안쪽) + 분리 ×3, 3.2s. CHEER 대체 (victory)."""
    pts_l = [
        _point(HOME,   0.4),
        _point(CLAP_L, 1.0),
        _point([-0.3, -0.5, 0.0, 0.5, 0.0, 0.0, 0.0], 1.4),
        _point(CLAP_L, 1.8),
        _point([-0.3, -0.5, 0.0, 0.5, 0.0, 0.0, 0.0], 2.2),
        _point(CLAP_L, 2.6),
        _point(HOME,   3.2),
    ]
    pts_r = [
        _point(HOME,   0.4),
        _point(CLAP_R, 1.0),
        _point([ 0.3, -0.5, 0.0, 0.5, 0.0, 0.0, 0.0], 1.4),
        _point(CLAP_R, 1.8),
        _point([ 0.3, -0.5, 0.0, 0.5, 0.0, 0.0, 0.0], 2.2),
        _point(CLAP_R, 2.6),
        _point(HOME,   3.2),
    ]
    return _both_arms(pts_l, pts_r)


def traj_bimanual_hug() -> list[Dispatch]:
    """안기 — 양손 안쪽 펴 모음 (HUG_L/R) + hold, 3s. HEART 대체 (ilove_you)."""
    pts_l = [_point(HOME, 0.5), _point(HUG_L, 1.5), _point(HUG_L, 2.3), _point(HOME, 3.0)]
    pts_r = [_point(HOME, 0.5), _point(HUG_R, 1.5), _point(HUG_R, 2.3), _point(HOME, 3.0)]
    return _both_arms(pts_l, pts_r)


def traj_asymmetric_point() -> list[Dispatch]:
    """비대칭 가리킴 — 왼손 PT (정면 reach), 오른손 home 유지, 2.5s. POINT_BACK 대체 (pointing_up)."""
    pts_l = [
        _point(HOME, 0.4),
        _point(PT,   1.2),
        _point(PT,   2.0),
        _point(HOME, 2.5),
    ]
    pts_r = [_point(HOME, 2.5)]   # 오른손은 home 유지 (single point)
    return _both_arms(pts_l, pts_r)


def traj_salute() -> list[Dispatch]:
    """경례 — 오른손 머리 옆 (어깨 위 + 엘보 굽힘 + 손목 회전), 왼손 home idle (asym).
    sub-spec b 결정: STRONG (closed_fist) trigger 자리 대체 — 주먹 -> 경례 의미.
    3.0s, peak velocity ~1.2 rad/s.
    """
    SALUTE_POSE = [0.0, -0.8, 0.0, 1.2, 0.0, 0.0, 0.3]
    pts_r = [
        _point(HOME,        0.4),
        _point(SALUTE_POSE, 1.4),
        _point(SALUTE_POSE, 2.2),   # hold
        _point(HOME,        3.0),
    ]
    pts_l = [_point(HOME, 3.0)]   # left arm idle
    return _both_arms(pts_l, pts_r)


def traj_handshake() -> list[Dispatch]:
    """악수 — 오른손 정면 reach (PT) + joint7 위아래 ±0.3 ×2 흔듦. left arm home idle (asym).
    sub-spec b 결정: HAND_OUT (hand_visible) trigger 자리 대체 — 그리퍼 흔듦 의미 유사.
    3.5s, peak velocity ~1.0 rad/s.
    """
    SHAKE_UP   = [0.0, -0.5, 0.0, 0.0, 0.0, 0.0,  0.3]
    SHAKE_DN   = [0.0, -0.5, 0.0, 0.0, 0.0, 0.0, -0.3]
    pts_r = [
        _point(HOME,     0.4),
        _point(PT,       1.1),
        _point(SHAKE_UP, 1.5),
        _point(SHAKE_DN, 1.9),
        _point(SHAKE_UP, 2.3),
        _point(SHAKE_DN, 2.7),
        _point(PT,       3.1),
        _point(HOME,     3.5),
    ]
    pts_l = [_point(HOME, 3.5)]   # left arm idle
    return _both_arms(pts_l, pts_r)


def traj_bimanual_grip_clap() -> list[Dispatch]:
    """양 그리퍼 close + 양손 박수 동시 (4 dispatch). GRIPPER_CLOSE 대체 (gripper_close)."""
    g_close = _build_gripper(GRIPPER_CLOSE_POS)
    clap_pts_l = [
        _point(HOME,   0.4),
        _point(CLAP_L, 1.2),
        _point(CLAP_L, 1.8),
        _point(HOME,   2.4),
    ]
    clap_pts_r = [
        _point(HOME,   0.4),
        _point(CLAP_R, 1.2),
        _point(CLAP_R, 1.8),
        _point(HOME,   2.4),
    ]
    return [
        Dispatch(LEFT_ARM_ACT,   _traj(LEFT_JOINTS,  clap_pts_l), 'trajectory'),
        Dispatch(RIGHT_ARM_ACT,  _traj(RIGHT_JOINTS, clap_pts_r), 'trajectory'),
        Dispatch(LEFT_GRIP_ACT,  g_close, 'gripper'),
        Dispatch(RIGHT_GRIP_ACT, g_close, 'gripper'),
    ]

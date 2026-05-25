"""trajectories — 6 P0 모션의 JointTrajectory factory.

OMX joint 매핑:
  joint1: base 회전 (좌우)
  joint2: shoulder pitch
  joint3: elbow pitch
  joint4: wrist pitch

안전 제약:
  - 각도: ±1.2 rad (~±69°) 이내 (test_positions_within_safe_range 게이트)
  - velocity: <= 2.0 rad/s 의 expressive motion 한계 — 2.5 rad/s gate 로 regression-protect
    (Dynamixel XM430 default ~4.8 rad/s 의 ~40% — visual crispness + safety 균형)
  - self-collision 회피 책임은 작성자
"""
from __future__ import annotations

from builtin_interfaces.msg import Duration
from control_msgs.action import GripperCommand
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from arm_reactor_core.dispatch import Dispatch

# OMX 의 두 action — arm 은 FollowJointTrajectory, 그리퍼는 GripperCommand
# (open_manipulator_bringup 의 controller_manager 가 gripper_controller 를
# position_controllers/GripperActionController 로 설정 — live verify 결과).
ARM_ACT = '/arm_controller/follow_joint_trajectory'
GRIPPER_ACT = '/gripper_controller/gripper_cmd'
GRIPPER_MAX_EFFORT = 5.0   # GripperSender default 와 동일

JOINT_NAMES = ['joint1', 'joint2', 'joint3', 'joint4']
HOME = [0.0, -1.0, 0.5, 0.5]              # OMX 의 일반 home 자세 (정면)


def _point(positions: list[float], t_sec: float) -> JointTrajectoryPoint:
    p = JointTrajectoryPoint()
    p.positions = list(positions)
    p.time_from_start = Duration(sec=int(t_sec),
                                 nanosec=int((t_sec - int(t_sec)) * 1e9))
    return p


def _traj(points: list[JointTrajectoryPoint]) -> JointTrajectory:
    t = JointTrajectory()
    t.joint_names = list(JOINT_NAMES)
    t.points = points
    return t


def _build_idle() -> JointTrajectory:
    """home pose 정지."""
    return _traj([_point(HOME, 0.5)])


def _build_hello() -> JointTrajectory:
    """home → 정면 + joint4 위로 ±30° × 2 (손 흔듦), 3s."""
    return _traj([
        _point(HOME,                   0.5),
        _point([0.0, -1.0, 0.5, 1.0],  1.0),
        _point([0.0, -1.0, 0.5, 0.0],  1.5),
        _point([0.0, -1.0, 0.5, 1.0],  2.0),
        _point([0.0, -1.0, 0.5, 0.0],  2.5),
        _point(HOME,                   3.0),
    ])


def _build_bye() -> JointTrajectory:
    """HELLO 슬로우 (1.5×), 4.5s."""
    return _traj([
        _point(HOME,                   0.75),
        _point([0.0, -1.0, 0.5, 1.0],  1.5),
        _point([0.0, -1.0, 0.5, 0.0],  2.25),
        _point([0.0, -1.0, 0.5, 1.0],  3.0),
        _point([0.0, -1.0, 0.5, 0.0],  3.75),
        _point(HOME,                   4.5),
    ])


def _build_dance_disco() -> JointTrajectory:
    """DISCO POINT — joint2 위 (만세 자세) + joint1 ±0.5 sway ×2, 4.2s. 디스코."""
    UP_C = [ 0.0, -1.2, 0.0, 0.0]
    UP_R = [ 0.5, -1.2, 0.0, 0.0]
    UP_L = [-0.5, -1.2, 0.0, 0.0]
    return _traj([
        _point(HOME, 0.4),
        _point(UP_C, 1.0),
        _point(UP_R, 1.6), _point(UP_L, 2.2),
        _point(UP_R, 2.8), _point(UP_L, 3.4),
        _point(UP_C, 3.8),
        _point(HOME, 4.2),
    ])


def _build_dance_robot() -> JointTrajectory:
    """ROBOT — joint1 staccato turn-hold (±0.7 snap + 0.5s hold) ×2, 4.4s. 기계적."""
    RT = [ 0.7, -1.0, 0.5, 0.5]
    LT = [-0.7, -1.0, 0.5, 0.5]
    return _traj([
        _point(HOME, 0.3),
        _point(RT,   0.9), _point(RT, 1.4),   # snap + hold
        _point(LT,   2.0), _point(LT, 2.5),
        _point(RT,   3.1), _point(RT, 3.6),
        _point(HOME, 4.4),
    ])


def _build_dance_twist() -> JointTrajectory:
    """TWIST — joint1 ±0.6 sway + joint4 wave 연속 ×3, 3.8s. 몸 트위스트."""
    T_RA = [ 0.6, -1.0, 0.5, 1.0]
    T_LA = [-0.6, -1.0, 0.5, 0.0]
    return _traj([
        _point(HOME, 0.3),
        _point(T_RA, 0.9), _point(T_LA, 1.5),
        _point(T_RA, 2.1), _point(T_LA, 2.7),
        _point(T_RA, 3.3),
        _point(HOME, 3.8),
    ])


def _build_dance_tango() -> JointTrajectory:
    """TANGO SWEEP — joint1 깊은 한쪽 sweep + hold + 반대 sweep + hold, 4.5s. 드라마틱."""
    SW_R = [ 1.0, -0.8, 0.3, 0.3]
    SW_L = [-1.0, -0.8, 0.3, 0.3]
    return _traj([
        _point(HOME, 0.4),
        _point(SW_R, 1.3), _point(SW_R, 2.0),
        _point(SW_L, 3.0), _point(SW_L, 3.7),
        _point(HOME, 4.5),
    ])


def _build_dance_pump() -> JointTrajectory:
    """PUMP — joint2/joint4 sync 펌프 ×3 (어깨 + 손목 같이), 3.5s."""
    UP = [0.0, -1.15, 0.5, 1.0]
    DN = [0.0, -0.85, 0.5, 0.0]
    return _traj([
        _point(HOME, 0.3),
        _point(UP,   0.8), _point(DN, 1.3),
        _point(UP,   1.8), _point(DN, 2.3),
        _point(UP,   2.8),
        _point(HOME, 3.5),
    ])


def _build_freeze() -> JointTrajectory:
    """현 자세 + joint2 살짝 down 0.02rad (기죽음), 1s."""
    return _traj([
        _point([0.0, -1.02, 0.5, 0.5], 1.0),
    ])


def _build_console() -> JointTrajectory:
    """joint1 정면, joint4 up/down ±0.25rad × 4 (쓰담쓰담), 4s."""
    return _traj([
        _point(HOME,                    0.4),
        _point([0.0, -1.0, 0.5, 0.75],  1.0),
        _point([0.0, -1.0, 0.5, 0.25],  1.6),
        _point([0.0, -1.0, 0.5, 0.75],  2.2),
        _point([0.0, -1.0, 0.5, 0.25],  2.8),
        _point([0.0, -1.0, 0.5, 0.75],  3.4),
        _point(HOME,                    4.0),
    ])


def _build_hand_out() -> JointTrajectory:
    """사용자가 손 내밀면 OMX 도 손 내밂 (mimic) — joint2 수평 + joint3 펴기 reach
    + 1s hold + home 복귀. 3.5s total. velocity peak ~0.91 rad/s.
    """
    REACH = [0.0, 0.0, 0.0, 0.5]
    return _traj([
        _point(HOME,  0.4),
        _point(REACH, 1.5),
        _point(REACH, 2.5),    # 1s hold
        _point(HOME,  3.5),
    ])


def _build_hands_up() -> JointTrajectory:
    """만세 — 팔 위로 쭉 펴기. joint2 -1.2 (shoulder 위 limit) + joint3 0 + joint4 0 (elbow/wrist 일자).
    + 0.4s hold + home 복귀. 2.7s.
    """
    UP = [0.0, -1.2, 0.0, 0.0]
    return _traj([
        _point(HOME, 0.4),
        _point(UP,   1.5),
        _point(UP,   1.9),    # hold
        _point(HOME, 2.7),
    ])


def _build_hands_up_wave() -> JointTrajectory:
    """팔 위로 쭉 + 좌우 흔들기 (인사/안녕) — UP 자세 유지 + joint1 ±0.7 swing × 2회. 5.2s."""
    UP      = [0.0,  -1.2, 0.0, 0.0]
    WAVE_R  = [0.7,  -1.2, 0.0, 0.0]
    WAVE_L  = [-0.7, -1.2, 0.0, 0.0]
    return _traj([
        _point(HOME,   0.4),
        _point(UP,     1.5),
        _point(WAVE_R, 2.1),
        _point(WAVE_L, 2.7),
        _point(WAVE_R, 3.3),
        _point(WAVE_L, 3.9),
        _point(UP,     4.5),
        _point(HOME,   5.2),
    ])


# DANCE rotation — 6 style variants (활기 ↔ 정적 교대). hands_up_wave 는 기존 함수 재활용.
_DANCE_BUILDERS = [_build_dance_disco, _build_dance_robot,
                   _build_dance_twist, _build_hands_up_wave,
                   _build_dance_tango, _build_dance_pump]
_dance_idx = [0]


def _build_dance() -> JointTrajectory:
    """DANCE rotation — 6 style 변형 순차 (disco → robot → twist → wave → tango → pump)."""
    b = _DANCE_BUILDERS[_dance_idx[0] % len(_DANCE_BUILDERS)]
    _dance_idx[0] += 1
    return b()


def _build_point_back() -> JointTrajectory:
    """가리킴 — joint1 한쪽 + joint3/joint4 펴기 (gripper 정면 reach), 2.5s."""
    PT = [0.6, -0.5, 0.0, 0.0]
    return _traj([
        _point(HOME, 0.4),
        _point(PT,   1.5),
        _point(PT,   1.9),
        _point(HOME, 2.5),
    ])


def _build_nod() -> JointTrajectory:
    """끄덕 — joint4 위아래 × 3 (좋아 응답), 3.3s. velocity peak 2.0 rad/s."""
    NOD_DN = [0.0, -1.0, 0.5, 1.0]
    NOD_UP = [0.0, -1.0, 0.5, 0.0]
    return _traj([
        _point(HOME,   0.4),
        _point(NOD_DN, 0.9),
        _point(NOD_UP, 1.4),
        _point(NOD_DN, 1.9),
        _point(NOD_UP, 2.4),
        _point(HOME,   3.3),
    ])


def _build_cheer() -> JointTrajectory:
    """축하 (V 사인) — joint1 ±0.5 × 4 + joint2 살짝 위, 3.7s. velocity peak 2.0 rad/s."""
    UP_R = [0.5,  -1.2, 0.0, 0.0]
    UP_L = [-0.5, -1.2, 0.0, 0.0]
    UP_C = [0.0,  -1.2, 0.0, 0.0]
    return _traj([
        _point(HOME, 0.4),
        _point(UP_C, 1.0),
        _point(UP_R, 1.5),
        _point(UP_L, 2.0),
        _point(UP_R, 2.5),
        _point(UP_L, 3.0),
        _point(UP_C, 3.4),
        _point(HOME, 3.7),
    ])


def _build_heart() -> JointTrajectory:
    """사랑해 손 — 부드러운 좌우 swing × 2 (천천히), 4.0s."""
    HRT_R = [0.4, -0.8, 0.3, 0.4]
    HRT_L = [-0.4, -0.8, 0.3, 0.4]
    return _traj([
        _point(HOME,  0.5),
        _point(HRT_R, 1.5),
        _point(HRT_L, 2.5),
        _point(HRT_R, 3.5),
        _point(HOME,  4.0),
    ])


def _build_strong() -> JointTrajectory:
    """강한 자세 (주먹) — joint1 한쪽 + joint2 위 + joint3/joint4 펴기 (힘찬 reach), 2.5s hold."""
    ST = [0.5, -1.2, 0.0, 0.0]
    return _traj([
        _point(HOME, 0.4),
        _point(ST,   1.2),
        _point(ST,   2.0),    # hold
        _point(HOME, 2.5),
    ])


def _build_sad() -> JointTrajectory:
    """슬픔 (엄지 아래) — joint2 down + joint3/joint4 굽힘 (머리 숙이듯), 3.0s."""
    SD = [0.0, -0.3, 1.0, 1.0]
    return _traj([
        _point(HOME, 0.5),
        _point(SD,   1.5),
        _point(SD,   2.3),    # hold
        _point(HOME, 3.0),
    ])


def _build_twinkle() -> JointTrajectory:
    """반짝반짝 — joint1 ±0.4 빠르게 alternating × 4 (base 좌우), 3.6s. velocity peak 2.0 rad/s."""
    TW_R = [0.4,  -1.0, 0.5, 0.5]
    TW_L = [-0.4, -1.0, 0.5, 0.5]
    return _traj([
        _point(HOME, 0.3),
        _point(TW_R, 0.7),
        _point(TW_L, 1.1),
        _point(TW_R, 1.5),
        _point(TW_L, 1.9),
        _point(TW_R, 2.3),
        _point(TW_L, 2.7),
        _point(TW_R, 3.1),
        _point(HOME, 3.6),
    ])


# ─── gripper — /gripper_controller/gripper_cmd (control_msgs/action/GripperCommand) ───
# OMX 의 그리퍼는 GripperActionController — position 단일 float (rad) 받음.
# GRIPPER_JOINT_NAMES 는 외부 import 호환 위해 유지 (현 sender 는 안 씀).

GRIPPER_JOINT_NAMES = ['gripper_left_joint']
GRIPPER_OPEN_ANGLE = 0.019    # OMX default open (rad)
GRIPPER_CLOSE_ANGLE = -0.010  # OMX default close


def _build_gripper_open() -> GripperCommand.Goal:
    """gripper 열기 — position +0.019 rad."""
    g = GripperCommand.Goal()
    g.command.position = float(GRIPPER_OPEN_ANGLE)
    g.command.max_effort = GRIPPER_MAX_EFFORT
    return g


def _build_gripper_close() -> GripperCommand.Goal:
    """gripper 닫기 — position -0.010 rad."""
    g = GripperCommand.Goal()
    g.command.position = float(GRIPPER_CLOSE_ANGLE)
    g.command.max_effort = GRIPPER_MAX_EFFORT
    return g


# ─── list[Dispatch] wrappers (외부 factory — Motion.trajectory 시그니처 만족) ──────
# OMX 는 단일 arm 이라 모든 모션이 1-element list. 그리퍼도 FollowJointTrajectory 라
# kind='trajectory' 일관. (OpenArm 의 GripperCommand 와는 sender 가 다름.)

def traj_idle() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_idle(), 'trajectory')]


def traj_hello() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_hello(), 'trajectory')]


def traj_bye() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_bye(), 'trajectory')]


def traj_dance() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_dance(), 'trajectory')]


def traj_freeze() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_freeze(), 'trajectory')]


def traj_console() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_console(), 'trajectory')]


def traj_hand_out() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_hand_out(), 'trajectory')]


def traj_hands_up() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_hands_up(), 'trajectory')]


def traj_hands_up_wave() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_hands_up_wave(), 'trajectory')]


def traj_point_back() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_point_back(), 'trajectory')]


def traj_nod() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_nod(), 'trajectory')]


def traj_cheer() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_cheer(), 'trajectory')]


def traj_heart() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_heart(), 'trajectory')]


def traj_strong() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_strong(), 'trajectory')]


def traj_sad() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_sad(), 'trajectory')]


def traj_twinkle() -> list[Dispatch]:
    return [Dispatch(ARM_ACT, _build_twinkle(), 'trajectory')]


def traj_gripper_open() -> list[Dispatch]:
    return [Dispatch(GRIPPER_ACT, _build_gripper_open(), 'gripper')]


def traj_gripper_close() -> list[Dispatch]:
    return [Dispatch(GRIPPER_ACT, _build_gripper_close(), 'gripper')]

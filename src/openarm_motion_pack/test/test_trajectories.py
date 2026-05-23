"""OpenArm v10 bimanual trajectories test — Dispatch + arm safe range/velocity + gripper goal."""
import pytest

from arm_reactor_core.dispatch import Dispatch
from openarm_motion_pack.trajectories import (
    traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
    traj_hand_out, traj_hands_up, traj_hands_up_wave,
    traj_nod, traj_sad, traj_strong, traj_twinkle, traj_gripper_open,
    traj_bimanual_clap, traj_bimanual_hug, traj_asymmetric_point, traj_bimanual_grip_clap,
    LEFT_ARM_ACT, RIGHT_ARM_ACT, LEFT_GRIP_ACT, RIGHT_GRIP_ACT,
    LEFT_JOINTS, RIGHT_JOINTS,
)

# arm-only factory (양손 trajectory 만, 그리퍼 dispatch 없음) — 16 개
ARM_ONLY_FACTORIES = [traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
                      traj_hand_out, traj_hands_up, traj_hands_up_wave,
                      traj_nod, traj_sad, traj_strong, traj_twinkle,
                      traj_bimanual_clap, traj_bimanual_hug, traj_asymmetric_point]

GRIPPER_ONLY_FACTORIES = [traj_gripper_open]
MIXED_FACTORIES = [traj_bimanual_grip_clap]   # 양손 + 양 그리퍼 (4 dispatch)

ALL_FACTORIES = ARM_ONLY_FACTORIES + GRIPPER_ONLY_FACTORIES + MIXED_FACTORIES

# OpenArm safe range — joint_limits.yaml 의 90% (lower/upper)
# joint1: ±1.396*0.9=±1.26, joint2: ±1.745*0.9=±1.57, joint3: ±1.570*0.9=±1.41,
# joint4: 0~2.443*0.9=2.20, joint5: ±1.570*0.9=±1.41, joint6: ±0.785*0.9=±0.71,
# joint7: ±1.570*0.9=±1.41
SAFE_LOWER = [-1.26, -1.57, -1.41, 0.00, -1.41, -0.71, -1.41]
SAFE_UPPER = [ 1.26,  1.57,  1.41, 2.20,  1.41,  0.71,  1.41]

MAX_VELOCITY_RAD_S = 2.5


# ─── 모든 factory 공통 ──────────────────────────────────────────────────

@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_returns_list_of_dispatch(factory):
    ds = factory()
    assert isinstance(ds, list) and len(ds) >= 1
    for d in ds:
        assert isinstance(d, Dispatch)


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_action_names_known(factory):
    known = {LEFT_ARM_ACT, RIGHT_ARM_ACT, LEFT_GRIP_ACT, RIGHT_GRIP_ACT}
    for d in factory():
        assert d.action_name in known, \
            f'{factory.__name__} unknown action {d.action_name}'


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_kind_matches_action(factory):
    arm_acts = {LEFT_ARM_ACT, RIGHT_ARM_ACT}
    grip_acts = {LEFT_GRIP_ACT, RIGHT_GRIP_ACT}
    for d in factory():
        if d.action_name in arm_acts:
            assert d.kind == 'trajectory', f'{factory.__name__} arm dispatch kind {d.kind}'
        else:
            assert d.action_name in grip_acts and d.kind == 'gripper', \
                f'{factory.__name__} gripper dispatch kind {d.kind}'


# ─── arm dispatch 검증 (joint_names + range + velocity) ─────────────────

def _arm_dispatches(factory):
    return [d for d in factory() if d.kind == 'trajectory']


@pytest.mark.parametrize('factory', ARM_ONLY_FACTORIES + MIXED_FACTORIES)
def test_arm_joint_names_match(factory):
    for d in _arm_dispatches(factory):
        if d.action_name == LEFT_ARM_ACT:
            assert list(d.msg.joint_names) == LEFT_JOINTS
        elif d.action_name == RIGHT_ARM_ACT:
            assert list(d.msg.joint_names) == RIGHT_JOINTS


@pytest.mark.parametrize('factory', ARM_ONLY_FACTORIES + MIXED_FACTORIES)
def test_arm_time_strictly_monotonic(factory):
    for d in _arm_dispatches(factory):
        times = [p.time_from_start.sec + p.time_from_start.nanosec * 1e-9
                 for p in d.msg.points]
        assert all(b > a for a, b in zip(times, times[1:])), \
            f'{factory.__name__} times not strictly monotonic: {times}'


@pytest.mark.parametrize('factory', ARM_ONLY_FACTORIES + MIXED_FACTORIES)
def test_arm_positions_within_safe_range(factory):
    for d in _arm_dispatches(factory):
        for p in d.msg.points:
            assert len(p.positions) == 7, f'{factory.__name__} expected 7 joints'
            for i, v in enumerate(p.positions):
                assert SAFE_LOWER[i] <= v <= SAFE_UPPER[i], \
                    f'{factory.__name__} joint{i+1}={v} out of safe range [{SAFE_LOWER[i]}, {SAFE_UPPER[i]}]'


@pytest.mark.parametrize('factory', ARM_ONLY_FACTORIES + MIXED_FACTORIES)
def test_arm_max_velocity_within_limit(factory):
    """Each segment's per-joint velocity must be <= MAX_VELOCITY_RAD_S."""
    for d in _arm_dispatches(factory):
        if len(d.msg.points) < 2:
            continue
        times = [p.time_from_start.sec + p.time_from_start.nanosec * 1e-9
                 for p in d.msg.points]
        for i in range(len(d.msg.points) - 1):
            dt = times[i + 1] - times[i]
            for j, (a, b) in enumerate(zip(d.msg.points[i].positions,
                                           d.msg.points[i + 1].positions)):
                v = abs(b - a) / dt
                assert v <= MAX_VELOCITY_RAD_S, \
                    (f'{factory.__name__} joint{j+1} segment {i}->{i+1}: '
                     f'v={v:.2f} > {MAX_VELOCITY_RAD_S} rad/s')


# ─── gripper dispatch 검증 (GripperCommand.Goal + position 안전 범위) ───

def _gripper_dispatches(factory):
    return [d for d in factory() if d.kind == 'gripper']


@pytest.mark.parametrize('factory', GRIPPER_ONLY_FACTORIES + MIXED_FACTORIES)
def test_gripper_returns_gripper_command_goal(factory):
    for d in _gripper_dispatches(factory):
        g = d.msg
        assert hasattr(g, 'command'), f'{factory.__name__} msg .command 없음'
        assert isinstance(g.command.position, float)
        assert isinstance(g.command.max_effort, float)
        # OpenArm finger range 0~0.043
        assert 0.0 <= g.command.position <= 0.043, \
            f'{factory.__name__} gripper position {g.command.position} 범위 [0, 0.043] 벗어남'


# ─── MOTIONS 등록부 smoke ──────────────────────────────────────────────

def test_motions_count_and_loadable():
    from openarm_motion_pack.motions import MOTIONS
    assert len(MOTIONS) == 18
    for m in MOTIONS:
        ds = m.trajectory()
        assert isinstance(ds, list) and len(ds) >= 1

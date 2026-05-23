import pytest

from arm_reactor_core.dispatch import Dispatch
from omx_reactor.trajectories import (
    traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
    traj_hand_out, traj_hands_up, traj_hands_up_wave,
    traj_point_back, traj_nod, traj_cheer, traj_heart, traj_strong, traj_sad, traj_twinkle,
    traj_gripper_open, traj_gripper_close,
    JOINT_NAMES, GRIPPER_JOINT_NAMES, ARM_ACT, GRIPPER_ACT,
)


# arm controller trajectory (joint1~4) — 모든 검증 항목 적용
ALL_FACTORIES = [traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
                 traj_hand_out, traj_hands_up, traj_hands_up_wave,
                 traj_point_back, traj_nod, traj_cheer, traj_heart, traj_strong, traj_sad,
                 traj_twinkle]


GRIPPER_FACTORIES = [traj_gripper_open, traj_gripper_close]


def _msg(factory):
    """factory() -> list[Dispatch] 의 첫 Dispatch 의 msg (JointTrajectory) 반환 헬퍼."""
    dispatches = factory()
    assert isinstance(dispatches, list) and len(dispatches) == 1, \
        f'{factory.__name__} expected 1-element list[Dispatch], got {dispatches!r}'
    return dispatches[0].msg


@pytest.mark.parametrize('factory', GRIPPER_FACTORIES)
def test_gripper_factory_uses_gripper_joint(factory):
    t = _msg(factory)
    assert list(t.joint_names) == GRIPPER_JOINT_NAMES
    assert len(t.points) >= 1
    for p in t.points:
        assert len(p.positions) == 1   # gripper 는 single joint


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_joint_names_match(factory):
    t = _msg(factory)
    assert list(t.joint_names) == JOINT_NAMES


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_time_strictly_monotonic(factory):
    t = _msg(factory)
    times = [p.time_from_start.sec + p.time_from_start.nanosec * 1e-9
             for p in t.points]
    assert all(b > a for a, b in zip(times, times[1:])), \
        f'{factory.__name__} times not strictly monotonic: {times}'


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_positions_within_safe_range(factory):
    t = _msg(factory)
    for p in t.points:
        for j, val in zip(t.joint_names, p.positions):
            assert -1.2 <= val <= 1.2, \
                f'{factory.__name__} {j}={val} out of safe ±1.2rad range'


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_positions_length_matches_joints(factory):
    t = _msg(factory)
    n = len(t.joint_names)
    for p in t.points:
        assert len(p.positions) == n


def test_at_least_one_point():
    for f in ALL_FACTORIES + GRIPPER_FACTORIES:
        assert len(_msg(f).points) >= 1


# velocity gate — expressive motion limit, hardware (Dynamixel XM430) default ~4.8 rad/s
# 2.5 rad/s = current peak (2.0 in DANCE/HELLO) + 0.5 headroom for future tuning
MAX_VELOCITY_RAD_S = 2.5


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_max_velocity_within_limit(factory):
    """Each segment's per-joint velocity must be <= MAX_VELOCITY_RAD_S.

    Single-point factories (IDLE, FREEZE) are exempt (no segments).
    Note: first segment's velocity from arbitrary prior pose is not gated here
    (this would require runtime tracking) — design assumes prior motion ends at HOME.
    """
    t = _msg(factory)
    if len(t.points) < 2:
        return
    times = [p.time_from_start.sec + p.time_from_start.nanosec * 1e-9
             for p in t.points]
    for i in range(len(t.points) - 1):
        dt = times[i + 1] - times[i]
        for j, (a, b) in enumerate(zip(t.points[i].positions,
                                       t.points[i + 1].positions)):
            v = abs(b - a) / dt
            assert v <= MAX_VELOCITY_RAD_S, \
                (f'{factory.__name__} joint{j+1} segment {i}->{i+1}: '
                 f'v={v:.2f} > {MAX_VELOCITY_RAD_S} rad/s')


# ─── Dispatch wrapper kind / action_name 검증 ──────────────────────────

@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_arm_factory_dispatch_action_and_kind(factory):
    dispatches = factory()
    assert all(isinstance(d, Dispatch) for d in dispatches)
    assert all(d.action_name == ARM_ACT for d in dispatches)
    assert all(d.kind == 'trajectory' for d in dispatches)


@pytest.mark.parametrize('factory', GRIPPER_FACTORIES)
def test_gripper_factory_dispatch_action_and_kind(factory):
    # OMX 그리퍼도 FollowJointTrajectory (controller_manager 의 GripperActionController X)
    # 라 kind 는 'trajectory'. action_name 만 GRIPPER_ACT 로 갈림.
    dispatches = factory()
    assert all(isinstance(d, Dispatch) for d in dispatches)
    assert all(d.action_name == GRIPPER_ACT for d in dispatches)
    assert all(d.kind == 'trajectory' for d in dispatches)

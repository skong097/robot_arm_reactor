import pytest

from omx_reactor.trajectories import (
    traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
    traj_hand_out, traj_hands_up, traj_hands_up_wave,
    JOINT_NAMES,
)


ALL_FACTORIES = [traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
                 traj_hand_out, traj_hands_up, traj_hands_up_wave]


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_joint_names_match(factory):
    t = factory()
    assert list(t.joint_names) == JOINT_NAMES


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_time_strictly_monotonic(factory):
    t = factory()
    times = [p.time_from_start.sec + p.time_from_start.nanosec * 1e-9
             for p in t.points]
    assert all(b > a for a, b in zip(times, times[1:])), \
        f'{factory.__name__} times not strictly monotonic: {times}'


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_positions_within_safe_range(factory):
    t = factory()
    for p in t.points:
        for j, val in zip(t.joint_names, p.positions):
            assert -1.2 <= val <= 1.2, \
                f'{factory.__name__} {j}={val} out of safe ±1.2rad range'


@pytest.mark.parametrize('factory', ALL_FACTORIES)
def test_positions_length_matches_joints(factory):
    t = factory()
    n = len(t.joint_names)
    for p in t.points:
        assert len(p.positions) == n


def test_at_least_one_point():
    for f in ALL_FACTORIES:
        assert len(f().points) >= 1


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
    t = factory()
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

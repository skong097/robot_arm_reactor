import pytest

from omx_reactor.trajectories import (
    traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console,
    JOINT_NAMES,
)


ALL_FACTORIES = [traj_idle, traj_hello, traj_bye, traj_dance, traj_freeze, traj_console]


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

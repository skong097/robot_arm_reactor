"""trajectories — 6 P0 모션의 JointTrajectory factory.

OMX joint 매핑:
  joint1: base 회전 (좌우)
  joint2: shoulder pitch
  joint3: elbow pitch
  joint4: wrist pitch
모든 각도 ±60° 이내. self-collision 회피 책임은 작성자.
"""
from __future__ import annotations

from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

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


def traj_idle() -> JointTrajectory:
    """home pose 정지."""
    return _traj([_point(HOME, 0.5)])


def traj_hello() -> JointTrajectory:
    """home → 정면 + joint4 위로 ±30° × 2 (손 흔듦), 3s."""
    return _traj([
        _point(HOME,                   0.5),
        _point([0.0, -1.0, 0.5, 1.0],  1.0),
        _point([0.0, -1.0, 0.5, 0.0],  1.5),
        _point([0.0, -1.0, 0.5, 1.0],  2.0),
        _point([0.0, -1.0, 0.5, 0.0],  2.5),
        _point(HOME,                   3.0),
    ])


def traj_bye() -> JointTrajectory:
    """HELLO 슬로우 (1.5×), 4.5s."""
    return _traj([
        _point(HOME,                   0.75),
        _point([0.0, -1.0, 0.5, 1.0],  1.5),
        _point([0.0, -1.0, 0.5, 0.0],  2.25),
        _point([0.0, -1.0, 0.5, 1.0],  3.0),
        _point([0.0, -1.0, 0.5, 0.0],  3.75),
        _point(HOME,                   4.5),
    ])


def traj_dance() -> JointTrajectory:
    """joint1 base ±0.8rad swing × 3 + joint4 wave, 4s."""
    return _traj([
        _point(HOME,                    0.4),
        _point([ 0.8, -1.0, 0.5, 1.0],  1.0),
        _point([-0.8, -1.0, 0.5, 0.0],  1.8),
        _point([ 0.8, -1.0, 0.5, 1.0],  2.6),
        _point([-0.8, -1.0, 0.5, 0.0],  3.4),
        _point(HOME,                    4.0),
    ])


def traj_freeze() -> JointTrajectory:
    """현 자세 + joint2 살짝 down 0.02rad (기죽음), 1s."""
    return _traj([
        _point([0.0, -1.02, 0.5, 0.5], 1.0),
    ])


def traj_console() -> JointTrajectory:
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

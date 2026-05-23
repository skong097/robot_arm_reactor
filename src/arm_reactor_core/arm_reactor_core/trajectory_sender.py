"""trajectory_sender — FollowJointTrajectory action client wrapper (arm-agnostic).

같은 노드 안에서 arm controller / gripper controller 등 여러 action server 에 대해
인스턴스 분리해 사용. dispatch 분기는 호출자 책임.
"""
from __future__ import annotations

from typing import Callable

from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory


class TrajectorySender:
    """JointTrajectory -> <action_name> action goal."""

    def __init__(self, node: Node, action_name: str):
        self._node = node
        self._client = ActionClient(node, FollowJointTrajectory, action_name)
        self._goal_handle = None
        self._on_finish: Callable[[], None] | None = None

    def wait_ready(self, timeout_sec: float = 5.0) -> bool:
        return self._client.wait_for_server(timeout_sec=timeout_sec)

    def send(self, trajectory, on_finish: Callable[[], None]) -> bool:
        if not self._client.server_is_ready():
            self._node.get_logger().warn('action server not ready — skip send')
            on_finish()
            return False
        self._on_finish = on_finish
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = trajectory
        fut = self._client.send_goal_async(goal)
        fut.add_done_callback(self._on_goal_response)
        return True

    def cancel_current(self) -> None:
        if self._goal_handle is not None:
            self._goal_handle.cancel_goal_async()

    def _on_goal_response(self, fut):
        gh = fut.result()
        if not gh or not gh.accepted:
            self._node.get_logger().warn('goal rejected')
            if self._on_finish:
                self._on_finish()
            return
        self._goal_handle = gh
        gh.get_result_async().add_done_callback(self._on_result)

    def _on_result(self, fut):
        self._goal_handle = None
        if self._on_finish:
            cb = self._on_finish
            self._on_finish = None
            cb()

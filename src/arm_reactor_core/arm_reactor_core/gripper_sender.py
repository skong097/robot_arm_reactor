"""gripper_sender — GripperCommand action client wrapper.

TrajectorySender 와 동일 패턴 (cancel_current / on_finish 콜백), msg type 만
control_msgs/action/GripperCommand. position 단일 float 받아 Goal 구성.
"""
from __future__ import annotations

from typing import Callable

from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import GripperCommand


class GripperSender:
    """position 값 -> <action_name> GripperCommand goal."""

    def __init__(self, node: Node, action_name: str, max_effort: float = 5.0):
        self._node = node
        self._client = ActionClient(node, GripperCommand, action_name)
        self._max_effort = max_effort
        self._goal_handle = None
        self._on_finish: Callable[[], None] | None = None

    def wait_ready(self, timeout_sec: float = 5.0) -> bool:
        return self._client.wait_for_server(timeout_sec=timeout_sec)

    def send(self, position: float, on_finish: Callable[[], None]) -> bool:
        if not self._client.server_is_ready():
            self._node.get_logger().warn(
                f'gripper action server not ready ({self._client._action_name}) — skip send')
            on_finish()
            return False
        self._on_finish = on_finish
        goal = GripperCommand.Goal()
        goal.command.position = float(position)
        goal.command.max_effort = self._max_effort
        fut = self._client.send_goal_async(goal)
        fut.add_done_callback(self._on_goal_response)
        return True

    def cancel_current(self) -> None:
        if self._goal_handle is not None:
            self._goal_handle.cancel_goal_async()

    def _on_goal_response(self, fut):
        gh = fut.result()
        if not gh or not gh.accepted:
            self._node.get_logger().warn('gripper goal rejected')
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

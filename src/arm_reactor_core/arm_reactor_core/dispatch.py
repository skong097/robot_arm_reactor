"""dispatch — Motion 실행 단위 (action_name + msg + kind)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Dispatch:
    """1 Motion 이 N 개 Dispatch 반환 — reactor 가 kind 별 sender 로 자동 분기.

    kind:
      'trajectory' — msg 는 trajectory_msgs/JointTrajectory, TrajectorySender 처리
      'gripper'    — msg 는 control_msgs/action/GripperCommand.Goal, GripperSender 처리
    """
    action_name: str
    msg: object
    kind: Literal['trajectory', 'gripper']

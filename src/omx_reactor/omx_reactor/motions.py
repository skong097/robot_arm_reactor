"""motions — Motion dataclass 정의 + MOTIONS 리스트 (Task 9 에서 채움)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from omx_reactor.context import Context

# trajectory 의 실제 반환 타입은 trajectory_msgs/JointTrajectory 이나,
# 본 모듈은 ROS 무의존 유지를 위해 Callable[[], object] 로 둠.
# 테스트 시 Callable[[], None] 으로 대체 가능.


@dataclass(frozen=True)
class Motion:
    """Plug-in 단위 모션. 새 모션 추가 = MOTIONS 리스트에 항목 1개 + trajectory factory 1개."""
    id: str
    trigger: Callable[[Context], bool]   # ctx -> 매치 여부
    priority: int                        # 높을수록 interrupt 가능
    cooldown_sec: float                  # 같은 id 재실행 최소 간격
    trajectory: Callable[[], object]     # () -> JointTrajectory


# MOTIONS 리스트는 Task 9 에서 작성 (trajectories.py 완성 후)
MOTIONS: list[Motion] = []

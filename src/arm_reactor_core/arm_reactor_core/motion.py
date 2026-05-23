"""motion — Plug-in 단위 Motion dataclass (arm 무관).

새 모션 추가 = motion pack 의 MOTIONS 리스트에 항목 1 개 + 해당 trajectory factory 1 개.
trajectory 반환은 list[Dispatch] (atomic 양손 모션 동시 dispatch 지원, 단일 arm 은 1-element list).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from arm_reactor_core.context import Context
from arm_reactor_core.dispatch import Dispatch


@dataclass(frozen=True)
class Motion:
    id: str
    trigger: Callable[[Context], bool]
    priority: int
    cooldown_sec: float
    trajectory: Callable[[], list[Dispatch]]

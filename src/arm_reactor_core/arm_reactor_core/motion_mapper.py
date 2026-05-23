"""motion_mapper — Context + Motion 리스트 -> 최적 Motion (priority 내림차순 첫 매치)."""
from __future__ import annotations

from omx_reactor.context import Context
from omx_reactor.motions import Motion


def select_motion(ctx: Context, motions: list[Motion]) -> Motion | None:
    """priority 내림차순으로 첫 trigger 매치 반환. 없으면 None."""
    for m in sorted(motions, key=lambda m: -m.priority):
        if m.trigger(ctx):
            return m
    return None

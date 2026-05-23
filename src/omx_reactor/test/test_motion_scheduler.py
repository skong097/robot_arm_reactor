import pytest

from omx_reactor.context import Context
from omx_reactor.motions import Motion
from omx_reactor.motion_scheduler import MotionScheduler, SchedulerAction


def _m(id_: str, priority: int = 10, cooldown: float = 5.0) -> Motion:
    return Motion(id=id_, trigger=lambda c: True, priority=priority,
                  cooldown_sec=cooldown, trajectory=lambda: None)


def test_submit_when_idle_starts():
    sch = MotionScheduler()
    res = sch.submit(_m('DANCE'), t_now=0.0)
    assert res == SchedulerAction.START


def test_submit_same_id_within_cooldown_ignored():
    sch = MotionScheduler()
    sch.submit(_m('DANCE'), t_now=0.0)
    sch.on_finish(t_now=2.0)                       # DANCE 끝, cooldown 시작
    res = sch.submit(_m('DANCE'), t_now=3.0)       # cooldown 5s 미만
    assert res == SchedulerAction.IGNORE


def test_submit_same_id_past_cooldown_starts():
    sch = MotionScheduler()
    sch.submit(_m('DANCE'), t_now=0.0)
    sch.on_finish(t_now=2.0)
    res = sch.submit(_m('DANCE'), t_now=8.0)       # cooldown 경과
    assert res == SchedulerAction.START


def test_submit_different_id_same_priority_queues():
    sch = MotionScheduler()
    sch.submit(_m('DANCE'), t_now=0.0)
    res = sch.submit(_m('FREEZE'), t_now=0.5)
    assert res == SchedulerAction.QUEUE


def test_queue_depth_one_overwrites():
    sch = MotionScheduler()
    sch.submit(_m('DANCE'), t_now=0.0)
    sch.submit(_m('FREEZE'), t_now=0.5)            # queued
    sch.submit(_m('CONSOLE'), t_now=0.7)           # overwrite
    nxt = sch.on_finish(t_now=2.0)
    assert nxt is not None and nxt.id == 'CONSOLE'


def test_higher_priority_interrupts():
    sch = MotionScheduler()
    sch.submit(_m('DANCE', priority=10), t_now=0.0)
    res = sch.submit(_m('HELLO', priority=100), t_now=0.5)
    assert res == SchedulerAction.INTERRUPT


def test_lower_priority_with_current_high_ignored():
    sch = MotionScheduler()
    sch.submit(_m('HELLO', priority=100), t_now=0.0)
    res = sch.submit(_m('DANCE', priority=10), t_now=0.5)
    assert res in (SchedulerAction.QUEUE, SchedulerAction.IGNORE)
    # 큐로 미루는 것까진 OK


def test_on_finish_returns_queued_motion():
    sch = MotionScheduler()
    sch.submit(_m('DANCE'), t_now=0.0)
    sch.submit(_m('FREEZE'), t_now=0.5)
    nxt = sch.on_finish(t_now=2.0)
    assert nxt is not None and nxt.id == 'FREEZE'


def test_on_finish_empty_queue_returns_none():
    sch = MotionScheduler()
    sch.submit(_m('DANCE'), t_now=0.0)
    nxt = sch.on_finish(t_now=2.0)
    assert nxt is None

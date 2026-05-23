import pytest

from arm_reactor_core.context import Context, EmotionSignal
from arm_reactor_core.dispatch import Dispatch
from arm_reactor_core.motion import Motion
from arm_reactor_core.motion_mapper import select_motion


def _ctx(quadrant: str | None, in_db: bool = False,
         session: str | None = None, t: float = 0.0) -> Context:
    emo = EmotionSignal(v=0.0, a=0.0, quadrant=quadrant,
                        in_deadband=in_db, confidence=1.0, source='face')
    return Context(emotion=emo, session_event=session, t_now=t)


def _dummy_traj():
    # mapper 는 trajectory 안 부르지만 Motion 시그니처상 list[Dispatch] 반환 필요
    return [Dispatch(action_name='/test', msg=None, kind='trajectory')]


M_DANCE   = Motion('DANCE',   trigger=lambda c: bool(c.emotion and c.emotion.quadrant == 'Q1'),  priority=10,  cooldown_sec=5.0, trajectory=_dummy_traj)
M_FREEZE  = Motion('FREEZE',  trigger=lambda c: bool(c.emotion and c.emotion.quadrant == 'Q2'),  priority=10,  cooldown_sec=5.0, trajectory=_dummy_traj)
M_CONSOLE = Motion('CONSOLE', trigger=lambda c: bool(c.emotion and c.emotion.quadrant == 'Q3'),  priority=10,  cooldown_sec=5.0, trajectory=_dummy_traj)
M_IDLE    = Motion('IDLE',    trigger=lambda c: bool(c.emotion and (c.emotion.quadrant == 'Q4' or c.emotion.in_deadband)), priority=0, cooldown_sec=0.0, trajectory=_dummy_traj)
M_HELLO   = Motion('HELLO',   trigger=lambda c: c.session_event == 'new_track',   priority=100, cooldown_sec=0.0, trajectory=_dummy_traj)
M_BYE     = Motion('BYE',     trigger=lambda c: c.session_event == 'track_gone',  priority=100, cooldown_sec=0.0, trajectory=_dummy_traj)

ALL = [M_DANCE, M_FREEZE, M_CONSOLE, M_IDLE, M_HELLO, M_BYE]


def test_q1_returns_dance():
    assert select_motion(_ctx('Q1'), ALL).id == 'DANCE'


def test_q2_returns_freeze():
    assert select_motion(_ctx('Q2'), ALL).id == 'FREEZE'


def test_q3_returns_console():
    assert select_motion(_ctx('Q3'), ALL).id == 'CONSOLE'


def test_q4_returns_idle():
    assert select_motion(_ctx('Q4'), ALL).id == 'IDLE'


def test_deadband_returns_idle():
    assert select_motion(_ctx(None, in_db=True), ALL).id == 'IDLE'


def test_new_track_session_wins_over_quadrant():
    # session 우선 (priority 100) > 분면 (priority 10)
    assert select_motion(_ctx('Q1', session='new_track'), ALL).id == 'HELLO'


def test_track_gone_session_wins_over_quadrant():
    assert select_motion(_ctx('Q3', session='track_gone'), ALL).id == 'BYE'


def test_no_emotion_no_session_returns_none():
    ctx = Context(emotion=None, session_event=None, t_now=0.0)
    assert select_motion(ctx, ALL) is None


def test_empty_motion_list_returns_none():
    assert select_motion(_ctx('Q1'), []) is None

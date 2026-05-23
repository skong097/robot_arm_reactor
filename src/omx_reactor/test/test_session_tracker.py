import pytest

from omx_reactor.session_tracker import SessionTracker


def test_first_valid_track_emits_new_track():
    st = SessionTracker(bye_grace_sec=3.0)
    assert st.update(current_track_id=7, t_now=0.0) == 'new_track'


def test_same_track_continues_no_event():
    st = SessionTracker(bye_grace_sec=3.0)
    st.update(7, t_now=0.0)
    assert st.update(7, t_now=0.5) is None
    assert st.update(7, t_now=1.0) is None


def test_track_lost_within_grace_no_event():
    st = SessionTracker(bye_grace_sec=3.0)
    st.update(7, t_now=0.0)
    assert st.update(-1, t_now=0.5) is None   # 잃은 직후
    assert st.update(-1, t_now=2.0) is None   # grace 내
    assert st.update(7, t_now=2.5) is None    # 복귀 — 재인사 X


def test_track_lost_past_grace_emits_track_gone():
    st = SessionTracker(bye_grace_sec=3.0)
    st.update(7, t_now=0.0)
    st.update(-1, t_now=1.0)
    # grace 경계 직후
    assert st.update(-1, t_now=4.01) == 'track_gone'


def test_track_gone_only_emitted_once():
    st = SessionTracker(bye_grace_sec=3.0)
    st.update(7, t_now=0.0)
    st.update(-1, t_now=1.0)
    assert st.update(-1, t_now=4.01) == 'track_gone'
    assert st.update(-1, t_now=5.0) is None    # 한 번만


def test_new_track_after_gone_emits_new_track_again():
    st = SessionTracker(bye_grace_sec=3.0)
    st.update(7, t_now=0.0)
    st.update(-1, t_now=1.0)
    st.update(-1, t_now=4.01)                  # gone
    assert st.update(9, t_now=5.0) == 'new_track'


def test_track_id_change_treated_as_new_track():
    # 같은 사람 다른 track_id 같은 케이스 — P0 단순화는 'new_track' 처리
    st = SessionTracker(bye_grace_sec=3.0)
    st.update(7, t_now=0.0)
    assert st.update(9, t_now=0.5) == 'new_track'


def test_same_id_returns_after_gone_emits_new_track():
    """Customer leaves >grace, gone fires, then SAME id reappears -> new session = new_track.

    Distinct from test_track_lost_within_grace_no_event (suppress re-greet only within grace).
    Distinct from test_new_track_after_gone_emits_new_track_again (which uses different id).
    """
    st = SessionTracker(bye_grace_sec=3.0)
    st.update(7, t_now=0.0)
    st.update(-1, t_now=1.0)
    st.update(-1, t_now=4.01)      # track_gone emitted
    assert st.update(7, t_now=5.0) == 'new_track'   # same id, but new session

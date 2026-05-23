"""TDD — Dispatch dataclass (action_name, msg, kind) frozen + literal."""
import pytest

from arm_reactor_core.dispatch import Dispatch


def test_dispatch_holds_three_fields():
    d = Dispatch(action_name='/arm_controller/follow_joint_trajectory',
                 msg=object(), kind='trajectory')
    assert d.action_name == '/arm_controller/follow_joint_trajectory'
    assert d.kind == 'trajectory'
    assert d.msg is not None


def test_dispatch_is_frozen():
    d = Dispatch(action_name='/x', msg=None, kind='trajectory')
    with pytest.raises(Exception):
        d.action_name = '/y'   # frozen dataclass → FrozenInstanceError


def test_dispatch_equality_by_value():
    a = Dispatch('/x', None, 'trajectory')
    b = Dispatch('/x', None, 'trajectory')
    assert a == b


def test_dispatch_gripper_kind():
    d = Dispatch(action_name='/gripper_controller/gripper_cmd',
                 msg=object(), kind='gripper')
    assert d.kind == 'gripper'

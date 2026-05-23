"""Backward-compat shim — reactor_node 는 arm_reactor_core.reactor_node 로 이동."""
from arm_reactor_core.reactor_node import ReactorNode, main   # noqa: F401

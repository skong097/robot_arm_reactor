"""reactor_node — V·A 신호 + 세션 이벤트 -> motion_mapper -> scheduler -> OMX action."""
from __future__ import annotations

import json
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from dobi_npc_msgs.msg import EmotionState, RapportEvent

from omx_reactor.context import Context, make_emotion_signal
from omx_reactor.motions import MOTIONS
from omx_reactor.motion_mapper import select_motion
from omx_reactor.motion_scheduler import MotionScheduler, SchedulerAction
from omx_reactor.session_tracker import SessionTracker
from omx_reactor.omx_trajectory_sender import OmxTrajectorySender


class ReactorNode(Node):

    def __init__(self):
        super().__init__('omx_reactor_node')
        self.declare_parameter('cooldown_default_sec', 5.0)
        self.declare_parameter('bye_grace_sec', 3.0)
        self.declare_parameter('deadband', 0.10)
        self.declare_parameter('tick_period_sec', 0.1)

        cd = float(self.get_parameter('cooldown_default_sec').value)
        self._bye_grace = float(self.get_parameter('bye_grace_sec').value)
        self._deadband = float(self.get_parameter('deadband').value)
        tick = float(self.get_parameter('tick_period_sec').value)

        self._session = SessionTracker(bye_grace_sec=self._bye_grace)
        self._scheduler = MotionScheduler(cooldown_default_sec=cd)
        self._sender = OmxTrajectorySender(self)

        self._latest_v: float = 0.0
        self._latest_a: float = 0.0
        self._latest_conf: float = 0.0
        self._latest_source: str = 'face'
        self._latest_track: int = -1
        self._pending_session_event: str | None = None

        self.create_subscription(EmotionState, '/emotion/state', self._on_emotion, 10)
        self.create_subscription(RapportEvent, '/rapport/event', self._on_rapport, 10)

        self._state_pub = self.create_publisher(String, '/omx_reactor/state', 10)
        self.create_timer(tick, self._tick)

        self.get_logger().info(
            f'omx_reactor_node ready — deadband={self._deadband}, '
            f'bye_grace={self._bye_grace}, cooldown_default={cd}, '
            f'tick={tick}, motions={len(MOTIONS)}')

    # ── 구독 ──────────────────────────────────────────────
    def _on_emotion(self, msg: EmotionState):
        # rapport 가 smoothed 값을 발행하므로 본 콜백은 track_id 만 사용
        self._latest_track = int(msg.track_id)
        self._latest_source = str(msg.source) or 'face'

    def _on_rapport(self, msg: RapportEvent):
        # rapport_tracker 가 EMA-smoothed V·A 를 emotion.valence/arousal 에 채움 (spec)
        self._latest_v = float(msg.emotion.valence)
        self._latest_a = float(msg.emotion.arousal)
        self._latest_conf = float(msg.emotion.confidence)
        if msg.emotion.track_id != -1:
            self._latest_track = int(msg.emotion.track_id)

    # ── tick ──────────────────────────────────────────────
    def _tick(self):
        t_now = self._now_sec()

        # 세션 이벤트 산출 (한 tick 만 살아있음)
        session_event = self._session.update(self._latest_track, t_now)

        emo = make_emotion_signal(
            v=self._latest_v, a=self._latest_a,
            confidence=self._latest_conf, source=self._latest_source,
            deadband=self._deadband,
        )
        ctx = Context(emotion=emo, session_event=session_event, t_now=t_now)

        chosen = select_motion(ctx, MOTIONS)
        if chosen is not None:
            action = self._scheduler.submit(chosen, t_now=t_now)
            if action == SchedulerAction.START:
                self._dispatch(chosen)
            elif action == SchedulerAction.INTERRUPT:
                self._sender.cancel_current()
                self._dispatch(chosen)
            # QUEUE / IGNORE 는 아무 것도 안 함

        self._publish_state(ctx, t_now)

    def _dispatch(self, motion):
        self.get_logger().info(f'▶ Motion {motion.id} (priority={motion.priority})')
        traj = motion.trajectory()
        self._sender.send(traj, on_finish=lambda: self._on_motion_finish())

    def _on_motion_finish(self):
        t_now = self._now_sec()
        nxt = self._scheduler.on_finish(t_now=t_now)
        if nxt is not None:
            self._dispatch(nxt)

    def _publish_state(self, ctx: Context, t_now: float):
        cur = self._scheduler.current
        nxt = self._scheduler.queued
        payload = {
            't': t_now,
            'v': ctx.emotion.v if ctx.emotion else None,
            'a': ctx.emotion.a if ctx.emotion else None,
            'quadrant': ctx.emotion.quadrant if ctx.emotion else None,
            'in_deadband': ctx.emotion.in_deadband if ctx.emotion else False,
            'confidence': ctx.emotion.confidence if ctx.emotion else 0.0,
            'source': ctx.emotion.source if ctx.emotion else '',
            'track_id': self._latest_track,
            'current_motion': cur.id if cur else None,
            'queued_motion': nxt.id if nxt else None,
            'session_event': ctx.session_event,
        }
        m = String()
        m.data = json.dumps(payload)
        self._state_pub.publish(m)

    def _now_sec(self) -> float:
        t = self.get_clock().now().nanoseconds * 1e-9
        return t


def main(args=None):
    rclpy.init(args=args)
    node = ReactorNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

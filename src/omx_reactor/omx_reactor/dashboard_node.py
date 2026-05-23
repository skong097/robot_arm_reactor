"""dashboard_node — /emotion/state, /rapport/event, /omx_reactor/state read-only 구독 후
FastAPI(HTTP) + WebSocket 으로 브라우저에 push."""
from __future__ import annotations

import asyncio
import json
import threading
from collections import deque
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from dobi_npc_msgs.msg import EmotionState, RapportEvent

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn


def _static_dir() -> Path:
    share = get_package_share_directory('omx_reactor')
    return Path(share) / 'web' / 'static'


class DashboardNode(Node):

    def __init__(self):
        super().__init__('omx_dashboard_node')
        self.declare_parameter('http_port', 8800)
        self._port = int(self.get_parameter('http_port').value)

        self._snapshot = {
            'emotion': None,          # raw EmotionState 최근 1건
            'rapport': None,          # raw RapportEvent 최근 1건
            'reactor': None,          # /omx_reactor/state JSON 최근
            'events': deque(maxlen=20),
        }
        self._clients: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._loop_ready = threading.Event()

        self.create_subscription(EmotionState, '/emotion/state', self._on_emotion, 10)
        self.create_subscription(RapportEvent, '/rapport/event', self._on_rapport, 10)
        self.create_subscription(String, '/omx_reactor/state', self._on_reactor, 10)

        self._app = self._build_app()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()
        self._loop_ready.wait(timeout=5.0)
        self.get_logger().info(f'omx_dashboard_node ready — http://localhost:{self._port}/')

    # ── FastAPI ──────────────────────────────────────────
    def _build_app(self) -> FastAPI:
        app = FastAPI(title='omx_reactor dashboard')
        static = _static_dir()

        @app.get('/')
        async def index():
            return FileResponse(static / 'index.html')

        @app.get('/api/snapshot')
        async def snapshot():
            return JSONResponse({
                'emotion': self._snapshot['emotion'],
                'rapport': self._snapshot['rapport'],
                'reactor': self._snapshot['reactor'],
                'events': list(self._snapshot['events']),
            })

        @app.websocket('/ws/stream')
        async def ws_stream(ws: WebSocket):
            await ws.accept()
            self._clients.add(ws)
            try:
                # 첫 push — 최신 snapshot
                await ws.send_text(json.dumps({
                    'type': 'snapshot',
                    'payload': {
                        'emotion': self._snapshot['emotion'],
                        'rapport': self._snapshot['rapport'],
                        'reactor': self._snapshot['reactor'],
                        'events': list(self._snapshot['events']),
                    },
                }))
                while True:
                    await ws.receive_text()  # client keep-alive
            except WebSocketDisconnect:
                pass
            finally:
                self._clients.discard(ws)

        app.mount('/static', StaticFiles(directory=static), name='static')
        return app

    def _serve(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop_ready.set()
        config = uvicorn.Config(self._app, host='0.0.0.0', port=self._port,
                                log_level='warning', loop='asyncio')
        server = uvicorn.Server(config)
        self._loop.run_until_complete(server.serve())

    # ── ROS 구독 → snapshot + WS push ───────────────────
    def _on_emotion(self, msg: EmotionState):
        self._snapshot['emotion'] = {
            'v': float(msg.valence), 'a': float(msg.arousal),
            'confidence': float(msg.confidence),
            'source': str(msg.source),
            'track_id': int(msg.track_id),
        }
        self._push({'type': 'emotion', 'payload': self._snapshot['emotion']})

    def _on_rapport(self, msg: RapportEvent):
        ev = {
            'event_type': str(msg.event_type),
            'weight': float(msg.weight),
            'reason': str(msg.reason),
            'v': float(msg.emotion.valence),
            'a': float(msg.emotion.arousal),
        }
        self._snapshot['rapport'] = ev
        self._snapshot['events'].append({'type': 'rapport', **ev})
        self._push({'type': 'rapport', 'payload': ev})

    def _on_reactor(self, msg: String):
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError:
            return
        prev = self._snapshot['reactor']
        self._snapshot['reactor'] = payload
        prev_motion = prev.get('current_motion') if prev else None
        cur_motion = payload.get('current_motion')
        if cur_motion is not None and prev_motion != cur_motion:
            self._snapshot['events'].append({'type': 'motion', **payload})
        self._push({'type': 'reactor', 'payload': payload})

    def _push(self, message: dict):
        if self._loop is None or not self._clients:
            return
        text = json.dumps(message)
        for ws in list(self._clients):
            asyncio.run_coroutine_threadsafe(self._send_safe(ws, text), self._loop)

    async def _send_safe(self, ws: WebSocket, text: str):
        try:
            await ws.send_text(text)
        except Exception:
            self._clients.discard(ws)


def main(args=None):
    rclpy.init(args=args)
    node = DashboardNode()
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

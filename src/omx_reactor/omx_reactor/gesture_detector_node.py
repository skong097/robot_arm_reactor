"""gesture_detector_node — /webcam/image_raw -> mediapipe HandLandmarker
-> /gesture/event (std_msgs/String JSON).

JSON payload: {ts, event_type, confidence, source}
  event_type: 'hand_visible' (현 단순 detection)
  confidence: HandLandmarker handedness score (0~1)
  source: 'mediapipe.HandLandmarker'

cooldown / visibility 판정은 gesture_detection.HandVisibilityDetector (pure logic, TDD).
모델 파일: share/omx_reactor/models/gesture/hand_landmarker.task (외부 부트스트랩).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

from omx_reactor.gesture_detection import HandVisibilityDetector


class GestureDetectorNode(Node):
    """mediapipe HandLandmarker 로 손 detection + HandVisibilityDetector cooldown."""

    def __init__(self):
        super().__init__('gesture_detector_node')
        self.declare_parameter('image_topic', '/webcam/image_raw')
        self.declare_parameter('event_topic', '/gesture/event')
        self.declare_parameter('cooldown_sec', 5.0)
        self.declare_parameter('model_path', '')

        img_topic = str(self.get_parameter('image_topic').value)
        event_topic = str(self.get_parameter('event_topic').value)
        cooldown = float(self.get_parameter('cooldown_sec').value)
        model_path = str(self.get_parameter('model_path').value)

        if not model_path:
            model_path = str(
                Path(get_package_share_directory('omx_reactor'))
                / 'models' / 'gesture' / 'hand_landmarker.task'
            )

        # mediapipe Tasks API — HandLandmarker
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision

        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._mp_image_cls = mp.Image       # top-level mediapipe.Image
        self._mp_image_fmt = mp.ImageFormat.SRGB

        self._detector = HandVisibilityDetector(cooldown_sec=cooldown)
        self._bridge = CvBridge()

        self.create_subscription(Image, img_topic, self._on_image, 1)
        self._pub = self.create_publisher(String, event_topic, 10)

        self.get_logger().info(
            f'gesture_detector_node ready — {img_topic} -> {event_topic}, '
            f'cooldown={cooldown}, model={model_path}'
        )

    def _on_image(self, msg: Image):
        try:
            bgr = self._bridge.imgmsg_to_cv2(msg, 'bgr8')
            rgb = bgr[:, :, ::-1].copy()
            mp_img = self._mp_image_cls(image_format=self._mp_image_fmt, data=rgb)
            result = self._landmarker.detect(mp_img)
        except Exception as e:
            self.get_logger().warning(
                f'HandLandmarker detect 실패: {e}',
                throttle_duration_sec=5.0,
            )
            return

        visible = len(result.hand_landmarks) > 0
        confidence = (
            float(result.handedness[0][0].score)
            if visible and result.handedness else 0.0
        )

        event = self._detector.update(visible=visible, t_now=time.time())
        if event is None:
            return

        payload = {
            'ts': time.time(),
            'event_type': event,
            'confidence': confidence,
            'source': 'mediapipe.HandLandmarker',
        }
        out = String()
        out.data = json.dumps(payload)
        self._pub.publish(out)
        self.get_logger().info(f'▶ {event} (conf={confidence:.2f})')


def main(args=None):
    rclpy.init(args=args)
    node = GestureDetectorNode()
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

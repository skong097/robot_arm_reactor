"""camera_file — 영상 파일 cycle 발행 (OpenCV) → /webcam/image_raw.

ros2 launch ... camera:=file file_path:=/path/to/clip.mp4
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    file_arg = DeclareLaunchArgument('file_path', default_value='')
    fps_arg = DeclareLaunchArgument('fps', default_value='10')
    # 단순 inline python publisher (별 노드 파일 없이)
    cmd = [
        'python3', '-c',
        'import sys, cv2, rclpy\n'
        'from rclpy.node import Node\n'
        'from sensor_msgs.msg import Image\n'
        'from cv_bridge import CvBridge\n'
        'class F(Node):\n'
        '    def __init__(self, path, fps):\n'
        '        super().__init__("camera_file_pub")\n'
        '        self.cap = cv2.VideoCapture(path)\n'
        '        self.br = CvBridge()\n'
        '        self.pub = self.create_publisher(Image, "/webcam/image_raw", 10)\n'
        '        self.create_timer(1.0/fps, self.tick)\n'
        '    def tick(self):\n'
        '        ok, frame = self.cap.read()\n'
        '        if not ok:\n'
        '            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0); return\n'
        '        msg = self.br.cv2_to_imgmsg(frame, encoding="bgr8")\n'
        '        msg.header.frame_id = "webcam_link"\n'
        '        self.pub.publish(msg)\n'
        'rclpy.init()\n'
        'path = sys.argv[1]; fps = float(sys.argv[2])\n'
        'n = F(path, fps); rclpy.spin(n)\n',
        LaunchConfiguration('file_path'),
        LaunchConfiguration('fps'),
    ]
    return LaunchDescription([
        file_arg, fps_arg,
        ExecuteProcess(cmd=cmd, output='screen'),
    ])

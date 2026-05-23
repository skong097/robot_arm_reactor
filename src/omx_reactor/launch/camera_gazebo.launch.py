"""camera_gazebo — Gazebo 내부 가상 카메라 토픽 → /webcam/image_raw 로 remap.

전제: omx_gazebo 또는 별 Gazebo world 가 가상 카메라를 띄움.
실제 topic 명은 Gazebo world 설정에 따라 다르며 본 launch 는 placeholder.
v1 데모는 v4l2 또는 file 사용 권장.
"""
from launch import LaunchDescription


def generate_launch_description():
    return LaunchDescription([])

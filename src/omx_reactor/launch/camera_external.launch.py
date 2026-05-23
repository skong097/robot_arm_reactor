"""camera_external — no-op. /webcam/image_raw 가 다른 launch 에서 발행 중 가정."""
from launch import LaunchDescription


def generate_launch_description():
    return LaunchDescription([])

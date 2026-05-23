"""camera_v4l2 — v4l2_camera_node spawn → /webcam/image_raw."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    device_arg = DeclareLaunchArgument('video_device', default_value='/dev/video0')
    return LaunchDescription([
        device_arg,
        Node(
            package='v4l2_camera', executable='v4l2_camera_node',
            name='webcam_master', output='screen',
            remappings=[('image_raw', '/webcam/image_raw')],
            parameters=[{
                'video_device': LaunchConfiguration('video_device'),
                'pixel_format': 'YUYV',
                'image_size': [640, 480],
                'camera_frame_id': 'webcam_link',
            }],
        ),
    ])

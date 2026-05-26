"""openarm_demo.launch.py — OpenArm v10 bimanual 데모.

ros2 launch openarm_motion_pack openarm_demo.launch.py [camera:=v4l2|file|external]

arm_reactor_core/common.launch.py + OpenArm bringup (openarm.bimanual.launch.py
use_fake_hardware:=true). motion_pack 은 'openarm_motion_pack' hardcoded.
RViz + mock_components fake_hw + 4 controller (left/right × jt/gripper).
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    camera_arg = DeclareLaunchArgument('camera', default_value='v4l2')
    file_path_arg = DeclareLaunchArgument('file_path', default_value='')
    video_device_arg = DeclareLaunchArgument('video_device', default_value='/dev/video0')

    arc_pack = FindPackageShare('arm_reactor_core')
    openarm_bringup = FindPackageShare('openarm_bringup')

    common = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([arc_pack, 'launch', 'common.launch.py'])
        ),
        launch_arguments={
            'motion_pack': 'openarm_motion_pack',
            'camera': LaunchConfiguration('camera'),
            'file_path': LaunchConfiguration('file_path'),
            'video_device': LaunchConfiguration('video_device'),
            'arm_view_mode': 'urdf',
        }.items(),
    )

    openarm = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([openarm_bringup, 'launch', 'openarm.bimanual.launch.py'])
        ),
        launch_arguments={
            'use_fake_hardware': 'true',
        }.items(),
    )

    return LaunchDescription([
        camera_arg, file_path_arg, video_device_arg,
        common,
        openarm,
    ])

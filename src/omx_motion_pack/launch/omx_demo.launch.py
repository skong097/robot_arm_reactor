"""omx_demo.launch.py — OMX 데모.

ros2 launch omx_motion_pack omx_demo.launch.py camera:=v4l2|file|external|gazebo [file_path:=...]

arm_reactor_core 의 common.launch.py (geva + rapport + gesture + dashboard + reactor)
+ omx_gazebo.launch.py (Gazebo + OMX URDF + 외부 카메라 SDF). motion_pack 은
'omx_motion_pack' hardcoded.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    camera_arg = DeclareLaunchArgument('camera', default_value='v4l2')
    file_path_arg = DeclareLaunchArgument('file_path', default_value='')

    arc_pack = FindPackageShare('arm_reactor_core')
    omx_pack = FindPackageShare('omx_motion_pack')

    common = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([arc_pack, 'launch', 'common.launch.py'])
        ),
        launch_arguments={
            'motion_pack': 'omx_motion_pack',
            'camera': LaunchConfiguration('camera'),
            'file_path': LaunchConfiguration('file_path'),
            'arm_view_mode': 'mjpeg',
        }.items(),
    )

    omx_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([omx_pack, 'launch', 'omx_gazebo.launch.py'])
        ),
    )

    return LaunchDescription([
        camera_arg, file_path_arg,
        common,
        omx_gazebo,
    ])

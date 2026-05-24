"""omx_gazebo — ROBOTIS open_manipulator_x gazebo launch include
+ 외부 시점 카메라 (dashboard 임베드용) spawn + GZ→ROS image bridge.
"""
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    share_robotis = get_package_share_directory('open_manipulator_bringup')
    share_pack = get_package_share_directory('omx_motion_pack')
    sdf_path = share_pack + '/models/external_cam/model.sdf'

    omx_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            share_robotis + '/launch/open_manipulator_x_gazebo.launch.py'
        ),
    )

    # 외부 시점 카메라 — Gazebo Sim 시작 후 충분 delay 후 spawn.
    # ros_gz_sim create 가 SDF 의 <pose> 무시 — -x/-y/-z/-R/-P/-Y 명시 강제.
    # (1.5, 0, 0.4) 정면 약간 위에서 OMX 향함 (yaw=π).
    spawn_cam = TimerAction(
        period=8.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'run', 'ros_gz_sim', 'create',
                     '-name', 'external_cam',
                     '-file', sdf_path,
                     '-x', '1.5', '-y', '0.0', '-z', '0.4',
                     '-R', '0.0', '-P', '0.15', '-Y', '3.14159'],
                output='screen',
            ),
        ],
    )

    # GZ Image -> ROS Image bridge. SDF 의 <topic>external_cam/image</topic> 사용.
    # spawn 후 bridge 시작이 안전 — 추가 delay.
    image_bridge = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='ros_gz_image',
                executable='image_bridge',
                arguments=['/external_cam/image'],
                output='screen',
            ),
        ],
    )

    return LaunchDescription([
        omx_gazebo,
        spawn_cam,
        image_bridge,
    ])

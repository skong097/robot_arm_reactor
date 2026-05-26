"""common.launch.py — arm 무관 노드 묶음 (geva + rapport + gesture + dashboard + reactor).

arg:
  motion_pack    (default 'omx_motion_pack')   — reactor 의 motion_pack_module ROS param 으로 전달
  camera         (default 'v4l2')              — webcam launch 분기 (v4l2|file|external|gazebo)
  file_path      (default '')                  — camera=file 인 경우의 비디오 경로

camera_*.launch.py 는 omx_motion_pack 의 share 에서 include (arm 무관 — 이주 비용 대비 가치 X).
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    motion_pack = DeclareLaunchArgument('motion_pack', default_value='omx_motion_pack',
                                        description='omx_motion_pack | openarm_motion_pack')
    camera_arg = DeclareLaunchArgument('camera', default_value='v4l2',
                                       description='v4l2|file|external|gazebo')
    file_path_arg = DeclareLaunchArgument('file_path', default_value='',
                                          description='camera=file 의 비디오 경로')
    video_device_arg = DeclareLaunchArgument('video_device', default_value='/dev/video0',
                                             description='camera=v4l2 의 /dev/videoN device')
    arm_view_mode_arg = DeclareLaunchArgument('arm_view_mode', default_value='mjpeg',
                                              description='mjpeg | urdf — dashboard 우측 패널 모드')

    omx_pack = FindPackageShare('omx_motion_pack')
    camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                omx_pack, 'launch',
                ['camera_', LaunchConfiguration('camera'), '.launch.py'],
            ])
        ),
        launch_arguments={
            'video_device': LaunchConfiguration('video_device'),
        }.items(),
    )

    geva = Node(package='dobi_npc_emotion', executable='geva_node',
                name='geva_node', output='screen',
                parameters=[{'input_topic': '/webcam/image_raw'}])

    rapport = Node(package='dobi_npc_emotion', executable='rapport_tracker',
                   name='rapport_tracker_node', output='screen',
                   parameters=[{'ema_alpha_base': 0.7, 'conf_min_gate': 0.2}])

    gesture = Node(package='arm_reactor_core', executable='gesture_detector_node',
                   name='gesture_detector_node', output='screen',
                   parameters=[{
                       'cooldown_sec': 5.0,
                       'up_threshold': 0.55,
                       'wave_window_size': 10,
                       'wave_oscillation_threshold': 0.15,
                   }])

    dashboard = Node(package='arm_reactor_core', executable='dashboard_node',
                     name='omx_dashboard_node', output='screen',
                     parameters=[{
                         'http_port': 7700,
                         'arm_view_mode': LaunchConfiguration('arm_view_mode'),
                     }])

    reactor = Node(package='arm_reactor_core', executable='reactor_node',
                   name='omx_reactor_node', output='screen',
                   parameters=[{
                       'motion_pack_module': LaunchConfiguration('motion_pack'),
                   }])

    return LaunchDescription([
        motion_pack, camera_arg, file_path_arg, video_device_arg, arm_view_mode_arg,
        camera_launch,
        geva, rapport, gesture, dashboard, reactor,
    ])

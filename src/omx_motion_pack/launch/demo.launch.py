"""demo.launch.py — 통합 데모.

ros2 launch omx_motion_pack demo.launch.py camera:=v4l2|file|external|gazebo [file_path:=...]
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    camera_arg = DeclareLaunchArgument('camera', default_value='v4l2',
                                       description='v4l2|file|external|gazebo')

    pkg_share = FindPackageShare('omx_motion_pack')

    camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                pkg_share, 'launch',
                ['camera_', LaunchConfiguration('camera'), '.launch.py'],
            ])
        ),
    )

    omx_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_share, 'launch', 'omx_gazebo.launch.py'])
        ),
    )

    geva = Node(package='dobi_npc_emotion', executable='geva_node',
                name='geva_node', output='screen',
                parameters=[{'input_topic': '/webcam/image_raw'}])

    rapport = Node(package='dobi_npc_emotion', executable='rapport_tracker',
                   name='rapport_tracker_node', output='screen',
                   parameters=[{'ema_alpha_base': 0.7, 'conf_min_gate': 0.2}])

    reactor = Node(package='omx_reactor', executable='reactor_node',
                   name='omx_reactor_node', output='screen')

    dashboard = Node(package='arm_reactor_core', executable='dashboard_node',
                     name='omx_dashboard_node', output='screen',
                     parameters=[{'http_port': 8800}])

    # gesture detector — /webcam/image_raw → /gesture/event (mediapipe GestureRecognizer + Open_Palm + wrist y + wave)
    # model 부트스트랩 필요: src/vendored/README.md 의 외부 모델 부트스트랩 절차
    gesture = Node(package='omx_reactor', executable='gesture_detector_node',
                   name='gesture_detector_node', output='screen',
                   parameters=[{
                       'cooldown_sec': 5.0,
                       'up_threshold': 0.55,           # wrist y < 이 값 시 hands_up 판정 (살짝 올린 자세도 OK)
                       'wave_window_size': 10,
                       'wave_oscillation_threshold': 0.15,
                   }])

    return LaunchDescription([
        camera_arg,
        camera_launch,
        omx_gazebo,
        geva,
        rapport,
        reactor,
        dashboard,
        gesture,
    ])

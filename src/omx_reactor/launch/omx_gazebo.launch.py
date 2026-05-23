"""omx_gazebo — ROBOTIS open_manipulator_x gazebo launch include."""
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    share = get_package_share_directory('open_manipulator_bringup')
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                share + '/launch/open_manipulator_x_gazebo.launch.py'
            ),
        ),
    ])

from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    params_file = os.path.join(
        get_package_share_directory("testbed_navigation"),
        "config",
        "amcl_params.yaml"
    )

    amcl = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        parameters=[params_file],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {
                "use_sim_time": True,
                "autostart": True,
                "node_names": ["amcl"],
            }
        ],
    )

    initial_pose = ExecuteProcess(
        cmd=[
            "ros2",
            "topic",
            "pub",
            "--once",
            "/initialpose",
            "geometry_msgs/msg/PoseWithCovarianceStamped",
            "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -0.155, y: 4.828, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: -0.2905, w: 0.9569}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 999.0, 0.0, 0.0, 0.0, 999.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1]}}"
        ],
        output="screen",
    )

    delayed_initial_pose = TimerAction(
        period=8.0,
        actions=[initial_pose],
    )

    return LaunchDescription([
        amcl,
        lifecycle_manager,
        delayed_initial_pose,
    ])

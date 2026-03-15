from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ------------------------------------------------------------------ args
    use_fake_hardware_arg = DeclareLaunchArgument(
        'use_fake_hardware', default_value='true',
        description='Use fake hardware (simulation) for both robots'
    )
    use_fake_hardware = LaunchConfiguration('use_fake_hardware')

    # ------------------------------------------------------------------ robot description

    robot_description_content = Command([
        FindExecutable(name='xacro'), ' ',
        PathJoinSubstitution([
            FindPackageShare('aubo_examples'),
            'urdf', 'aubo.urdf.xacro'
        ]),
        ' use_sim:=false',
        ' aubo_use_fake_hardware:=', use_fake_hardware,
    ])
    robot_description = {
        'robot_description': ParameterValue(robot_description_content, value_type=str)
    }

    # ------------------------------------------------------------------ nodes
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            robot_description,
            PathJoinSubstitution([
                FindPackageShare('aubo_examples'),
                'config', 'ros2_controllers.yaml'
            ]),
        ],
        output='screen',
    )

    # Spawners — each waits for the controller_manager to be available
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster',
                   '--controller-manager', '/controller_manager'],
        output='screen',
    )

    aubo_jtc_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['aubo_joint_trajectory_controller',
                   '--controller-manager', '/controller_manager'],
        output='screen',
    )

    # Start JTC spawners only after joint_state_broadcaster is active
    aubo_jtc_spawner_delayed = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[aubo_jtc_spawner],
        )
    )

    # rqt_joint_trajectory_controller — GUI for manually commanding joints
    rqt_joint_trajectory_controller = Node(
        package='rqt_joint_trajectory_controller',
        executable='rqt_joint_trajectory_controller',
        output='screen',
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', PathJoinSubstitution([
            FindPackageShare('aubo_examples'),
            'config', 'aubo.rviz'
        ])]
    )

    return LaunchDescription([
        use_fake_hardware_arg,
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        aubo_jtc_spawner_delayed,
        rqt_joint_trajectory_controller,
        rviz,
    ])

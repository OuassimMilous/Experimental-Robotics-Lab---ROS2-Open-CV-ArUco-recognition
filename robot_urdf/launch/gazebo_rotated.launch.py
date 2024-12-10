import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare



def generate_launch_description():
    test_robot_description_share = FindPackageShare(package='robot_urdf').find('robot_urdf')
    default_model_path = os.path.join(test_robot_description_share, 'urdf/robot4.xacro')
    rviz_config_path = os.path.join(test_robot_description_share, 'config/rviz.rviz')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
    )
    
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )
   

    # GAZEBO_MODEL_PATH has to be correctly set for Gazebo to be able to find the model
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
						arguments=['-entity', 'my_test_robot', '-topic', '/robot_description', '-x', '0.025', '-y', '0.015', '-Y'],
                        output='screen')

    aruco_node = Node(
        package='ros2_aruco',
        executable='aruco_node',
        name='aruco_node',
        output='screen'
    )

    # Load the joint state broadcaster
    controller_manager = Node(
        package='controller_manager',
        executable='spawner.py',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    # Load the joint velocity controller
    spawn_camera_controller = Node(
        package='controller_manager',
        executable='spawner.py',
        arguments=['joint_velocity_controller'],
        output='screen'
    )

    
    
    NodeB = Node(
        package='robot_urdf',
        executable='NodeB.py',
        name='NodeB',
        output='screen'
    )
    
    
    return LaunchDescription([
        DeclareLaunchArgument(name='model', default_value=default_model_path,
                                    description='Absolute path to robot urdf file'),
        robot_state_publisher_node,
        joint_state_publisher_node,
        spawn_entity,
        ExecuteProcess(
            cmd=['gazebo', '--verbose', os.path.join(test_robot_description_share, 'worlds/world_markers.world'), '-s', 'libgazebo_ros_factory.so'],
            output='screen'),
        ExecuteProcess(
            cmd=['rviz2', '-d', rviz_config_path],
            output='screen'),
        aruco_node,
        controller_manager,
        spawn_camera_controller,
        NodeB
    ])
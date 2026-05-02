#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Package paths
    tb3_gazebo_launch = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch')
    pkg_bulter_bot = get_package_share_directory('bulter_bringup')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Paths
    world_path = os.path.join(pkg_bulter_bot, 'world', 'hotel', 'empty_world.world')
    hotel_model = os.path.join(pkg_bulter_bot, 'world', 'hotel', 'model.sdf')
    table_model = os.path.join(pkg_bulter_bot, 'models', 'table', 'model.sdf')

    # Configurations
    config_dir = os.path.join(pkg_bulter_bot, 'config')
    map_file = os.path.join(config_dir, 'hotel_map.yaml')
    nav2_params = os.path.join(config_dir, 'tb3_nav_params.yaml')
    rviz_config = os.path.join(config_dir, 'tb3_nav.rviz')

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-5.0')
    y_pose = LaunchConfiguration('y_pose', default='-3.0')

    # Gazebo server
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world_path}.items()
    )

    # Gazebo client
    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))
    )

    # Robot State Publisher
    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tb3_gazebo_launch, 'robot_state_publisher.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # Spawn TurtleBot3
    spawn_tb3_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tb3_gazebo_launch, 'spawn_turtlebot3.launch.py')),
        launch_arguments={
            'x_pose': x_pose,
            'y_pose': y_pose,
            'use_sim_time': use_sim_time
        }.items()
    )

    # RViz
    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_node',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Nav2
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_file,
            'params_file': nav2_params,
            'use_sim_time': use_sim_time,
            'autostart': 'true'
        }.items()
    )
    
    #Spawning models
    hotel_model_node = Node(
        package='bulter_bringup',
        executable='sdf_spawner',
        name='hotel_spawner',
        output='screen',
        arguments=[hotel_model, 'hotel', '0.0', '0.0']
    )

    table_1 = Node(
        package='bulter_bringup',
        executable='sdf_spawner',
        name='table_1_spawner',
        output='screen',
        arguments=[table_model, 'table_1', '-0.6', '3.99']
    )
    table_2 = Node(
        package='bulter_bringup',
        executable='sdf_spawner',
        name='table_2_spawner',
        output='screen',
        arguments=[table_model, 'table_2', '4.52', '3.99']
    )
    table_3 = Node(
        package='bulter_bringup',
        executable='sdf_spawner',
        name='table_3_spawner',
        output='screen',
        arguments=[table_model, 'table_3', '4.53', '-3.17']
    )

    table_4 = Node(
        package='bulter_bringup',
        executable='sdf_spawner',
        name='table_4_spawner',
        output='screen',
        arguments=[table_model, 'table_4', '-0.6', '-3.17']
    )
    butler_delivery_node = Node(
        package='bulter_bringup',
        executable='butler_delivery_node',
        name='butler_delivery_node',
        output='screen',
                )


    return LaunchDescription([
        gzserver_cmd,
        gzclient_cmd,
        robot_state_publisher_cmd,
        spawn_tb3_cmd,
        hotel_model_node,
        table_1,
        table_2,
        table_3,
        table_4,
        rviz_cmd,
        nav2_bringup,
        butler_delivery_node
    ])

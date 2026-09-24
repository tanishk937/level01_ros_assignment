# Testbed Navigation

This package contains the navigation setup developed for the ERIC Robotics Level 1 ROS2 Navigation Assignment.

The goal was to build the navigation workflow manually using individual Nav2 components instead of starting the complete stack through `nav2_bringup`.

## Environment

* Ubuntu 22.04
* ROS2 Humble
* Gazebo Classic 11.10.2
* RViz2
* Nav2

Robot:

* Testbed-T1.0.0
* Differential drive
* 2D LiDAR
* IMU

Main topics used by the navigation stack:

```text
/scan
/odom
/cmd_vel
/map
/initialpose
```

## Package structure

```text
testbed_navigation/
├── config/
│   ├── amcl_params.yaml
│   └── nav2_params.yaml
├── launch/
│   ├── map_loader.launch.py
│   ├── localization.launch.py
│   └── navigation.launch.py
├── CMakeLists.txt
├── package.xml
└── README.md
```

## How the navigation system is separated

The navigation workflow is divided into three launch files.

### 1. Map loading

`map_loader.launch.py`

This starts:

* `nav2_map_server`
* Map lifecycle manager

The map is loaded from:

```text
testbed_bringup/maps/testbed_world.yaml
```

The map server uses simulation time because the robot is running in Gazebo.

Run:

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

### 2. Localization

`localization.launch.py`

This starts:

* `nav2_amcl`
* Localization lifecycle manager

AMCL uses the existing map together with the robot's LiDAR and odometry to estimate the robot pose.

The main frames are:

```text
map
 └── odom
      └── base_footprint
           └── base_link
                └── lidar_link_1
```

For the supplied Gazebo testbed, the launch file publishes the initial robot pose automatically. For a different starting position, the pose can be supplied from RViz using **2D Pose Estimate** or from the terminal.

Example:

```bash
ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 5.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: -0.2905, w: 0.9569}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 999.0, 0.0, 0.0, 0.0, 999.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1]}}"
```

Run:

```bash
ros2 launch testbed_navigation localization.launch.py
```

## 3. Navigation

`navigation.launch.py`

The navigation launch file starts the main Nav2 servers individually:

* Planner Server
* Controller Server
* BT Navigator
* Behavior Server
* Waypoint Follower
* Navigation lifecycle manager

The planner uses:

```text
NavFnPlanner
```

and the controller uses:

```text
DWB
```

The global costmap uses the static map together with obstacle and inflation layers.

The local costmap uses a rolling window around the robot and receives obstacle information from the LiDAR.

Run:

```bash
ros2 launch testbed_navigation navigation.launch.py
```

## Starting the complete system

Open separate terminals and source the workspace in each terminal.

### Terminal 1 — Gazebo and RViz

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

### Terminal 2 — Map Server

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch testbed_navigation map_loader.launch.py
```

### Terminal 3 — Localization

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch testbed_navigation localization.launch.py
```

The localization launch file publishes the testbed's initial pose automatically after AMCL starts. This keeps the startup procedure repeatable for the supplied Gazebo testbed.

For a different robot starting position, the initial pose should be set manually in RViz or by publishing to `/initialpose`.

### Terminal 4 — Navigation

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch testbed_navigation navigation.launch.py
```

## Sending a navigation goal

A goal can be sent from RViz using the Nav2 goal tool.

It can also be sent from the terminal:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map'}, pose: {position: {x: 0.67, y: 4.28, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: -0.2875, w: 0.9578}}}}"
```

A successful test returned:

```text
Goal accepted
Goal finished with status: SUCCEEDED
```

During the test, `/cmd_vel` contained non-zero linear and angular velocity commands while the robot was moving and returned to zero after reaching the goal.

## Useful checks

Check the lifecycle state:

```bash
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /bt_navigator
ros2 lifecycle get /behavior_server
```

The navigation servers should report:

```text
active [3]
```

Check available navigation actions:

```bash
ros2 action list
```

The important actions are:

```text
/navigate_to_pose
/navigate_through_poses
```

Check the map:

```bash
ros2 topic echo /map --once
```

Check localization:

```bash
ros2 topic echo /amcl_pose --once
```

Check velocity commands:

```bash
ros2 topic echo /cmd_vel
```

Check the TF chain:

```bash
ros2 run tf2_ros tf2_echo map base_footprint
```

## Debugging and fixes during development

One issue encountered while starting the navigation stack was a parameter type error in the costmap configuration.

The local costmap `width` and `height` parameters were initially written as floating-point values:

```yaml
width: 3.000
height: 3.000
```

Nav2 expected these parameters as integers, so they were changed to:

```yaml
width: 3
height: 3
```

After this change, the controller server started correctly and the navigation lifecycle manager brought the required Nav2 servers to the active state.

The starter repository issues are documented separately in the root-level `BUG_FIXES.md`.

## Result

The final setup was tested in the Gazebo simulation.

The following parts were verified:

* Map Server loaded the supplied map.
* AMCL accepted an initial pose and published localization.
* The Nav2 planner generated paths.
* The controller generated velocity commands.
* Global and local costmaps were available.
* The navigation action server accepted goals.
* The robot moved in Gazebo.
* A `NavigateToPose` goal completed with `SUCCEEDED`.

The implementation keeps map loading, localization and navigation as separate launch files, while the individual Nav2 servers are started directly rather than using `nav2_bringup` as the main navigation launcher.

## Evidence

The final navigation setup was tested in Gazebo and RViz.

### Screenshots

* [RViz map and navigation setup](screenshots/01_rviz_map.png)
* [Navigation goal reached successfully](screenshots/02_goal_reached.png)
* [TF tree](screenshots/03_tf_tree.png)

### Demo Video

A complete navigation demonstration is included here:

`final_test_vedio.webm`

The demonstration shows the simulation, localization, navigation and successful goal completion.
# Bug Fixes

During the initial build and testing of the starter repository, I found two issues that were preventing the project from working correctly.

## 1. `ament_package` was not called correctly

**File:** `testbed_description/CMakeLists.txt`

### Problem

The file contained:

```cmake
ament_package
```

The CMake macro needs to be called with parentheses. Because of this, the package could not be configured correctly.

### Fix

Changed it to:

```cmake
ament_package()
```

### Check

After making the change, I rebuilt the workspace with:

```bash
colcon build --symlink-install
```

`testbed_description` then built successfully.

## 2. Incorrect map image path

**File:** `testbed_bringup/maps/testbed_world.yaml`

### Problem

The map configuration pointed to a file that was not present:

```yaml
image: wrong_path_testbed_world.pgm
```

The actual map image supplied with the repository is:

```text
testbed_world.pgm
```

### Fix

Changed the entry to:

```yaml
image: testbed_world.pgm
```

I also made sure that the `testbed_bringup` package installs its `maps` directory so the map is available from the installed package.

### Check

After the change, the Nav2 map server loaded the map successfully.

The map server reported:

```text
Read map ...: 405 X 400 map @ 0.05 m/cell
```

The `/map` topic was then available as a valid `nav_msgs/OccupancyGrid`.

## Navigation work

After fixing the starter code, I created the `testbed_navigation` package required by the assignment.

The navigation setup was built manually instead of using `nav2_bringup` as a single launch file. The package separates map loading, localization and navigation into individual launch files.

The implemented navigation components are:

* Map Server
* AMCL
* Planner Server
* Controller Server
* BT Navigator
* Behavior Server
* Waypoint Follower
* Global Costmap
* Local Costmap
* Lifecycle Managers

The complete stack was tested in Gazebo. A `NavigateToPose` goal was accepted and completed successfully, and the robot generated `/cmd_vel` commands and moved to the requested goal.

# Butler Bringup (`butler_bringup`)

### Autonomous Indoor Delivery Robot — ROS 2 & Nav2

A ROS 2–based autonomous service robot designed for structured indoor environments such as cafés, hotels, and hospitals. This package enables waypoint navigation, multi-stage delivery scenarios, and real-time command control using TurtleBot3 and the Nav2 stack.

---

## 📁 Project Structure

```
butler_bringup/
├── launch/
│   ├── butler_bringup.launch.py     # Full system launch
│   └── mapping.launch.py            # Cartographer mapping launch
├── butler_bringup/
│   ├── butler_delivery_node.py      # Core delivery state machine
│   ├── occupancy_grid_pub.py        # Occupancy grid publisher
│   └── spawn_entity.py              # Gazebo entity spawner
├── config/
│   ├── tb3_nav_params.yaml          # Nav2 parameters
│   ├── hotel_map.yaml               # Map metadata
│   ├── tb3_nav.rviz                 # RViz config for navigation
│   ├── mapping.rviz                 # RViz config for mapping
│   └── tb3_cartographer.lua         # Cartographer SLAM config
├── models/                          # Custom Gazebo models
├── world/                           # Gazebo world files
├── media/
│   ├── screenshots/
│   │   └── ui_dashboard.png
│   └── demos/
│       ├── test_case1.webm
│       ├── test_case2.webm
│       ├── test_case3_a.webm
│       ├── test_case3_b.webm
│       ├── test_case4.webm
│       ├── test_case5.webm
│       ├── test_case6.webm
│       └── test_case7.webm
├── test/
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- ROS 2 (Humble or later)
- Nav2 stack
- TurtleBot3 packages
- Gazebo simulator

### 1. Build the package

```bash
colcon build --packages-select butler_bringup
source install/setup.bash
```

> **Note:** The original package directory uses the name `butler_bringup`. Ensure it matches your workspace spelling.

### 2. Set the robot model

```bash
export TURTLEBOT3_MODEL=burger
```

### 3. Launch the full system

```bash
ros2 launch butler_bringup butler_bringup.launch.py
```

This starts Gazebo, Nav2, AMCL localization, and RViz in a single command.

---

## 🧠 Features

| Feature | Description |
|---|---|
| Autonomous navigation | Powered by Nav2 with AMCL localization on a static map |
| Waypoint-based delivery | Navigates between Home, Kitchen, and Tables 1–4 |
| Multi-stage delivery | Supports complex Home → Kitchen → Table sequences |
| Mid-task cancellation | Cancel navigation at any point via command topic |
| Dynamic waypoint calibration | Update waypoint coordinates at runtime |
| JSON command interface | Simple string-based command protocol over ROS 2 topics |
| Simulation-ready | Fully integrated with Gazebo and RViz |

---

## 🎮 Command Interface

Commands are published as JSON strings to the `/butler_command` topic.

### Publish a command

```bash
ros2 topic pub /butler_command std_msgs/String \
  "data: '{\"action\":\"goto\",\"waypoint\":\"kitchen\"}'"
```



### Supported actions

| Action | Description |
|---|---|
| `goto` | Navigate to a named waypoint |
| `cancel` | Cancel the currently active task |
| `calibrate` | Update the coordinate of a named waypoint |

### Example: Calibrate a waypoint

```bash
ros2 topic pub /butler_command std_msgs/String \
  "data: '{\"action\":\"calibrate\",\"waypoint\":\"table1\",\"x\":1.5,\"y\":-0.8}'"
```

---

## 📍 Waypoints

The following named waypoints are supported out of the box:

| Waypoint | Role |
|---|---|
| `home` | Robot idle/docking position |
| `kitchen` | Food or item pickup point |
| `table1` | Delivery destination — Table 1 |
| `table2` | Delivery destination — Table 2 |
| `table3` | Delivery destination — Table 3 |
| `table4` | Delivery destination — Table 4 |

> Waypoint coordinates are recorded from RViz using the `/initialpose` topic and stored in the delivery node config.

---

## 🖥️ UI Dashboard — Mission Control

The system includes a real-time web-based control dashboard for monitoring and managing robot operations.

### Features

- Live robot status display (idle / navigating / waiting / error)
- Per-table order management
- Full mission tracking (Home → Kitchen → Table)
- Emergency cancel button
- ROS bridge connection monitoring

### Dashboard Preview

![UI Dashboard](media/screenshots/ui.png)

### Prerequisites

- ROS2 WebBridge (for connecting the UI to the ROS 2 system)

### Running the UI

The user interface is packaged as a Debian (.deb) file generated using Tauri. This provides a native desktop application for the web-based dashboard.

1. Install the deb file:
   ```bash
   sudo dpkg -i butler-ui.deb
   ```

2. Launch the application from your desktop or run it via command line.

Ensure ROS2 WebBridge is running in your ROS 2 environment to enable communication between the UI and the robot system.

---

## 🎥 Demo Videos

All scenario demos are located in `media/demos/`. Open `.webm` files directly in a browser or VS Code preview.

| Test Case | Scenario | File |
|---|---|---|
| Test Case 1 | Basic single-table delivery flow | `media/demos/test_case1.webm` |
| Test Case 2 | Sequential multi-stop navigation | `media/demos/test_case2.webm` |
| Test Case 3A | Timeout handling at table | `media/demos/test_case3_a.webm` |
| Test Case 3B | Alternate timeout / retry path | `media/demos/test_case3_b.webm` |
| Test Case 4 | Cancel mid-navigation | `media/demos/test_case4.webm` |
| Test Case 5 | Multi-table delivery run | `media/demos/test_case5.webm` |
| Test Case 6 | Skip logic (no confirmation) | `media/demos/test_case6.webm` |
| Test Case 7 | Dynamic waypoint modification | `media/demos/test_case7.webm` |

---

## 🗺️ Mapping (Optional)

To generate a new map of your environment using Cartographer SLAM:

### 1. Launch the mapping stack

```bash
ros2 launch butler_bringup mapping.launch.py
```

### 2. Drive the robot to build the map

Teleoperate the robot around the environment until coverage is sufficient.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### 3. Save the map

```bash
ros2 run nav2_map_server map_saver_cli -f hotel_map
```

This saves `hotel_map.pgm` and `hotel_map.yaml` to your current directory. Copy them into `config/`.

---

## 🧪 Testing

```bash
colcon test --packages-select butler_bringup
colcon test-result --verbose
```

---

## 🤖 Real-World Deployment Notes

The package is designed to run on both simulation and a physical TurtleBot3.

- **Initial pose**: Set via `/initialpose` in RViz before starting any delivery task
- **Localization**: AMCL requires a pre-built static map (`hotel_map.pgm` + `hotel_map.yaml`)
- **Coordinate recording**: Waypoint coordinates are captured from RViz during calibration
- **Recovery behaviors**: Nav2 handles obstacle avoidance and navigation recovery automatically

### Real-world scenarios covered

- Delivery confirmation (robot waits at table for acknowledgement)
- Mid-task cancellation (safe stop and return to home)
- Navigation recovery (automatic replanning on blocked paths)

---

## 📌 Future Improvements

- [ ] Multi-robot fleet management and task allocation
- [ ] Voice assistant integration for order placement
- [ ] AI-based dynamic path optimization
- [ ] Full web-based dashboard with persistent order history
- [ ] Integration with POS or ordering systems

---

## 📚 References

- [ROS 2 Documentation](https://docs.ros.org/en/humble/)
- [Nav2 Stack](https://navigation.ros.org/)
- [TurtleBot3 Manual](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/)
- [Cartographer ROS](https://google-cartographer-ros.readthedocs.io/)
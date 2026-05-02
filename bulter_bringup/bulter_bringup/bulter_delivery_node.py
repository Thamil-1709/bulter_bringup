#!/usr/bin/env python3
"""
ButlerDeliveryNode
==================
All mission logic lives in the browser UI. This node only:
  - Receives navigation commands from the UI via rosbridge topics
  - Executes Nav2 goToPose for each command
  - Publishes real-time status back to the UI

Subscribed topics (UI → Node):
  /butler_command  (std_msgs/String)
      JSON payload: { "action": "goto", "waypoint": "kitchen" }
      JSON payload: { "action": "cancel" }
      JSON payload: { "action": "calibrate", "waypoint": "table1" }

Published topics (Node → UI):
  /butler_status   (std_msgs/String)
      Plain strings: "KITCHEN" | "TABLE" | "HOME" | "ARRIVED" | "FAILED" | "CANCELLED"
"""

import json
import rclpy
import time  # Added to handle loop timing without blocking
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from std_msgs.msg import String
from rclpy.executors import MultiThreadedExecutor

TABLE_NAMES = {'table1', 'table2', 'table3', 'table4'}

# Default waypoint coordinates
DEFAULT_COORDS = {
    'home':    (-3.9855, -3.5611),
    'kitchen': (-2.2671,  0.0210),
    'table1':  (-0.5259, -2.0090),
    'table2':  ( 4.4208, -1.9739),
    'table3':  ( 3.5527,  2.1479),
    'table4':  ( 4.1743,  2.7148),
}


class ButlerDeliveryNode(Node):
    def __init__(self):
        super().__init__('butler_delivery_node')

        self.navigator = BasicNavigator()
        self.navigator.waitUntilNav2Active()

        self.cancel_requested = False
        self._latest_amcl_pose: PoseStamped | None = None

        self.locations: dict[str, PoseStamped] = {
            name: self._make_pose(x, y) for name, (x, y) in DEFAULT_COORDS.items()
        }

        # UI → Node: navigation commands[cite: 5]
        self.create_subscription(String, '/butler_command', self._on_command, 10)

        # Node → UI: status updates[cite: 5]
        self.status_pub = self.create_publisher(String, '/butler_status', 10)

        # AMCL pose for calibration[cite: 5]
        self.create_subscription(
            PoseWithCovarianceStamped, '/amcl_pose', self._on_amcl_pose, 10
        )

        self._publish_initial_pose()
        self.get_logger().info("ButlerDeliveryNode ready — waiting for UI commands.")

    # ------------------------------------------------------------------
    # Pose helpers
    # ------------------------------------------------------------------

    def _make_pose(self, x: float, y: float) -> PoseStamped:
        p = PoseStamped()
        p.header.frame_id = 'map'
        p.pose.position.x = float(x)
        p.pose.position.y = float(y)
        p.pose.orientation.w = 1.0
        return p

    def _publish_initial_pose(self):
        pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.pose.pose = self.locations['home'].pose
        msg.pose.covariance[0] = msg.pose.covariance[7] = 0.25
        msg.pose.covariance[35] = 0.0685
        for _ in range(5):
            pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.1)

    def _on_amcl_pose(self, msg: PoseWithCovarianceStamped):
        ps = PoseStamped()
        ps.header = msg.header
        ps.pose = msg.pose.pose
        self._latest_amcl_pose = ps

    # ------------------------------------------------------------------
    # Status publisher
    # ------------------------------------------------------------------

    def _publish_status(self, status: str):
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)
        self.get_logger().info(f"[STATUS] {status}")

    # ------------------------------------------------------------------
    # Command handler — entry point for all UI messages
    # ------------------------------------------------------------------

    def _on_command(self, msg: String):
        try:
            cmd = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().error(f"Invalid JSON command: {msg.data}")
            return

        action = cmd.get('action', '')

        if action == 'goto':
            waypoint = cmd.get('waypoint', '').lower()
            if waypoint not in self.locations:
                self.get_logger().error(f"Unknown waypoint: '{waypoint}'")
                return
            self.cancel_requested = False
            self._navigate_to(waypoint)

        elif action == 'cancel':
            self.cancel_requested = True
            if not self.navigator.isTaskComplete():
                self.navigator.cancelTask()
            self._publish_status('CANCELLED')

        elif action == 'calibrate':
            waypoint = cmd.get('waypoint', '').lower()
            self._calibrate(waypoint)

        else:
            self.get_logger().warn(f"Unknown action: '{action}'")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _navigate_to(self, waypoint: str):
        if self.cancel_requested:
            self._publish_status('CANCELLED')
            return

        # Tell the UI which leg is starting[cite: 5]
        if waypoint in TABLE_NAMES:
            self._publish_status('TABLE')
        else:
            self._publish_status(waypoint.upper())

        pose = self.locations[waypoint]
        pose.header.stamp = self.navigator.get_clock().now().to_msg()

        self.get_logger().info(f">> Navigating to {waypoint}")
        self.navigator.goToPose(pose)

        # Monitor task completion without spin_once to avoid deadlock
        while not self.navigator.isTaskComplete():
            if self.cancel_requested:
                self.navigator.cancelTask()
                self._publish_status('CANCELLED')
                return
            # Use sleep to yield to the MultiThreadedExecutor
            time.sleep(0.1)

        if self.navigator.getResult() == TaskResult.SUCCEEDED:
            self.get_logger().info(f"✔ Reached {waypoint}")
            # ARRIVED tells the UI to show its confirmation modal / proceed[cite: 5]
            self._publish_status('ARRIVED')
        else:
            self.get_logger().error(f"Failed to reach {waypoint}")
            self._publish_status('FAILED')

    # ------------------------------------------------------------------
    # Calibration
    # ------------------------------------------------------------------

    def _calibrate(self, waypoint: str):
        if waypoint not in TABLE_NAMES:
            self.get_logger().error(f"Calibration only valid for tables, got: '{waypoint}'")
            return
        if self._latest_amcl_pose is None:
            self.get_logger().error("No AMCL pose available for calibration.")
            return
        self.locations[waypoint] = self._latest_amcl_pose
        self.get_logger().info(
            f"[CALIBRATION] '{waypoint}' → "
            f"({self._latest_amcl_pose.pose.position.x:.3f}, "
            f"{self._latest_amcl_pose.pose.position.y:.3f})"
        )
        self._publish_status(f'CALIBRATED:{waypoint}')


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main():
    rclpy.init()
    node = ButlerDeliveryNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
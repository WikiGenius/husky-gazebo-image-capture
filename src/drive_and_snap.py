#!/usr/bin/env python3
"""
DriveAndSnap ROS2 node
- Teleoperate Husky with keyboard (W/A/S/D/Q/E, SPACE to stop, ESC to quit)
- Press 'P' to capture synced image + odometry
- Saves images to HUSKY_SNAP_DIR or ~/husky_snaps/ and logs poses.csv
"""
import os
import sys
import csv
import threading

import rclpy
import cv2

from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge
from pynput import keyboard  # pip install pynput

# ────── configurable parameters ──────
LIN_VEL     = 0.5    # m/s forward/backward speed
ANG_VEL     = 1.0    # rad/s rotation speed
PUB_FREQ    = 10.0   # Hz for cmd_vel publishing
SNAP_KEY    = 'p'    # key to capture snapshot
SNAP_DIR    = os.path.expanduser(os.environ.get('HUSKY_SNAP_DIR', '~/husky_snaps'))
CSV_FIELDS  = ['timestamp','filename','x','y','z','qx','qy','qz','qw']


def twist(vx=0.0, wz=0.0):
    """Create a Twist message given linear and angular velocities."""
    t = Twist()
    t.linear.x  = vx
    t.angular.z = wz
    return t


class DriveAndSnap(Node):
    def __init__(self):
        super().__init__('drive_and_snap')

        # state
        self._bridge            = CvBridge()
        self._lock              = threading.Lock()
        self._last_image        = None
        self._last_image_stamp  = None
        self._last_odom         = None
        self._pressed_keys      = set()

        # prepare snapshot directory and CSV
        os.makedirs(SNAP_DIR, exist_ok=True)
        self._csv_path = os.path.join(SNAP_DIR, 'poses.csv')
        if not os.path.exists(self._csv_path):
            with open(self._csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_FIELDS)

        # publishers & subscribers
        self._cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(
            Image, '/camera/color/image_raw', self._on_image,
            qos_profile_sensor_data)
        self.create_subscription(
            Odometry, '/husky_velocity_controller/odom', self._on_odom,
            10)

        # timer to publish Twist
        self.create_timer(1.0 / PUB_FREQ, self._publish_twist)

        # keyboard listener thread
        listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release)
        listener.daemon = True
        listener.start()

        self.get_logger().info(
            f"Drive: WASD/QE, SPACE=stop, {SNAP_KEY.upper()}=snapshot, ESC=quit.")

    def _on_key_press(self, key):
        """Handle key press events for driving and snapshot."""
        # movement keys
        try:
            c = key.char.lower()
            if c in ('w','a','s','d','q','e',' '):
                self._pressed_keys.add(c)
            elif c == SNAP_KEY:
                self._save_snapshot()
        except AttributeError:
            if key == keyboard.Key.esc:
                self.get_logger().info('ESC pressed: shutting down')
                rclpy.shutdown()
                sys.exit(0)

    def _on_key_release(self, key):
        """Remove movement keys when released."""
        try:
            c = key.char.lower()
            self._pressed_keys.discard(c)
        except Exception:
            pass

    def _publish_twist(self):
        """Publish Twist based on current pressed keys."""
        vx, wz = 0.0, 0.0
        if 'w' in self._pressed_keys: vx += LIN_VEL
        if 's' in self._pressed_keys: vx -= LIN_VEL
        if 'a' in self._pressed_keys: wz += ANG_VEL
        if 'd' in self._pressed_keys: wz -= ANG_VEL
        if 'q' in self._pressed_keys: wz += ANG_VEL
        if 'e' in self._pressed_keys: wz -= ANG_VEL
        if ' ' in self._pressed_keys: vx, wz = 0.0, 0.0

        self._cmd_pub.publish(twist(vx, wz))

    def _on_image(self, msg: Image):
        """Callback for image topic: store last image and timestamp."""
        img = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        with self._lock:
            self._last_image       = img
            self._last_image_stamp = stamp

    def _on_odom(self, msg: Odometry):
        """Callback for odometry: store last odom message."""
        with self._lock:
            self._last_odom = msg

    def _save_snapshot(self):
        """Save current image and odometry to disk and CSV."""
        with self._lock:
            img   = self._last_image
            t     = self._last_image_stamp
            odom  = self._last_odom

        if img is None or odom is None:
            self.get_logger().warn('No image or odom available.')
            return

        # prepare file paths
        basename = f"{int(t*1000)}"
        img_path = os.path.join(SNAP_DIR, f"{basename}.png")

        # write image
        cv2.imwrite(img_path, img)

        # extract pose
        p = odom.pose.pose.position
        o = odom.pose.pose.orientation
        row = [f"{t:.3f}", f"{basename}.png",
               f"{p.x:.6f}", f"{p.y:.6f}", f"{p.z:.6f}",
               f"{o.x:.6f}", f"{o.y:.6f}",
               f"{o.z:.6f}", f"{o.w:.6f}"]

        # append to CSV
        with open(self._csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        self.get_logger().info(f"Saved snapshot {basename}.png")


def main():
    rclpy.init()
    node = DriveAndSnap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

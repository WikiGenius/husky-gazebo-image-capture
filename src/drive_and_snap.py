#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from pynput import keyboard  # pip install pynput

# ────── tunable parameters ──────
LIN_VEL = 0.5   # forward/backward speed (m/s)
ANG_VEL = 1.0   # rotation speed (rad/s)
PUB_FREQ = 10.0  # Hz

class DriveAndSnap(Node):
    def __init__(self):
        super().__init__('drive_and_snap')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pressed = set()

        # start timer to publish at PUB_FREQ
        self.create_timer(1.0 / PUB_FREQ, self._publish_twist)

        # start keyboard listener thread
        listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        listener.daemon = True
        listener.start()

        self.get_logger().info(
            "Controls: W/S forward/back, A/D turn left/right, "
            "Q/E extra rotate, SPACE stop, ESC quit"
        )

    # ────── keyboard callbacks ──────
    def _on_press(self, key):
        # add recognized chars to the set
        try:
            c = key.char.lower()
            if c in ('w','a','s','d','q','e',' '):
                self.pressed.add(c)
        except AttributeError:
            if key == keyboard.Key.esc:
                self.get_logger().info('ESC pressed, shutting down.')
                rclpy.shutdown()
                sys.exit(0)

    def _on_release(self, key):
        # remove when key is let go
        try:
            c = key.char.lower()
            if c in self.pressed:
                self.pressed.remove(c)
        except Exception:
            pass

    # ────── publish Twist based on keys held ──────
    def _publish_twist(self):
        vx = 0.0
        wz = 0.0

        # forward/back
        if 'w' in self.pressed:
            vx += LIN_VEL
        if 's' in self.pressed:
            vx -= LIN_VEL

        # primary turning
        if 'a' in self.pressed:
            wz += ANG_VEL
        if 'd' in self.pressed:
            wz -= ANG_VEL

        # extra rotate
        if 'q' in self.pressed:
            wz += ANG_VEL
        if 'e' in self.pressed:
            wz -= ANG_VEL

        # full stop
        if ' ' in self.pressed:
            vx = 0.0
            wz = 0.0

        t = Twist()
        t.linear.x = vx
        t.angular.z = wz
        self.pub.publish(t)

def main():
    rclpy.init()
    node = DriveAndSnap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

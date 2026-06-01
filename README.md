# ORB-SLAM Demo

## Overview
This repository is a ROS 2 Humble scaffold for ORB-SLAM-style visual state-estimation experiments. It is kept public as supporting evidence for the state-estimation side of a robotics research portfolio focused on mobile manipulation, active perception, and structure-aware scanning.

The repository is intentionally lightweight and public-safe. It should be used as a place to document reproducible SLAM demo workflows without exposing unpublished research code or private datasets.

## Research/Engineering Motivation
Active scanning and mobile manipulation depend on reliable robot and camera state estimates. Visual SLAM methods such as ORB-SLAM connect camera motion, feature tracking, map structure, and localization quality.

This demo supports the broader research direction by providing a public ROS 2 place to experiment with visual state estimation and its relationship to scan planning.

## Features
- ROS 2 Humble package scaffold.
- Python/ROS 2 dependencies for geometry messages and state-estimation demos.
- Public structure for future launch files, datasets, and demo notes.
- Intended integration point for visual SLAM experiments.

## Method
The planned workflow is:

1. Provide an image/video or camera stream.
2. Run a visual SLAM or pose-estimation node.
3. Publish or record pose estimates.
4. Compare estimated motion with expected robot/camera motion.
5. Document failure cases, uncertainty, and sensing constraints.

## Installation
Create or enter a ROS 2 workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/WikiGenius/orb_slam_demo.git
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select orb_slam_demo
source install/setup.bash
```

## Run
Planned run pattern after demo nodes/launch files are added:

```bash
ros2 launch orb_slam_demo demo.launch.py
```

Until then, use this repository as a public scaffold for ROS 2 visual-SLAM experiments.

## Results
Future public results can include:

- camera trajectory plots,
- RViz screenshots,
- pose-estimation logs,
- notes on tracking failures and viewpoint constraints.

## Limitations
- This is currently a scaffold, not a complete ORB-SLAM release.
- Private datasets and unpublished experiments are intentionally omitted.
- SLAM backend integration still needs to be documented.

## Roadmap
- [ ] Add launch workflow.
- [ ] Add minimal camera-stream example.
- [ ] Add trajectory visualization.
- [ ] Add notes on SLAM failure modes under scanning constraints.

## Citation / Acknowledgment
Acknowledge ORB-SLAM, ROS 2, and any visual-SLAM libraries or datasets used when implementation details are added.

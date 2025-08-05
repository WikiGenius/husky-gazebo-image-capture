cmake_minimum_required(VERSION 3.8)
project(orb_slam_demo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)

# Install Python executables ---------------------------------
install(
  PROGRAMS
    src/drive_and_snap.py          # ← add this line
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

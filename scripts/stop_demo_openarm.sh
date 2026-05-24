#!/bin/bash
# OpenArm 데모 잔존 process + ros_gz / openarm controller / robot_state_publisher 정리.
set -u

PATTERNS=(
    'ros2 launch openarm_motion_pack'
    'openarm_demo.launch.py'
    'robot_state_publisher'
    'controller_manager'
    'openarm_hardware_interface'
    'gz_ros2_control'
    'omx_reactor_node'
    'omx_dashboard_node'
    'gesture_detector_node'
    'geva_node'
    'rapport_tracker'
    'v4l2_camera_node'
    'rviz2'
    'gz sim'
    'gzserver'
    'gzclient'
    'ros_gz_bridge'
    'ros_gz_image'
    'spawner_'
)

# Stage 1 — graceful SIGINT
for pat in "${PATTERNS[@]}"; do
    pkill -INT -f "$pat" 2>/dev/null || true
done
sleep 2

# Stage 2 — SIGTERM
for pat in "${PATTERNS[@]}"; do
    pkill -TERM -f "$pat" 2>/dev/null || true
done
sleep 1

# Stage 3 — SIGKILL
for pat in "${PATTERNS[@]}"; do
    pkill -KILL -f "$pat" 2>/dev/null || true
done

# Stage 4 — 카메라 device handle release (v4l2 lock)
if command -v fuser >/dev/null 2>&1; then
    fuser -k -9 /dev/video* 2>/dev/null || \
        sudo -n fuser -k -9 /dev/video* 2>/dev/null || true
fi

echo '[stop_demo_openarm] 청소 완료'

#!/bin/bash
# 잔존 데모 프로세스 청소. 멱등 (no-op safe).

PATTERNS=(
    'ros2 launch omx_reactor'
    'geva_node'
    'rapport_tracker'
    'omx_reactor_node'
    'omx_dashboard_node'
    'reactor_node'
    'dashboard_node'
    'v4l2_camera_node'
    'camera_file_pub'
    'gz sim'
    'gzserver'
    'gzclient'
    'open_manipulator_bringup'
    'controller_manager'
    'spawner.*arm_controller'
)

for pat in "${PATTERNS[@]}"; do
    pkill -f "$pat" 2>/dev/null || true
done

sleep 2

for pat in "${PATTERNS[@]}"; do
    pkill -9 -f "$pat" 2>/dev/null || true
done

echo "[stop_demo] 청소 완료"

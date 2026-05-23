#!/bin/bash
# OpenArm 데모 잔존 process + ros_gz / openarm controller 정리.
set -u

# Stage 1 — graceful SIGINT
for pat in 'openarm_demo.launch.py' 'controller_manager' 'openarm_hardware_interface' \
           'omx_reactor_node' 'omx_dashboard_node' 'gesture_detector_node' \
           'geva_node' 'rapport_tracker_node' 'rviz2' 'ros_gz_bridge' 'ros_gz_image'; do
    pkill -INT -f "$pat" 2>/dev/null || true
done
sleep 2

# Stage 2 — SIGTERM
for pat in 'openarm_demo.launch.py' 'controller_manager' 'openarm_hardware_interface' \
           'omx_reactor_node' 'omx_dashboard_node' 'gesture_detector_node' \
           'geva_node' 'rapport_tracker_node' 'rviz2' 'ros_gz_bridge' 'ros_gz_image'; do
    pkill -TERM -f "$pat" 2>/dev/null || true
done
sleep 1

# Stage 3 — SIGKILL
for pat in 'openarm_demo.launch.py' 'controller_manager' 'openarm_hardware_interface' \
           'omx_reactor_node' 'omx_dashboard_node' 'gesture_detector_node' \
           'geva_node' 'rapport_tracker_node' 'rviz2'; do
    pkill -KILL -f "$pat" 2>/dev/null || true
done

# Stage 4 — 카메라 device handle release (v4l2 lock)
if command -v fuser >/dev/null 2>&1; then
    fuser -k -9 /dev/video* 2>/dev/null || \
        sudo -n fuser -k -9 /dev/video* 2>/dev/null || true
fi

echo '[stop_demo_openarm] 청소 완료'

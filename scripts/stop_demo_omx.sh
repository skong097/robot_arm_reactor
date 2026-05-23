#!/bin/bash
# 잔존 데모 프로세스 청소. 멱등 (no-op safe).
#
# 종료 단계:
#   1. SIGINT to ros2 launch (graceful — child 들 cleanup)
#   2. SIGTERM by pattern
#   3. SIGKILL by pattern
#   4. fuser -k 로 카메라 device handle release (sudo 필요 가능)

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

# Stage 1: graceful SIGINT to ros2 launch process group (child SIGINT propagation)
for pid in $(pgrep -f "ros2 launch omx_reactor" 2>/dev/null); do
    pgid=$(ps -o pgid= "$pid" 2>/dev/null | tr -d ' ')
    [ -n "$pgid" ] && kill -INT "-$pgid" 2>/dev/null || true
done
sleep 4

# Stage 2: SIGTERM by pattern
for pat in "${PATTERNS[@]}"; do
    pkill -f "$pat" 2>/dev/null || true
done
sleep 2

# Stage 3: SIGKILL fallback
for pat in "${PATTERNS[@]}"; do
    pkill -9 -f "$pat" 2>/dev/null || true
done

# Stage 4: 카메라 device handle release — SIGKILL 후 mmap 안 풀림 보호.
# 일반 fuser 가 mmap region kernel handle 못 풀 때 sudo fallback (NOPASSWD 설정 시).
for dev in /dev/video0 /dev/video1 /dev/video2 /dev/video3; do
    [ -e "$dev" ] || continue
    fuser -k -9 "$dev" 2>/dev/null \
        || sudo -n fuser -k -9 "$dev" 2>/dev/null \
        || true
done

echo "[stop_demo] 청소 완료"

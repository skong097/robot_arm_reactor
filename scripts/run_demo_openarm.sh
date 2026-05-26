#!/bin/bash
# OpenArm v10 bimanual fake_hw 데모. Ctrl+C 한 번에 자식 다 종료.
# 옵션:
#   --camera=v4l2|file|external          (default v4l2 — Gazebo 카메라는 OpenArm 미지원)
#   --file-path=/abs/path/to/clip.mp4
#   --video-device=/dev/videoN           (camera=v4l2 인 경우, default /dev/video0)
#   --no-browser
set -u

# 동일 LAN 의 doby_controller (ROS_DOMAIN_ID=22 기본) 그래프와 격리 — /emotion/state 등 토픽 충돌 방지
export ROS_DOMAIN_ID=99
export ROS_LOCALHOST_ONLY=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="$(cd "$SCRIPT_DIR/.." && pwd)"

CAMERA=v4l2
FILE_PATH=""
VIDEO_DEVICE=""
BROWSER=1
for arg in "$@"; do
    case "$arg" in
        --camera=*)         CAMERA="${arg#*=}" ;;
        --file-path=*)      FILE_PATH="${arg#*=}" ;;
        --video-device=*)   VIDEO_DEVICE="${arg#*=}" ;;
        --no-browser)       BROWSER=0 ;;
        -h|--help)          sed -n '2,/^$/p' "$0" | sed 's/^# *//' ; exit 0 ;;
        *) echo "알 수 없는 옵션: $arg" >&2; exit 1 ;;
    esac
done

if [ ! -f "$WS/install/setup.bash" ]; then
    echo "★ install/setup.bash 없음 — 먼저 'colcon build'" >&2; exit 1
fi
if [ ! -f "$HOME/openarm_ros2_ws/install/setup.bash" ]; then
    echo "★ ~/openarm_ros2_ws/install/setup.bash 없음 — 먼저 OpenArm workspace 빌드" >&2; exit 1
fi

set +u
source /opt/ros/jazzy/setup.bash
source "$WS/install/setup.bash"
source "$HOME/openarm_ros2_ws/install/setup.bash"
set -u

bash "$SCRIPT_DIR/stop_demo_openarm.sh" >/dev/null 2>&1 || true

if [ "$BROWSER" = 1 ]; then
    ( sleep 3 && xdg-open http://localhost:7700/ >/dev/null 2>&1 ) &
fi

LAUNCH_ARGS="camera:=$CAMERA"
[ -n "$FILE_PATH" ] && LAUNCH_ARGS="$LAUNCH_ARGS file_path:=$FILE_PATH"
[ -n "$VIDEO_DEVICE" ] && LAUNCH_ARGS="$LAUNCH_ARGS video_device:=$VIDEO_DEVICE"

exec ros2 launch openarm_motion_pack openarm_demo.launch.py $LAUNCH_ARGS

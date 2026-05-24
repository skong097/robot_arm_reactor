# Robot Arm Reactor

카메라 앞 사람의 **감정/제스처에 로봇 팔이 실시간 표현 모션으로 반응**하는 데모. 두 robot arm 플랫폼 지원 — **OpenManipulator-X (4-DOF, Gazebo)** + **OpenArm v10 bimanual (16 DOF, RViz fake_hw)**. 같은 reactor / 같은 dashboard 위에서 motion pack 만 다르게 작동 (arm-agnostic 시스템).

```
[웹캠] -> mediapipe (face V·A / hand gesture)
       -> rapport EMA + 감정 분면 + gesture event
       -> motion mapper (priority + cooldown + 큐 깊이 1 scheduler)
       -> arm 컨트롤러 (FollowJointTrajectory + GripperCommand) — atomic 양손 dispatch
       -> FastAPI + WebSocket -> 단일 페이지 대시보드
              ├─ OMX 데모: Gazebo MJPEG view
              └─ OpenArm 데모: three.js + urdf-loader (양손 실시간 URDF)
```

## 한 줄 요약

```
얼굴 표정 (V·A 4분면) + 손 제스처 (mediapipe Gesture Recognizer 7종 + thumb-index distance)
   -> 18 표현 모션 (per arm — OMX 단일 4-DOF / OpenArm 양손 16 DOF atomic)
```

## 지원 arm

| Arm | DOF | Controller | View 모드 |
|---|---|---|---|
| **OpenManipulator-X (OMX)** | 4 + 1 그리퍼 (단일 arm) | `/arm_controller/follow_joint_trajectory` + `/gripper_controller/gripper_cmd` | Gazebo MJPEG (외부 카메라) |
| **OpenArm v10 bimanual** | 7×2 + 1×2 그리퍼 (양손, 16 DOF) | `/{left,right}_joint_trajectory_controller/follow_joint_trajectory` + `/{left,right}_gripper_controller/gripper_cmd` (4 action) | three.js URDF (양손 실시간) |

## 모션 라이브러리 (각 arm 18종)

같은 trigger set (gesture event), arm 별 motion pack 의 motion ID 와 trajectory 가 다름. OpenArm 은 양손 특화 motion 4 (BIMANUAL_CLAP / HUG / GRIP_CLAP, ASYMMETRIC_POINT) 가 OMX 의 CHEER/HEART/POINT_BACK/GRIPPER_CLOSE 자리에 대체.

| Trigger | OMX motion | OpenArm motion |
|---|---|---|
| Q1 (V+ A+) | DANCE | DANCE (양손 sym swing) |
| Q2 (V- A+) | FREEZE | FREEZE |
| Q3 (V- A-) | CONSOLE | CONSOLE |
| Q4 / deadband | IDLE | IDLE |
| new_track | HELLO | HELLO (양손 sym wave) |
| track_gone | BYE | BYE |
| hand_visible | HAND_OUT | HAND_OUT (양손 reach) |
| twinkle | TWINKLE | TWINKLE |
| hands_up | HANDS_UP | HANDS_UP (양손 만세) |
| hands_up_wave | HANDS_UP_WAVE | HANDS_UP_WAVE |
| pointing_up | POINT_BACK | **ASYMMETRIC_POINT** (왼손 reach + 오른손 idle) |
| thumb_up | NOD | NOD |
| thumb_down | SAD | SAD |
| victory | CHEER | **BIMANUAL_CLAP** |
| ilove_you | HEART | **BIMANUAL_HUG** |
| closed_fist | STRONG | STRONG |
| gripper_open | GRIPPER_OPEN | GRIPPER_OPEN (양 그리퍼 동시) |
| gripper_close | GRIPPER_CLOSE | **BIMANUAL_GRIP_CLAP** (양 그리퍼 close + 양손 박수 — 4 dispatch atomic) |

새 motion 추가 = 해당 arm 의 motion pack 의 `motions.py` 의 `MOTIONS` 리스트에 한 항목 + `trajectories.py` 에 trajectory factory 1개 (반환: `list[Dispatch]`). `arm_reactor_core` 의 mapper/scheduler/sender 0 수정 (plug-in 구조).

새 arm 지원 = 새 motion pack 패키지 추가 (예: `arm_X_motion_pack`) + 같은 reactor 가 ROS param `motion_pack_module:='arm_X_motion_pack'` 으로 동적 import.

## Architecture

```
                                arm_reactor_core
                       (arm 무관 — reactor / scheduler / dashboard / sender / gesture)
                                       │
                  ┌────────────────────┼────────────────────┐
                  ▼                    ▼                    ▼
            reactor_node       dashboard_node        gesture_detector_node
            ├─ ROS param            ├─ FastAPI                ↑
            │  motion_pack_module    │  /ws/v1/engaging       │
            │  (importlib 동적)     │  /ws/joint_states (urdf)│
            │                       │  /ws/stream             │
            ├─ Motion list[Dispatch]│  /api/openarm/urdf      │
            ├─ TrajectorySender     │  /api/meshes/{pkg}/{*}  │
            ├─ GripperSender        │  /api/gazebo_view.mjpg  │
            └─ DoneCounter          └─ /api/config            │
                  │                                            │
                  ▼                                            │
            ┌─────┴──────────┐                          /webcam/image_raw
            ▼                ▼                                ▲
   omx_motion_pack    openarm_motion_pack                    │
   ├─ 18 motion       ├─ 18 motion (양손)              v4l2_camera
   ├─ trajectories    ├─ trajectories (LEFT/RIGHT)
   ├─ launch:         ├─ launch:
   │  omx_demo +      │  openarm_demo +
   │  omx_gazebo      │  openarm.bimanual
   └─ models/         └─ (OpenArm bringup
      external_cam       의 mesh 재사용)
            ▼                ▼
   OMX Gazebo simulation  OpenArm RViz + mock_components
```

3 ROS 2 패키지:
- **`arm_reactor_core`** (arm-agnostic) — `reactor_node`, `dashboard_node`, `gesture_detector_node`, `Motion` / `Dispatch` dataclass, `TrajectorySender` + `GripperSender`, `motion_mapper`, `motion_scheduler`, `session_tracker`, `context`, 대시보드 web/static + vendor (three.js + urdf-loader)
- **`omx_motion_pack`** — OMX 18 motion + trajectory + Gazebo launch
- **`openarm_motion_pack`** — OpenArm bimanual 18 motion + trajectory + launch

## Prerequisites

| 종류 | 항목 | 비고 |
|---|---|---|
| OS | Ubuntu 24.04 | |
| ROS | ROS 2 Jazzy | desktop 권장 |
| ROBOTIS (OMX 만) | open_manipulator stack | apt 또는 source 빌드 |
| Enactic (OpenArm 만) | openarm ROS 2 stack | `~/openarm_ros2_ws/` 빌드 |
| Python | mediapipe 0.10.14, fastapi, uvicorn, websockets | `requirements.txt` |
| 시스템 | numpy 1.26.4, opencv 4.6.0, cv_bridge, v4l2_camera | mediapipe 가 user site 에 numpy 2.x / opencv-* 끌어옴, **cleanup 필수** |
| 하드웨어 | USB 웹캠 (`/dev/video0`) | gesture 인식 |
| 브라우저 | OpenGL/WebGL 호환 | three.js URDF 뷰 (OpenArm 데모) |

### 외부 부트스트랩 (한 번)

#### 1. ROBOTIS world SDF 의 Sensors plugin 추가 (OMX 의 Gazebo 가상 카메라 작동 필수)

`open_manipulator_bringup/worlds/empty_world.sdf` 의 plugin 블록에 한 줄:
```xml
<plugin name='gz::sim::systems::Sensors' filename='gz-sim-sensors-system'>
  <render_engine>ogre2</render_engine>
</plugin>
```
ROBOTIS default world 에 Sensors plugin 빠져 있어 OMX MJPEG view 가 작동 안 함.

#### 2. OpenArm workspace 빌드 (OpenArm 데모만 필요)

```bash
cd ~/openarm_ros2_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

#### 3. mediapipe 모델 다운로드

`src/vendored/README.md` 의 외부 모델 부트스트랩 절차 참고 (face_landmarker / efficientdet_lite0 / gesture_recognizer / hand_landmarker — 총 4 파일, ~23MB).

#### 4. three.js + urdf-loader vendor (OpenArm dashboard URDF 뷰)

`src/arm_reactor_core/arm_reactor_core/web/static/vendor/README.md` 의 부트스트랩 — 5 파일 wget (three.js r140 UMD + STL/Collada/OrbitControls + URDFLoader). 약 750 KB.

## Installation

```bash
git clone https://github.com/skong097/robot_arm_reactor.git ~/robot_arm_reactor
cd ~/robot_arm_reactor

# Python deps + opencv/numpy cleanup
pip install --user -r requirements.txt
pip uninstall --yes numpy opencv-python opencv-python-headless opencv-contrib-python
python3 -c "import numpy, cv2; print(numpy.__version__, cv2.__version__)"   # 1.26.4 / 4.6.0

# 모델 부트스트랩 — src/vendored/README.md 참고
# vendor JS 부트스트랩 — src/arm_reactor_core/arm_reactor_core/web/static/vendor/README.md 참고

# 빌드
source /opt/ros/jazzy/setup.bash
source ~/robot_arm/install/setup.bash         # OMX 용 (apt 의 ros-jazzy-open-manipulator-* 대체 가능)
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
# OMX 데모 (Gazebo, 4-DOF 단일 arm)
bash scripts/run_demo_omx.sh                  # default: v4l2 카메라
bash scripts/run_demo_omx.sh --camera=file --file-path=samples/x.mp4
bash scripts/run_demo.sh                       # ← 별칭 (backward compat — run_demo_omx.sh 와 같음)

# OpenArm bimanual 데모 (RViz fake_hw, 양손 16 DOF)
bash scripts/run_demo_openarm.sh

# 종료 (해당 터미널 Ctrl+C — 잔존 청소 + 카메라 device release)
bash scripts/stop_demo_omx.sh
bash scripts/stop_demo_openarm.sh
bash scripts/stop_demo.sh                      # ← 별칭
```

대시보드: <http://localhost:8800/> (양 데모 같은 URL, arm 별 우측 패널 모드 자동 분기)

## Demo Scenarios

### 감정 인식 (양 arm 공통)
| 표정 | 분면 | OMX 모션 | OpenArm 모션 |
|---|---|---|---|
| 미소 | Q1 (V+ A+) | DANCE — base swing | DANCE — 양손 sym swing |
| 무표정 | deadband | IDLE | IDLE (양손 zero) |
| 슬픈 | Q3 (V- A-) | CONSOLE | CONSOLE — 양손 부드러운 wave |
| 화난 | Q2 (V- A+) | FREEZE | FREEZE — 양손 살짝 down |

### 세션 인사
- 카메라 앞 새 등장 -> HELLO (OMX joint4 wave / OpenArm 양손 sym wave)
- 3 초 자리 비움 -> BYE (위 슬로우)

### 손 제스처 (mediapipe Gesture Recognizer + Open_Palm 자세 분기) — 18 trigger
위 "모션 라이브러리" 표 참조. 같은 gesture, arm 별 다른 표현 모션.

### 대시보드 (1x2 반응형)
- **왼쪽** — 감정 분석 (V·A 좌표 + circumplex SVG 4분면 + EMA 시계열 그래프 + rapport 카운터)
- **오른쪽** — arm view (**`arm_view_mode` ROS param 으로 자동 분기**)
  - OMX → Gazebo MJPEG view + zoom slider 0.5x ~ 3.0x
  - OpenArm → three.js URDF (양손 실시간, OrbitControls 마우스 drag)
  - 공통 — 실시간 모션 이벤트 list 15개
- **반응형** — 폭 < 768px 시 1 column 으로 wrap

## Project Structure

```
robot_arm_reactor/
├── README.md
├── requirements.txt
├── LICENSE                                # Apache-2.0
├── scripts/
│   ├── run_demo_omx.sh + stop_demo_omx.sh
│   ├── run_demo_openarm.sh + stop_demo_openarm.sh
│   └── run_demo.sh + stop_demo.sh         # ← *_omx.sh 별칭 (backward compat)
└── src/
    ├── arm_reactor_core/                  # arm-agnostic core (3 entry_point + 대시보드)
    │   ├── arm_reactor_core/
    │   │   ├── context.py / motion.py / dispatch.py
    │   │   ├── motion_mapper.py / motion_scheduler.py
    │   │   ├── session_tracker.py / gesture_detection.py
    │   │   ├── trajectory_sender.py (FollowJointTrajectory)
    │   │   ├── gripper_sender.py (GripperCommand — sub-spec b)
    │   │   ├── reactor_node.py (motion_pack_module ROS param + importlib 동적)
    │   │   ├── dashboard_node.py (FastAPI + 6 endpoint + 3 WS)
    │   │   ├── gesture_detector_node.py (mediapipe)
    │   │   └── web/static/
    │   │       ├── index.html + app.js + components.css + ...
    │   │       ├── urdf_view.js (three.js + urdf-loader)
    │   │       └── vendor/   ← three.min.js + 3 loader + URDFLoader
    │   ├── launch/common.launch.py (arm 무관 노드 묶음)
    │   ├── models/gesture/   ← mediapipe .task (gitignored)
    │   └── test/  ← 52 단위 테스트
    │
    ├── omx_motion_pack/                   # OMX (4-DOF) motion pack
    │   ├── omx_motion_pack/
    │   │   ├── trajectories.py  (18 factory + ARM_ACT/GRIPPER_ACT 상수)
    │   │   └── motions.py       (18 MOTIONS)
    │   ├── launch/
    │   │   ├── omx_demo.launch.py    (common + omx_gazebo include)
    │   │   ├── omx_gazebo.launch.py
    │   │   └── camera_v4l2/file/external/gazebo.launch.py
    │   ├── models/external_cam/      (Gazebo 외부 카메라 SDF)
    │   └── test/  ← 101 단위 테스트
    │
    ├── openarm_motion_pack/               # OpenArm bimanual motion pack
    │   ├── openarm_motion_pack/
    │   │   ├── trajectories.py  (18 factory, LEFT/RIGHT × ARM/GRIP 4 controller 상수)
    │   │   └── motions.py       (18 MOTIONS — 4 양손 특화 대체)
    │   ├── launch/openarm_demo.launch.py  (common + openarm.bimanual include)
    │   └── test/  ← 125 단위 테스트 (safe range 90% + velocity ≤ 2.5 rad/s)
    │
    ├── omx_reactor/                       # 옛 단일 패키지 shim (외부 import 호환만)
    │
    └── vendored/                          # cafe NPC funnel BT 발췌 (0 modification)
        ├── README.md
        ├── dobi_npc_msgs/
        └── dobi_npc_emotion/              # geva_node + rapport_tracker
```

## Development

### 단위 테스트 (278 tests, pure logic 우선 TDD)

```bash
cd src/arm_reactor_core   && python3 -m pytest test/ -v   # 52
cd src/omx_motion_pack    && python3 -m pytest test/ -v   # 101
cd src/openarm_motion_pack && python3 -m pytest test/ -v  # 125
```

| 모듈 | 테스트 수 | 검증 |
|---|---:|---|
| arm_reactor_core: motion_mapper | 9 | priority 내림차순 + trigger 매치 |
| arm_reactor_core: motion_scheduler | 10 | cooldown / interrupt / 큐 depth 1 |
| arm_reactor_core: session_tracker | 8 | new_track / track_gone / grace |
| arm_reactor_core: dispatch | 4 | frozen / kind literal / equality |
| arm_reactor_core: gesture_detection | 21 | visibility cooldown / classify / wave |
| omx_motion_pack: trajectories | 101 | joint name / 시간 단조 / ±1.2rad 안전 / velocity ≤2.5rad/s / Dispatch action+kind |
| openarm_motion_pack: trajectories | 125 | 위 + OpenArm safe range 90% + 4 controller action_name + gripper position 0~0.043 |

## Roadmap / Status

### Phase 1 — UI + 데이터 통합 (완료)
- doby_controller 의 모객 분석 UI carry-over (V·A circumplex + EMA 시계열 그래프 + rapport counters)
- 1x2 반응형 대시보드
- OMX Gazebo MJPEG view 임베드 + zoom slider
- 모션 이벤트 실시간 list

### Phase 1.5 — 제스처 mimic (완료)
- mediapipe Gesture Recognizer 통합
- 10 제스처 mimic 모션
- thumb-index distance 기반 그리퍼 제어

### Phase 2 — Arm-agnostic 통합 (완료)
- **sub-spec (a)** — Motion `list[Dispatch]` + `TrajectorySender` + `GripperSender` + atomic 양손 dispatch + DoneCounter
- **sub-spec (b)** — `openarm_motion_pack` 18 motion (양손) + script 이원화 + `gesture_detector_node` 이주 + `motion_pack_module` ROS param + `wait_for_server(2s)` fallback
- **sub-spec (c)** — dashboard 우측 패널 dual-mode (`arm_view_mode='mjpeg'|'urdf'`) + 4 신규 endpoint + three.js + urdf-loader vendored static + z-up→y-up rotation fix

### Phase 3 — Customer ReID + 영속 기록 (보류)
- 얼굴 ReID 로 영속 customer_id 부여 (insightface ArcFace)
- customer 별 EMA 누적 + reaction_history
- MySQL 적재 + 30 일 retention purge

## Acknowledgments

본 데모의 감정 인식 파이프라인 (`geva_node`, `rapport_tracker`) + 모객 분석 대시보드 컴포넌트 (engaging-analytics.js + V·A circumplex SVG + engagement-timeline) 는 별 프로젝트인 cafe NPC funnel BT (PinkLAB internal `doby_controller`) 에서 발췌 — `src/vendored/` 디렉토리, 0 수정 카피, 출처는 `src/vendored/README.md` 참조.

- OMX URDF + 컨트롤러 + Gazebo bringup — [ROBOTIS open_manipulator](https://github.com/ROBOTIS-GIT/open_manipulator)
- OpenArm v10 URDF + bringup + bimanual moveit_config — [Enactic openarm_ros2](https://github.com/enactic/openarm_ros2)
- three.js (MIT) + urdf-loader (Apache-2.0) — dashboard URDF 뷰 (vendored UMD)
- mediapipe (Apache-2.0) — face landmarker + gesture recognizer

## License

Apache-2.0

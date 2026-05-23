# OMX Reactor

> 카메라 앞 사람의 감정 (V·A 4분면) 에 OpenManipulator-X 가 Gazebo 시뮬에서 실시간 표현 모션으로 반응하는 데모.
>
> P0 = 6 모션 (DANCE / FREEZE / CONSOLE / IDLE + HELLO / BYE).
> P1+ 자리 마련 = 동작 (gesture), 자세 (pose).

## 한 줄 요약

EMA-smoothed Valence·Arousal 좌표 → 4분면 매핑 → OMX 표현 모션 + 세션 경계 인사. 단일 터미널 launch, 단일 페이지 웹 대시보드.

## 데모 시연 (1분 시나리오)

| T+ | 입력 | 기대 출력 |
|---|---|---|
| 00s | launch + 카메라 앞 앉음 | — |
| 02s | (새 track 등장) | HELLO — 손 흔듦 |
| 05s | 미소 (Q1) | DANCE — base swing |
| 15s | 무표정 (deadband) | IDLE |
| 20s | 슬픈 표정 (Q3) | CONSOLE — 쓰담쓰담 |
| 30s | 화난 표정 (Q2) | FREEZE — 자세 down |
| 40s | 자리 비움 (3s grace 후) | BYE |

## 빌드 / 실행 / 종료

```bash
# 사전 — ROS Jazzy + ROBOTIS open_manipulator + Python 의존성
sudo apt install ros-jazzy-open-manipulator-*  # 또는 ~/robot_arm/ 에 source 빌드
pip install --user -r requirements.txt
# ⚠ mediapipe 가 numpy 2.x / opencv-* 를 user site 에 끌어와 ROS 의 numpy 1.26.4 / cv2 4.6.0 충돌 가능. cleanup:
pip uninstall --yes numpy opencv-python opencv-python-headless opencv-contrib-python
python3 -c "import numpy, cv2; print(numpy.__version__, cv2.__version__)"   # 1.26.4 / 4.6.0 재확인

# 빌드
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash

# 데모 (단일 터미널 — Ctrl+C 한 번에 자식 다 종료)
bash scripts/run_demo.sh                            # default: v4l2 카메라
bash scripts/run_demo.sh --camera=file --file-path=samples/x.mp4
bash scripts/run_demo.sh --camera=external          # 카메라는 다른 곳에서

# 종료 (해당 터미널 Ctrl+C — 잔존 청소는 stop_demo)
bash scripts/stop_demo.sh

# 단위 테스트 (TDD — 4 파일)
cd src/omx_reactor && python3 -m pytest test/ -v
```

대시보드: <http://localhost:8800/>

## 아키텍처

```
[웹캠] → v4l2_camera_node → /webcam/image_raw
                            → geva_node (vendored)  → /emotion/state
                            → rapport_tracker (vendored) → /rapport/event
                            → omx_reactor_node → motion_mapper → scheduler → OMX action
                            → omx_dashboard_node → FastAPI + WS → 브라우저
```

본 repo 의 신규 코드 = `src/omx_reactor/`. doby_controller 발췌 = `src/vendored/`.

## 확장 — 새 모션 추가

`src/omx_reactor/omx_reactor/motions.py` 의 `MOTIONS` 리스트에 한 항목 + `trajectories.py` 에 trajectory factory 1개. mapper/scheduler 0 수정.

```python
Motion('WAVE_BACK',
       trigger=lambda c: c.gesture and c.gesture.event == 'wave',
       priority=80, cooldown_sec=3.0, trajectory=traj_wave_back),
```

`Context` 의 `gesture` / `pose` sub-dataclass 자리는 이미 마련됨 (`context.py` 참조).

## 디자인 / 계획 문서

- 디자인 스펙: [docs/superpowers/specs/2026-05-23-omx-reactor-design.md](docs/superpowers/specs/2026-05-23-omx-reactor-design.md)
- 구현 plan: [docs/superpowers/plans/2026-05-23-omx-reactor-p0.md](docs/superpowers/plans/2026-05-23-omx-reactor-p0.md)

## Acknowledgments

본 데모의 감정 인식 파이프라인 (`geva_node`, `rapport_tracker`) + `engagement-timeline` 시각화 컴포넌트는 별 프로젝트 (cafe NPC funnel BT) 에서 발췌 — `src/vendored/` 디렉토리, 출처는 `src/vendored/README.md` 참조. OMX URDF + 컨트롤러 + Gazebo bringup 은 ROBOTIS 공식 [open_manipulator](https://github.com/ROBOTIS-GIT/open_manipulator) 사용.

## 라이센스

Apache-2.0

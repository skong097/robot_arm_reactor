# Vendored Packages — doby_controller 발췌

본 디렉토리는 doby_controller 의 자산 일부를 0 수정 카피한 것입니다.

## 출처

- Source repo: `~/physical-ai-repo-3` (PinkLAB internal, GitHub 미공개)
- Sub-tree: `src/controller/doby_controller/src/dobi_npc/`
- 발췌 시점: 2026-05-23
- 발췌 시점 git sha: `e2ce801e7eebddde5abf884fd7414c0f8342cd6a`

```bash
cd ~/physical-ai-repo-3 && git rev-parse HEAD
```

## 카피 대상

| 패키지 | 발췌 범위 |
|---|---|
| `dobi_npc_msgs` | `msg/EmotionState.msg`, `msg/RapportEvent.msg`, `msg/PersonTrack.msg`, `msg/PersonTrackArray.msg` (CMakeLists.txt 의 generate_interfaces 도 해당 4개로 축소) |
| `dobi_npc_emotion` | 패키지 전체 (geva_node, rapport_tracker_node, dummy/person_detector 도 무해하게 같이 옴) |

## 수정 정책

- **0 수정 원칙**: 본 디렉토리 안 코드는 omx_reactor 의 개발 과정에서 수정하지 않습니다.
- 필요한 동작 변경은 omx_reactor 측 wrapper 또는 launch parameter 로 해결.
- 예외 (필요 시 본 README 에 기록): geva_node 의 `track_id` 발행 검증 미충족 시 최소 patch — 추후 doby_controller 원본 PR 권장.
- 예외 1 (Task 2 + Task 3): `dobi_npc_msgs/CMakeLists.txt` 의 generate_interfaces 를 EmotionState/RapportEvent/PersonTrack/PersonTrackArray 4개만 등록하도록 축소. 다른 msg 는 omx_reactor 에서 사용 X. (Task 3 진행 중 geva_node 가 PersonTrackArray 의존이 확인되어 PersonTrack + PersonTrackArray 를 0 수정 카피로 추가함.)
- 예외 2 (2026-05-24 — engaging-analytics UI 포팅): doby_controller `src/moca_opserver/static/` 의 4 자산을 omx_reactor 의 `src/omx_reactor/omx_reactor/web/static/` 으로 0 수정 카피.
  - `js/engaging-analytics.js` → `engaging-analytics.js` (264 lines, V·A circumplex + rapport + minigame card 렌더러)
  - `components/engagement-timeline.js` → `engagement-timeline.js` (114 lines, V/A/score 3 라인 SVG web component, 2026-05-23 발췌분)
  - `css/tokens.css` → `tokens.css` (디자인 토큰 — `--bg-*`, `--pink-*`, `--success/--warning/--danger` 등 vendored 셀렉터 의존)
  - `css/components.css` → `components.css` (발췌 — `.card / .card__subtitle / .form-* / .btn* / .engaging-analytics / .ea-* / .circumplex / .engagement-timeline` 셀렉터만 카피; doby 원본 line 75-148, 538-619, 667-673, 897-1046, 1068-1115)
  - `pages/modes.html` 의 `<section class="card engaging-analytics" id="engaging-analytics">` (doby 원본 line 166-272) → `index.html` 안에 verbatim 임베드. doby 원본은 mode=engaging 일 때만 표시 (`hidden` 속성) — omx_reactor 는 mode 분기 없어 `hidden` 속성 제거. 그 외 HTML 0 수정.
  - 폐기: omx_reactor 의 임의 자산 `va_quadrant.js` (4분면 캔버스 + DANCE/FREEZE/CONSOLE/IDLE 라벨 — 사용자 동의 없이 만든 것) `git rm` + `index.html` 의 임의 4분면 섹션 제거 + `style.css` 의 canvas 관련 부분 제거.
  - adapter (omx_reactor `app.js` 재작성): `/ws/stream` payload (snapshot / emotion / rapport / reactor) 를 vendored engaging-analytics.js 가 기대하는 doby shape `{ts, emotion: {latest, trajectory}, rapport: {counters, recent}, minigame, mode}` 로 변환. engaging-analytics.js 가 `/ws/v1/engaging` (doby endpoint, omx 에는 없음) 으로 WS 를 여는데 — `window.WebSocket` 을 hijack 해서 해당 URL 만 FakeWS 로 가로채고 변환된 payload 를 inject. engaging-analytics.js 코드 자체는 0 수정.
  - 제한: engaging-analytics.js 의 "강제 발화" 폼 click handler 는 `window.api`/`/dialog/utter` 의존 — omx_reactor 에 endpoint 없어 NET 에러로 떨어짐 (HTML 폼만 보임, 기능 X). minigame/group_id 도 omx 데이터에 없어 항상 빈/Solo 로 표시. mode 분기는 `window.store` 없을 시 init 가 건너뜀 → 섹션 always visible.

### Task 3 검증 — geva_node track_id 발행 (spec §12 리스크)

`/home/gjkong/omx_reactor/src/vendored/dobi_npc_emotion/dobi_npc_emotion/geva_node.py` 의 track_id 발행 검증 결과: **PASS**.

```text
203:        self._closest_track_id: int = -1
235:            self._closest_track_id = -1
240:        self._closest_track_id = int(top.track_id)
270:            # 2026-05-21 Track B — track_id/group_id (stale guard 포함)
272:                msg.track_id = -1
275:                msg.track_id = self._closest_track_id
291:        # 2026-05-21 Track B — track_id/group_id (stale guard 포함)
293:            msg.track_id = -1
296:            msg.track_id = self._closest_track_id
```

- `_cb_tracks` (line 228-242) 가 `/person/tracks` 의 `PersonTrackArray` 를 받아 `select_closest_track` 으로 closest track 의 `track_id` 를 캐시.
- `_tick` (line 244-) 가 `EmotionState` 발행 시 두 경로 (no-face / face 검출) 모두에서 `msg.track_id = self._closest_track_id` 설정 (line 275, 296).
- Stale guard: `_last_tracks_ts` 가 `_tracks_stale_timeout` 초과면 `msg.track_id = -1` (line 272, 293).
- 정수값 (PersonTrack.track_id 는 BoT-SORT tracker int) 이 set 되므로 patch 불필요.

## 외부 모델 부트스트랩 (fresh clone 시 필요)

`dobi_npc_emotion` 의 `geva_node` 가 사용하는 mediapipe 모델 파일은 `.gitignore` 의
`*.task` / `*.tflite` / `*.onnx` 룰로 git tracking 에서 제외됩니다 (크기/라이센스 정책).
fresh clone 시 다음 절차로 모델을 부트스트랩하세요.

### 옵션 A — 인터넷 다운로드 (권장)

```bash
WS=$(pwd)   # ~/omx_reactor 가정
MODELS_DIR="$WS/src/vendored/dobi_npc_emotion/models"
mkdir -p "$MODELS_DIR"
# mediapipe FaceLandmarker (얼굴 랜드마크 + Blendshapes)
curl -fsSL https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task \
  -o "$MODELS_DIR/face_landmarker.task"
# mediapipe EfficientDet-Lite0 (person detection, gefa 후속용)
curl -fsSL https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/latest/efficientdet_lite0.tflite \
  -o "$MODELS_DIR/efficientdet_lite0.tflite"
ls -lh "$MODELS_DIR"
```
Expected: 두 파일 다운로드 (face_landmarker.task ~3.7MB, efficientdet_lite0.tflite ~4.4MB).

### 옵션 B — doby_controller 로컬 카피 (개발자 본인)

doby_controller workspace 가 이미 있는 경우:
```bash
cp /home/gjkong/physical-ai-repo-3/src/controller/doby_controller/src/dobi_npc/dobi_npc_emotion/models/* \
   $WS/src/vendored/dobi_npc_emotion/models/
```

### 검증

```bash
cd $WS && source install/setup.bash
export ROS_DOMAIN_ID=99 ROS_LOCALHOST_ONLY=1
timeout 12 ros2 run dobi_npc_emotion geva_node 2>&1 | grep -E "FaceLandmarker|모델|Error"
```
Expected: `FaceLandmarker 초기화 완료` 같은 로그. 에러 메시지 있으면 모델 path 또는 다운로드 재확인.

> 모델 부트스트랩 후 colcon build 재실행은 불필요 (symlink-install 인 경우 — 모델은 share/ 로 install_data_files 통해 자동 install).

## 추후 병합 절차

omx_reactor 가 doby_controller `src/dobi_npc/dobi_npc_arm/` 로 병합되는 시점:
1. 본 vendored/ 디렉토리 통째 `git rm -r`
2. omx_reactor/package.xml 의 `<depend>dobi_npc_msgs</depend>` 와 `<depend>dobi_npc_emotion</depend>` 는 그대로 (원본 의존)
3. import 경로도 그대로 (vendored vs 원본 둘 다 동일 패키지명)
4. launch 의 vendored 노드 spawn 부분을 doby_controller 의 dev_common.launch.py 와 중복 회피 (멱등 가드)

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

## 추후 병합 절차

omx_reactor 가 doby_controller `src/dobi_npc/dobi_npc_arm/` 로 병합되는 시점:
1. 본 vendored/ 디렉토리 통째 `git rm -r`
2. omx_reactor/package.xml 의 `<depend>dobi_npc_msgs</depend>` 와 `<depend>dobi_npc_emotion</depend>` 는 그대로 (원본 의존)
3. import 경로도 그대로 (vendored vs 원본 둘 다 동일 패키지명)
4. launch 의 vendored 노드 spawn 부분을 doby_controller 의 dev_common.launch.py 와 중복 회피 (멱등 가드)

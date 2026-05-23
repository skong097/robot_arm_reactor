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
| `dobi_npc_msgs` | `msg/EmotionState.msg`, `msg/RapportEvent.msg` 만 (CMakeLists.txt 의 generate_interfaces 도 해당 2개로 축소) |
| `dobi_npc_emotion` | 패키지 전체 (geva_node, rapport_tracker_node, dummy/person_detector 도 무해하게 같이 옴) |

## 수정 정책

- **0 수정 원칙**: 본 디렉토리 안 코드는 omx_reactor 의 개발 과정에서 수정하지 않습니다.
- 필요한 동작 변경은 omx_reactor 측 wrapper 또는 launch parameter 로 해결.
- 예외 (필요 시 본 README 에 기록): geva_node 의 `track_id` 발행 검증 미충족 시 최소 patch — 추후 doby_controller 원본 PR 권장.
- 예외 1 (Task 2): `dobi_npc_msgs/CMakeLists.txt` 의 generate_interfaces 를 EmotionState/RapportEvent 만 등록하도록 축소. 다른 msg 는 omx_reactor 에서 사용 X.

## 추후 병합 절차

omx_reactor 가 doby_controller `src/dobi_npc/dobi_npc_arm/` 로 병합되는 시점:
1. 본 vendored/ 디렉토리 통째 `git rm -r`
2. omx_reactor/package.xml 의 `<depend>dobi_npc_msgs</depend>` 와 `<depend>dobi_npc_emotion</depend>` 는 그대로 (원본 의존)
3. import 경로도 그대로 (vendored vs 원본 둘 다 동일 패키지명)
4. launch 의 vendored 노드 spawn 부분을 doby_controller 의 dev_common.launch.py 와 중복 회피 (멱등 가드)

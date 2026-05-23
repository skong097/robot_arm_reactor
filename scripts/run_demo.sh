#!/bin/bash
# DEPRECATED — backward-compat alias to run_demo_omx.sh.
# 새 진입점: run_demo_omx.sh (OMX) / run_demo_openarm.sh (OpenArm bimanual).
exec "$(dirname "${BASH_SOURCE[0]}")/run_demo_omx.sh" "$@"

#!/usr/bin/env bash
set -uo pipefail
status=0
bash "$1/tests/android-all-smoke.sh" "$2" "$3" || status=1
python3 patches/check-transport-ui.py smoke-output/ui.xml | tee smoke-output/accessibility.log || status=1
python3 patches/ui-navigation-smoke.py | tee smoke-output/navigation.log || status=1
exit "$status"

#!/usr/bin/env bash
set -euo pipefail
mkdir -p smoke-output
trap 'adb logcat -d -t 2000 > smoke-output/logcat.txt || true; adb exec-out screencap -p > smoke-output/screen.png || true' EXIT
adb install -r "$1"
adb logcat -c
adb shell am start -W -n app.remix.player/.MainActivity | tee smoke-output/launch.txt
sleep 3
adb shell pidof app.remix.player
python3 patches/startup-ui.py smoke-output/ui.xml
grep -q 'Моя музыка' smoke-output/ui.xml
grep -q 'Найти музыку на телефоне' smoke-output/ui.xml
adb shell input keyevent KEYCODE_HOME
sleep 1
adb shell am start -W -n app.remix.player/.MainActivity
sleep 2
adb shell pidof app.remix.player
adb logcat -d -s AndroidRuntime:E > smoke-output/crashes.txt
if grep -q 'FATAL EXCEPTION' smoke-output/crashes.txt; then exit 1; fi

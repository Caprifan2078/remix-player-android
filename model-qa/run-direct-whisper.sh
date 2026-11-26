#!/usr/bin/env bash
set -euo pipefail
mkdir -p model-results
trap 'adb logcat -d > model-results/logcat.txt || true' EXIT
adb install -r apk/app-debug.apk
adb install -r test-apk/app-debug-androidTest.apk
adb shell run-as app.remix.player mkdir -p files/mixes
adb push model-fixtures/qa-whisper.wav /data/local/tmp/remix-qa-whisper.wav
adb shell run-as app.remix.player cp /data/local/tmp/remix-qa-whisper.wav files/mixes/qa-whisper.wav
adb logcat -c
timeout 900 adb shell am instrument -w -r -e class app.remix.player.DirectWhisperDownloadTest app.remix.player.test/androidx.test.runner.AndroidJUnitRunner | tr -d '\r' | tee model-results/direct-whisper.txt
python3 - <<'PY'
import pathlib,re
s=pathlib.Path('model-results/direct-whisper.txt').read_text()
assert re.findall(r'^INSTRUMENTATION_STATUS: test=(.*)$',s,re.M)==['downloadActivateAndTranscribeOnDevice']*2
assert re.findall(r'^INSTRUMENTATION_STATUS_CODE: (-?\d+)$',s,re.M)==['1','0']
assert re.findall(r'\bOK \(1 test\)',s)==['OK (1 test)']
assert re.findall(r'^INSTRUMENTATION_CODE: (-?\d+)$',s,re.M)==['-1']
PY

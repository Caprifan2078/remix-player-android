#!/usr/bin/env bash
set -euo pipefail
mkdir -p model-results
trap 'adb logcat -d > model-results/logcat.txt || true; adb shell dumpsys meminfo app.remix.player > model-results/meminfo.txt || true' EXIT
adb install -r apk/app-debug.apk
adb install -r test-apk/app-debug-androidTest.apk
adb shell am force-stop app.remix.player
adb shell run-as app.remix.player mkdir -p files/mixes
adb push model-fixtures/qa-whisper.wav /data/local/tmp/remix-qa-whisper.wav
adb push model-fixtures/qa-whisper-tiny.bin /data/local/tmp/remix-qa-whisper-tiny.bin
adb shell run-as app.remix.player cp /data/local/tmp/remix-qa-whisper.wav files/mixes/qa-whisper.wav
adb shell run-as app.remix.player cp /data/local/tmp/remix-qa-whisper-tiny.bin files/mixes/qa-whisper-tiny.bin
adb logcat -c
# Run each independently so a model failure cannot hide the other results.
status=0
for test in actualFourStemDemucs actualSixStemDemucs actualAstClassifier actualWhisperTinySpeech; do
  log="model-results/$test.txt"
  timeout 720 adb shell am instrument -w -r -e class "app.remix.player.RealModelAcceptanceTest#$test" app.remix.player.test/androidx.test.runner.AndroidJUnitRunner | tee "$log" || status=1
  python3 - "$log" "$test" <<'PY' || status=1
import pathlib,re,sys
s=pathlib.Path(sys.argv[1]).read_text()
assert re.findall(r'^INSTRUMENTATION_STATUS: test=(.*)$',s,re.M)==[sys.argv[2],sys.argv[2]],'Wrong test identity'
assert re.findall(r'^INSTRUMENTATION_STATUS_CODE: (-?\d+)$',s,re.M)==['1','0'],'Unsuccessful test'
assert re.findall(r'\bOK \(1 test\)',s)==['OK (1 test)'],'Missing success'
assert re.findall(r'^INSTRUMENTATION_CODE: (-?\d+)$',s,re.M)==['-1'],'Bad terminal result'
PY
done
# Run direct download last; the preceding test cleans up the active model.
log="model-results/direct-whisper.txt"
timeout 720 adb shell am instrument -w -r -e class "app.remix.player.DirectWhisperDownloadTest#downloadActivateAndTranscribeOnDevice" app.remix.player.test/androidx.test.runner.AndroidJUnitRunner | tee "$log" || status=1
python3 - "$log" downloadActivateAndTranscribeOnDevice <<'PY' || status=1
import pathlib,re,sys
s=pathlib.Path(sys.argv[1]).read_text()
assert re.findall(r'^INSTRUMENTATION_STATUS: test=(.*)$',s,re.M)==[sys.argv[2],sys.argv[2]],'Wrong test identity'
assert re.findall(r'^INSTRUMENTATION_STATUS_CODE: (-?\d+)$',s,re.M)==['1','0'],'Unsuccessful test'
assert re.findall(r'\bOK \(1 test\)',s)==['OK (1 test)'],'Missing success'
assert re.findall(r'^INSTRUMENTATION_CODE: (-?\d+)$',s,re.M)==['-1'],'Bad terminal result'
PY
exit "$status"

#!/usr/bin/env bash
set -euo pipefail
mkdir -p model-results
trap 'adb logcat -d > model-results/logcat.txt || true; adb shell dumpsys meminfo app.remix.player > model-results/meminfo.txt || true' EXIT
adb install -r apk/app-debug.apk
adb install -r test-apk/app-debug-androidTest.apk
adb shell am force-stop app.remix.player
adb shell run-as app.remix.player mkdir -p files/mixes
adb push model-fixtures/qa-whisper.wav /data/local/tmp/remix-qa-whisper.wav
adb push model-fixtures/qa-whisper-ru.wav /data/local/tmp/remix-qa-whisper-ru.wav
adb push model-fixtures/qa-whisper-tiny.bin /data/local/tmp/remix-qa-whisper-tiny.bin
adb shell run-as app.remix.player cp /data/local/tmp/remix-qa-whisper.wav files/mixes/qa-whisper.wav
adb shell run-as app.remix.player cp /data/local/tmp/remix-qa-whisper-ru.wav files/mixes/qa-whisper-ru.wav
adb shell run-as app.remix.player cp /data/local/tmp/remix-qa-whisper-tiny.bin files/mixes/qa-whisper-tiny.bin
adb logcat -c
# Run each independently so a model failure cannot hide the other results.
status=0
for test in actualFourStemDemucs actualSixStemDemucs actualAstClassifier actualWhisperTinySpeech; do
  log="model-results/$test.txt"
  timeout 720 adb shell am instrument -w -r -e class "app.remix.player.RealModelAcceptanceTest#$test" app.remix.player.test/androidx.test.runner.AndroidJUnitRunner | tee "$log" || status=1
  python3 model-qa/verify_model_log.py "$log" "$test" || status=1
done
# Run direct download last; the preceding test cleans up the active model.
for test in downloadActivateAndTranscribeOnDevice quantizedBaseSpeech fullBaseSpeech quantizedSmallSpeech fullSmallSpeech quantizedMediumSpeech turboSpeech fullLargeV3Speech; do
  log="model-results/$test.txt"
  adb shell am force-stop app.remix.player
  adb shell run-as app.remix.player rm -f files/whisper-tiny.bin || true
  timeout 2400 adb shell am instrument -w -r -e class "app.remix.player.DirectWhisperDownloadTest#$test" app.remix.player.test/androidx.test.runner.AndroidJUnitRunner | tee "$log" || status=1
  python3 model-qa/verify_model_log.py "$log" "$test" || status=1
  case "$test" in
    downloadActivateAndTranscribeOnDevice) id=tiny;;
    quantizedBaseSpeech) id=base-q5_1;;
    fullBaseSpeech) id=base;;
    quantizedSmallSpeech) id=small-q5_1;;
    fullSmallSpeech) id=small;;
    quantizedMediumSpeech) id=medium-q5_0;;
    turboSpeech) id=large-v3-turbo-q5_0;;
    fullLargeV3Speech) id=large-v3-q5_0;;
    *) exit 1;;
  esac
  report="model-results/whisper-$id.json"
  adb exec-out run-as app.remix.player cat "files/qa-whisper-$id.json" > "$report" || status=1
  python3 model-qa/verify_benchmark.py "$report" "$id" >> model-results/whisper-benchmark.txt || status=1
  report="model-results/whisper-$id-ru.json"
  adb exec-out run-as app.remix.player cat "files/qa-whisper-$id-ru.json" > "$report" || status=1
  python3 model-qa/verify_benchmark.py "$report" "$id" ru >> model-results/whisper-benchmark.txt || status=1
  case "$id" in
    tiny|base-q5_1|base|small-q5_1|small)
      adb exec-out run-as app.remix.player cat "files/qa-ablation-$id.json" > "model-results/ablation-$id.json" || status=1
      ;;
  esac
done
python3 model-qa/verify_ablation.py model-results > model-results/ablation-summary.txt || status=1
python3 model-qa/compare_qa30.py model-results > model-results/qa30-comparison.txt || status=1
exit "$status"

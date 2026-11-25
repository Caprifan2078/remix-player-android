#!/usr/bin/env bash
set -uo pipefail
status=0
bash "$1/tests/android-smoke.sh" "$2" || status=1
bash "$1/tests/android-playback.sh" "$3" || status=1
# Direct instrumentation now verifies real mixer buttons, service, position, pause and lyrics spans.
# uiautomator dump waits for idle, and cannot capture a continuously updating playback screen.
for name in mixer-resumed mixer-paused karaoke-word karaoke-seek; do
    adb exec-out run-as app.remix.player cat "files/qa-$name.png" > "smoke-output/$name.png" || status=1
    python3 -c 'import sys; assert open(sys.argv[1],"rb").read(8)==b"\x89PNG\r\n\x1a\n"' "smoke-output/$name.png" || status=1
done
adb shell am force-stop app.remix.player || status=1
python3 patches/check-transport-ui.py smoke-output/ui.xml | tee smoke-output/accessibility.log || status=1
python3 patches/ui-navigation-smoke.py | tee smoke-output/navigation.log || status=1
python3 patches/check-test-identities.py smoke-output/instrumentation.txt "$1/app/src/androidTest" | tee smoke-output/test-identities.log || status=1
exit "$status"

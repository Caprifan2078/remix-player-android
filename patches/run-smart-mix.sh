#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$root/app/src/main/java/app/remix/player/SmartMix.kt" patches/SmartMixTest.kt patches/MixQualityTest.kt patches/RadioSimilarityTest.kt -include-runtime -d "$tmp/test.jar"
java -cp "$tmp/test.jar" app.remix.player.SmartMixTestKt
java -cp "$tmp/test.jar" app.remix.player.MixQualityTestKt
java -cp "$tmp/test.jar" app.remix.player.RadioSimilarityTestKt

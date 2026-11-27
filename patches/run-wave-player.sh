#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d);trap 'rm -rf "$tmp"' EXIT
kotlinc "$1/app/src/main/java/app/remix/player/WaveBins.kt" patches/WaveBinsTest.kt patches/WaveCoverageTest.kt -include-runtime -d "$tmp/wave.jar"
java -cp "$tmp/wave.jar" app.remix.player.WaveBinsTestKt
java -cp "$tmp/wave.jar" app.remix.player.WaveCoverageTestKt

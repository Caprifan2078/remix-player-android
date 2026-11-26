#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d);trap 'rm -rf "$tmp"' EXIT
kotlinc "$1/app/src/main/java/app/remix/player/WaveBins.kt" patches/WaveBinsTest.kt -include-runtime -d "$tmp/wave.jar"
java -jar "$tmp/wave.jar"

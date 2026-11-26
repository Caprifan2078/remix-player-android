#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1/app/src/main/java/app/remix/player/AudioCore.kt" "$1/app/src/main/java/app/remix/player/EffectMenu.kt" patches/EffectMenuTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"

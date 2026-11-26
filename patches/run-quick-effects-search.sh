#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1"/app/src/main/java/app/remix/player/{AudioCore,LyricsMatch,LyricsSearchPlan,QuickEffects}.kt patches/QuickEffectsSearchTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"
kotlinc "$1/app/src/main/java/app/remix/player/AudioCore.kt" patches/StereoOrbitTest.kt -include-runtime -d "$tmp/orbit.jar"
java -jar "$tmp/orbit.jar"

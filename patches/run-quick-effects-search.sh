#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1"/app/src/main/java/app/remix/player/{AudioCore,LyricsMatch,LyricsSearchPlan,QuickEffects}.kt patches/QuickEffectsSearchTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"
kotlinc "$1/app/src/main/java/app/remix/player/AudioCore.kt" patches/StereoOrbitTest.kt -include-runtime -d "$tmp/orbit.jar"
java -jar "$tmp/orbit.jar"
kotlinc "$1/app/src/main/java/app/remix/player/AudioCore.kt" patches/EffectQualityTest.kt -include-runtime -d "$tmp/quality.jar"
java -jar "$tmp/quality.jar"
kotlinc "$1/app/src/main/java/app/remix/player/"{AudioCore,LiveEffectSwitch}.kt patches/LiveEffectSwitchTest.kt -include-runtime -d "$tmp/switch.jar"
java -jar "$tmp/switch.jar"
kotlinc "$1/app/src/main/java/app/remix/player/AudioCore.kt" patches/EffectAliasTest.kt -include-runtime -d "$tmp/alias.jar"
java -jar "$tmp/alias.jar"
kotlinc "$1/app/src/main/java/app/remix/player/AudioCore.kt" patches/DspOptimizationTest.kt -include-runtime -d "$tmp/opt.jar"
java -jar "$tmp/opt.jar"

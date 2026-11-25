#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$root"/app/src/main/java/app/remix/player/{StemCore,TransitionMix}.kt patches/TransitionEnergyTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"

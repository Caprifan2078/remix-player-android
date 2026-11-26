#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1/app/src/main/java/app/remix/player/WaveEnvelope.kt" patches/WaveEnvelopeTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"

#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$root"/app/src/main/java/app/remix/player/{AudioCore,WhisperSegments,SubtitleCore,StemCore,AnalysisMono,WordLyrics}.kt patches/WhisperWindowRegression.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"
bash "$root/tests/run-whisper63.sh"

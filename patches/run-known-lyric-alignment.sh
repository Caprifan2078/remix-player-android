#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1"/app/src/main/java/app/remix/player/{AudioCore,StemCore,AnalysisMono,SubtitleCore,WordLyrics,LyricDocument,LyricAlign,PhraseAlign,KnownLyricAlignment}.kt patches/KnownLyricAlignmentTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"

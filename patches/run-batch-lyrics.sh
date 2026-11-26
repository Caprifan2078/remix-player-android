#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1"/app/src/main/java/app/remix/player/{LyricsMatch,LyricsSearchPlan,BatchLyricPolicy}.kt patches/BatchLyricPolicyTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"
kotlinc "$1/app/src/main/java/app/remix/player/TranscriptMatch.kt" patches/TranscriptMatchTest.kt -include-runtime -d "$tmp/transcript.jar"
java -jar "$tmp/transcript.jar"
kotlinc "$1/app/src/main/java/app/remix/player/BrowserLyricImport.kt" patches/BrowserLyricImportTest.kt -include-runtime -d "$tmp/browser.jar"
java -jar "$tmp/browser.jar"
node patches/lyrics-extract-test.js

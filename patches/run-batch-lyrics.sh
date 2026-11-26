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
kotlinc "$1/app/src/main/java/app/remix/player/LyricScanState.kt" patches/LyricScanStateTest.kt -include-runtime -d "$tmp/scan-state.jar"
java -jar "$tmp/scan-state.jar"
kotlinc patches/CoverSwipe.kt patches/CoverSwipeTest.kt -include-runtime -d "$tmp/CoverSwipe.jar"
java -jar "$tmp/CoverSwipe.jar"
kotlinc patches/SourceEffectBalance.kt patches/SourceEffectBalanceTest.kt -include-runtime -d "$tmp/SourceEffectBalance.jar"
java -jar "$tmp/SourceEffectBalance.jar"
kotlinc patches/TrackIdentityFix.kt patches/TrackIdentityFixTest.kt -include-runtime -d "$tmp/TrackIdentityFix.jar"
java -jar "$tmp/TrackIdentityFix.jar"

#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1"/app/src/main/java/app/remix/player/{AudioCore,StemCore,AnalysisMono,SubtitleCore,WordLyrics,LyricDocument,LyricAlign,PhraseAlign,KnownLyricAlignment,GroupedLyricMatch,LyricTimingUpgrade}.kt patches/KnownLyricAlignmentTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"
kotlinc "$1/app/src/main/java/app/remix/player/GroupedLyricMatch.kt" patches/GroupedLyricMatchTest.kt -include-runtime -d "$tmp/grouped.jar"
java -jar "$tmp/grouped.jar"
kotlinc "$1/app/src/main/java/app/remix/player/LyricTimingUpgrade.kt" patches/LyricTimingUpgradeTest.kt -include-runtime -d "$tmp/upgrade.jar"
java -jar "$tmp/upgrade.jar"

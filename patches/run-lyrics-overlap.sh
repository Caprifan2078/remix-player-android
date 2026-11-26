#!/usr/bin/env bash
set -euo pipefail
root="$1"
jar=$(mktemp --suffix=.jar)
trap 'rm -f "$jar"' EXIT
export JAVA_OPTS=-Xmx1g
kotlinc "$root"/app/src/main/java/app/remix/player/{AudioCore,WordLyrics,SubtitleExport,OverlapCore,OverlapStall}.kt patches/SubtitleRegression.kt patches/KaraokeOverlapTest.kt patches/OverlapStallTest.kt -include-runtime -d "$jar"
java -cp "$jar" app.remix.player.SubtitleRegressionKt
java -cp "$jar" app.remix.player.KaraokeOverlapTestKt
java -cp "$jar" app.remix.player.OverlapStallTestKt

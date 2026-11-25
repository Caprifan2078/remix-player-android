#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1"/app/src/main/java/app/remix/player/{VerifiedDownload,CatalogDownload,ModelCatalog}.kt patches/HashCancelTest.kt patches/DownloadProgressTest.kt -include-runtime -d "$tmp/test.jar"
java -cp "$tmp/test.jar" app.remix.player.HashCancelTestKt
java -cp "$tmp/test.jar" app.remix.player.DownloadProgressTestKt

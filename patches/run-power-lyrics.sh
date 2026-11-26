#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$root/app/src/main/java/app/remix/player/PlaybackCadence.kt" "$root/app/src/main/java/app/remix/player/Mp3Lyrics.kt" patches/PowerCadenceTest.kt patches/Mp3LyricsTest.kt "$root/app/src/main/java/app/remix/player/WidgetPolicy.kt" patches/WidgetPolicyTest.kt "$root/app/src/main/java/app/remix/player/TransportPolicy.kt" patches/TransportPolicyTest.kt -include-runtime -d "$tmp/test.jar"
java -cp "$tmp/test.jar" app.remix.player.PowerCadenceTestKt
java -cp "$tmp/test.jar" app.remix.player.WidgetPolicyTestKt
java -cp "$tmp/test.jar" app.remix.player.TransportPolicyTestKt
for version in 0 3 4; do
  ffmpeg -v error -y -f lavfi -i 'sine=frequency=440:duration=3' -metadata title='Pulse fixture' -metadata artist='QA' -id3v2_version "$version" -write_id3v1 0 -c:a libmp3lame "$tmp/before.mp3"
  java -cp "$tmp/test.jar" app.remix.player.Mp3LyricsTestKt "$tmp/before.mp3" "$tmp/after.mp3"
  ffmpeg -v error -i "$tmp/before.mp3" -f s16le "$tmp/before.pcm" -y
  ffmpeg -v error -i "$tmp/after.mp3" -f s16le "$tmp/after.pcm" -y
  cmp "$tmp/before.pcm" "$tmp/after.pcm"
  ffprobe -v error -show_entries format_tags -of json "$tmp/after.mp3" > "$tmp/tags.json"
  python3 - "$tmp/tags.json" "$version" <<'PY'
import json,sys
tags=json.load(open(sys.argv[1]))['format']['tags']
assert tags['lyrics-und']=='Привет мир\nHello world'
assert tags['lyrics-LRC-und']=='[00:01.00]Привет мир'
if sys.argv[2]!='0':
    assert tags['title']=='Pulse fixture' and tags['artist']=='QA'
PY
done
echo "PASS: MP3 audio decode identity and metadata on ID3v2.3, v2.4 and untagged files"

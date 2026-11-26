#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export JAVA_OPTS=-Xmx1g
kotlinc "$root"/app/src/main/java/app/remix/player/{GenrePhrase,GenrePhraseWeights,NeuralTone,NeuralInstrumental,NeuralDrums,PhraseWeights,Harmony,AdaptiveGroove,RhythmMap,StemCore,GenreEngine,GenreMix,Arrangement,LeadSynth,VocalSpace,GenreDynamics,Tempo,MusicAnalysis,SoundProfile,SectionMap,StructureCore,RemixAdvisor,MusicalIntelligence,TimeStretch,AudioCore,Mastering}.kt patches/StudioUpgradeTest.kt patches/LeadColorTest.kt patches/GenreKickTest.kt patches/AudioPerformanceTest.kt -include-runtime -d "$tmp/studio.jar"
java -cp "$tmp/studio.jar" app.remix.player.StudioUpgradeTestKt
java -cp "$tmp/studio.jar" app.remix.player.LeadColorTestKt
java -cp "$tmp/studio.jar" app.remix.player.GenreKickTestKt
java -cp "$tmp/studio.jar" app.remix.player.AudioPerformanceTestKt

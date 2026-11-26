#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$root"/app/src/main/java/app/remix/player/{StemCore,MusicAnalysis,Tempo,Harmony,RhythmMap,SoundProfile,SectionMap,AnalysisMono,BackingFit,EffectRender,TimeStretch,AudioCore,AudioFileCore,Arrangement,AdaptiveGroove,GenreEngine,GenrePhrase,GenrePhraseWeights,GenreMix,GenreDynamics,LeadSynth,VocalSpace,NeuralTone,NeuralInstrumental,NeuralDrums,PhraseWeights,StructureCore,RemixAdvisor,MusicalIntelligence,DjTransition,TransitionMix}.kt patches/DjTransitionTest.kt -include-runtime -d "$tmp/test.jar"
java -cp "$tmp/test.jar" app.remix.player.DjTransitionTestKt

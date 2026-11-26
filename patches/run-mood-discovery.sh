#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
kotlinc "$1"/app/src/main/java/app/remix/player/{GenrePhrase,GenrePhraseWeights,NeuralTone,NeuralInstrumental,NeuralDrums,PhraseWeights,Harmony,AdaptiveGroove,RhythmMap,StemCore,GenreEngine,GenreMix,Arrangement,LeadSynth,VocalSpace,GenreDynamics,Tempo,MusicAnalysis,SoundProfile,SectionMap,StructureCore,RemixAdvisor,MusicalIntelligence,TimeStretch,AudioCore,MoodDiscovery}.kt patches/MoodDiscoveryTest.kt -include-runtime -d "$tmp/test.jar"
java -jar "$tmp/test.jar"

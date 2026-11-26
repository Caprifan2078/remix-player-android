# Music intelligence: offline mood and model acceptance
2026-11-26. Research and engineering plan, not a claim of installed or working new neural models.

## Existing path
MoodDiscovery and LocalDiscovery use acoustic features rather than neural inference. Keep this path available offline without model downloads. Eight mood profiles, related tracks, and queue/playlist operations. Scores are heuristic affinities, not calibrated emotion probabilities. Major/minor is a limited proxy; do not present it as understanding lyrics.

## Candidate models, in implementation priority
1. MusiCNN MSD + Essentia mood heads (happy, sad, relaxed, aggressive), MIREX and danceability. Official: https://essentia.upf.edu/models.html . Music-specific embeddings, mono 16 kHz input and exact publisher mel preprocessing; verify graph format and input/output contract for each artifact. MTG models CC BY-NC-SA 4.0; separate commercial license required if commercial use is planned. Do not bundle without review.
2. Discogs-EffNet + mood, genre and voice/instrumental heads: same official registry and license. Compare quality/memory against MusiCNN on the same test clips; use one encoder, not two concurrent heavyweight networks. No assumption that every head has a ready ONNX export.
3. YAMNet (Google MediaPipe, about 4.1 MB TFLite): https://developers.google.com/edge/mediapipe/solutions/audio/audio_classifier . Candidate for audio event/instrument/speech tags, not a trained mood classifier. Do not confuse presence of music with emotion. Avoid adding another runtime unless it has a clear benefit. See https://huggingface.co/litert-community/MediaPipe-AudioClassifier-YAMNet for artifact metadata.
4. MERT-v1-95M: https://huggingface.co/m-a-p/MERT-v1-95M . Music embeddings for acoustic similarity; requires trained downstream head for mood labels. Keep experimental, not an automatic download. Verify model/license/export and benchmark on ARM64.
5. Separation alternative: https://github.com/deezer/spleeter . Candidate comparison, not a proven low-memory Android replacement for Demucs. Confirm actual peak memory, quality and license of the weights before release.

## Integration gates
- Model selection in one existing settings section; no new tab. Optional download, explicit size/license and publisher SHA-256, exact pinned revision, validated tensor names/shapes/dtypes. No arbitrary model execution or code download.
- Use short bounded mono PCM excerpts from several positions, exact documented preprocessing, sequential inference off the UI thread; release native resources, cancel promptly, guard memory and storage. Never send songs to remote services.
- Aggregate per-window scores and keep model identity/revision in the cache. Missing, nonfinite or incompatible output must fall back to acoustic estimates; do not persist it as neural data. Do not label unscanned or silent tracks as sad. No silent automatic queue replacement.
- Compare model vs acoustic baseline on manually tagged, licensed music clips with varied genres, instrumental/vocal, remixes, silence, and ambiguous/mixed moods. Measure per-class precision/recall, coverage, latency, RAM peak, and cancellation. No arbitrary accuracy claim.
- Real ARM64 device and emulator: successful install, real inference, repeat run, memory pressure, background/foreground, cancellation, cache invalidation, offline playback, and no regressions in lyrics or mixing.
- Keep current model blockers explicit: previous Demucs runs killed under memory pressure; AST int8 ConvInteger failed; FP32 AST candidate and memory guards are not evidence of recovery; Whisper tiny speech success does not prove sung lyric accuracy.
- Release requires successful Android build and real-model acceptance. Until then show only existing acoustic functionality.

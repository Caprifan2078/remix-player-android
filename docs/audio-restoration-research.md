# Music restoration / super-resolution research gate

2026-11-26. No enhancement model is advertised as installed or usable until an actual Android inference test passes.

## Candidates
- UniverSR audio: https://github.com/woongzip1/UniverSR and https://huggingface.co/woongzip1/universr-audio — music/speech/sound effects, 8/12/16/24 kHz to 48 kHz, flow matching in complex STFT. Evaluate conversion, exact preprocessing, weight license, stereo preservation and CPU/RAM before adding to the catalogue.
- AudioSR basic: https://github.com/haoheliu/versatile_audio_super_resolution — general audio diffusion; upstream explicitly warns about MP3 spectral holes and unfamiliar cutoff patterns. Not a guaranteed MP3 restoration.
- FastWave: https://github.com/Nikait/FastWave — research candidate, advertises 1.3M parameters; independently verify released weights, license, actual compute and quality before adoption.
- A2SB: https://github.com/NVIDIA/diffusion-audio-restoration — music bandwidth extension/inpainting research; do not assume phone deployment.
- Android resampling: https://developer.android.com/ndk/guides/audio/sampling-audio — unnecessary conversion can reduce quality. A bigger sampling-rate or bit-depth number does not restore missing source content.

## Acceptance
1. No modification of original. Export separate version, no network upload. Use explicit opt-in for model download and SHA256/size verification.
2. Compare same-loudness A/B on legal stereo fixtures: clean reference, low-pass versions, MP3/AAC degradation, clipping, silence, vocals and instruments. Reject merely louder output or unnecessary processing of full-band input.
3. Measure low-band preservation, duration, channel balance, phase, reconstructed-band error against available reference, sample peaks, and listening preference. Report uncertainty; hallucinated high frequencies are not recovered original detail.
4. Establish source bandwidth and decoder limits, exact model preprocessing/postprocessing, chunk continuity, cancellation, memory/disk budgets, stereo routing. Do not ship a speech-only model as a music enhancer.
5. Verify genuine model inference on Android ARM64 and emulator separately; no identity ONNX or synthetic inference as evidence of restoration. Benchmark processing time and memory. Offline only initially, not in playback callback.
6. Bypass on already good recordings by default; manual override only. Do not promote conversion to FLAC, 96 kHz or 24-bit as restoration.

First practical deliverable: source quality inspection and an offline A/B restoration experiment. No model weights downloaded or licensed for redistribution by this change.

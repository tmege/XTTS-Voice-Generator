# XTTS Voice Generator

Desktop macOS app to generate audio with voice cloning via [XTTS v2](https://github.com/coqui-ai/TTS) (Coqui TTS).

![XTTS Voice Generator](assets/Screenshot%202026-03-27%20at%2023.04.53.png)

## Features

- Multilingual text-to-speech (fr, en, es, de, it, pt, etc.)
- 58 built-in XTTS v2 voices selectable from a dropdown
- Voice cloning from an external audio file (.wav, .mp3)
- Direct playback of the generated file within the app
- Output folder and filename selection
- PyQt5 interface, background generation (QThread)

## Target Architecture

Developed and tested on **Mac Apple Silicon (M4)**. XTTS v2 and its dependencies (PyTorch, Coqui TTS) are not natively optimized for ARM / Apple Silicon, which required several adaptations:

- **Python 3.11** required (some Coqui TTS dependencies fail to compile on 3.12+ with ARM)
- **`torch.load` patch**: recent PyTorch enforces `weights_only=True` by default, which breaks XTTS v2 checkpoint loading — we force `weights_only=False` at startup
- **No CUDA**: generation runs on CPU (MPS partially supported but unstable with XTTS) — expect ~10-30s per generation
- ARM64 PyTorch wheels are used automatically via pip, no custom build needed

> On Intel x86 architecture, these adaptations remain compatible but the `torch.load` patch is the only one strictly necessary.

## Prerequisites

- macOS 11+ (tested on macOS 15 / Apple M4)
- Python 3.11 (not 3.12+, incompatible with some Coqui TTS dependencies)
- ~5 GB disk space (XTTS v2 model + dependencies)

## Installation

```bash
# Create the venv (Python 3.11 required)
python3.11 -m venv xtts-env
source xtts-env/bin/activate

# Install dependencies
pip install TTS PyQt5 cutlet unidic-lite

# The XTTS v2 model downloads automatically on first launch (~1.8 GB)
```

## Usage

### From the terminal

```bash
xtts-env/bin/python3.11 xtts_app.py
```

### Double-click (macOS .app)

Run `build_app.sh` to generate the bundle:

```bash
bash build_app.sh
```

This creates `XTTS Voice Generator.app` — double-click to launch. Drag to the Dock or `/Applications` for quick access.

> **Note:** The app uses a shell launcher that calls `xtts-env/bin/python3.11` directly (not PyInstaller). This is much more stable for PyTorch/TTS on macOS.

## Structure

```
.
├── xtts_app.py          # Main app (UI + TTS backend)
├── build_app.sh         # macOS .app generation (launcher)
├── assets/              # README screenshots and resources
├── xtts-env/            # Python 3.11 venv (not versioned)
├── xtts_voices/         # Custom voices (reference audio files)
└── xtts_output/         # Generated .wav files (default)
```

## Known Vulnerabilities

- **`torch.load(weights_only=False)`**: This app patches `torch.load` to disable the `weights_only` safety check at startup. This is required because XTTS v2 checkpoints rely on pickle-based serialization which is incompatible with `weights_only=True`. Loading a malicious model file could lead to arbitrary code execution. Only use trusted model sources.
- **`QThread.terminate()`**: The cancel button uses `QThread.terminate()` to stop generation, which is discouraged by Qt documentation as it can leave shared resources (mutexes, memory) in an inconsistent state. In practice this is low-risk since the thread only performs PyTorch inference, but it could theoretically cause instability.

## Notes

- The `torch.load(weights_only=False)` patch is applied automatically at startup (required by XTTS v2)
- The first launch downloads the model (~1.8 GB) into `~/.local/share/tts/`
- Generation takes ~10-30s depending on text length (CPU)

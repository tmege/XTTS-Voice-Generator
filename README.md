# XTTS Voice Generator

macOS desktop app for audio generation with voice cloning via [XTTS v2](https://github.com/coqui-ai/TTS) (Coqui TTS).

## Features

- Multilingual speech synthesis (fr, en, es, de, it, pt, etc.)
- 58 built-in XTTS v2 voices selectable from a dropdown
- Voice cloning from an external audio file (.wav, .mp3)
- Direct playback of the generated file within the app
- Custom output folder and filename selection
- PyQt5 interface with background generation (QThread)

## Target Architecture

Developed and tested on **Mac Apple Silicon (M4)**. XTTS v2 and its dependencies (PyTorch, Coqui TTS) are not natively optimized for ARM / Apple Silicon, which required several adaptations:

- **Python 3.11** required (some Coqui TTS dependencies fail to compile on 3.12+ with ARM)
- **`torch.load` patch**: Recent PyTorch enforces `weights_only=True` by default, which breaks XTTS v2 checkpoint loading — we force `weights_only=False` at startup
- **No CUDA**: Generation runs on CPU (MPS is partially supported but unstable with XTTS) — expect ~10-30s per generation
- ARM64 PyTorch wheels are used automatically via pip, no custom build needed

> On Intel x86 architecture, these adaptations remain compatible but the `torch.load` patch is the only one truly necessary.

## Prerequisites

- macOS 11+ (tested on macOS 15 / Apple M4)
- Python 3.11 (not 3.12+, incompatible with some Coqui TTS dependencies)
- ~5 GB of disk space (XTTS v2 model + dependencies)

## Installation

```bash
# Create the venv (Python 3.11 required)
python3.11 -m venv xtts-env
source xtts-env/bin/activate

# Install dependencies
pip install TTS PyQt5

# The XTTS v2 model is downloaded automatically on first launch (~1.8 GB)
```

## Usage

### From the terminal

```bash
source xtts-env/bin/activate
python3 xtts_app.py
```

### Double-click (macOS .app)

Run `build_app.sh` to generate the app bundle:

```bash
bash build_app.sh
```

This creates `XTTS Voice Generator.app` — double-click to launch. Drag it to the Dock or `/Applications` for quick access.

## Structure

```
.
├── xtts_app.py          # Main app (UI + TTS backend)
├── build_app.sh         # macOS .app bundle generation
├── xtts-env/            # Python venv (not versioned)
└── xtts_output/         # Generated .wav files (default)
```

## Known Vulnerabilities

- **`torch.load(weights_only=False)`**: This app patches `torch.load` to disable the `weights_only` safety check at startup. This is required because XTTS v2 checkpoints rely on pickle-based serialization which is incompatible with `weights_only=True`. Loading a malicious model file could lead to arbitrary code execution. Only use trusted model sources.
- **`QThread.terminate()`**: The cancel button uses `QThread.terminate()` to stop generation, which is discouraged by Qt documentation as it can leave shared resources (mutexes, memory) in an inconsistent state. In practice this is low-risk since the thread only performs PyTorch inference, but it could theoretically cause instability.

## XTTS v2 Usage Rules (Coqui Public Model License)

This app uses the XTTS v2 model, released under the [Coqui Public Model License (CPML) 1.0.0](https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt). By using this application, you agree to comply with the following terms:

- **Non-commercial use only** — The XTTS v2 model may not be used for any activity that generates direct or indirect revenue.
- **Allowed uses** — Personal research, experimentation, private study, entertainment, hobby projects, and evaluation by commercial entities for non-commercial purposes.
- **Prohibited uses** — Revenue-generating activities, commercial model training, sublicensing, and redistribution without the license terms.
- **Attribution required** — You must include the CPML license terms or a link to them when distributing the model or outputs derived from it.
- **No warranty** — The model is provided "as is" with no guarantee of any kind.

> Coqui AI ceased operations in January 2024. Commercial licenses are no longer available. For any use beyond personal/non-commercial, verify the applicable license terms independently.

## Notes

- The `torch.load(weights_only=False)` patch is applied automatically at startup (required by XTTS v2)
- The first launch downloads the model (~1.8 GB) to `~/.local/share/tts/`
- Generation takes ~10-30s depending on text length (CPU)

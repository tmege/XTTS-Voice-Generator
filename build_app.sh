#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/xtts-env"

echo "=== XTTS App Builder ==="

# Activate venv
source "$VENV/bin/activate"

# Ensure PyInstaller is installed
pip install pyinstaller 2>/dev/null || true

echo "Building .app with PyInstaller..."
pyinstaller \
    --name "XTTS Voice Generator" \
    --windowed \
    --noconfirm \
    --clean \
    --hidden-import=TTS \
    --hidden-import=TTS.api \
    --hidden-import=TTS.tts.models.xtts \
    --hidden-import=torch \
    --hidden-import=PyQt5 \
    --hidden-import=PyQt5.QtMultimedia \
    --collect-all TTS \
    --collect-all torch \
    "$SCRIPT_DIR/xtts_app.py"

echo ""
echo "Build complete!"
echo "App location: $SCRIPT_DIR/dist/XTTS Voice Generator.app"
echo "You can move it to /Applications if you want."

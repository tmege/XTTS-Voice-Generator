#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="XTTS Voice Generator"
APP_DIR="$SCRIPT_DIR/$APP_NAME.app"

echo "=== XTTS App Builder ==="

# Clean previous build
rm -rf "$APP_DIR"

# Create .app bundle structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Create launcher script
cat > "$APP_DIR/Contents/MacOS/launch" << 'LAUNCHER'
#!/bin/bash
APP_DIR="$HOME/Dev/XTTS Voice Generator"
exec "$APP_DIR/xtts-env/bin/python3.11" "$APP_DIR/xtts_app.py"
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/launch"

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>XTTS Voice Generator</string>
    <key>CFBundleDisplayName</key>
    <string>XTTS Voice Generator</string>
    <key>CFBundleIdentifier</key>
    <string>com.pab7o.xtts-voice-generator</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

echo ""
echo "Build complete!"
echo "App location: $APP_DIR"
echo "You can move it to /Applications if you want."

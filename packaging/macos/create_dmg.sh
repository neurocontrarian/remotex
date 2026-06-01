#!/usr/bin/env bash
# Create a distributable DMG from the already-built Commandeck.app.
# Run after build_app.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP="$SCRIPT_DIR/dist/Commandeck.app"
VERSION="2.0.0"
DMG_NAME="Commandeck-${VERSION}-macOS-AppleSilicon.dmg"
DMG_PATH="$SCRIPT_DIR/dist/$DMG_NAME"

if [[ ! -d "$APP" ]]; then
    echo "ERROR: $APP not found. Run build_app.sh first." >&2
    exit 1
fi

echo "==> Creating $DMG_NAME"

# Remove old DMG if present
rm -f "$DMG_PATH"

# Create a temporary staging folder with the app and a symlink to /Applications
STAGING="$(mktemp -d)"
cp -R "$APP" "$STAGING/Commandeck.app"
ln -s /Applications "$STAGING/Applications"

hdiutil create \
    -volname "Commandeck $VERSION" \
    -srcfolder "$STAGING" \
    -ov \
    -format UDZO \
    "$DMG_PATH"

rm -rf "$STAGING"

echo "==> Created: $DMG_PATH"
echo "    Size:   $(du -sh "$DMG_PATH" | cut -f1)"

#!/usr/bin/env bash
# Build Commandeck.app for macOS (Apple Silicon arm64).
# Usage: ./build_app.sh [--free|--pro]  (default: --pro)
# Run from repo root or packaging/macos/. Requires Python 3.10+ and pip.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

# Parse --free / --pro flag
BUILD_TYPE="pro"
for arg in "$@"; do
    case "$arg" in
        --free) BUILD_TYPE="free" ;;
        --pro)  BUILD_TYPE="pro"  ;;
    esac
done
export COMMANDECK_PRO
[[ "$BUILD_TYPE" == "pro" ]] && COMMANDECK_PRO=1 || COMMANDECK_PRO=0

VERSION="$(python3 -c "import importlib.metadata; print(importlib.metadata.version('commandeck'))" 2>/dev/null || grep '^version' pyproject.toml | head -1 | cut -d'"' -f2)"
: "${VERSION:=2.0.0}"

echo "==> Building Commandeck $VERSION for macOS arm64 ($BUILD_TYPE)"

# --- venv ---------------------------------------------------------------
if [[ ! -d .venv-mac ]]; then
    python3 -m venv .venv-mac
fi
# shellcheck disable=SC1091
source .venv-mac/bin/activate

echo "==> Installing dependencies"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet PyInstaller

# --- ICNS ---------------------------------------------------------------
# Convert the 512×512 PNG to a proper .icns using iconutil (macOS-only tool).
echo "==> Creating Commandeck.icns"
ICONSET="$SCRIPT_DIR/Commandeck.iconset"
SRC_512="$ROOT/data/resources/icons/hicolor/512x512/apps/io.github.neurocontrarian.commandeck.png"
SRC_256="$ROOT/data/resources/icons/hicolor/256x256/apps/io.github.neurocontrarian.commandeck.png"
SRC_128="$ROOT/data/resources/icons/hicolor/128x128/apps/io.github.neurocontrarian.commandeck.png"
SRC_48="$ROOT/data/resources/icons/hicolor/48x48/apps/io.github.neurocontrarian.commandeck.png"

mkdir -p "$ICONSET"
# Required sizes for iconutil
sips -z 16  16  "$SRC_48"  --out "$ICONSET/icon_16x16.png"   >/dev/null
sips -z 32  32  "$SRC_48"  --out "$ICONSET/icon_16x16@2x.png" >/dev/null
sips -z 32  32  "$SRC_48"  --out "$ICONSET/icon_32x32.png"   >/dev/null
sips -z 64  64  "$SRC_128" --out "$ICONSET/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "$SRC_128" --out "$ICONSET/icon_128x128.png" >/dev/null
sips -z 256 256 "$SRC_256" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "$SRC_256" --out "$ICONSET/icon_256x256.png" >/dev/null
sips -z 512 512 "$SRC_512" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
cp "$SRC_512"              "$ICONSET/icon_512x512.png"
sips -z 1024 1024 "$SRC_512" --out "$ICONSET/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET" -o "$SCRIPT_DIR/Commandeck.icns"
rm -rf "$ICONSET"

# --- PyInstaller --------------------------------------------------------
echo "==> Running PyInstaller"
cd "$SCRIPT_DIR"
pyinstaller --noconfirm --clean Commandeck.spec

echo ""
echo "==> Done: $SCRIPT_DIR/dist/Commandeck.app  [$BUILD_TYPE]"
echo "    Run:  open $SCRIPT_DIR/dist/Commandeck.app"

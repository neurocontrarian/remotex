#!/usr/bin/env bash
# Build a Commandeck Qt AppImage from a PyInstaller onedir dist.
#
# Usage: ./packaging/linux/build_appimage.sh [--free|--pro]  (default: --pro)
# Run from repo root. Requires: pyinstaller, appimagetool (in PATH or
# downloaded automatically), python3 3.10+.
#
# Output: dist/Commandeck-<VERSION>-Linux-<x86_64|ARM64>.AppImage
#         dist/Commandeck-Pro-<VERSION>-Linux-<x86_64|ARM64>.AppImage  (Pro build)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

# --------------------------------------------------------------------------
# Parse --free / --pro flag
# --------------------------------------------------------------------------
BUILD_TYPE="pro"
for arg in "$@"; do
    case "$arg" in
        --free) BUILD_TYPE="free" ;;
        --pro)  BUILD_TYPE="pro"  ;;
    esac
done
export COMMANDECK_PRO
[[ "$BUILD_TYPE" == "pro" ]] && COMMANDECK_PRO=1 || COMMANDECK_PRO=0

# --------------------------------------------------------------------------
# Version — prefer $COMMANDECK_VERSION env (set by CI from the git tag),
# then pyproject.toml, then a safe fallback.
# --------------------------------------------------------------------------
if [[ -z "${COMMANDECK_VERSION:-}" ]]; then
    COMMANDECK_VERSION="$(python3 -c "import importlib.metadata; print(importlib.metadata.version('commandeck'))" 2>/dev/null \
        || grep '^version' "$ROOT/pyproject.toml" | head -1 | cut -d'"' -f2 \
        || echo "0.0.0")"
fi
# Strip leading 'v' if present (tag v2.0.9 → 2.0.9)
VERSION="${COMMANDECK_VERSION#v}"

ARCH="$(uname -m)"   # x86_64 or aarch64 — used for appimagetool/runtime downloads

# Human-friendly arch for the download filename (tooling still uses $ARCH).
case "$ARCH" in
    x86_64)  DISPLAY_ARCH="x86_64" ;;
    aarch64) DISPLAY_ARCH="ARM64" ;;
    *)       DISPLAY_ARCH="$ARCH" ;;
esac

if [[ "$BUILD_TYPE" == "pro" ]]; then
    APP_NAME="Commandeck-Pro"
else
    APP_NAME="Commandeck"
fi

APPIMAGE_FILENAME="${APP_NAME}-${VERSION}-Linux-${DISPLAY_ARCH}.AppImage"

echo "==> Building ${APPIMAGE_FILENAME}"

# --------------------------------------------------------------------------
# Step 1 — PyInstaller (onedir → dist/Commandeck/)
# --------------------------------------------------------------------------
# Bake the build version into the app so the About dialog matches the tag
# (the source fallback in _version.py is only used for local dev builds).
echo "==> Stamping version ${VERSION} into commandeck_qt/_version.py"
printf '__version__ = "%s"\n' "$VERSION" > "$ROOT/commandeck_qt/_version.py"

echo "==> Running PyInstaller"
pyinstaller --noconfirm --clean packaging/linux/Commandeck.spec

DIST_DIR="$ROOT/dist/Commandeck"
if [[ ! -d "$DIST_DIR" ]]; then
    echo "ERROR: PyInstaller onedir not found at $DIST_DIR" >&2
    exit 1
fi

# --------------------------------------------------------------------------
# Step 2 — Assemble AppDir
# --------------------------------------------------------------------------
APPDIR="$ROOT/dist/Commandeck.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/icons/hicolor/48x48/apps"

# Copy the onedir into AppDir/usr/bin/Commandeck/
cp -r "$DIST_DIR" "$APPDIR/usr/bin/Commandeck"

# Desktop file (AppImage spec requires it at AppDir root)
DESKTOP_FILE="$APPDIR/io.github.neurocontrarian.commandeck.desktop"
cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Name=Commandeck
Comment=Run local and remote commands in one click
Exec=Commandeck
Icon=io.github.neurocontrarian.commandeck
Type=Application
Categories=Utility;System;
StartupNotify=true
EOF

# Icons
ICON_SRC_256="$ROOT/data/resources/icons/hicolor/256x256/apps/io.github.neurocontrarian.commandeck.png"
ICON_SRC_48="$ROOT/data/resources/icons/hicolor/48x48/apps/io.github.neurocontrarian.commandeck.png"

cp "$ICON_SRC_256" "$APPDIR/usr/share/icons/hicolor/256x256/apps/io.github.neurocontrarian.commandeck.png"
cp "$ICON_SRC_48"  "$APPDIR/usr/share/icons/hicolor/48x48/apps/io.github.neurocontrarian.commandeck.png"

# Root-level icon copy (required by some AppImage tools)
cp "$ICON_SRC_256" "$APPDIR/io.github.neurocontrarian.commandeck.png"

# AppRun — delegates to the PyInstaller binary inside usr/bin/Commandeck/
cat > "$APPDIR/AppRun" << 'EOF'
#!/usr/bin/env bash
# AppRun for Commandeck Qt AppImage — launch the PyInstaller onedir binary.
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$SELF_DIR/usr/bin/Commandeck/Commandeck" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# --------------------------------------------------------------------------
# Step 3 — appimagetool
# --------------------------------------------------------------------------
if ! command -v appimagetool &>/dev/null; then
    echo "==> appimagetool not in PATH — downloading..."
    APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    curl -fsSL -o /tmp/appimagetool "$APPIMAGETOOL_URL"
    chmod +x /tmp/appimagetool
    APPIMAGETOOL=/tmp/appimagetool
else
    APPIMAGETOOL=appimagetool
fi

# Embed the modern static type2-runtime instead of appimagetool's default
# AppImageKit runtime. The default runtime hard-links against libfuse.so.2, so
# the produced AppImage refuses to launch ("AppImages require FUSE to run") on
# distros that ship only fuse3 (recent Ubuntu/Mint). The type2-runtime is static
# and mounts via fuse3 — same runtime the GTK full-bundle build already uses.
RUNTIME_FILE="/tmp/type2-runtime-${ARCH}"
if [[ ! -f "$RUNTIME_FILE" ]]; then
    echo "==> Downloading type2-runtime for ${ARCH}..."
    curl -fsSL -o "$RUNTIME_FILE" \
        "https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-${ARCH}"
fi

mkdir -p "$ROOT/dist"
# APPIMAGE_EXTRACT_AND_RUN avoids needing FUSE on CI runners (appimagetool is
# itself an AppImage) — same workaround as build-aux/appimage/build-fullbundle.sh.
ARCH="$ARCH" APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" \
    --runtime-file "$RUNTIME_FILE" \
    "$APPDIR" "$ROOT/dist/$APPIMAGE_FILENAME"

echo ""
echo "==> Done: dist/${APPIMAGE_FILENAME}  [${BUILD_TYPE}]"

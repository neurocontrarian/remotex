#!/bin/bash
# Development runner — no meson install required
# Usage: ./run_dev.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOURCES_XML="$SCRIPT_DIR/data/resources/remotex.gresource.xml"
GRESOURCE_OUT="/tmp/remotex.gresource"
SCHEMA_DIR="/tmp/remotex-schemas"

VENV="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV" ]; then
  echo "Creating virtual environment..."
  python3 -m venv --system-site-packages "$VENV"
fi
if ! dpkg -s librsvg2-common &>/dev/null 2>&1; then
  echo "⚠  Missing system package: librsvg2-common"
  echo "   Icons will not render correctly without it."
  echo "   Fix: sudo apt install librsvg2-common"
  echo ""
fi
if ! command -v wmctrl &>/dev/null 2>&1; then
  echo "⚠  Missing system package: wmctrl"
  echo "   'Always on top' will not work without it."
  echo "   Fix: sudo apt install wmctrl"
  echo ""
fi

echo "Checking Python dependencies..."
"$VENV/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo "Installing app icon to local icon theme..."
ICON_BASE="$SCRIPT_DIR/data/resources/icons/hicolor"
for size in 48 128 256 512; do
    ICON="$ICON_BASE/${size}x${size}/apps/com.github.remotex.RemoteX.png"
    xdg-icon-resource install --novendor --size "$size" "$ICON" com.github.remotex.RemoteX 2>/dev/null || \
      (mkdir -p "$HOME/.local/share/icons/hicolor/${size}x${size}/apps" && \
       cp "$ICON" "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/com.github.remotex.RemoteX.png")
done
gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo "Compiling GResource bundle..."
glib-compile-resources \
  --sourcedir="$SCRIPT_DIR/data/resources" \
  --target="$GRESOURCE_OUT" \
  "$RESOURCES_XML"

echo "Compiling GSettings schemas..."
mkdir -p "$SCHEMA_DIR"
cp "$SCRIPT_DIR/data/com.github.remotex.RemoteX.gschema.xml" "$SCHEMA_DIR/"
glib-compile-schemas "$SCHEMA_DIR"

echo "Starting RemoteX..."
export GSETTINGS_SCHEMA_DIR="$SCHEMA_DIR:/usr/share/glib-2.0/schemas"

cd "$SCRIPT_DIR/src"

"$VENV/bin/python3" -c "
import os, sys, traceback
sys.path.insert(0, os.getcwd())

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio

resource = Gio.Resource.load('/tmp/remotex.gresource')
resource._register()

try:
    from main import main
    sys.exit(main())
except Exception:
    traceback.print_exc()
    sys.exit(1)
"

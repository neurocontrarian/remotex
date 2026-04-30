"""Unified icon loader for RemoteX.

Loading priority per icon name:
  1. Custom user directories  (GSettings icon-search-paths)  — .png then .svg
  2. Bundled Bootstrap Icons   (GResource)                    — .svg via cairosvg
  3. System icon theme         (existing resolve_icon logic)  — GTK fallback

SVG rendering uses cairosvg → PNG bytes → Gdk.Texture, bypassing GdkPixbuf
entirely (GdkPixbuf PNG loading is broken in this PyGObject/system combo).
"""

import os

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gdk, GLib, Gio

_RESOURCE_PREFIX = '/com/github/remotex/RemoteX/bootstrap'


# ── cairosvg rendering ────────────────────────────────────────────────────────

def _svg_to_texture(svg_bytes: bytes, size: int):
    """Render raw SVG bytes to a Gdk.Texture using cairosvg.

    Bootstrap Icons use fill="currentColor". Without a CSS context cairosvg
    may resolve that to transparent, so we replace it with black explicitly.
    """
    try:
        import cairosvg
    except ImportError:
        return None
    try:
        svg_text = svg_bytes.decode('utf-8').replace('currentColor', 'black')
        png = cairosvg.svg2png(
            bytestring=svg_text.encode('utf-8'),
            output_width=size,
            output_height=size,
        )
        if not png:
            return None
        return Gdk.Texture.new_from_bytes(GLib.Bytes.new(png))
    except Exception:
        return None


# ── per-source loaders ────────────────────────────────────────────────────────

def _from_file(path: str, size: int):
    """Load a PNG or SVG file into a Gdk.Texture."""
    if path.endswith('.png'):
        try:
            return Gdk.Texture.new_from_file(Gio.File.new_for_path(path))
        except Exception:
            return None
    if path.endswith('.svg'):
        try:
            with open(path, 'rb') as f:
                return _svg_to_texture(f.read(), size)
        except Exception:
            return None
    return None


def _from_resource(icon_name: str, size: int):
    """Load a bundled Bootstrap Icon (SVG) from GResource via cairosvg."""
    try:
        data = Gio.resources_lookup_data(
            f'{_RESOURCE_PREFIX}/{icon_name}.svg',
            Gio.ResourceLookupFlags.NONE,
        )
        if data:
            return _svg_to_texture(bytes(data.get_data()), size)
    except Exception:
        pass
    return None


# ── public API ────────────────────────────────────────────────────────────────

def load_icon_texture(icon_name: str, size: int,
                      extra_dirs: list[str] | None = None):
    """Return a Gdk.Texture for icon_name at the requested pixel size, or None.

    Callers should fall back to Gtk.Image.set_from_icon_name() when None is returned.

    extra_dirs: additional directories to search (in order) before the GResource.
                GSettings icon-search-paths are always prepended automatically.
    """
    if not icon_name:
        return None

    # Collect search directories: GSettings paths + caller-supplied extra
    search_dirs: list[str] = []
    try:
        settings = Gio.Settings.new('com.github.remotex.RemoteX')
        search_dirs.extend(settings.get_strv('icon-search-paths'))
    except Exception:
        pass
    if extra_dirs:
        search_dirs.extend(extra_dirs)

    # 1. Custom / extra directories
    for directory in search_dirs:
        if not os.path.isdir(directory):
            continue
        for ext in ('.png', '.svg'):
            path = os.path.join(directory, icon_name + ext)
            if os.path.isfile(path):
                t = _from_file(path, size)
                if t:
                    return t

    # 2. Bundled GResource Bootstrap Icons
    return _from_resource(icon_name, size)


def bundled_icon_names() -> list[str]:
    """Return the list of icon names available in the bundled Bootstrap Icons set."""
    try:
        children = Gio.resources_enumerate_children(
            _RESOURCE_PREFIX, Gio.ResourceLookupFlags.NONE
        )
        return [name.removesuffix('.svg') for name in children if name.endswith('.svg')]
    except Exception:
        return []

import html
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

from models.command_button import CommandButton
from i18n import _

_FALLBACK_ICON = "utilities-terminal-symbolic"
_svg_support_cache: bool | None = None


def _has_svg_support() -> bool:
    """Return True only if GdkPixbuf can actually decode an SVG in memory.

    Checking get_formats() is unreliable — the loader may be listed but broken.
    The only authoritative test is to actually try decoding a minimal SVG.
    """
    global _svg_support_cache
    if _svg_support_cache is not None:
        return _svg_support_cache
    try:
        gi.require_version('GdkPixbuf', '2.0')
        from gi.repository import GdkPixbuf, Gio, GLib
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>'
        stream = Gio.MemoryInputStream.new_from_bytes(GLib.Bytes.new(svg))
        GdkPixbuf.Pixbuf.new_from_stream(stream, None)
        _svg_support_cache = True
    except Exception:
        _svg_support_cache = False
    return _svg_support_cache


def resolve_icon(icon_name: str) -> str:
    """Return icon_name if renderable on this system, else return the fallback.

    Two failure modes are handled:
    - GResource SVGs (resource:// or bare /org/ path): GTK's own recolor engine
      fails on many Linux systems independently of librsvg2.
    - File-based SVGs (file://): require GdkPixbuf SVG loader to be registered.
      Even when librsvg2-common is installed the loader cache may be stale.
    """
    if not icon_name:
        return _FALLBACK_ICON
    display = Gdk.Display.get_default()
    if display is None:
        return icon_name
    theme = Gtk.IconTheme.get_for_display(display)
    paintable = theme.lookup_icon(icon_name, None, 48, 1,
                                  Gtk.TextDirection.NONE, 0)
    if paintable is None:
        return _FALLBACK_ICON
    f = paintable.get_file()
    if f is not None:
        uri = f.get_uri() or f.get_path() or ""
        if uri.endswith(".svg"):
            is_file = uri.startswith("file://")
            if not is_file or not _has_svg_support():
                return _FALLBACK_ICON
    return icon_name


@Gtk.Template(resource_path='/com/github/remotex/RemoteX/ui/button_tile.ui')
class ButtonTile(Gtk.Button):
    __gtype_name__ = 'ButtonTile'

    tile_icon = Gtk.Template.Child()
    tile_label = Gtk.Template.Child()
    tile_spinner = Gtk.Template.Child()

    _ICON_SIZES = {"small": 20, "medium": 32, "large": 48}

    def __init__(self, command_button: CommandButton, size: str = "medium", **kwargs):
        super().__init__(**kwargs)
        self.command_button = command_button
        self._size = size
        self._css_provider = None
        self._apply_style()

    def _apply_style(self):
        # Label text — use Pango markup for text color (CSS cascade to child labels
        # is unreliable in GTK4 with per-widget providers)
        display_name = _(self.command_button.name)
        name_escaped = html.escape(display_name)
        if self.command_button.text_color:
            self.tile_label.set_markup(
                f'<span foreground="{self.command_button.text_color}">{name_escaped}</span>'
            )
        else:
            self.tile_label.set_text(display_name)

        self._load_icon()
        self._update_tooltip()

        # Visibility: icon-only / text-only modes
        self.tile_label.set_visible(not self.command_button.hide_label)
        self.tile_icon.set_visible(not self.command_button.hide_icon)

        # Size class
        for s in ("size-small", "size-medium", "size-large"):
            self.remove_css_class(s)
        self.add_css_class(f"size-{self._size}")

        # Dynamic CSS for background color
        if self.command_button.color:
            self._css_provider = Gtk.CssProvider()
            self._css_provider.load_from_data(
                f"button.button-tile {{ background-color: {self.command_button.color}; }}".encode()
            )
            self.get_style_context().add_provider(
                self._css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def _load_icon(self):
        """Load icon: custom dirs → bundled Bootstrap Icons → system theme."""
        import sys
        icon_name = self.command_button.icon_name
        size = self._ICON_SIZES.get(self._size, 32)

        # 1. Custom dirs + bundled Bootstrap Icons via cairosvg
        try:
            from utils.icon_loader import load_icon_texture
            texture = load_icon_texture(icon_name, size)
            if texture is not None:
                self.tile_icon.set_from_paintable(texture)
                self.tile_icon.set_pixel_size(size)
                return
        except Exception as e:
            print(f'[RemoteX] icon_loader error for "{icon_name}": {e}', file=sys.stderr)

        # 2. System icon theme fallback
        resolved = resolve_icon(icon_name)
        self.tile_icon.set_from_icon_name(resolved)
        self.tile_icon.set_pixel_size(size)

    def _update_tooltip(self):
        btn = self.command_button
        if btn.tooltip:
            lines = [html.escape(_(btn.tooltip))]
        else:
            lines = [f'<tt>{html.escape(btn.command)}</tt>']
        remote_ids = [mid for mid in btn.machine_ids if mid]
        if remote_ids:
            if len(btn.machine_ids) > 1:
                lines.append(f'<small>{html.escape(_("Multi-machine — asks which one at run time"))}</small>')
            else:
                lines.append(f'<small>{html.escape(_("Remote execution"))}</small>')
        if btn.confirm_before_run:
            lines.append(f'<small>{html.escape(_("Asks for confirmation before running"))}</small>')
        self.set_tooltip_markup('\n'.join(lines))

    def set_selected(self, selected: bool) -> None:
        """Toggle the 'selected' CSS class (multi-select mode)."""
        if selected:
            self.add_css_class('selected')
        else:
            self.remove_css_class('selected')

    def set_running(self, running: bool):
        """Show/hide spinner and toggle the 'running' CSS class."""
        self.tile_spinner.set_visible(running)
        self.tile_spinner.set_spinning(running)
        self.tile_icon.set_visible(not running and not self.command_button.hide_icon)
        self.set_sensitive(not running)
        if running:
            self.add_css_class('running')
        else:
            self.remove_css_class('running')

    def flash_result(self, success: bool):
        """Briefly apply success/error CSS class, then revert after 1.5s."""
        css_class = 'success' if success else 'error'
        self.add_css_class(css_class)
        GLib.timeout_add(1500, self._remove_flash_class, css_class)

    def _remove_flash_class(self, css_class: str) -> bool:
        self.remove_css_class(css_class)
        return GLib.SOURCE_REMOVE

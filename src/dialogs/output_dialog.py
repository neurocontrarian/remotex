import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from services.executor import ExecutionResult
from i18n import _


def show_output_dialog(parent, button_name: str, result: ExecutionResult):
    """Show command output (stdout/stderr) in an independent window."""
    win = Adw.Window(title=button_name)
    win.set_default_size(600, 400)

    toolbar_view = Adw.ToolbarView()
    header = Adw.HeaderBar()
    toolbar_view.add_top_bar(header)

    scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
    text_view = Gtk.TextView(
        editable=False,
        monospace=True,
        wrap_mode=Gtk.WrapMode.WORD_CHAR,
        top_margin=12,
        bottom_margin=12,
        left_margin=12,
        right_margin=12,
    )

    output = result.stdout
    if result.stderr:
        if output:
            output += '\n--- stderr ---\n'
        output += result.stderr

    if not output:
        output = _('(no output)')

    text_view.get_buffer().set_text(output)
    scrolled.set_child(text_view)

    status = Gtk.Label(
        label=f'{"✓" if result.success else "✗"}  Exit {result.return_code}  —  {result.duration_ms}ms',
        xalign=0,
        margin_start=12,
        margin_end=12,
        margin_top=6,
        margin_bottom=6,
    )
    status.add_css_class('caption')

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.append(scrolled)
    box.append(Gtk.Separator())
    box.append(status)

    toolbar_view.set_content(box)
    win.set_content(toolbar_view)
    if parent:
        win.set_transient_for(parent)
    from utils.desktop import apply_always_on_top
    win.connect('realize', lambda w: apply_always_on_top(w))
    win.present()

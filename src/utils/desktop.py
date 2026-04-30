import subprocess


def apply_always_on_top(win):
    """Set always-on-top on a Gtk.Window via wmctrl (X11 only, no-op elsewhere)."""
    try:
        from gi.repository import GdkX11
        surface = win.get_surface()
        if isinstance(surface, GdkX11.X11Surface):
            xid = surface.get_xid()
            subprocess.Popen(
                ['wmctrl', '-i', '-r', hex(xid), '-b', 'add,above'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            return
    except Exception:
        pass
    # Fallback by window title
    try:
        title = win.get_title() or ''
        if title:
            subprocess.Popen(
                ['wmctrl', '-r', title, '-b', 'add,above'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass


def make_floating_window(win, parent, width: int, height: int):
    """Configure win as a floating top-level window and queue always-on-top."""
    win.set_default_size(width, height)
    if parent:
        win.set_transient_for(parent)
    win.connect('realize', lambda w: apply_always_on_top(w))

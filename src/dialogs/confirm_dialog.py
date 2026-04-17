import html
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw
from typing import Callable

from models.command_button import CommandButton
from i18n import _


def show_confirm_dialog(parent, button: CommandButton, on_confirm: Callable):
    """Show a confirmation dialog before running a command."""
    dialog = Adw.AlertDialog(
        heading=f'Run "{button.name}"?',
        body=f'<tt>{html.escape(button.command)}</tt>',
        body_use_markup=True,
    )
    dialog.add_response('cancel', _('Cancel'))
    dialog.add_response('run', _('Run'))
    dialog.set_response_appearance('run', Adw.ResponseAppearance.SUGGESTED)
    dialog.set_default_response('run')
    dialog.set_close_response('cancel')

    def on_response(dlg, response):
        if response == 'run':
            on_confirm()

    dialog.connect('response', on_response)
    dialog.present(parent)

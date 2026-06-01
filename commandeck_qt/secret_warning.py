"""One-shot warning when a secret had to be stored without an OS keychain.

Per the 2026-05-29 secrets design: secrets go to the OS keychain; if none is
available we fall back to an obfuscated local file (never in backups) and MUST
warn the user that obfuscation is not strong encryption.
"""
from PySide6.QtWidgets import QMessageBox

from commandeck_core.i18n import _


def warn_if_no_keychain(parent, password_was_set: bool) -> None:
    if not password_was_set:
        return
    from commandeck_core.services import secret_store
    if secret_store.keyring_available():
        return
    QMessageBox.warning(
        parent,
        _("Password saved without a system keychain"),
        _("No system keychain (e.g. GNOME Keyring / KWallet) is available, so this "
          "password was saved in an obfuscated local file — that is not strong "
          "encryption. It is never included in backups. For stronger protection, "
          "use an SSH key instead, or enable your desktop keychain."),
    )

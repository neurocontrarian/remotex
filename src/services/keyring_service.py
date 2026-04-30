"""Keyring service — stores sudo passwords in the system Secret Service (GNOME Keyring / KWallet).

Passwords are never written to disk by this module. The TOML profile only
stores a boolean flag (has_sudo_password) to know whether a secret exists.
"""

_SERVICE_NAME = "remotex"
_ATTRIBUTE_KEY = "remotex_profile_id"


def is_available() -> bool:
    """Return True if the Secret Service is reachable."""
    try:
        import secretstorage
        conn = secretstorage.dbus_init()
        secretstorage.get_default_collection(conn)
        return True
    except Exception:
        return False


def store_password(profile_id: str, password: str) -> None:
    import secretstorage
    conn = secretstorage.dbus_init()
    collection = secretstorage.get_default_collection(conn)
    if collection.is_locked():
        collection.unlock()
    attrs = {_ATTRIBUTE_KEY: profile_id}
    collection.create_item(
        f"RemoteX sudo — {profile_id}",
        attrs,
        password,
        replace=True,
    )


def get_password(profile_id: str) -> str | None:
    try:
        import secretstorage
        conn = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(conn)
        if collection.is_locked():
            return None
        attrs = {_ATTRIBUTE_KEY: profile_id}
        items = list(collection.search_items(attrs))
        if items:
            return items[0].get_secret().decode()
        return None
    except Exception:
        return None


def delete_password(profile_id: str) -> None:
    try:
        import secretstorage
        conn = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(conn)
        if collection.is_locked():
            return
        attrs = {_ATTRIBUTE_KEY: profile_id}
        for item in collection.search_items(attrs):
            item.delete()
    except Exception:
        pass

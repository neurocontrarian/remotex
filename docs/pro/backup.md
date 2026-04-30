# Backup & Restore

!!! tip "Pro feature"
    Config backup and restore requires [RemoteX Pro](../pro.md).

RemoteX provides two separate export formats, intentionally kept apart for security reasons.

Access both from **Preferences → (scroll to bottom)**.

---

## Buttons & Settings backup — `.rxbackup`

This archive contains:

- `buttons.toml` — all your buttons and their configuration
- `gsettings.json` — all Preferences settings (columns, button size, theme, language, etc.)

### When to use it

- Before a major change (deleting many buttons, reorganising categories)
- When migrating RemoteX to a new computer
- As a periodic snapshot of your button library

### Exporting

Click **Export Buttons & Settings**. A file picker opens. Choose a location and save the `.rxbackup` file.

### Importing

Click **Import Buttons & Settings**. Select a `.rxbackup` file. RemoteX **merges** the imported buttons with your current buttons — it does not wipe your existing configuration first.

!!! note
    Default buttons (Linux Essentials, Development) seeded by RemoteX are never overwritten during import — newly added defaults from a later version are preserved.

---

## Machines backup — `.rxmachines`

This archive contains:

- `machines.toml` — all SSH machine definitions (name, host, user, port, key path, icon)

### What is NOT included

SSH **private keys** are never exported. The archive only stores the path to the key file (`~/.ssh/id_ed25519`), not the key itself.

!!! warning
    The `.rxmachines` file contains hostnames, IP addresses, SSH usernames, and port numbers. Treat it like any network configuration file — do not share it publicly or store it in an unencrypted public location.

### When to use it

- When setting up RemoteX on a second computer (you still need to copy the SSH keys separately)
- As a record of your server infrastructure configuration

### Exporting

Click **Export Machines**. Choose a location and save the `.rxmachines` file.

### Importing

Click **Import Machines**. Select a `.rxmachines` file. Machines are merged with any existing machines. Duplicates (same host + user combination) are skipped.

---

## Restoring on a new computer

Full migration checklist:

1. Install RemoteX on the new machine
2. Copy your SSH private keys to `~/.ssh/` on the new machine (use `scp` or a USB drive — keep them secure)
3. Activate your Pro license in Preferences
4. Import the `.rxbackup` file to restore buttons and settings
5. Import the `.rxmachines` file to restore machine definitions
6. Test each machine connection from **Menu → Manage Machines → (select machine) → Test**

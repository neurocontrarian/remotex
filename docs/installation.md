# Installation

Commandeck runs on **Linux, macOS, and Windows**. Every release lists the files for all
three platforms together:
**[GitHub Releases](https://github.com/neurocontrarian/commandeck/releases/latest)** —
that link always points to the newest version, so bookmark it.

All **Pro** builds include a **14-day free trial** — no account, no card. The trial
starts automatically on first launch.

---

## Linux (AppImage)

One file, no installation. Download it, make it executable, and run it. The AppImage is
**self-contained** — it bundles Python, Qt, and every dependency, so there is nothing to
install on the host.

| File | When to use |
|------|-------------|
| `Commandeck-VERSION-Linux-x86_64.AppImage` | **Free — Intel/AMD.** |
| `Commandeck-VERSION-Linux-ARM64.AppImage` | **Free — ARM64** (Raspberry Pi 4+, ARM server, Apple Silicon VM). |
| `Commandeck-Pro-VERSION-Linux-x86_64.AppImage` | **Pro — Intel/AMD.** 14-day trial included. |
| `Commandeck-Pro-VERSION-Linux-ARM64.AppImage` | **Pro — ARM64.** 14-day trial included. |

Not sure which CPU you have? Run `uname -m` — `x86_64` for Intel/AMD, `aarch64` for ARM.

```bash
chmod +x Commandeck-*.AppImage
./Commandeck-*.AppImage
```

If your distro reports a missing Qt platform plugin on launch, install `libxcb-cursor0`:

=== "Debian / Ubuntu / Linux Mint"

    ```bash
    sudo apt install libxcb-cursor0
    ```

=== "Fedora"

    ```bash
    sudo dnf install xcb-util-cursor
    ```

=== "Arch Linux"

    ```bash
    sudo pacman -S xcb-util-cursor
    ```

---

## macOS (Apple Silicon)

| File | When to use |
|------|-------------|
| `Commandeck-VERSION-macOS-AppleSilicon.dmg` | **Free.** |
| `Commandeck-Pro-VERSION-macOS-AppleSilicon.dmg` | **Pro.** 14-day trial included. |

Open the `.dmg` and drag **Commandeck** into Applications.

The app is **not yet code-signed**, so on first launch macOS Gatekeeper will block it.
Right-click the app → **Open** (then confirm), or run:

```bash
xattr -dr com.apple.quarantine /Applications/Commandeck.app
```

---

## Windows (x86_64)

| File | When to use |
|------|-------------|
| `Commandeck-VERSION-Windows-x64.exe` | **Free** — installer (Start-menu shortcut + uninstaller). |
| `Commandeck-Pro-VERSION-Windows-x64.exe` | **Pro** installer. 14-day trial included. |

Run the installer. It is **not yet code-signed**, so SmartScreen may warn you: click
**More info → Run anyway**.

---

## From source

For users who prefer installing from source or want to contribute. Works on all three
platforms.

### Requirements

- Python 3.10 or later
- On Linux: install `libxcb-cursor0` if Qt reports a missing platform plugin
  (`sudo apt install libxcb-cursor0` on Debian/Ubuntu/Mint)

### Clone and run

```bash
git clone https://github.com/neurocontrarian/commandeck.git
cd commandeck
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python3 -m commandeck_qt
```

The first launch seeds your button grid with ready-to-use default buttons.

## Updating

```bash
cd commandeck
git pull
pip install -e ".[dev]"
python3 -m commandeck_qt
```

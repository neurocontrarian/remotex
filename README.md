# Commandeck

**Run your commands — on any machine — in one click.**

Stop retyping the same commands every day. Commandeck gives you a desktop button grid —
click once, your command runs locally or on a remote server over SSH. No terminal required.

[![Demo](docs/assets/demo_preview.gif)](https://raw.githubusercontent.com/neurocontrarian/commandeck/main/docs/assets/demo.mp4)
*▶ Click to watch the demo*

**[Documentation](https://neurocontrarian.github.io/commandeck)** ·
**[Download](https://github.com/neurocontrarian/commandeck/releases/latest)** ·
**[Get Pro →](https://neurocontrarian.lemonsqueezy.com/checkout/buy/9c16845a-8ab6-4a36-b8da-9874d9d64f33)**

---

## New to the terminal?

Memorizing commands is tedious. Commandeck gives you a dashboard of buttons for the
things you do every day — check disk space, update your system, reboot — without
typing a single command.

**Commandeck ships with ready-to-use buttons** the moment you install it. No setup,
no configuration. Open the app, click a button, done.

When you're ready to go further, creating your own button takes 30 seconds: paste a
command, give it a name, pick an icon. That's it.

---

## Managing servers?

Commandeck turns your SSH connections into one-click operations.

Assign any button to one or more remote machines. Click — the command runs over SSH
and the output appears instantly. No more opening a terminal, logging in, and
retyping the same command you ran yesterday on three different servers.

- Run the same command across multiple machines with a single click
- Organize buttons by host, environment, or team
- Output shows in a clean dialog, or opens directly in a terminal

If you live in the terminal, Commandeck doesn't replace it — it handles the repetitive
parts so you can focus on what actually needs thinking.

---

## Shaped by the community

The buttons that ship with Commandeck came from real workflows. The goal is for that
list to keep growing: as users share what they've added, the most useful commands
become part of the default set — so every new user starts with a better toolkit.

**Have a command worth sharing?** Drop it in
[Discussions](https://github.com/neurocontrarian/commandeck/discussions) — the criteria
are simple: works reliably, clearly useful, produces readable output.

---

## Free & Pro

Commandeck is free. No account, no telemetry, no expiry on the free tier.

The **Pro tier** ($29/year) removes limits on custom buttons and unlocks SSH machine
management, multi-machine dispatch, button themes, config backup/restore, and an MCP
server for AI assistant integration.

**Try Pro free for 14 days** — download the Pro build below and the trial starts
automatically. No card, no email required.

| | Free | Pro |
|--|------|-----|
| Local command execution | Unlimited | Unlimited |
| Default buttons (use & delete) | ✓ | ✓ |
| Default buttons (edit) | — | ✓ |
| Custom buttons | Up to 3 | Unlimited |
| SSH machines | — | Unlimited |
| Multi-machine buttons | — | ✓ |
| Multi-select + group actions | — | ✓ |
| Button themes | 1 (Bold) | 6 + custom CSS |
| Config backup / restore | — | ✓ |
| MCP server (AI integration) | — | ✓ |

**[Get a Pro license →](https://neurocontrarian.lemonsqueezy.com/checkout/buy/9c16845a-8ab6-4a36-b8da-9874d9d64f33)**

### Why a paid Pro tier?

Commandeck is built and maintained by one person. The free tier is genuinely useful and
will stay free. Pro licenses fund the time it takes to build new features, test on
multiple platforms, write documentation, and keep everything working across OS updates.

The core is open source (AGPLv3). Your buttons and config are plain text files on your
own machine — no cloud, no account, no lock-in. Pro is about what gets built *next*.

---

## Installation

> **The latest version for every platform is always here:
> [github.com/neurocontrarian/commandeck/releases/latest](https://github.com/neurocontrarian/commandeck/releases/latest)**
> That link never changes — bookmark it. Each release page lists Linux, macOS and
> Windows files together. Download the one for your system.

All **Pro** builds include a **14-day free trial** — no account, no card required.
The trial starts automatically on first launch.

### Linux (AppImage)

| File | When to use |
|------|-------------|
| `Commandeck-VERSION-Linux-x86_64.AppImage` | **Free — Intel/AMD.** |
| `Commandeck-VERSION-Linux-ARM64.AppImage` | **Free — ARM64** (Raspberry Pi, ARM server). |
| `Commandeck-Pro-VERSION-Linux-x86_64.AppImage` | **Pro — Intel/AMD.** 14-day trial included. |
| `Commandeck-Pro-VERSION-Linux-ARM64.AppImage` | **Pro — ARM64.** 14-day trial included. |

```bash
chmod +x Commandeck-*.AppImage
./Commandeck-*.AppImage
```

### macOS (Apple Silicon)

| File | When to use |
|------|-------------|
| `Commandeck-VERSION-macOS-AppleSilicon.dmg` | **Free.** |
| `Commandeck-Pro-VERSION-macOS-AppleSilicon.dmg` | **Pro.** 14-day trial included. |

The app is **not yet code-signed**, so on first launch macOS Gatekeeper will block it.
Right-click the app → **Open** (then confirm), or run
`xattr -dr com.apple.quarantine /Applications/Commandeck.app`.

### Windows (x86_64)

| File | When to use |
|------|-------------|
| `Commandeck-VERSION-Windows-x64.exe` | **Free** — Inno Setup installer (Start menu shortcut + uninstaller). |
| `Commandeck-Pro-VERSION-Windows-x64.exe` | **Pro** installer. 14-day trial included. |

The installer is **not yet code-signed**, so SmartScreen may warn: click
**More info → Run anyway**.

### From source

```bash
git clone https://github.com/neurocontrarian/commandeck.git
cd commandeck
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python3 -m commandeck_qt
```

Requires Python 3.10+. On Linux, also install `libxcb-cursor0` if Qt reports a
missing platform plugin (`sudo apt install libxcb-cursor0` on Debian/Ubuntu/Mint).

---

## Features

<details>
<summary>Full feature list</summary>

### Button grid
- Auto-reflowing button grid — three button sizes
- Per-button: background color, text color, icon, label, tooltip
- Hide label (icon only) or hide icon (text only)
- Categories with filterable tab bar — right-click to hide a category
- Search bar · keyboard shortcuts

### Command execution
- **Local** — runs a shell command on your machine (bash/sh on Linux/macOS, PowerShell on Windows)
- **SSH** — via Fabric/Paramiko, key-based auth, no passwords stored in plaintext
- Three output modes: **Silent** (toast notification), **Show output** (dialog), **Open in terminal**
- Optional confirmation dialog before sensitive commands
- Configurable timeout (5–300 s)

### SSH & machines *(Pro)*
- Unlimited SSH machines (host, user, port, key)
- Machine icons (desktop, laptop, server, router…)
- Multi-machine buttons — picker dialog at run time
- SSH key generation and server copy built in — including in-app host fingerprint verification

### Multi-select *(Pro)*
- Click and rubber-band selection
- Group actions: delete, change category, assign machine

### Appearance
- Per-button colors (background + text) — 40-color palette
- Six themes: Bold, Cards, Phone keys, Neon, Tron, Retro *(Pro)*
- Custom CSS targeting `QFrame#ButtonTile` (Qt Style Sheets) *(Pro)*
- Light / Dark / System color scheme

### MCP server *(Pro)*
Built-in [MCP](https://modelcontextprotocol.io) server — AI assistants (Claude
Desktop, Cursor…) can read, create, and run your buttons. 17 tools. Disabled by
default; enable in Preferences → Desktop Integration.

### Other
- Always on top · Launch at login
- 11 interface languages
- Config backup / restore *(Pro)*

</details>

---

## Tech stack

| Component | Choice |
|-----------|--------|
| GUI | Python 3.10+ / PySide6 (Qt6) |
| SSH | Fabric 3.x / Paramiko |
| Config | TOML (plain text, platform config dir) |
| Packaging | PyInstaller + AppImage (Linux), DMG (macOS), Inno Setup (Windows) |

---

## License

Commandeck is **open core**:

- **Core — GNU AGPLv3** (see [LICENSE](LICENSE)): free software you can use, study, modify, and share. Modified versions you distribute (or run as a network service) must also be released under the AGPLv3.
- **Pro features** (`commandeck_core/pro/`) — proprietary, All Rights Reserved (see [LICENSE-PRO](LICENSE-PRO.md)).

Contributions are accepted under a [Contributor License Agreement](CLA.md). The **Commandeck** name and logo are trademarks of the author and are not licensed under the AGPL.

[Terms](https://neurocontrarian.github.io/commandeck/legal/terms/) ·
[Privacy](https://neurocontrarian.github.io/commandeck/legal/privacy/) ·
[Refund](https://neurocontrarian.github.io/commandeck/legal/refund/)

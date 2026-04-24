# RemoteX

**A visual command launcher for Linux — run local and SSH commands with one click.**

**[Full documentation](https://neurocontrarian.github.io/remotex)**

> No more typing the same commands over and over. Build a button grid for the tasks you repeat every day.

<video src="docs/assets/demo.mp4" controls width="100%"></video>

---

## What is RemoteX?

RemoteX is a GTK4 desktop app that lets you create a grid of clickable buttons, each running a shell command — locally or on a remote server over SSH.

**If you're new to Linux:** RemoteX ships with 34 ready-to-use buttons for the most common tasks (disk usage, system update, temperature…). No terminal needed.

**If you manage servers:** assign buttons to one or more SSH machines, launch commands across your infrastructure with a single click, and see the output in a clean dialog.

---

## Features

### Button grid

- Drag-and-drop reordering
- Configurable grid size (1–20 columns) and three button sizes: Small / Medium / Large
- Per-button: background color, text color, icon, label, tooltip
- Hide label (icon only) or hide icon (text only) per button
- Categories with a filterable tab bar — right-click a category to hide it

<!-- [SCREENSHOT: grid with mixed colors, category bar showing "All / Linux Essentials / Development"] -->

### Command execution

- **Local execution** — runs directly in a shell on your machine
- **SSH execution** — runs on a remote server via Fabric/Paramiko (key-based auth, no passwords stored)
- Three output modes per button: **Silent** (toast notification), **Show output** (dialog), **Open in terminal**
- Optional confirmation dialog before running sensitive commands
- Configurable command timeout (5–300 s)

### Default buttons

RemoteX ships with **34 ready-to-use buttons** across two categories, visible and usable immediately on the free tier:

**Linux Essentials** (20 buttons) — Disk Usage, Memory, CPU Load, Temperature, Running Processes, Network Interfaces, Open Ports, Block Devices, System Update, Reboot, Shutdown, and more.

**Development** (14 buttons) — Git Status/Log/Diff, Docker PS/Images/Clean, Python/Node versions, Disk I/O, Listening Services, and more.

All commands are cross-distro (apt / dnf / pacman).

### SSH machines *(Pro)*

- Unlimited SSH machines (host, user, port, SSH key)
- Machine icons (desktop, laptop, server, router…)
- Assign a button to **multiple machines** — a picker dialog lets you choose at run time
- SSH key generation and copy-to-server built in

<!-- [SCREENSHOT: machine picker dialog showing 3 machines] -->

### Multi-select *(Pro)*

- Toggle select mode from the header bar
- Rubber-band (click and drag) selection on empty space
- Group actions on the selection: **Delete**, **Change category**, **Assign machine**

<!-- [SCREENSHOT: select mode with 4 buttons highlighted and the action bar at the bottom] -->

### Appearance

- Per-button color overrides (background + text) with a 40-color GNOME palette
- Five built-in button themes: Bold, Cards, Phone keys, Neon, Retro *(Pro)*
- Custom CSS theme — write your own `.css` targeting `.button-tile` *(Pro)*
- Light / Dark / System color scheme

<!-- [SCREENSHOT: side-by-side of Bold vs Neon theme] -->

### MCP server

RemoteX includes a built-in [MCP](https://modelcontextprotocol.io) server so AI assistants (Claude Desktop, Cursor…) can read and edit your button configuration.

Enable it in **Preferences → Desktop Integration → Allow MCP access** (disabled by default).

Available tools: `list_buttons`, `get_button`, `create_button`, `update_button`, `list_categories`, `list_machines`. Deletion is intentionally not available via MCP.

Add to your MCP client config (e.g. `~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "remotex": {
      "command": "python3",
      "args": ["/path/to/remotex/src/mcp_server.py"]
    }
  }
}
```

### Other

- Search bar (filter buttons by name)
- Keyboard shortcuts: `Ctrl+N` add button · `Ctrl+,` preferences · `Ctrl+?` shortcuts · `Ctrl+Q` quit
- Window state persistence (size, maximized)
- Always on top
- Launch at login (autostart)
- 11 interface languages: English, French, German, Spanish, Italian, Korean, Japanese, Chinese, Russian, Portuguese, Arabic, Hindi

---

## RemoteX Pro

RemoteX is free for everyday local use. The Pro tier removes limits and unlocks power-user features.

| | Free | Pro |
|--|------|-----|
| Local command execution | Unlimited | Unlimited |
| Default buttons (use) | Unlimited | Unlimited |
| Default buttons (edit) | Read-only | Editable |
| Custom buttons | **3** | Unlimited |
| SSH machines | — | Unlimited |
| Multi-machine buttons | — | ✓ |
| Multi-select | — | ✓ |
| Button themes | Bold only | All 5 + custom CSS |
| Config backup / restore | — | ✓ |

**Pricing:** $20/year or $40 lifetime — [get a license →](https://github.com/flelard/remotex)

Activate in **Preferences → License → Activate Pro**.

> Free tier limits apply per device. Default buttons are always visible, executable and deletable on the free tier — only editing them requires Pro.

---

## Installation

### Quick start (from source)

**Requirements:** Python 3.10+, GTK 4, libadwaita

```bash
git clone https://github.com/flelard/remotex.git
cd remotex
./run_dev.sh
```

`run_dev.sh` creates a virtual environment, installs Python dependencies (`fabric`, `tomli_w`, `paramiko`), compiles the GSettings schema, and launches the app. No system-wide install needed.

On Debian/Ubuntu, install the GTK runtime if missing:

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libgtk-4-1 \
  python3-gi-cairo libglib2.0-bin
```

### Flatpak *(coming soon)*

A Flatpak package will be published on Flathub.

---

## Tech stack

| Component | Choice |
|-----------|--------|
| GUI | Python 3.10+ / GTK4 / libadwaita |
| SSH | Fabric 3.x (Paramiko) |
| Config | TOML (`tomllib` + `tomli_w`) |
| Build | Meson |

---

## Contributing

### Default button ideas

RemoteX ships with 34 built-in buttons (Linux Essentials, Development). If you have ideas for useful commands that should be included by default, share them in the [Discussions](https://github.com/neurocontrarian/remotex/discussions) section on GitHub.

Good candidates: cross-distro commands, broadly useful for beginners or sysadmins, with clear output.

---

## License

The core of RemoteX is released under the **MIT License** — see [LICENSE](LICENSE).

Pro features (`src/pro/`) are proprietary — All Rights Reserved.

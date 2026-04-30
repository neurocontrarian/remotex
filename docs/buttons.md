# Buttons

## Default buttons

RemoteX ships with **34 ready-to-use buttons** seeded on first launch. They are visible, executable and deletable on the free tier.

### Linux Essentials (20 buttons)

| Button | Command |
|--------|---------|
| Disk Usage | `df -h` |
| Memory Usage | `free -h` |
| CPU Load | `uptime` + `top` snapshot |
| Temperature | `sensors` (requires lm-sensors) |
| Running Processes | `ps aux` sorted by CPU |
| Network Interfaces | `ip addr` |
| Active Connections | `ss -tp state established` |
| Open Ports | `ss -tulpn` |
| Block Devices | `lsblk` |
| Largest Directories | `du -sh /*` |
| System Info | `uname -a` + `lsb_release` |
| Logged-in Users | `w` |
| Last Logins | `last` |
| Failed Services | `systemctl --failed` |
| System Journal | `journalctl -n 50` |
| Kernel Messages | `dmesg` |
| Clear Trash | Empties `~/.local/share/Trash` |
| System Update | apt / dnf / pacman auto-detected |
| Reboot | `systemctl reboot` |
| Shutdown | `systemctl poweroff` |

### Development (14 buttons)

Git Status · Git Log · Git Diff · Docker PS · Docker PS All · Docker Images · Docker Clean · Tail Syslog · Disk I/O · Python Version · Pip Outdated · Node Version · NPM Outdated · Listening Services

---

## Custom buttons

Click **+** (or `Ctrl+N`) to create a custom button. See [Your first button](first-button.md) for a full walkthrough.

!!! info "Free tier limit"
    The free tier allows **3 custom buttons**. Default buttons are not counted toward this limit. [Upgrade to Pro](pro.md) for unlimited custom buttons.

## Grid layout

Adjust the number of columns and button size in **Preferences → Button Grid Layout**:

- **Buttons per row** — 1 to 20 columns (applied live)
- **Button size** — Small (80×80) · Medium (120×120) · Large (160×160)

## Search

Press the search icon in the header bar (or start typing anywhere) to filter buttons by name in real time.

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Add a new button |
| `Ctrl+,` | Open Preferences |
| `Ctrl+?` | Show keyboard shortcuts |
| `Ctrl+Q` | Quit |

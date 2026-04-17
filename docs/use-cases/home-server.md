# Use Case: Home Server Management

This guide walks through setting up RemoteX to manage a typical home server — a machine running Plex, Pi-hole, or acting as a NAS. The goal: common maintenance tasks reduced to a single click.

## The scenario

You have a Raspberry Pi or mini-PC on your home network. It runs:

- **Plex Media Server** — your personal streaming server
- **Pi-hole** — network-wide ad blocking
- **Samba** — file sharing across the house

You are tired of SSH-ing in every time you need to restart a service or check disk usage.

---

## Step 1 — Add the server as an SSH machine

Open **Menu → Manage Machines → +** and fill in:

| Field | Example value |
|-------|---------------|
| Name | `Home Server` |
| Host | `192.168.1.50` |
| SSH User | `pi` |
| Port | `22` |
| SSH Key Path | `~/.ssh/id_ed25519` |
| Icon | Server |

If you don't have an SSH key set up yet, click **Generate SSH key** then **Copy key to server** and enter your password once. After that, click **Test** to confirm the connection works.

!!! tip "Pro feature"
    Adding SSH machines requires [RemoteX Pro](../pro.md).

---

## Step 2 — Create a "Home Server" category

In the Button Editor, every button you create for this server will use **Category: Home Server**. This groups them under a dedicated pill tab.

---

## Step 3 — Create the buttons

### Check disk space

| Field | Value |
|-------|-------|
| Label | `Disk Usage` |
| Command | `df -h` |
| Category | `Home Server` |
| Target | `Home Server` (your SSH machine) |
| Execution mode | `Show output` |
| Icon | `drive-harddisk-symbolic` |

This shows a breakdown of every filesystem on the server. The output dialog opens automatically.

---

### Restart Plex

| Field | Value |
|-------|-------|
| Label | `Restart Plex` |
| Command | `sudo systemctl restart plexmediaserver` |
| Category | `Home Server` |
| Target | `Home Server` |
| Execution mode | `Silent` |
| Confirm before running | Enabled |
| Tooltip | `Restart the Plex Media Server service` |
| Icon | `media-playback-start-symbolic` |

The confirmation dialog prevents accidental restarts when someone is watching.

---

### Update packages

| Field | Value |
|-------|-------|
| Label | `System Update` |
| Command | `sudo apt update && sudo apt upgrade -y` |
| Category | `Home Server` |
| Target | `Home Server` |
| Execution mode | `Show output` |
| Tooltip | `Update all installed packages` |

The `Show output` mode lets you see what was upgraded.

---

### Flush Pi-hole DNS cache

| Field | Value |
|-------|-------|
| Label | `Flush DNS` |
| Command | `pihole restartdns` |
| Category | `Home Server` |
| Target | `Home Server` |
| Execution mode | `Silent` |

---

### Check Samba status

| Field | Value |
|-------|-------|
| Label | `Samba Status` |
| Command | `sudo systemctl status smbd nmbd` |
| Category | `Home Server` |
| Target | `Home Server` |
| Execution mode | `Show output` |

---

### Reboot the server

| Field | Value |
|-------|-------|
| Label | `Reboot Server` |
| Command | `sudo systemctl reboot` |
| Category | `Home Server` |
| Target | `Home Server` |
| Execution mode | `Silent` |
| Confirm before running | Enabled |
| Color | `#e01b24` (red — signals danger) |
| Tooltip | `Reboot the home server — disconnects all clients` |

---

## Step 4 — Multi-machine: run on several servers

If you later add a second server (NAS, spare Pi), you can configure buttons to target multiple machines. For example, a **System Update** button that you want to run on both:

1. Open the button editor for the existing **System Update** button
2. In **Target machines**, enable both `Home Server` and your second machine
3. Save

From now on, clicking the button opens the [machine picker](../reference/ssh-machines.md#the-machine-picker) — choose which machine to update, or run it twice for both.

---

## Result

Your **Home Server** category tab gives you one-click access to everything you need. No terminal required.

!!! tip
    If you manage the server frequently throughout the day, enable **Always on top** in the hamburger menu. RemoteX stays visible while you work in other applications.

# Use Case: Linux Beginner Guide

You just installed RemoteX and you're not sure where to start. This guide is for you. You don't need to know any Linux commands — RemoteX already includes 34 ready-to-use buttons.

---

## You already have 34 buttons

The first time RemoteX launches, it populates your grid with two categories of pre-built buttons:

- **Linux Essentials** (20 buttons) — system information, network, disk, users, logs, and basic maintenance
- **Development** (14 buttons) — git, docker, Python, Node, and system services

These buttons are ready to use right now. No setup needed.

---

## What each default button does

### Linux Essentials

| Button | What it shows you |
|--------|-------------------|
| **Disk Usage** | How full each partition is (`df -h`) |
| **Memory Usage** | RAM and swap usage (`free -h`) |
| **CPU Load** | Current load averages (`uptime`) |
| **Temperature** | CPU temperature if `lm-sensors` is installed |
| **Running Processes** | All processes, sorted by CPU usage |
| **Network Interfaces** | Your IP addresses and network cards |
| **Active Connections** | Established TCP connections |
| **Open Ports** | Services listening on your machine |
| **Block Devices** | Hard drives, USB drives, partitions (`lsblk`) |
| **Largest Directories** | Biggest folders under `/` |
| **System Info** | Kernel version and Linux distribution |
| **Logged-in Users** | Who is currently logged in |
| **Last Logins** | Login history |
| **Failed Services** | Services that have crashed or failed to start |
| **System Journal** | Last 50 lines of the system log |
| **Kernel Messages** | Hardware and driver messages (`dmesg`) |
| **Clear Trash** | Empties your Trash folder |
| **System Update** | Updates your system (works on Ubuntu, Fedora, Arch) |
| **Reboot** | Reboots the computer |
| **Shutdown** | Powers off the computer |

!!! warning
    **Reboot** and **Shutdown** have **Confirm before running** enabled — a dialog will ask you to confirm before anything happens.

### Development

Git Status · Git Log · Git Diff · Docker PS · Docker PS All · Docker Images · Docker Clean · Tail Syslog · Disk I/O · Python Version · Pip Outdated · Node Version · NPM Outdated · Listening Services

---

## Start by clicking things

Click **Disk Usage**. A small dialog pops up with your filesystem information. Click **Memory Usage**. Try a few more.

You cannot break anything by clicking these buttons — they only read information. The two buttons that actually do something (Reboot and Shutdown) ask for confirmation first.

---

## Hide the categories you don't need

If you don't do development, the Development category is just noise. You can hide it:

1. Right-click the **Development** pill in the tab bar
2. Click **Hide category**

The tab and all its buttons disappear from view. They are not deleted — you can bring them back any time via **Preferences → Categories**.

---

## Customise a button name or color

The default button names are functional but generic. You can rename or recolor them to suit your style.

!!! note
    Editing default buttons requires [RemoteX Pro](../pro.md). On the free tier, you can use, hide, and delete default buttons, but not edit them.

With Pro, right-click any button → **Edit**:

- Change the **Label** to something friendlier (`Disk Usage` → `How full is my disk?`)
- Pick a **Color** to make important buttons stand out
- Change the **Icon** to one that makes sense to you

---

## Create your first custom button

You get **3 free custom buttons**. Here is an easy one to start:

1. Press `Ctrl+N` (or click **+**)
2. **Label:** `My IP address`
3. **Command:** `hostname -I`
4. **Execution mode:** `Show output`
5. Click **Save**

Now you have a one-click way to see your local IP address.

---

## What if a button shows an error?

Some buttons require software that may not be installed:

- **Temperature** — needs `lm-sensors` (`sudo apt install lm-sensors`)
- **Docker** buttons — need Docker installed
- Development buttons for Python/Node — need those runtimes

If a command fails, an output dialog opens showing the exact error. Usually it is a missing package — copy the package name and install it.

---

## Getting more out of RemoteX

Once you are comfortable with the defaults:

- [Create custom buttons](../quick-start.md#3-create-your-first-custom-button) for your own frequent commands
- [Organise with categories](../reference/main-window.md#category-bar) to group related buttons
- [Adjust the grid layout](../reference/preferences.md#buttons-per-row) to fit your screen
- Consider [RemoteX Pro](../pro.md) when you want to manage a remote server

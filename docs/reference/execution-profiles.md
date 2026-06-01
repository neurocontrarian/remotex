# Execution Profiles

!!! tip "Pro feature"
    Execution profiles require [Commandeck Pro](../pro.md).

🔰 **In plain terms:** a profile is a small set of "run conditions" you save once and reuse on many buttons — *who* runs the command (a different user) and *where* it runs (a folder). Instead of writing `sudo -u www-data` and `cd /var/www` in every button, you set them once in a profile and pick that profile on the button.

![Execution Profiles list](../assets/profiles-list.png)

## Creating a profile

Open **Menu ☰ → Execution Profiles → Add**, then fill in:

![Profile editor](../assets/profile-dialog.png)

| Field | What it does |
|-------|--------------|
| **Name** | How the profile appears in the button editor's dropdown. |
| **Run as user** | Run the command as this user instead of you (uses `sudo -u <user>`). Leave empty to run as yourself. |
| **Working directory** | The folder the command starts in (like running `cd` there first). |
| **Description** | Optional note to remind you what the profile is for. |
| **Sudo password** | Optional. Needed only when *Run as user* requires a password. Stored locally, encrypted — see [Security](security.md). |

## Using a profile on a button

In the [button editor](button-editor.md), pick your profile from the **Execution profile** dropdown. The button now runs with that profile's user and folder — the command field stays clean, holding only the actual command.

!!! example "Before / after"
    Instead of one button with `sudo -u www-data bash -c 'cd /var/www/app && git pull'`, create:

    - a profile **Web Deploy** → *Run as user* `www-data`, *Working directory* `/var/www/app`
    - a button with command `git pull`, profile **Web Deploy**

    Cleaner, and the same profile is reusable for every web-app button.

⚙️ **For sysadmins**

- *Run as user* wraps the command with `sudo -u <user>`. If that target requires a password, set the profile's **Sudo password**; Commandeck passes it via `sudo -S` at runtime, so no terminal prompt appears.
- A profile applies the **same** way locally and over SSH — the `sudo -u` / working-directory wrapping happens on whichever machine the button targets.
- Profiles pair naturally with [multi-machine buttons](../use-cases/homelab.md): one "deploy" profile, one button, several servers.
- An AI assistant can create and assign profiles for you via the [MCP server](../pro/mcp.md) — it decomposes a pasted shell one-liner into a profile + a clean command automatically.

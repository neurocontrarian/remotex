# Installing Commandeck on macOS

Commandeck v2.0 for macOS is distributed as an unsigned `.app` inside a DMG.
Because it is not yet notarized by Apple, macOS Gatekeeper will block the
first launch. Follow the steps below to bypass this.

## Requirements

- macOS 12 Monterey or later
- Apple Silicon (M1/M2/M3/M4) — Intel Mac not yet supported

## Installation

1. Download `Commandeck-2.0.0-arm64.dmg` from the
   [GitHub Releases](https://github.com/neurocontrarian/commandeck/releases) page.

2. Open the DMG and drag **Commandeck** into your **Applications** folder.

3. **First launch — bypass Gatekeeper** (one-time only):

   - **Option A (recommended):** Right-click (or Control-click) `Commandeck.app`
     in Applications → click **Open** → click **Open** in the dialog.

   - **Option B:** After the "unidentified developer" dialog appears, go to
     **System Settings → Privacy & Security**, scroll down, and click
     **Open Anyway** next to the Commandeck entry.

4. On subsequent launches, double-click the app normally.

## Configuration

Commandeck stores its configuration in:

```
~/Library/Application Support/Commandeck/
  buttons.toml      ← your button grid
  machines.toml     ← SSH machines (Pro)
  license.key       ← Pro license (Pro)
```

## Pro license

To activate a Pro license, open **Preferences → License** and enter your
license key. An internet connection is required for the initial activation.

## Autostart at login

Enable **Preferences → Desktop Integration → Launch at login**.
This installs a LaunchAgent at:
`~/Library/LaunchAgents/io.github.neurocontrarian.commandeck.plist`

To disable, toggle the same setting off or delete the plist and run:
```bash
launchctl unload ~/Library/LaunchAgents/io.github.neurocontrarian.commandeck.plist
```

## Terminal mode

Buttons set to "Open in terminal" will open **Terminal.app** with the command.
The terminal window stays open until you press a key.

## Uninstall

1. Delete `/Applications/Commandeck.app`
2. Delete `~/Library/Application Support/Commandeck/` (config data)
3. Delete `~/Library/LaunchAgents/io.github.neurocontrarian.commandeck.plist` (if autostart was enabled)

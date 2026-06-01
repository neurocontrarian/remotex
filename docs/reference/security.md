# Security & how it works

🔰 **In plain terms:** Commandeck runs commands *you* write and click, on your own machines. It never stores plaintext passwords, never opens a network port for normal use, and asks for confirmation on anything you mark as sensitive. This page explains the safeguards in detail — useful if you're a sysadmin deciding whether to trust it.

## Your commands, visible and editable

Every button's command is shown in plain text in the [button editor](button-editor.md). Nothing is hidden or obfuscated — what you see is exactly what runs. Commandeck never injects or rewrites your commands (it only wraps them with a profile's `cd` / `sudo -u` when you ask it to).

## SSH: keys, not passwords

SSH connections (Pro) use **key-based authentication only** — Commandeck never stores an SSH login password.

- Connections use Paramiko with a strict host-key policy and your `known_hosts`.
- **First contact (TOFU):** the first time you connect to a new host, Commandeck shows the host's key fingerprint and asks you to confirm before trusting it — the same check `ssh` does on the command line, but in a dialog.
- Keys protected by a passphrase require a running `ssh-agent`; Commandeck shows a clear error if the agent is locked rather than failing silently.
- Copying your public key to a server uses SFTP — no shell command is built from your input, so there is no injection surface.

## Sudo passwords

A profile's optional [sudo password](execution-profiles.md) is **never stored in plaintext**. It is XOR-encoded with your machine's unique ID and written to the local config only. Because the key is the machine ID, the encoded value is **not portable** — copying the config to another machine will not reveal or reuse the password. At runtime it is passed to `sudo -S` so no terminal prompt is needed.

## Per-button confirmation

Any button can require **Confirm before running** (button editor → Behaviour). When set, Commandeck shows the exact command and waits for your OK before executing — recommended for reboots, deletions, and anything with `sudo`.

## AI / MCP access (Pro)

The [MCP server](../pro/mcp.md) lets an AI assistant read and edit your buttons. It is **off by default** and guarded:

- **Reading/editing** requires turning on *Allow MCP access* in Preferences.
- **Executing** a button by AI requires **three** independent opt-ins — a global toggle, a per-button flag, and (for sensitive buttons) a confirmation handshake. If any one is off, execution is blocked.
- Every AI-triggered execution is written to an audit log (`<config>/.mcp_executions.log`) with timestamp, button, target, exit code, and duration.
- The server uses stdio (no network port) when launched by a desktop AI client. Only the mcpo bridge (for Open WebUI) opens a local HTTP port — keep it on your LAN, behind your firewall.

## Threat model

Commandeck is a **single-user desktop tool**. It assumes the person at the keyboard is trusted to run commands on their own machines — it is not a multi-tenant or privilege-separation boundary. Its safeguards exist to prevent *accidents* (running the wrong thing, leaking a secret into a sync, an AI acting without consent), not to defend against a hostile local user who already controls your account.

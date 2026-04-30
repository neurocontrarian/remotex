# AI Integration (MCP)

!!! warning "Experimental"
    AI integration is experimental. Tool support and behaviour vary across models and clients. Results are not guaranteed — always review what the AI creates or modifies.

RemoteX includes an MCP (Model Context Protocol) server. Once configured, your AI assistant can read and manage your buttons directly — no copy-pasting, no explaining your setup.

> *"Add a button called 'Restart Nginx' that runs `sudo systemctl restart nginx` in the Server category"*

## Step 1 — Enable MCP access in RemoteX

MCP is **off by default**. Turn it on once:

**Preferences → Desktop Integration → Allow MCP access**

## Step 2 — Configure your AI client

Pick your tool below. The setup is done once; after that it works automatically.

=== "Claude Desktop"

    **Config file location:**

    | OS | Path |
    |----|------|
    | Linux | `~/.config/Claude/claude_desktop_config.json` |
    | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
    | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

    Add this to the file (create it if it doesn't exist):

    ```json
    {
      "mcpServers": {
        "remotex": {
          "command": "python3",
          "args": ["/path/to/remotex/src/pro/mcp_server.py"]
        }
      }
    }
    ```

    Restart Claude Desktop. RemoteX will appear as a connected tool.

=== "Claude Code"

    Run this command once in a terminal:

    ```bash
    claude mcp add remotex python3 /path/to/remotex/src/pro/mcp_server.py
    ```

    To verify: `claude mcp list`

=== "Cursor"

    Edit `~/.cursor/mcp_config.json`:

    ```json
    {
      "mcpServers": {
        "remotex": {
          "command": "python3",
          "args": ["/path/to/remotex/src/pro/mcp_server.py"]
        }
      }
    }
    ```

    Restart Cursor.

=== "Windsurf"

    Edit `~/.codeium/windsurf/mcp_config.json`:

    ```json
    {
      "mcpServers": {
        "remotex": {
          "command": "python3",
          "args": ["/path/to/remotex/src/pro/mcp_server.py"]
        }
      }
    }
    ```

    Restart Windsurf.

=== "Continue.dev"

    Add to `.continue/config.yaml` in your project:

    ```yaml
    mcpServers:
      - name: remotex
        command: python3
        args:
          - /path/to/remotex/src/pro/mcp_server.py
    ```

    MCP tools are only available in **Agent mode**.

=== "Open WebUI (llama.cpp / Ollama)"

    Open WebUI connects to tools via HTTP, not stdio. Use [mcpo](https://github.com/open-webui/mcpo) (the official Open WebUI proxy) to bridge RemoteX.

    **Step 1 — Install mcpo (once):**

    ```bash
    pip install mcpo
    # if pip is blocked by your OS (externally-managed-environment):
    pipx install mcpo
    ```

    **Step 2 — Find your machine's local IP (if Open WebUI is on another machine):**

    ```bash
    hostname -I | awk '{print $1}'
    ```

    Note this IP — you'll need it in Step 4.

    **Step 3 — Start the proxy (keep this terminal open):**

    ```bash
    mcpo --port 8000 -- python3 /path/to/remotex/src/pro/mcp_server.py
    ```

    You should see: `Uvicorn running on http://0.0.0.0:8000`

    **Step 4 — Add the tool server in Open WebUI:**

    Go to **Admin Panel → Integrations → Manage tool servers → `+`** and fill in:

    | Field | Value |
    |-------|-------|
    | Type | **OpenAPI** |
    | Name | `remotex` |
    | URL | `http://<your-ip>:8000` |
    | Auth | None |

    !!! warning "Use your machine's IP, not localhost"
        If Open WebUI runs on a different machine (e.g. a server), `localhost` would point to that server — not to your Linux Mint machine where mcpo is running. Use the IP from Step 2 instead.

    **Step 5 — Enable the tool in a chat:**

    Start a new chat, click the **`+`** (tools) icon near the input field, and enable **remotex**.

    !!! tip
        This works with any backend supported by Open WebUI — llama.cpp, Ollama, OpenAI-compatible APIs, etc. The tool layer is independent of the model. Tool-calling support varies by model — instruction-tuned models generally work best.

    ---

    **When to restart mcpo**

    mcpo launches `mcp_server.py` as a subprocess at startup and keeps it in memory. You must restart mcpo whenever:

    - You update RemoteX (`git pull`) — the old `mcp_server.py` stays loaded until restart
    - You enable or disable **Allow MCP access** in Preferences

    If using systemd (see below): `systemctl --user restart mcpo-remotex`

    Otherwise: press `Ctrl+C` in the mcpo terminal and relaunch Step 3.

    ---

    **Step 6 — (Optional) Make mcpo persistent across reboots**

    Create a systemd user service so mcpo starts automatically at login:

    ```bash
    mkdir -p ~/.config/systemd/user
    cat > ~/.config/systemd/user/mcpo-remotex.service << 'EOF'
    [Unit]
    Description=mcpo proxy for RemoteX MCP server

    [Service]
    ExecStart=%h/.local/bin/mcpo --port 8000 -- %h/remotex/.venv/bin/python3 %h/remotex/src/pro/mcp_server.py
    Restart=on-failure
    RestartSec=5

    [Install]
    WantedBy=default.target
    EOF

    systemctl --user daemon-reload
    systemctl --user enable --now mcpo-remotex
    ```

    Useful commands:

    ```bash
    systemctl --user status mcpo-remotex    # check status
    systemctl --user restart mcpo-remotex   # restart after a git pull
    systemctl --user stop mcpo-remotex      # stop
    journalctl --user -u mcpo-remotex -f    # live logs
    ```

    !!! note
        Adjust the paths in `ExecStart` if your RemoteX installation is not at `~/remotex` or if mcpo is not installed via pipx. Run `which mcpo` to find the correct path.

Replace `/path/to/remotex` with your actual installation path — typically the folder where you cloned the repo.

---

## Recommended system prompt

Paste the prompt below into your AI client's system prompt field. It primes the model to call
`help` first, follow correct lookup workflows, and decompose complex shell commands into RemoteX
components rather than pasting them as-is.

```
You are an assistant for RemoteX, a desktop application on Linux. RemoteX lets the user run
commands by clicking buttons, like a remote control. You can create, read, and modify the
user's buttons, machines, and profiles using your tools.

Rules:
- Before doing anything, call the help tool to read the instructions.
- When the user explicitly names a button, use get_button(name="X") directly. When you don't
  know the exact name, use list_buttons.
- Never call get_button before create_button.
- For buttons: a duplicate means SAME NAME, not same command. If no button has the exact same
  name, create it without asking.
- For machines: a duplicate means SAME HOST address. Always call list_machines and check by
  host before creating.
- For profiles: a duplicate means same name. Call list_profiles before creating.
- When asked to change a property, always apply the change. Never decide the current value is
  already acceptable.
- In multi-step requests, if a required resource exists, use it and proceed.
- When you need a machine ID or profile ID, always look it up first.

When a user asks you to add or refactor a shell command, decompose it before creating a button:
1. `cd /some/path` → Execution Profile working_dir (strip from command)
2. `sudo -u user` wrapper → run_as_user on the profile or button's run_as field
   (strip the wrapper, keep the inner command)
3. Opens an interactive shell (bash, zsh, exec bash) → execution_mode = "terminal"
4. Produces output the user wants to read → execution_mode = "output"; fire-and-forget → "silent"
5. What remains after stripping context wrappers is the command field.

Example: `sudo -u www-data bash -c 'cd /var/www/myapp && git pull'`
→ Create Profile: name="Web Deploy", run_as_user="www-data", working_dir="/var/www/myapp"
→ Create button: command="git pull", execution_mode="output", assign that profile
```

=== "Open WebUI"

    In Open WebUI, go to **Admin Panel → Settings → System prompt** and paste the prompt above
    (or into the chat's system prompt field in Model Settings).

=== "Claude Desktop"

    Claude Desktop does not expose a system prompt field. The `help` tool description is
    self-explanatory for Claude — no extra prompt needed.

=== "Other clients"

    Paste the prompt into whatever system prompt or instruction field your client exposes
    before the conversation starts.

---

## What your AI can do

**Buttons**

| Tool | Description |
|------|-------------|
| `help` | Return the full workflow guide — always call this first |
| `list_buttons` | List all buttons, optionally filtered by category |
| `get_button` | Get details of a button by name or ID |
| `create_button` | Create a new button (name, command, category, color, icon, execution_mode, profile, machines…) |
| `update_button` | Modify any field on an existing button — call `get_button` first to get the ID |
| `execute_button` | Run a button's command and return its output (off by default — see [Allowing AI execution](#allowing-ai-to-run-buttons)) |
| `delete_button` | Delete a button by ID |

**Categories**

| Tool | Description |
|------|-------------|
| `list_categories` | List all category names |

**SSH Machines** *(Pro feature)*

| Tool | Description |
|------|-------------|
| `list_machines` | List configured SSH machines (name, host, user, port — no private keys) |
| `create_machine` | Add a new SSH machine |
| `update_machine` | Rename or reconfigure an SSH machine — call `list_machines` first to get the ID |
| `delete_machine` | Delete an SSH machine by ID |

**Execution Profiles** *(Pro feature)*

| Tool | Description |
|------|-------------|
| `list_profiles` | List all execution profiles |
| `get_profile` | Get details of a profile by name or ID |
| `create_profile` | Create a reusable profile (run_as_user, working_dir) |
| `update_profile` | Modify an existing profile — call `get_profile` first to get the ID |
| `delete_profile` | Delete a profile by ID |

!!! warning "Review before deleting"
    `delete_button`, `delete_machine`, and `delete_profile` are available via MCP. Always verify
    the correct item with `get_button` or `list_machines` before asking your AI to delete anything.

!!! tip "Refreshing the grid after AI changes"
    After an AI creates or modifies a button, press **F5** (or menu → Refresh Buttons) to reload the grid without restarting RemoteX.

!!! tip "Tip for updating buttons"
    If the AI says it cannot update a button, ask it to call `get_button` with the button name first to retrieve the ID, then call `update_button` with that ID.

---

## Allowing AI to run buttons

By default, your AI can **read and edit** buttons but cannot **run** them. To let it actually trigger commands, you must opt in at three levels — any one of them blocks execution if disabled.

**1. Global toggle** — *Preferences → Desktop Integration → Allow AI execution*

Off by default. This is the master switch for the whole feature.

**2. Per-button opt-in** — *Edit a button → Behaviour → Allow AI to run this button*

Off by default on every button, including those you've already created. Enable it only for buttons whose commands you're comfortable letting an AI trigger autonomously — e.g. read-only checks (`df -h`, `systemctl status`), idempotent operations, safe deploys.

**3. Confirmation handshake** — *Edit a button → Behaviour → Confirm before running*

When this is on, the AI cannot run the button silently. It receives a `requires_confirmation` response containing the exact command and is instructed to show it to you and wait for your approval before re-calling with `confirmed=true`. Recommended for any sensitive command (restarts, deletions, sudo).

**Audit log:** Every MCP execution is appended to `~/.config/remotex/.mcp_executions.log` with the timestamp, button name, target machine, exit code, and duration.

**Limitations:**

- Buttons with `Open in terminal` mode cannot be executed via MCP — there is no terminal in a headless AI context. The AI receives an error if it tries.
- Output sent back to the AI is capped (4 KB stdout, 2 KB stderr) to keep its context manageable. The full output is still in the log if you need it.
- Multi-target buttons require the AI to specify which machine to run on. If it doesn't, the server returns the list of valid targets and asks for clarification.

---

## Security

The MCP server uses **stdio transport** — it runs as a subprocess of your AI client, communicating only through stdin/stdout. No network port is opened. Only the process that launched the server can communicate with it.

When using mcpo (Open WebUI), the HTTP port (8000) is opened on your machine. Make sure it is not exposed to untrusted networks.

!!! warning
    When MCP access is enabled, your AI assistant can create, modify and delete buttons. Disable the toggle in Preferences when you don't need it. Button **execution** is a separate, opt-in feature — see [Allowing AI to run buttons](#allowing-ai-to-run-buttons).

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
          "args": ["/path/to/remotex/src/mcp_server.py"]
        }
      }
    }
    ```

    Restart Claude Desktop. RemoteX will appear as a connected tool.

=== "Claude Code"

    Run this command once in a terminal:

    ```bash
    claude mcp add remotex python3 /path/to/remotex/src/mcp_server.py
    ```

    To verify: `claude mcp list`

=== "Cursor"

    Edit `~/.cursor/mcp_config.json`:

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

    Restart Cursor.

=== "Windsurf"

    Edit `~/.codeium/windsurf/mcp_config.json`:

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

    Restart Windsurf.

=== "Continue.dev"

    Add to `.continue/config.yaml` in your project:

    ```yaml
    mcpServers:
      - name: remotex
        command: python3
        args:
          - /path/to/remotex/src/mcp_server.py
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
    mcpo --port 8000 -- python3 /path/to/remotex/src/mcp_server.py
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
    ExecStart=%h/.local/bin/mcpo --port 8000 -- %h/remotex/.venv/bin/python3 %h/remotex/src/mcp_server.py
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

## What your AI can do

| Tool | Description |
|------|-------------|
| `list_buttons` | List all buttons, optionally filtered by category |
| `get_button` | Get details of a button by name or ID |
| `create_button` | Create a new button (name, command, category, color, icon, appearance…) |
| `update_button` | Modify any field on an existing button — call `get_button` first to get the ID |
| `list_categories` | List all category names |
| `list_machines` | List SSH machines (name, host, user — no private keys) |

!!! note "Deletion is not available via MCP"
    Buttons can only be deleted from the RemoteX interface itself (right-click → Delete, or multi-select). This is intentional — it prevents an AI assistant from accidentally removing your buttons.

!!! tip "Refreshing the grid after AI changes"
    After an AI creates or modifies a button, press **F5** (or menu → Refresh Buttons) to reload the grid without restarting RemoteX.

!!! tip "Tip for updating buttons"
    If the AI says it cannot update a button, ask it to call `get_button` with the button name first to retrieve the ID, then call `update_button` with that ID.

---

## Security

The MCP server uses **stdio transport** — it runs as a subprocess of your AI client, communicating only through stdin/stdout. No network port is opened. Only the process that launched the server can communicate with it.

When using mcpo (Open WebUI), the HTTP port (8000) is opened on your machine. Make sure it is not exposed to untrusted networks.

!!! warning
    When MCP access is enabled, your AI assistant can create, modify and delete buttons. Disable the toggle in Preferences when you don't need it.

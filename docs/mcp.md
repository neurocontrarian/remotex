# AI Integration (MCP)

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

=== "Open WebUI"

    !!! note
        Open WebUI only supports **HTTP-based** MCP servers, not the stdio transport used by RemoteX. Direct connection is not supported.

        As a workaround, you can use [mcpo](https://github.com/open-webui/mcpo) to proxy the RemoteX MCP server over HTTP, but this is an advanced setup.

Replace `/path/to/remotex` with your actual installation path — typically the folder where you cloned the repo.

---

## What your AI can do

| Tool | Description |
|------|-------------|
| `list_buttons` | List all buttons, optionally filtered by category |
| `get_button` | Get details of a button by name or ID |
| `create_button` | Create a new button |
| `update_button` | Modify fields on an existing button |
| `delete_button` | Delete a button |
| `list_categories` | List all category names |
| `list_machines` | List SSH machines (name, host, user — no private keys) |

---

## Security

The MCP server uses **stdio transport** — it runs as a subprocess of your AI client, communicating only through stdin/stdout. No network port is opened. Only the process that launched the server can communicate with it.

!!! warning
    When MCP access is enabled, your AI assistant can create, modify and delete buttons. Disable the toggle in Preferences when you don't need it.

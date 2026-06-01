# Use Case: Drive Commandeck from a local AI

!!! tip "Pro feature"
    AI integration (MCP) requires [Commandeck Pro](../pro.md).

🔰 **The idea:** instead of building buttons by hand, you *ask* an AI assistant — "add a button that restarts Nginx in the Server category" — and it creates it for you. The AI can read your buttons, machines and profiles, and (if you allow it) run them. It works with cloud assistants like Claude **and** with a fully local model running on your own hardware.

This page walks the local-model path end to end with **Open WebUI** + a local LLM (e.g. Llama, Gemma). For the full client matrix and options, see the [AI Integration reference](../pro/mcp.md).

## Why local?

A local model keeps everything on your machine — your buttons, commands, and server names never leave your network. Great for homelabs and privacy-conscious setups.

## Step by step

### 1. Turn on MCP access

**Preferences → Desktop Integration → Allow MCP access.**

![Allow MCP access](../assets/preferences-desktop.png)

### 2. Launch the Commandeck MCP server

The server is built into the app. Run your Commandeck build with `--mcp-server`:

```bash
/path/to/Commandeck-Pro-VERSION-Linux-x86_64.AppImage --mcp-server
```

!!! warning "Run it as the user who uses Commandeck"
    The server reads the buttons of **whoever launches it**. Launch it from a terminal logged in as your normal desktop user, or the AI will see the wrong (or empty) set of buttons.

### 3. Bridge to Open WebUI with mcpo

Open WebUI talks to tools over HTTP, so put the [mcpo](https://github.com/open-webui/mcpo) proxy in front:

```bash
mcpo --port 8000 -- /path/to/Commandeck-Pro-VERSION-Linux-x86_64.AppImage --mcp-server
```

Then in Open WebUI: **Admin Panel → Settings → Tools → +**, type **OpenAPI**, URL `http://<machine-ip>:8000`. If Open WebUI runs on a different box, use the IP of the machine running mcpo — not `localhost`.

### 4. Talk to your buttons

Start a chat, enable the **commandeck** tool, paste the [recommended system prompt](../pro/mcp.md#recommended-system-prompt), and try:

> *"List my buttons."*
> *"Add a button called 'Disk Usage' that runs `df -h` in the System category."*

Press **F5** in Commandeck to see new buttons appear.

⚙️ **Notes for power users**

- **Model matters.** The tool layer is model-independent, but tool-calling quality varies a lot. Instruction-tuned models work best; small local models often need the system prompt to call tools reliably.
- **Letting the AI *run* buttons** is a separate, three-gate opt-in (global toggle + per-button flag + optional confirmation). Off by default. See [Allowing AI to run buttons](../pro/mcp.md#allowing-ai-to-run-buttons).
- **Persisting the bridge:** a systemd user service keeps mcpo running across reboots — see the [MCP reference](../pro/mcp.md).

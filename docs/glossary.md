# Glossary

New to some of the words in this wiki? Here they are in plain language.

**Command**
: A line of text that tells the computer to do something — e.g. `df -h` shows free disk space. Commandeck runs a command for you when you click a button, so you don't have to type it.

**Button (tile)**
: One square in the Commandeck grid. Each button holds one command and runs it on click.

**Shell**
: The program that reads and runs commands. On Linux and macOS it's usually `bash` or `zsh`; on Windows it's **PowerShell**. Commandeck uses the right one for your system automatically.

**Terminal**
: The black text window where commands are normally typed. Commandeck exists so you can avoid it — though a button can open one if you choose "Open in terminal" mode.

**Category**
: A label that groups related buttons (e.g. *Network*, *Hardware*). Categories appear as tabs above the grid so you can filter what you see.

**SSH** *(Pro)*
: A secure way to run commands on another computer over the network — for example managing a home server from your laptop. Commandeck uses SSH to send a button's command to a remote machine.

**Machine** *(Pro)*
: A remote computer you've added to Commandeck (its address, username, and SSH key). Buttons can target one or several machines.

**sudo / run as user**
: `sudo` runs a command with administrator rights; *run as user* runs it as a specific account (e.g. a service user like `www-data`). Commandeck can do this for you via an [execution profile](reference/execution-profiles.md).

**Execution profile** *(Pro)*
: A saved bundle of "run conditions" — which user and which folder — that you reuse across buttons. See [Execution Profiles](reference/execution-profiles.md).

**Output**
: What a command prints back (e.g. the disk-usage numbers). A button can show it in a window, run silently, or open a terminal.

**AppImage**
: A single-file Linux app — download it, make it executable, run it. No installation, nothing to set up system-wide.

**MCP** *(Pro)*
: The bridge that lets an AI assistant read and manage your buttons for you. See [AI Integration](pro/mcp.md).

**Free vs Pro**
: The **Free** tier runs unlimited local commands with up to 3 custom buttons. **Pro** adds SSH machines, multi-machine buttons, themes, profiles, backup, and AI integration — with a 14-day free trial.

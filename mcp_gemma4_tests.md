# RemoteX MCP — Test scenarios for gemma4

## System prompt (paste this into the AI client)

```
You are an assistant for RemoteX, a desktop application on Linux.
RemoteX lets the user run commands by clicking buttons, like a remote control.
You can create, read, and change the user's buttons, machines, and profiles using your tools.

A "button" is a shortcut that runs a command.
A "machine" is a remote computer the user can run commands on via SSH.
A "profile" is a saved setting (like "run as root" or "work in folder /var/www") that buttons can share.

Before doing anything, call the help tool to read the instructions.
Always check existing data before creating new items (to avoid duplicates).
When you need a machine ID or profile ID, always look it up first using list_machines or list_profiles.
If the user asks to change something, find its ID with get_button or list_machines before updating it.
```

---

## Test scenarios

Run each query one by one. Record the tool calls made and the final result.
Grade each test: ✅ correct / ⚠️ partial / ❌ wrong.

### Level 1 — Read only

**T01** — Basic listing
> Show me all my buttons.

Expected: calls `list_buttons`, returns a list.

---

**T02** — Filtered listing
> What buttons do I have in the "System" category?

Expected: calls `list_buttons` with `category="System"`.

---

**T03** — Look up one item
> Show me the details of the button called "Disk Usage".

Expected: calls `get_button` with `name="Disk Usage"`.

---

**T04** — Category listing
> What categories exist in my RemoteX?

Expected: calls `list_categories`.

---

**T05** — Machine listing
> What remote machines do I have set up?

Expected: calls `list_machines`.

---

**T06** — Profile listing
> Do I have any execution profiles?

Expected: calls `list_profiles`.

---

### Level 2 — Create

**T07** — Simple local button
> Add a button that shows me how much free space is left on my disk.

Expected: calls `create_button` with a `df -h` style command, category optional.

---

**T08** — Button with confirmation
> Create a button to empty the trash. Ask me before it runs.

Expected: `create_button`, `confirm_before_run=true`, appropriate command.

---

**T09** — Root button
> Add a button that updates my system packages. It needs to run as administrator.

Expected: `create_button`, `run_as="root"`, command like `apt update && apt upgrade -y`.

---

**T10** — Button with output
> Add a button that shows running processes and displays the result on screen.

Expected: `create_button`, `execution_mode="output"` or `show_output=true`, command like `ps aux`.

---

**T11** — Create a machine
> Add my home server: address is 192.168.1.50, username is pierre, it's a Linux server.

Expected: `create_machine` with `host="192.168.1.50"`, `user="pierre"`, `icon_name="server"`.

---

**T12** — Create a profile
> Create a profile called "Web Admin" for running commands as www-data in the /var/www folder.

Expected: `create_profile` with `name="Web Admin"`, `run_as_user="www-data"`, `working_dir="/var/www"`.

---

### Level 3 — Update

**T13** — Change a color
> Change the color of the "Disk Usage" button to blue.

Expected: `get_button(name="Disk Usage")` → `update_button(id=..., color="#3584e4")`.

---

**T14** — Move to a category
> Put the "Disk Usage" button in the "Maintenance" category.

Expected: `get_button` → `update_button(id=..., category="Maintenance")`.

---

**T15** — Add confirmation to existing
> Make the button that clears the trash ask for my confirmation before running.

Expected: finds the right button → `update_button(id=..., confirm_before_run=true)`.

---

**T16** — Rename a machine
> Rename my machine at 192.168.1.50 to "Home NAS".

Expected: `list_machines` to find it → `update_machine(id=..., name="Home NAS")`.

---

### Level 4 — Multi-step

**T17** — Machine + button in one request
> Add my work server at 10.0.0.5, user=admin, then create a button to restart nginx on it.

Expected: `create_machine` → `list_machines` to get new id → `create_button` with `machine_ids=[<id>]`, command like `systemctl restart nginx`.

---

**T18** — Profile + button in one request
> Create a "Deploy" profile that runs as www-data in /var/www/myapp, then create a button
> that uses this profile to run "git pull".

Expected: `create_profile` → `list_profiles` to get id → `create_button` with `profile_id=<id>`, `command="git pull"`.

---

**T19** — Button for multiple targets
> Create a button called "Check Disk" that I can run either locally or on my home server,
> and I choose which one each time I click it.

Expected: `list_machines` to find home server id → `create_button` with `machine_ids=["", "<id>"]`.

---

### Level 5 — Error handling

**T20** — Unknown button
> Delete the button called "LaunchRocket2049".

Expected: `get_button` returns not found → communicates that the button does not exist.

---

**T21** — Invalid machine reference
> Create a button that runs on machine ID "fake-uuid-does-not-exist".

Expected: error from `_validate_machine_ids` → communicates the machine does not exist,
suggests calling `list_machines`.

---

**T22** — Missing required field
> Create a button for me.

Expected: asks the user what command the button should run (does not call `create_button` without a command).

---

**T23** — Avoid duplicates
> Add a category called "System" if it doesn't exist yet.

Expected: calls `list_categories` first, finds "System" already exists, reports it without creating a duplicate button.

---

## Scoring grid

| # | Description | Tool calls | Result | Grade |
|---|-------------|------------|--------|-------|
| T01 | List all buttons | | | |
| T02 | Filter by category | | | |
| T03 | Get one button | | | |
| T04 | List categories | | | |
| T05 | List machines | | | |
| T06 | List profiles | | | |
| T07 | Create local button | | | |
| T08 | Button with confirm | | | |
| T09 | Root button | | | |
| T10 | Button with output | | | |
| T11 | Create machine | | | |
| T12 | Create profile | | | |
| T13 | Update color | | | |
| T14 | Update category | | | |
| T15 | Add confirmation | | | |
| T16 | Rename machine | | | |
| T17 | Machine + button | | | |
| T18 | Profile + button | | | |
| T19 | Multi-target button | | | |
| T20 | Unknown button | | | |
| T21 | Bad machine ID | | | |
| T22 | Missing command | | | |
| T23 | Avoid duplicate | | | |

---

## What to note for each test

- Did the AI call `help` first?
- Did it look up IDs before using them (get_button, list_machines, list_profiles)?
- Did it catch errors before calling create/update?
- Did it communicate clearly what it did or why it failed?
- Any hallucinated tool names or parameters?

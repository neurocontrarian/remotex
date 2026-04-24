# RemoteX MCP — gemma4 test results

Run: 2026-04-24 15:51 — 24 tests — 139s — score: 59/59 checks

| # | Group | Prompt | Tools used | Score |
|---|-------|--------|------------|-------|
| T01 | Read | Show me all my buttons. | list_buttons | ✅ 2/2 |
| T02 | Read | What buttons do I have in the "System" category? | list_buttons | ✅ 2/2 |
| T03 | Read | Show me the details of the button called "Disk Usage… | get_button | ✅ 2/2 |
| T04 | Read | What categories exist in my RemoteX? | list_categories | ✅ 1/1 |
| T05 | Read | What remote machines do I have set up? | list_machines | ✅ 1/1 |
| T06 | Read | Do I have any execution profiles? | list_profiles | ✅ 1/1 |
| T07 | Create | Create a button called "Free Disk Space" that shows … | create_button | ✅ 3/3 |
| T08 | Create | Create a button to empty the trash. Ask me before it… | help, list_buttons, create_button | ✅ 3/3 |
| T09 | Create | Add a button that updates my system packages. It nee… | help, list_buttons, create_button | ✅ 3/3 |
| T10 | Create | Create a button called "Show Running Processes" that… | help, create_button | ✅ 3/3 |
| T11 | Create | Add my home server: address is 192.168.1.50, usernam… | list_machines | ✅ 2/2 |
| T12 | Create | Create a profile called "Web Admin" for running comm… | list_profiles | ✅ 2/2 |
| T13 | Update | Change the color of the "Disk Usage" button to red. | get_button, update_button | ✅ 3/3 |
| T14 | Update | Put the "Disk Usage" button in the "Maintenance" cat… | get_button | ✅ 2/2 |
| T15 | Update | Make the button that updates system packages ask for… | list_buttons, update_button | ✅ 1/1 |
| T16 | Update | Rename my machine at 192.168.1.50 to 'Home NAS'. | list_machines | ✅ 2/2 |
| T17 | Multi-step | Add my work server at 10.0.0.5, user=admin, then cre… | list_machines, create_button | ✅ 4/4 |
| T18 | Multi-step | Create a "Deploy" profile that runs as www-data in /… | help, list_profiles, create_profile, create_button | ✅ 4/4 |
| T19 | Multi-step | Create a button called "Check Disk" that I can run e… | help, list_machines, list_buttons, create_button | ✅ 4/4 |
| T20 | Error | Delete the button called "LaunchRocket2049". | get_button, list_buttons | ✅ 2/2 |
| T21 | Error | Create a button that runs on machine ID "fake-uuid-d… | help | ✅ 2/2 |
| T22 | Error | Create a button for me. | help | ✅ 2/2 |
| T23 | Error | Add a category called "System" if it does not exist … | list_categories | ✅ 2/2 |
| T24 | Multi-step | Create a button called "Deploy Website" that runs "g… | help, list_machines, list_profiles, create_button | ✅ 6/6 |

---

## Detailed results

### T01 — Show me all my buttons.

**Score: 2/2** ✅
- ✅ list_buttons called
- ✅ No standalone get_button guess

**Call 1:** `list_buttons({"category": ""})`
```
[
  {
    "id": "demo-001",
    "name": "Disk Usage",
    "command": "df -h",
    "category": "Maintenance",
    "tooltip": "Show disk space usage for all mounted filesystems",
    "icon_name": "drive-harddisk-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "hide_icon"…
```
**Final answer:**
> Here are your current buttons:

| Name | Command | Category | Tooltip |
| :--- | :--- | :--- | :--- |
| **Disk Usage** | `df -h` | Maintenance | Show disk space usage for all mounted filesystems |
| **Memory** | `free -h` | System | Show total, used and free RAM and swap memory |
| **CPU Load** | `uptime` | System | Show system uptime and CPU load averages |
| **System Info** | `uname -a` | Network | Show kernel version and system architecture |
| **Running Processes** | `ps aux \| head -20` | *(None)* | *(None)* |

---

### T02 — What buttons do I have in the "System" category?

**Score: 2/2** ✅
- ✅ list_buttons called
- ✅ category="System" passed

**Call 1:** `list_buttons({"category": "System"})`
```
[
  {
    "id": "demo-002",
    "name": "Memory",
    "command": "free -h",
    "category": "System",
    "tooltip": "Show total, used and free RAM and swap memory",
    "icon_name": "emblem-system-symbolic",
    "color": "#3584e4",
    "text_color": "",
    "hide_label": false,
    "hide_icon": fal…
```
**Final answer:**
> You have two buttons in the "System" category:

1.  **Memory**: Runs `free -h` to show total, used, and free RAM and swap memory.
2.  **CPU Load**: Runs `uptime` to show system uptime and CPU load averages.

---

### T03 — Show me the details of the button called "Disk Usage".

**Score: 2/2** ✅
- ✅ get_button called (name is explicit)
- ✅ name="Disk Usage" passed

**Call 1:** `get_button({"name": "Disk Usage"})`
```
{
  "id": "demo-001",
  "name": "Disk Usage",
  "command": "df -h",
  "category": "Maintenance",
  "tooltip": "Show disk space usage for all mounted filesystems",
  "icon_name": "drive-harddisk-symbolic",
  "color": "",
  "text_color": "",
  "hide_label": false,
  "hide_icon": false,
  "show_output"…
```
**Final answer:**
> The details for the "Disk Usage" button are:

*   **ID:** `demo-001`
*   **Command:** `df -h`
*   **Category:** Maintenance
*   **Tooltip:** Show disk space usage for all mounted filesystems
*   **Icon:** `drive-harddisk-symbolic`
*   **Execution Mode:** (Not specified, defaults to `silent`)
*   **Show Output:** Yes
*   **Confirm Before Run:** No
*   **Machine IDs:** None (runs locally)
*   **Profile ID:** None

---

### T04 — What categories exist in my RemoteX?

**Score: 1/1** ✅
- ✅ list_categories called

**Call 1:** `list_categories({})`
```
["Maintenance", "Network", "System"]
```
**Final answer:**
> The categories currently in your RemoteX are:
* Maintenance
* Network
* System

---

### T05 — What remote machines do I have set up?

**Score: 1/1** ✅
- ✅ list_machines called

**Call 1:** `list_machines({})`
```
[
  {
    "id": "aaa-111",
    "name": "Plex Server",
    "host": "192.168.1.10",
    "user": "fabien",
    "port": 22,
    "icon_name": "server",
    "group": ""
  },
  {
    "id": "bbb-222",
    "name": "Dev Laptop",
    "host": "192.168.1.20",
    "user": "fabien",
    "port": 22,
    "icon_name"…
```
**Final answer:**
> You have the following remote machines set up:

*   **Plex Server** (192.168.1.10, user: fabien)
*   **Dev Laptop** (192.168.1.20, user: fabien)
*   **Home NAS** (192.168.1.50, user: pierre)
*   **Work Server** (10.0.0.5, user: admin)
*   **home server** (192.168.1.50, user: pierre)

---

### T06 — Do I have any execution profiles?

**Score: 1/1** ✅
- ✅ list_profiles called

**Call 1:** `list_profiles({})`
```
[
  {
    "id": "b854982d-1797-47df-94ab-1f9d815b5c08",
    "name": "Web Admin",
    "run_as_user": "www-data",
    "working_dir": "/var/www",
    "description": "",
    "has_sudo_password": false
  }
]
```
**Final answer:**
> Yes, you have one execution profile:
- **Web Admin** (ID: `b854982d-1797-47df-94ab-1f9d815b5c08`)
  - **Run as user:** `www-data`
  - **Working directory:** `/var/www`

---

### T07 — Create a button called "Free Disk Space" that shows how much free disk space I have.

**Score: 3/3** ✅
- ✅ list_buttons OR direct create (name given)
- ✅ create_button called
- ✅ No get_button before create

**Call 1:** `create_button({"command": "df -h", "execution_mode": "output", "name": "Free Disk Space"})`
```
{
  "created": {
    "id": "2c2a3635-e0f7-4241-baaf-166e7bd20ac2",
    "name": "Free Disk Space",
    "command": "df -h",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "hide_icon": false,
   …
```
**Final answer:**
> I've created the "Free Disk Space" button for you. It runs the `df -h` command and will show the output in a dialog window when clicked.

---

### T08 — Create a button to empty the trash. Ask me before it runs.

**Score: 3/3** ✅
- ✅ list_buttons used (not direct get_button guess)
- ✅ create_button called
- ✅ confirm_before_run=True set

**Call 1:** `help({})`
```
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by …
```
**Call 2:** `list_buttons({})`
```
[
  {
    "id": "demo-001",
    "name": "Disk Usage",
    "command": "df -h",
    "category": "Maintenance",
    "tooltip": "Show disk space usage for all mounted filesystems",
    "icon_name": "drive-harddisk-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "hide_icon"…
```
**Call 3:** `create_button({"command": "gio trash --empty", "confirm_before_run": true, "name": "Empty Trash"})`
```
{
  "created": {
    "id": "aad9e93d-6bc7-422e-8bd9-7b14c2cfdd75",
    "name": "Empty Trash",
    "command": "gio trash --empty",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "hide_icon": fa…
```
**Final answer:**
> I've created the "Empty Trash" button for you. It runs the command `gio trash --empty` and will ask for confirmation before executing.

---

### T09 — Add a button that updates my system packages. It needs to run as administrator.

**Score: 3/3** ✅
- ✅ list_buttons called to search
- ✅ create_button called
- ✅ run_as=root

**Call 1:** `help({})`
```
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by …
```
**Call 2:** `list_buttons({})`
```
[
  {
    "id": "demo-001",
    "name": "Disk Usage",
    "command": "df -h",
    "category": "Maintenance",
    "tooltip": "Show disk space usage for all mounted filesystems",
    "icon_name": "drive-harddisk-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "hide_icon"…
```
**Call 3:** `create_button({"command": "apt update && apt upgrade -y", "execution_mode": "terminal", "name": "Update System Packages", "run_as": "root"})`
```
{
  "created": {
    "id": "16d48059-3d19-4547-9df2-fb362188c575",
    "name": "Update System Packages",
    "command": "apt update && apt upgrade -y",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": fals…
```
**Final answer:**
> I've created a new button called "Update System Packages". 

It is configured to run the command `apt update && apt upgrade -y` as **root** using a **terminal** execution mode, which will allow you to interactively provide your sudo password if needed.

---

### T10 — Create a button called "Show Running Processes" that lists active processes and displays the output.

**Score: 3/3** ✅
- ✅ list_buttons OR direct create (name given)
- ✅ create_button called
- ✅ output mode set

**Call 1:** `help({})`
```
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by …
```
**Call 2:** `create_button({"command": "ps aux", "execution_mode": "output", "name": "Show Running Processes"})`
```
{
  "created": {
    "id": "0f44adbf-32ef-469b-9327-234c9cc56f8a",
    "name": "Show Running Processes",
    "command": "ps aux",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "hide_icon": fa…
```
**Final answer:**
> The button "Show Running Processes" has been successfully created. It runs the command `ps aux` and will display the output in a dialog window.

---

### T11 — Add my home server: address is 192.168.1.50, username is pierre, it's a Linux server.

**Score: 2/2** ✅
- ✅ list_machines called first
- ✅ No duplicate machine created

**Call 1:** `list_machines({})`
```
[
  {
    "id": "aaa-111",
    "name": "Plex Server",
    "host": "192.168.1.10",
    "user": "fabien",
    "port": 22,
    "icon_name": "server",
    "group": ""
  },
  {
    "id": "bbb-222",
    "name": "Dev Laptop",
    "host": "192.168.1.20",
    "user": "fabien",
    "port": 22,
    "icon_name"…
```
**Final answer:**
> It looks like you already have two machines configured with that address (192.168.1.50) and username (pierre):

* **home server**
* **Home NAS**

Would you like me to update one of these, or were you looking to add a different one?

---

### T12 — Create a profile called "Web Admin" for running commands as www-data in the /var/www folder.

**Score: 2/2** ✅
- ✅ list_profiles called first
- ✅ No duplicate profile created

**Call 1:** `list_profiles({})`
```
[
  {
    "id": "b854982d-1797-47df-94ab-1f9d815b5c08",
    "name": "Web Admin",
    "run_as_user": "www-data",
    "working_dir": "/var/www",
    "description": "",
    "has_sudo_password": false
  }
]
```
**Final answer:**
> The profile "Web Admin" already exists with the settings you requested (running as `www-data` in `/var/www`).

---

### T13 — Change the color of the "Disk Usage" button to red.

**Score: 3/3** ✅
- ✅ Looked up button (get or list)
- ✅ update_button called
- ✅ color set to a blue hex

**Call 1:** `get_button({"name": "Disk Usage"})`
```
{
  "id": "demo-001",
  "name": "Disk Usage",
  "command": "df -h",
  "category": "Maintenance",
  "tooltip": "Show disk space usage for all mounted filesystems",
  "icon_name": "drive-harddisk-symbolic",
  "color": "",
  "text_color": "",
  "hide_label": false,
  "hide_icon": false,
  "show_output"…
```
**Call 2:** `update_button({"color": "#ff0000", "id": "demo-001"})`
```
{
  "updated": {
    "id": "demo-001",
    "name": "Disk Usage",
    "command": "df -h",
    "category": "Maintenance",
    "tooltip": "Show disk space usage for all mounted filesystems",
    "icon_name": "drive-harddisk-symbolic",
    "color": "#ff0000",
    "text_color": "",
    "hide_label": fals…
```
**Final answer:**
> The color of the "Disk Usage" button has been changed to red (#ff0000).

---

### T14 — Put the "Disk Usage" button in the "Maintenance" category.

**Score: 2/2** ✅
- ✅ Looked up button (get or list)
- ✅ No unnecessary update (already in Maintenance)

**Call 1:** `get_button({"name": "Disk Usage"})`
```
{
  "id": "demo-001",
  "name": "Disk Usage",
  "command": "df -h",
  "category": "Maintenance",
  "tooltip": "Show disk space usage for all mounted filesystems",
  "icon_name": "drive-harddisk-symbolic",
  "color": "#ff0000",
  "text_color": "",
  "hide_label": false,
  "hide_icon": false,
  "show_…
```
**Final answer:**
> The "Disk Usage" button is already in the "Maintenance" category.

---

### T15 — Make the button that updates system packages ask for confirmation before running.

**Score: 1/1** ✅
- ✅ list_buttons called

**Call 1:** `list_buttons({"category": ""})`
```
[
  {
    "id": "demo-001",
    "name": "Disk Usage",
    "command": "df -h",
    "category": "Maintenance",
    "tooltip": "Show disk space usage for all mounted filesystems",
    "icon_name": "drive-harddisk-symbolic",
    "color": "#ff0000",
    "text_color": "",
    "hide_label": false,
    "hid…
```
**Call 2:** `update_button({"confirm_before_run": true, "id": "16d48059-3d19-4547-9df2-fb362188c575"})`
```
{
  "updated": {
    "id": "16d48059-3d19-4547-9df2-fb362188c575",
    "name": "Update System Packages",
    "command": "apt update && apt upgrade -y",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": fals…
```
**Final answer:**
> The "Update System Packages" button has been updated to ask for confirmation before running.

---

### T16 — Rename my machine at 192.168.1.50 to 'Home NAS'.

**Score: 2/2** ✅
- ✅ list_machines called
- ✅ No unnecessary rename

**Call 1:** `list_machines({})`
```
[
  {
    "id": "aaa-111",
    "name": "Plex Server",
    "host": "192.168.1.10",
    "user": "fabien",
    "port": 22,
    "icon_name": "server",
    "group": ""
  },
  {
    "id": "bbb-222",
    "name": "Dev Laptop",
    "host": "192.168.1.20",
    "user": "fabien",
    "port": 22,
    "icon_name"…
```
---

### T17 — Add my work server at 10.0.0.5, user=admin, then create a button to restart nginx on it.

**Score: 4/4** ✅
- ✅ list_machines called
- ✅ No duplicate machine created
- ✅ create_button called
- ✅ machine_ids set on button

**Call 1:** `list_machines({})`
```
[
  {
    "id": "aaa-111",
    "name": "Plex Server",
    "host": "192.168.1.10",
    "user": "fabien",
    "port": 22,
    "icon_name": "server",
    "group": ""
  },
  {
    "id": "bbb-222",
    "name": "Dev Laptop",
    "host": "192.168.1.20",
    "user": "fabien",
    "port": 22,
    "icon_name"…
```
**Call 2:** `create_button({"command": "sudo systemctl restart nginx", "machine_ids": ["e843396c-fdd2-4085-a9b8-be1179beef34"], "name": "Restart Nginx"})`
```
{
  "created": {
    "id": "9755d639-55bb-44d6-bac7-a25989d31877",
    "name": "Restart Nginx",
    "command": "sudo systemctl restart nginx",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "h…
```
**Final answer:**
> I've checked your machines and found that "Work Server" (10.0.0.5) was already configured. I have now created a new button called **"Restart Nginx"** that runs `sudo systemctl restart nginx` on that server.

---

### T18 — Create a "Deploy" profile that runs as www-data in /var/www/myapp, then create a button that uses this profile to run "git pull".

**Score: 4/4** ✅
- ✅ list_profiles called before create_profile
- ✅ create_profile called
- ✅ create_button called
- ✅ profile_id set on button

**Call 1:** `help({})`
```
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by …
```
**Call 2:** `list_profiles({})`
```
[
  {
    "id": "b854982d-1797-47df-94ab-1f9d815b5c08",
    "name": "Web Admin",
    "run_as_user": "www-data",
    "working_dir": "/var/www",
    "description": "",
    "has_sudo_password": false
  }
]
```
**Call 3:** `create_profile({"name": "Deploy", "run_as_user": "www-data", "working_dir": "/var/www/myapp"})`
```
{
  "created": {
    "id": "e7324648-5686-400d-a3e9-b59146560f37",
    "name": "Deploy",
    "run_as_user": "www-data",
    "working_dir": "/var/www/myapp",
    "description": "",
    "has_sudo_password": false
  }
}
```
**Call 4:** `create_button({"command": "git pull", "name": "Deploy App", "profile_id": "e7324648-5686-400d-a3e9-b59146560f37"})`
```
{
  "created": {
    "id": "e95f0ff3-45c7-40db-9cad-1aabed466e69",
    "name": "Deploy App",
    "command": "git pull",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "hide_icon": false,
    "…
```
**Final answer:**
> I have successfully created the "Deploy" profile and the "Deploy App" button.

1.  **Profile Created**: "Deploy"
    *   **User**: `www-data`
    *   **Working Directory**: `/var/www/myapp`
    *   **ID**: `e7324648-5686-400d-a3e9-b59146560f37`

2.  **Button Created**: "Deploy App"
    *   **Command**: `git pull`
    *   **Profile Linked**: "Deploy"
    *   **ID**: `e95f0ff3-45c7-40db-9cad-1aabed466e69`

---

### T19 — Create a button called "Check Disk" that I can run either locally or on my home server, and I choose which one each time I click it.

**Score: 4/4** ✅
- ✅ list_machines called
- ✅ create_button called
- ✅ machine_ids includes "" (local pick)
- ✅ machine_ids includes a real UUID

**Call 1:** `help({})`
```
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by …
```
**Call 2:** `list_machines({})`
```
[
  {
    "id": "aaa-111",
    "name": "Plex Server",
    "host": "192.168.1.10",
    "user": "fabien",
    "port": 22,
    "icon_name": "server",
    "group": ""
  },
  {
    "id": "bbb-222",
    "name": "Dev Laptop",
    "host": "192.168.1.20",
    "user": "fabien",
    "port": 22,
    "icon_name"…
```
**Call 3:** `list_buttons({})`
```
[
  {
    "id": "demo-001",
    "name": "Disk Usage",
    "command": "df -h",
    "category": "Maintenance",
    "tooltip": "Show disk space usage for all mounted filesystems",
    "icon_name": "drive-harddisk-symbolic",
    "color": "#ff0000",
    "text_color": "",
    "hide_label": false,
    "hid…
```
**Call 4:** `create_button({"command": "df -h", "machine_ids": ["", "917de03a-904f-4e87-bd91-084b28d17c10"], "name": "Check Disk"})`
```
{
  "created": {
    "id": "9809b63f-380e-4e2b-9d3e-a2159ed7fba0",
    "name": "Check Disk",
    "command": "df -h",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "hide_icon": false,
    "sho…
```
**Final answer:**
> I've created the "Check Disk" button for you. 

I configured it with the command `df -h` and set the machine targets to include both your local machine (represented by an empty string in the machine list) and your "home server" (`917de03a-904f-4e87-bd91-084b28d17c10`). 

When you click the button, RemoteX will prompt you to choose which one to run it on.

---

### T20 — Delete the button called "LaunchRocket2049".

**Score: 2/2** ✅
- ✅ Looked up button (get or list)
- ✅ delete_button NOT called (not found)

**Call 1:** `get_button({"name": "LaunchRocket2049"})`
```
Error: button not found
```
**Call 2:** `list_buttons({})`
```
[
  {
    "id": "demo-001",
    "name": "Disk Usage",
    "command": "df -h",
    "category": "Maintenance",
    "tooltip": "Show disk space usage for all mounted filesystems",
    "icon_name": "drive-harddisk-symbolic",
    "color": "#ff0000",
    "text_color": "",
    "hide_label": false,
    "hid…
```
**Final answer:**
> I couldn't find a button named "LaunchRocket2049" to delete.

---

### T21 — Create a button that runs on machine ID "fake-uuid-does-not-exist".

**Score: 2/2** ✅
- ✅ Machines checked or immediately refused
- ✅ Fake UUID never used successfully

**Call 1:** `help({})`
```
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by …
```
**Final answer:**
> To create the button, I'll need a couple more details:
1. What should the **name** of the button be?
2. What **command** should it run?

---

### T22 — Create a button for me.

**Score: 2/2** ✅
- ✅ No blind create_button
- ✅ Asked user for name/command

**Call 1:** `help({})`
```
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by …
```
**Final answer:**
> I'd be happy to help you create a button! To do that, I'll need a few details:

1.  **Name**: What should the button be labeled?
2.  **Command**: What shell command should it run?

**Optional details you can also provide:**
*   **Category**: A name to group it with other buttons.
*   **Color**: A hex color (e.g., `#3584e4`) for the button background.
*   **Execution Mode**: How should it run? (`silent` for a toast, `output` for a dialog, or `terminal` to open a terminal).
*   **Machine**: Should it run on a specific remote machine? (If so, let me know the machine's name).
*   **Profile**: Shou

---

### T23 — Add a category called "System" if it does not exist yet.

**Score: 2/2** ✅
- ✅ list_categories called
- ✅ No create action

**Call 1:** `list_categories({})`
```
["Maintenance", "Network", "System"]
```
**Final answer:**
> The "System" category already exists.

---

### T24 — Create a button called "Deploy Website" that runs "git pull && composer install" on my Work Server, using the "Web Admin" profile, and running as root.

**Score: 6/6** ✅
- ✅ list_machines called
- ✅ list_profiles called
- ✅ create_button called
- ✅ machine_ids set
- ✅ profile_id set
- ✅ run_as=root

**Call 1:** `help({})`
```
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by …
```
**Call 2:** `list_machines({})`
```
[
  {
    "id": "aaa-111",
    "name": "Plex Server",
    "host": "192.168.1.10",
    "user": "fabien",
    "port": 22,
    "icon_name": "server",
    "group": ""
  },
  {
    "id": "bbb-222",
    "name": "Dev Laptop",
    "host": "192.168.1.20",
    "user": "fabien",
    "port": 22,
    "icon_name"…
```
**Call 3:** `list_profiles({})`
```
[
  {
    "id": "b854982d-1797-47df-94ab-1f9d815b5c08",
    "name": "Web Admin",
    "run_as_user": "www-data",
    "working_dir": "/var/www",
    "description": "",
    "has_sudo_password": false
  },
  {
    "id": "e7324648-5686-400d-a3e9-b59146560f37",
    "name": "Deploy",
    "run_as_user": "ww…
```
**Call 4:** `create_button({"command": "git pull && composer install", "machine_ids": ["e843396c-fdd2-4085-a9b8-be1179beef34"], "name": "Deploy Website", "profile_id": "b854982d-1797-47df-94ab-1f9d815b5c08", "run_as": "root"})`
```
{
  "created": {
    "id": "2d12aabc-c76f-4c64-b3d4-7d8379d32a80",
    "name": "Deploy Website",
    "command": "git pull && composer install",
    "category": "",
    "tooltip": "",
    "icon_name": "utilities-terminal-symbolic",
    "color": "",
    "text_color": "",
    "hide_label": false,
    "…
```
**Final answer:**
> The button "Deploy Website" has been successfully created. It is configured to run `git pull && composer install` on the **Work Server** using the **Web Admin** profile and will execute as **root**.

---

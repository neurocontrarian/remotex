"""Default buttons seeded on first run when buttons.toml does not exist."""

import sys

from .command_button import CommandButton


def get_default_buttons() -> list[CommandButton]:
    if sys.platform.startswith("win"):
        buttons = _windows_essentials() + _windows_development()
    else:
        buttons = _linux_essentials() + _linux_development()
    for i, btn in enumerate(buttons):
        btn.position = i
        btn.is_default = True
    return buttons


def _linux_essentials() -> list[CommandButton]:
    return [
        CommandButton(
            name="Disk Usage",
            command="df -h",
            icon_name="hdd",
            color="#99c1f1",
            show_output=True,
            tooltip="Show disk space usage for all mounted filesystems",
            category="Hardware",
        ),
        CommandButton(
            name="Memory Usage",
            command="free -h",
            icon_name="memory",
            color="#8ff0a4",
            show_output=True,
            tooltip="Show total, used and free RAM and swap memory",
            category="Hardware",
        ),
        CommandButton(
            name="CPU Load",
            command="uptime && echo && top -bn1 | head -15",
            icon_name="cpu",
            color="#ffbe6f",
            show_output=True,
            tooltip="Show system uptime, load averages and top CPU processes",
            category="Hardware",
        ),
        CommandButton(
            name="Temperature",
            command="sensors 2>/dev/null || echo 'lm-sensors is not installed.\nTo install: sudo apt install lm-sensors && sudo sensors-detect'",
            icon_name="thermometer-half",
            color="#ff7800",
            show_output=True,
            tooltip="Show CPU and GPU temperatures (requires lm-sensors)",
            category="Hardware",
        ),
        CommandButton(
            name="Running Processes",
            command="ps aux --sort=-%cpu | head -20",
            icon_name="activity",
            color="#dc8add",
            show_output=True,
            tooltip="List top 20 processes sorted by CPU usage",
            category="Linux Essentials",
        ),
        CommandButton(
            name="Network Interfaces",
            command="ip addr",
            icon_name="ethernet",
            color="#62a0ea",
            show_output=True,
            tooltip="Show all network interfaces and their IP addresses",
            category="Network",
        ),
        CommandButton(
            name="Active Connections",
            command="ss -tp state established",
            icon_name="plug",
            color="#57e389",
            show_output=True,
            tooltip="Show all active TCP connections and the processes using them",
            category="Network",
        ),
        CommandButton(
            name="Open Ports",
            command="ss -tulpn",
            icon_name="broadcast",
            color="#57e389",
            show_output=True,
            tooltip="List all open TCP/UDP ports and the processes using them",
            category="Network",
        ),
        CommandButton(
            name="Block Devices",
            command="lsblk",
            icon_name="stack",
            color="#cdab8f",
            show_output=True,
            tooltip="List all block devices (disks, partitions, loop devices)",
            category="Hardware",
        ),
        CommandButton(
            name="Largest Directories",
            # -x stays on the root filesystem: skips /proc, /sys and mounted
            # filesystems (snap squashfs, network mounts) that otherwise make
            # this hang and balloon the numbers.
            command="du -shx /* 2>/dev/null | sort -rh | head -15",
            icon_name="folder2",
            color="#e5a50a",
            show_output=True,
            timeout=120,
            tooltip="Show the 15 largest top-level directories by disk usage",
            category="Hardware",
        ),
        CommandButton(
            name="NVIDIA GPU",
            command="nvidia-smi 2>/dev/null || echo 'nvidia-smi not found. Install the NVIDIA proprietary driver.'",
            icon_name="pc-display",
            color="#76b900",
            show_output=True,
            tooltip="Show NVIDIA GPU activity, memory and processes (requires nvidia-smi)",
            category="Hardware",
        ),
        CommandButton(
            name="AMD GPU",
            command=(
                'echo "=== AMD GPU ==="; '
                'lspci 2>/dev/null | grep -iE "vga|3d|display" | grep -iE "amd|radeon" '
                '|| echo "(no AMD GPU detected via lspci)"; '
                'echo; echo "=== Activity ==="; '
                'found=0; for f in /sys/class/drm/card*/device/gpu_busy_percent; do '
                '[ -f "$f" ] && echo "$(echo $f | awk -F/ \'{print $5}\'): $(cat $f)%" && found=1; '
                'done; [ "$found" = "0" ] && echo "(activity counters not exposed by driver)"; '
                'echo; echo "=== Temperature & power ==="; '
                'sensors 2>/dev/null | awk \'/amdgpu/{p=1} p; /^$/{p=0}\' '
                '|| echo "(install lm-sensors for temperature: sudo apt install lm-sensors)"'
            ),
            icon_name="pc-display-horizontal",
            color="#ed1c24",
            show_output=True,
            tooltip="Show AMD GPU model, activity (sysfs) and temperature (sensors) — no extra packages required",
            category="Hardware",
        ),
        CommandButton(
            name="NCDU",
            command="command -v ncdu >/dev/null && ncdu / || echo 'ncdu not found. Install: sudo apt install ncdu'",
            icon_name="hdd",
            color="#3584e4",
            execution_mode="terminal",
            tooltip="Interactive disk usage analyzer (requires ncdu)",
            category="Hardware",
        ),
        CommandButton(
            name="btop",
            command="command -v btop >/dev/null && btop || echo 'btop not found. Install: sudo apt install btop'",
            icon_name="activity",
            color="#5e5c64",
            execution_mode="terminal",
            tooltip="Interactive resource monitor (requires btop)",
            category="Hardware",
        ),
        CommandButton(
            name="NVIDIA Settings",
            command="(nvidia-settings >/dev/null 2>&1 & disown) && echo 'nvidia-settings launched.' || echo 'nvidia-settings not found. Install: sudo apt install nvidia-settings'",
            icon_name="pc-display",
            color="#76b900",
            show_output=True,
            tooltip="Open the NVIDIA control panel to tune power limit, fan curves, clocks, etc.",
            category="Hardware",
        ),
        CommandButton(
            name="Hardware Info",
            command=(
                'if command -v inxi >/dev/null 2>&1; then '
                '  inxi -Fxz; '
                'else '
                '  echo "Tip: install inxi for a one-shot report — sudo apt install inxi"; echo; '
                '  echo "=== CPU ==="; lscpu | head -20; echo; '
                '  echo "=== Memory ==="; free -h; echo; '
                '  echo "=== Block devices ==="; lsblk; echo; '
                '  echo "=== PCI devices ==="; lspci | grep -iE "vga|3d|audio|network|ethernet"; echo; '
                '  echo "=== Motherboard / BIOS ==="; '
                '  (sudo -n dmidecode -t baseboard -t bios 2>/dev/null '
                '   || cat /sys/devices/virtual/dmi/id/board_{vendor,name,version} 2>/dev/null); '
                'fi'
            ),
            icon_name="cpu",
            color="#3584e4",
            show_output=True,
            timeout=60,
            tooltip="Show CPU, memory, motherboard, GPU, network and storage in one report (uses inxi if installed)",
            category="Hardware",
        ),
        CommandButton(
            name="System Info",
            command="uname -a && echo && lsb_release -a 2>/dev/null || cat /etc/os-release",
            icon_name="info-circle",
            color="#f9f06b",
            show_output=True,
            tooltip="Show kernel version and Linux distribution information",
            category="Linux Essentials",
        ),
        CommandButton(
            name="Logged-in Users",
            command="w",
            icon_name="people",
            color="#c061cb",
            show_output=True,
            tooltip="Show who is logged in and what they are doing",
            category="Linux Essentials",
        ),
        CommandButton(
            name="Last Logins",
            command="last | head -20",
            icon_name="person-check",
            color="#9141ac",
            show_output=True,
            tooltip="Show the last 20 login and logout events",
            category="Linux Essentials",
        ),
        CommandButton(
            name="Failed Services",
            command="systemctl --failed",
            icon_name="exclamation-triangle",
            color="#f66151",
            show_output=True,
            tooltip="List all systemd services that have failed — useful for diagnosing broken features",
            category="Linux Essentials",
        ),
        CommandButton(
            name="System Journal",
            command="journalctl -n 50 --no-pager",
            icon_name="journal-text",
            color="#ffa348",
            show_output=True,
            tooltip="Show the last 50 lines of the system journal (all services, cross-distro)",
            category="Linux Essentials",
        ),
        CommandButton(
            name="Kernel Messages",
            command="dmesg | tail -30",
            icon_name="cpu",
            color="#ffa348",
            show_output=True,
            tooltip="Show the last 30 kernel ring buffer messages (hardware, boot events)",
            category="Linux Essentials",
        ),
        CommandButton(
            name="Clear Trash",
            command="rm -rf ~/.local/share/Trash/files/* ~/.local/share/Trash/info/* 2>/dev/null && echo 'Trash cleared.'",
            icon_name="trash",
            color="#865e3c",
            confirm_before_run=True,
            tooltip="Permanently delete all files in the Trash",
            category="Linux Essentials",
        ),
        CommandButton(
            name="System Update",
            command="bash -c 'if command -v apt >/dev/null 2>&1; then sudo apt update && sudo apt upgrade -y; elif command -v dnf >/dev/null 2>&1; then sudo dnf upgrade -y; elif command -v pacman >/dev/null 2>&1; then sudo pacman -Syu --noconfirm; else echo \"Unknown package manager\"; fi'",
            icon_name="cloud-download",
            color="#62a0ea",
            show_output=True,
            confirm_before_run=True,
            tooltip="Refresh package lists and upgrade all installed packages (apt / dnf / pacman)",
            category="Linux Essentials",
        ),
        CommandButton(
            name="Reboot",
            command="systemctl reboot",
            icon_name="arrow-clockwise",
            color="#f8e45c",
            confirm_before_run=True,
            tooltip="Reboot the system immediately",
            category="Linux Essentials",
        ),
        CommandButton(
            name="Shutdown",
            command="systemctl poweroff",
            icon_name="power",
            color="#f66151",
            confirm_before_run=True,
            tooltip="Power off the system immediately",
            category="Linux Essentials",
        ),
    ]


def _linux_development() -> list[CommandButton]:
    return [
        CommandButton(
            name="Git Status",
            command="git status",
            icon_name="git",
            color="#dc8add",
            show_output=True,
            tooltip="Show working tree status (staged, unstaged, untracked files)",
            category="Development",
        ),
        CommandButton(
            name="Git Log",
            command="git log --oneline -15",
            icon_name="clock-history",
            color="#c061cb",
            show_output=True,
            tooltip="Show the last 15 commits in compact one-line format",
            category="Development",
        ),
        CommandButton(
            name="Git Diff",
            command="git diff",
            icon_name="file-earmark-diff",
            color="#cdab8f",
            show_output=True,
            tooltip="Show unstaged changes in the current working directory",
            category="Development",
        ),
        CommandButton(
            name="Docker PS",
            command="docker ps",
            icon_name="box-seam",
            color="#99c1f1",
            show_output=True,
            tooltip="List currently running Docker containers",
            category="Development",
        ),
        CommandButton(
            name="Docker PS All",
            command="docker ps -a",
            icon_name="box-seam",
            color="#62a0ea",
            show_output=True,
            tooltip="List all Docker containers including stopped ones",
            category="Development",
        ),
        CommandButton(
            name="Docker Images",
            command="docker images",
            icon_name="stack",
            color="#62a0ea",
            show_output=True,
            tooltip="List all locally available Docker images",
            category="Development",
        ),
        CommandButton(
            name="Docker Clean",
            command="docker system prune -f",
            icon_name="trash",
            color="#f66151",
            confirm_before_run=True,
            show_output=True,
            tooltip="Remove all stopped containers, unused networks, dangling images and build cache",
            category="Development",
        ),
        CommandButton(
            name="Tail Syslog",
            command="tail -n 50 /var/log/syslog 2>/dev/null || journalctl -n 50 --no-pager",
            icon_name="file-text",
            color="#ffa348",
            show_output=True,
            tooltip="Show the last 50 lines of the system log (syslog or journald)",
            category="Development",
        ),
        CommandButton(
            name="Disk I/O",
            command="iostat -x 1 3 2>/dev/null || vmstat -d 1 3 2>/dev/null || cat /proc/diskstats",
            icon_name="hdd",
            color="#cdab8f",
            show_output=True,
            tooltip="Show disk I/O statistics — uses iostat, vmstat or /proc/diskstats (whichever is available)",
            category="Hardware",
        ),
        CommandButton(
            name="Python Version",
            command="python3 --version && pip3 --version",
            icon_name="filetype-py",
            color="#f9f06b",
            show_output=True,
            tooltip="Show installed Python 3 and pip versions",
            category="Development",
        ),
        CommandButton(
            name="Pip Outdated",
            command="pip3 list --outdated 2>/dev/null | head -20 || echo 'pip3 not found'",
            icon_name="filetype-py",
            color="#e5a50a",
            show_output=True,
            tooltip="List Python packages that have newer versions available",
            category="Development",
        ),
        CommandButton(
            name="Node Version",
            command="node --version && npm --version",
            icon_name="filetype-js",
            color="#8ff0a4",
            show_output=True,
            tooltip="Show installed Node.js and npm versions",
            category="Development",
        ),
        CommandButton(
            name="NPM Outdated",
            command="npm outdated 2>/dev/null || echo 'npm not found or not in a Node project'",
            icon_name="filetype-js",
            color="#57e389",
            show_output=True,
            tooltip="List npm packages with newer versions available (run from a Node project folder)",
            category="Development",
        ),
        CommandButton(
            name="Listening Services",
            command="ss -tlnp",
            icon_name="broadcast",
            color="#57e389",
            show_output=True,
            tooltip="List all services listening on TCP ports",
            category="Network",
        ),
    ]


# --- Windows (Phase 27) ---------------------------------------------------
# Local commands run via `powershell -NoProfile -Command` (see
# services/executor.py::_run_local_windows), so these use PowerShell cmdlets.
# Constraints: statement separator is ';' (Windows PowerShell 5.1 has no '&&'),
# string literals use single quotes only (no double quotes — the whole command
# is passed as one argv element through list2cmdline), and execution_mode stays
# "" (output) because the terminal launcher is Linux-only.

def _windows_essentials() -> list[CommandButton]:
    return [
        CommandButton(
            name="Disk Usage",
            command="Get-PSDrive -PSProvider FileSystem",
            icon_name="hdd",
            color="#99c1f1",
            show_output=True,
            tooltip="Show disk space usage for all mounted filesystems",
            category="Hardware",
        ),
        CommandButton(
            name="Memory Usage",
            command=(
                "Get-CimInstance Win32_OperatingSystem | Select-Object "
                "@{N='TotalRAM(GB)';E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, "
                "@{N='FreeRAM(GB)';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}} | Format-List"
            ),
            icon_name="memory",
            color="#8ff0a4",
            show_output=True,
            tooltip="Show total, used and free RAM and swap memory",
            category="Hardware",
        ),
        CommandButton(
            name="CPU Load",
            command=(
                "Get-Process | Sort-Object CPU -Descending | Select-Object -First 15 "
                "Name, Id, CPU, @{N='Mem(MB)';E={[math]::Round($_.WS/1MB,1)}} | Format-Table -AutoSize"
            ),
            icon_name="cpu",
            color="#ffbe6f",
            show_output=True,
            tooltip="List the 15 processes using the most CPU",
            category="Hardware",
        ),
        CommandButton(
            name="Network Interfaces",
            command=(
                "Get-NetIPAddress | Where-Object AddressState -eq 'Preferred' | "
                "Sort-Object InterfaceAlias | Format-Table InterfaceAlias, IPAddress, "
                "AddressFamily, PrefixLength -AutoSize"
            ),
            icon_name="ethernet",
            color="#62a0ea",
            show_output=True,
            tooltip="Show all network interfaces and their IP addresses",
            category="Network",
        ),
        CommandButton(
            name="Open Ports",
            command=(
                "Get-NetTCPConnection -State Listen | Sort-Object LocalPort | Select-Object "
                "LocalAddress, LocalPort, OwningProcess, "
                "@{N='Process';E={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Name}} | "
                "Format-Table -AutoSize"
            ),
            icon_name="broadcast",
            color="#57e389",
            show_output=True,
            tooltip="List all open TCP/UDP ports and the processes using them",
            category="Network",
        ),
        CommandButton(
            name="Active Connections",
            command=(
                "Get-NetTCPConnection -State Established | Select-Object LocalAddress, LocalPort, "
                "RemoteAddress, RemotePort, "
                "@{N='Process';E={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Name}} | "
                "Format-Table -AutoSize"
            ),
            icon_name="plug",
            color="#57e389",
            show_output=True,
            tooltip="Show all active TCP connections and the processes using them",
            category="Network",
        ),
        CommandButton(
            name="Ping",
            command="ping 8.8.8.8",
            icon_name="wifi",
            color="#62a0ea",
            show_output=True,
            tooltip="Send 4 test packets to a public server to check internet connectivity",
            category="Network",
        ),
        CommandButton(
            name="System Info",
            command=(
                "Get-ComputerInfo | Select-Object CsName, WindowsProductName, WindowsVersion, "
                "OsArchitecture, CsManufacturer, CsModel, "
                "@{N='RAM(GB)';E={[math]::Round($_.CsTotalPhysicalMemory/1GB,1)}} | Format-List"
            ),
            icon_name="info-circle",
            color="#f9f06b",
            show_output=True,
            timeout=60,
            tooltip="Show Windows edition, version, hardware model and total memory",
            category="Windows Essentials",
        ),
        CommandButton(
            name="Running Services",
            command=(
                "Get-Service | Where-Object Status -eq 'Running' | Sort-Object DisplayName | "
                "Format-Table Status, Name, DisplayName -AutoSize"
            ),
            icon_name="server",
            color="#dc8add",
            show_output=True,
            tooltip="List all Windows services that are currently running",
            category="Windows Essentials",
        ),
        CommandButton(
            name="System Events",
            command=(
                "Get-EventLog -LogName System -Newest 20 -EntryType Error, Warning | "
                "Format-Table TimeGenerated, EntryType, Source, EventID -AutoSize"
            ),
            icon_name="journal-text",
            color="#ffa348",
            show_output=True,
            tooltip="Show the 20 most recent System event-log errors and warnings",
            category="Windows Essentials",
        ),
        CommandButton(
            name="Restart Explorer",
            command=(
                "Stop-Process -Name explorer -Force; Start-Sleep -Seconds 2; "
                "if (-not (Get-Process -Name explorer -ErrorAction SilentlyContinue)) { Start-Process explorer }; "
                "Write-Output 'Explorer restarted.'"
            ),
            icon_name="arrow-clockwise",
            color="#f8e45c",
            confirm_before_run=True,
            show_output=True,
            tooltip="Restart Windows Explorer (taskbar and desktop) to clear display glitches",
            category="Windows Essentials",
        ),
        CommandButton(
            name="Empty Recycle Bin",
            command="Clear-RecycleBin -Force -ErrorAction SilentlyContinue; Write-Output 'Recycle Bin emptied.'",
            icon_name="trash",
            color="#865e3c",
            confirm_before_run=True,
            show_output=True,
            tooltip="Permanently delete all files in the Recycle Bin",
            category="Windows Essentials",
        ),
        CommandButton(
            name="Reboot",
            command="Restart-Computer -Force",
            icon_name="arrow-clockwise",
            color="#f8e45c",
            confirm_before_run=True,
            show_output=True,
            tooltip="Reboot the system immediately",
            category="Windows Essentials",
        ),
        CommandButton(
            name="Shutdown",
            command="Stop-Computer -Force",
            icon_name="power",
            color="#f66151",
            confirm_before_run=True,
            show_output=True,
            tooltip="Power off the system immediately",
            category="Windows Essentials",
        ),
    ]


def _windows_development() -> list[CommandButton]:
    return [
        CommandButton(
            name="Git Status",
            command=(
                "if (Get-Command git -ErrorAction SilentlyContinue) { git status } "
                "else { Write-Output 'Git is not installed. Get it from https://git-scm.com' }"
            ),
            icon_name="git",
            color="#dc8add",
            show_output=True,
            tooltip="Show working tree status (staged, unstaged, untracked files)",
            category="Development",
        ),
        CommandButton(
            name="Git Log",
            command=(
                "if (Get-Command git -ErrorAction SilentlyContinue) { git log --oneline -15 } "
                "else { Write-Output 'Git is not installed. Get it from https://git-scm.com' }"
            ),
            icon_name="clock-history",
            color="#c061cb",
            show_output=True,
            tooltip="Show the last 15 commits in compact one-line format",
            category="Development",
        ),
        CommandButton(
            name="Python Version",
            command=(
                # The Microsoft Store ships a stub 'python' in WindowsApps that
                # only prints an install prompt; skip it, prefer the py launcher,
                # and use 'python -m pip' since pip.exe is often not on PATH.
                "$p = Get-Command python -ErrorAction SilentlyContinue; "
                "if ($p -and $p.Source -notlike '*WindowsApps*') { python --version; python -m pip --version } "
                "elseif (Get-Command py -ErrorAction SilentlyContinue) { py --version; py -m pip --version } "
                "else { Write-Output 'Python is not installed. Get it from https://python.org' }"
            ),
            icon_name="filetype-py",
            color="#f9f06b",
            show_output=True,
            tooltip="Show installed Python 3 and pip versions",
            category="Development",
        ),
        CommandButton(
            name="Node Version",
            command=(
                "if (Get-Command node -ErrorAction SilentlyContinue) { node --version; npm --version } "
                "else { Write-Output 'Node.js is not installed. Get it from https://nodejs.org' }"
            ),
            icon_name="filetype-js",
            color="#8ff0a4",
            show_output=True,
            tooltip="Show installed Node.js and npm versions",
            category="Development",
        ),
        CommandButton(
            name="Global npm Packages",
            command=(
                "if (Get-Command npm -ErrorAction SilentlyContinue) { npm list -g --depth=0 } "
                "else { Write-Output 'npm is not installed. Install Node.js from https://nodejs.org' }"
            ),
            icon_name="filetype-js",
            color="#57e389",
            show_output=True,
            tooltip="List npm packages installed globally",
            category="Development",
        ),
        CommandButton(
            name="Docker PS",
            command=(
                "if (Get-Command docker -ErrorAction SilentlyContinue) { docker ps } "
                "else { Write-Output 'Docker is not installed. Get Docker Desktop from https://docker.com' }"
            ),
            icon_name="box-seam",
            color="#99c1f1",
            show_output=True,
            tooltip="List currently running Docker containers",
            category="Development",
        ),
        CommandButton(
            name="Docker Images",
            command=(
                "if (Get-Command docker -ErrorAction SilentlyContinue) { docker images } "
                "else { Write-Output 'Docker is not installed. Get Docker Desktop from https://docker.com' }"
            ),
            icon_name="stack",
            color="#62a0ea",
            show_output=True,
            tooltip="List all locally available Docker images",
            category="Development",
        ),
        CommandButton(
            name="Editor Processes",
            command=(
                "Get-Process | Where-Object { $_.ProcessName -match "
                "'code|devenv|sublime|idea|pycharm|webstorm|rider|atom|notepad' } | "
                "Format-Table ProcessName, Id, @{N='Mem(MB)';E={[math]::Round($_.WS/1MB,1)}} -AutoSize"
            ),
            icon_name="pencil",
            color="#cdab8f",
            show_output=True,
            tooltip="Show running code editors and IDEs and their memory use",
            category="Development",
        ),
        CommandButton(
            name="Installed Packages",
            command=(
                "if (Get-Command winget -ErrorAction SilentlyContinue) { winget list } "
                "else { Write-Output 'winget is not available. Install App Installer from the Microsoft Store.' }"
            ),
            icon_name="box-seam",
            color="#99c1f1",
            show_output=True,
            tooltip="List all applications installed through winget",
            category="Development",
        ),
        CommandButton(
            name="Available Updates",
            command=(
                "if (Get-Command winget -ErrorAction SilentlyContinue) { winget upgrade } "
                "else { Write-Output 'winget is not available. Install App Installer from the Microsoft Store.' }"
            ),
            icon_name="cloud-download",
            color="#62a0ea",
            show_output=True,
            tooltip="List applications that have updates available through winget",
            category="Development",
        ),
    ]

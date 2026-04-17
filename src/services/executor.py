import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Callable

from models.command_button import CommandButton
from models.config import ConfigManager
from models.machine import Machine
from utils.threading import run_in_thread

# Terminal emulators tried in order. Each entry: [binary, separator_flag].
# The command built is: binary separator_flag bash -c "cmd"
_TERMINAL_CANDIDATES = [
    ["xterm", "-e"],
    ["gnome-terminal", "--"],
    ["konsole", "-e"],
    ["xfce4-terminal", "-e"],
    ["mate-terminal", "-e"],
    ["tilix", "-e"],
    ["terminator", "-e"],
    ["alacritty", "-e"],
    ["kitty"],
]


def detect_terminal() -> list[str] | None:
    """Return the prefix command for the first available terminal emulator, or None."""
    for cmd in _TERMINAL_CANDIDATES:
        if shutil.which(cmd[0]):
            return cmd
    return None


@dataclass
class ExecutionResult:
    success: bool
    return_code: int
    stdout: str
    stderr: str
    duration_ms: int
    button_id: str = ""


class CommandExecutor:
    def __init__(self, config: ConfigManager):
        self._config = config
        self._ssh = None  # Lazy import to avoid circular dependency

    def _get_timeout(self) -> int:
        try:
            import gi
            gi.require_version('Gio', '2.0')
            from gi.repository import Gio
            return Gio.Settings.new('com.github.remotex.RemoteX').get_int('command-timeout')
        except Exception:
            return 30

    def execute(self, button: CommandButton, callback: Callable[[ExecutionResult], None],
                machine_id: str | None = None):
        """Dispatch command execution to a background thread.

        machine_id: explicit machine to run on (overrides button.machine_ids).
                    None = derive from button: first remote UUID, or local if none.
                    ""   = explicit local execution.
        """
        # Terminal mode: local terminal, or auto-SSH when a machine is targeted.
        if button.execution_mode == "terminal":
            if machine_id is None:
                non_local = [mid for mid in button.machine_ids if mid]
                resolved_id = non_local[0] if non_local else ""
            else:
                resolved_id = machine_id

            if resolved_id:
                machine = self._find_machine(resolved_id)
                if machine is None:
                    callback(ExecutionResult(
                        success=False, return_code=-1,
                        stdout="", stderr=f"Machine '{resolved_id}' not found in config.",
                        duration_ms=0, button_id=button.id,
                    ))
                    return
                terminal_cmd = self._build_ssh_command(
                    machine, button.command, button.run_as_user
                )
            else:
                terminal_cmd = button.command

            run_in_thread(self._run_in_terminal, callback, terminal_cmd, button.id)
            return

        if machine_id is None:
            non_local = [mid for mid in button.machine_ids if mid]
            resolved_id = non_local[0] if non_local else ""
        else:
            resolved_id = machine_id

        if resolved_id:
            machine = self._find_machine(resolved_id)
            if machine is None:
                callback(ExecutionResult(
                    success=False, return_code=-1,
                    stdout="", stderr=f"Machine '{resolved_id}' not found in config.",
                    duration_ms=0, button_id=button.id,
                ))
                return
            run_in_thread(self._run_remote, callback, button.command, machine, button.id)
        else:
            run_in_thread(self._run_local, callback, button.command, button.id)

    def test_connection(self, machine: Machine, callback: Callable[[bool, str], None]):
        """Test SSH connectivity in a background thread."""
        ssh = self._get_ssh()
        run_in_thread(ssh.test_connection, lambda result: callback(*result), machine)

    def _run_local(self, command: str, button_id: str = "") -> ExecutionResult:
        timeout = self._get_timeout()
        start = time.monotonic()
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return ExecutionResult(
                success=(proc.returncode == 0),
                return_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_ms=int((time.monotonic() - start) * 1000),
                button_id=button_id,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="", stderr=f"Command timed out after {timeout} seconds.",
                duration_ms=timeout * 1000, button_id=button_id,
            )
        except Exception as e:
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="", stderr=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
                button_id=button_id,
            )

    def _build_ssh_command(self, machine: Machine, command: str, run_as_user: str = "") -> str:
        """Build an ssh -t command string for use inside bash -c."""
        args = ["ssh", "-t"]
        if machine.port != 22:
            args += ["-p", str(machine.port)]
        if machine.identity_file:
            args += ["-i", machine.identity_file]
        args.append(f"{machine.user}@{machine.host}")

        if run_as_user:
            remote_cmd = f"sudo -u {shlex.quote(run_as_user)} bash -c {shlex.quote(command)}"
        else:
            remote_cmd = command

        args.append(remote_cmd)
        # Join as a shell-safe string — will be passed to local bash -c
        return " ".join(shlex.quote(a) for a in args)

    def _run_in_terminal(self, command: str, button_id: str = "") -> ExecutionResult:
        """Open the command in a new terminal window (keeps the window open after exit)."""
        terminal = detect_terminal()
        if terminal is None:
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="",
                stderr="No terminal emulator found. Install xterm, gnome-terminal, or konsole.",
                duration_ms=0, button_id=button_id,
            )
        try:
            # Keep the terminal open after the command exits so the user can read output.
            bash_cmd = f'{command}; echo; read -p "Press Enter to close..."'
            subprocess.Popen(
                terminal + ["bash", "-c", bash_cmd],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return ExecutionResult(
                success=True, return_code=0,
                stdout="", stderr="",
                duration_ms=0, button_id=button_id,
            )
        except Exception as e:
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="", stderr=str(e),
                duration_ms=0, button_id=button_id,
            )

    def _run_remote(self, command: str, machine: Machine, button_id: str = "") -> ExecutionResult:
        return self._get_ssh().run_command(machine, command, button_id)

    def _find_machine(self, machine_id: str) -> Machine | None:
        return next((m for m in self._config.load_machines() if m.id == machine_id), None)

    def _get_ssh(self):
        if self._ssh is None:
            from services.ssh_service import SSHService
            self._ssh = SSHService()
        return self._ssh

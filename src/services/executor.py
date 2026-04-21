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

_TERM_COLS = 60
_TERM_ROWS = 18
_TERM_GEO = f"{_TERM_COLS}x{_TERM_ROWS}"

# Terminal emulators tried in order.
# Format: all args that come BEFORE ["bash", "-c", cmd].
_TERMINAL_CANDIDATES = [
    ["xterm", "-fa", "Monospace", "-fs", "13", "-geometry", _TERM_GEO, "-e"],
    ["gnome-terminal", f"--geometry={_TERM_GEO}", "--"],
    ["konsole", "-e"],
    ["xfce4-terminal", f"--geometry={_TERM_GEO}", "-e"],
    ["mate-terminal", f"--geometry={_TERM_GEO}", "-e"],
    ["tilix", "-e"],
    ["terminator", f"--geometry={_TERM_GEO}", "-e"],
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

    def _resolve_profile(self, button: CommandButton):
        """Return (run_as_user, working_dir) from assigned profile or button fields."""
        if button.profile_id:
            profile = self._config.get_profile_by_id(button.profile_id)
            if profile:
                return profile.run_as_user, profile.working_dir
        return button.run_as_user, ""

    def _get_sudo_password(self, button: CommandButton) -> str:
        pwd = button.get_sudo_password()
        if pwd:
            return pwd
        if button.profile_id:
            profile = self._config.get_profile_by_id(button.profile_id)
            if profile:
                return profile.get_sudo_password()
        return ""

    def execute(self, button: CommandButton, callback: Callable[[ExecutionResult], None],
                machine_id: str | None = None):
        """Dispatch command execution to a background thread.

        machine_id: explicit machine to run on (overrides button.machine_ids).
                    None = derive from button: first remote UUID, or local if none.
                    ""   = explicit local execution.
        """
        resolved_id = self._resolve_machine_id(button, machine_id)
        run_as_user, working_dir = self._resolve_profile(button)

        sudo_password = self._get_sudo_password(button) if run_as_user else ""

        if button.execution_mode == "terminal":
            if resolved_id:
                machine = self._find_machine(resolved_id)
                if machine is None:
                    callback(self._machine_not_found(resolved_id, button.id))
                    return
                terminal_cmd = self._build_ssh_command(
                    machine, button.command, run_as_user, working_dir,
                    sudo_password=sudo_password,
                )
            else:
                terminal_cmd = self._build_local_terminal_command(
                    button.command, run_as_user, working_dir, sudo_password=sudo_password
                )
            run_in_thread(self._run_in_terminal, callback, terminal_cmd, button.id)
            return

        if resolved_id:
            machine = self._find_machine(resolved_id)
            if machine is None:
                callback(self._machine_not_found(resolved_id, button.id))
                return
            run_in_thread(self._run_remote, callback, button.command, machine, button.id,
                          run_as_user, working_dir, sudo_password)
        else:
            run_in_thread(self._run_local, callback, button.command, button.id,
                          run_as_user, working_dir, sudo_password)

    def test_connection(self, machine: Machine, callback: Callable[[bool, str], None]):
        """Test SSH connectivity in a background thread."""
        ssh = self._get_ssh()
        run_in_thread(ssh.test_connection, lambda result: callback(*result), machine)

    def _run_local(self, command: str, button_id: str = "",
                   run_as_user: str = "", working_dir: str = "",
                   sudo_password: str = "") -> ExecutionResult:
        timeout = self._get_timeout()
        start = time.monotonic()
        try:
            effective_cmd = command
            stdin_input = None
            if run_as_user:
                if sudo_password:
                    effective_cmd = f"sudo -S -p '' -u {shlex.quote(run_as_user)} bash -c {shlex.quote(command)}"
                    stdin_input = sudo_password + "\n"
                else:
                    effective_cmd = f"sudo -u {shlex.quote(run_as_user)} bash -c {shlex.quote(command)}"
            cwd = working_dir if working_dir else None
            proc = subprocess.run(
                effective_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                input=stdin_input,
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

    def _build_ssh_command(self, machine: Machine, command: str,
                           run_as_user: str = "", working_dir: str = "",
                           sudo_password: str = "") -> str:
        """Build an ssh -t command string for use inside bash -c."""
        args = ["ssh", "-t"]
        if machine.port != 22:
            args += ["-p", str(machine.port)]
        if machine.identity_file:
            args += ["-i", machine.identity_file]
        args.append(f"{machine.user}@{machine.host}")

        base_cmd = f"cd {shlex.quote(working_dir)} && {command}" if working_dir else command
        if run_as_user:
            inner = f"exec < /dev/tty; {base_cmd}"
            if sudo_password:
                remote_cmd = (f"sudo -S -p '' -u {shlex.quote(run_as_user)} bash -c "
                              f"{shlex.quote(inner)} <<< {shlex.quote(sudo_password)}")
            else:
                remote_cmd = f"sudo -u {shlex.quote(run_as_user)} bash -c {shlex.quote(inner)}"
        else:
            remote_cmd = base_cmd

        args.append(remote_cmd)
        return " ".join(shlex.quote(a) for a in args)

    def _build_local_terminal_command(self, command: str,
                                      run_as_user: str = "",
                                      working_dir: str = "",
                                      sudo_password: str = "") -> str:
        base_cmd = f"cd {shlex.quote(working_dir)} && {command}" if working_dir else command
        if run_as_user:
            # exec < /dev/tty restores terminal stdin after sudo -S consumes the here-string.
            inner = f"exec < /dev/tty; {base_cmd}"
            if sudo_password:
                return (f"sudo -S -p '' -u {shlex.quote(run_as_user)} bash -c "
                        f"{shlex.quote(inner)} <<< {shlex.quote(sudo_password)}")
            return f"sudo -u {shlex.quote(run_as_user)} bash -c {shlex.quote(inner)}"
        return base_cmd

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

    def _run_remote(self, command: str, machine: Machine, button_id: str = "",
                    run_as_user: str = "", working_dir: str = "",
                    sudo_password: str = "") -> ExecutionResult:
        base = f"cd {shlex.quote(working_dir)} && {command}" if working_dir else command
        if run_as_user:
            if sudo_password:
                effective = (f"printf '%s\\n' {shlex.quote(sudo_password)} | "
                             f"sudo -S -p '' -u {shlex.quote(run_as_user)} bash -c {shlex.quote(base)}")
            else:
                effective = f"sudo -u {shlex.quote(run_as_user)} bash -c {shlex.quote(base)}"
        else:
            effective = base
        return self._get_ssh().run_command(machine, effective, button_id)

    def _resolve_machine_id(self, button: CommandButton, override: str | None) -> str:
        if override is not None:
            return override
        non_local = [mid for mid in button.machine_ids if mid]
        return non_local[0] if non_local else ""

    def _machine_not_found(self, machine_id: str, button_id: str) -> ExecutionResult:
        return ExecutionResult(
            success=False, return_code=-1,
            stdout="", stderr=f"Machine '{machine_id}' not found in config.",
            duration_ms=0, button_id=button_id,
        )

    def _find_machine(self, machine_id: str) -> Machine | None:
        return next((m for m in self._config.load_machines() if m.id == machine_id), None)

    def _get_ssh(self):
        if self._ssh is None:
            from services.ssh_service import SSHService
            self._ssh = SSHService()
        return self._ssh

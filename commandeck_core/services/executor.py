import functools
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Callable

from commandeck_core.models.command_button import CommandButton
from commandeck_core.models.config import ConfigManager
from commandeck_core.utils.threading import run_in_thread
from commandeck_core.utils.sandbox import host_argv, host_shell_argv, host_which
from commandeck_core.utils.exec_log import log as _exec_log


def _thread_name() -> str:
    import threading as _t
    return _t.current_thread().name

_TERM_COLS = 80
_TERM_ROWS = 24
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


@functools.cache
def detect_terminal() -> list[str] | None:
    """Return the prefix command for the first available terminal emulator, or None.

    Inside Flatpak, lookup happens on the host (sandbox runtime ships no terminal).
    """
    for cmd in _TERMINAL_CANDIDATES:
        if host_which(cmd[0]):
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
    def __init__(self, config: ConfigManager, get_timeout: Callable[[], int] | None = None):
        self._config = config
        self._get_global_timeout = get_timeout
        self._ssh = None  # Reserved for Pro extension (CommandExecutorPro)

    def _get_timeout(self, button: CommandButton | None = None) -> int:
        if button is not None and button.timeout > 0:
            return button.timeout
        if self._get_global_timeout is not None:
            return self._get_global_timeout()
        return 30  # default when no timeout source is injected (e.g. MCP / headless)

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
        SSH execution is not available in the free tier — use CommandExecutorPro.
        """
        _exec_log(f"executor.execute: button={button.name!r} cmd={button.command!r} mode={button.execution_mode!r} machine_id={machine_id!r}")
        resolved_id = self._resolve_machine_id(button, machine_id)
        run_as_user, working_dir = self._resolve_profile(button)
        sudo_password = self._get_sudo_password(button) if run_as_user else ""
        _exec_log(f"  resolved: resolved_id={resolved_id!r} run_as={run_as_user!r} cwd={working_dir!r} has_sudo_pw={bool(sudo_password)}")

        if button.execution_mode == "terminal":
            if resolved_id:
                callback(ExecutionResult(
                    success=False, return_code=-1,
                    stdout="", stderr="SSH execution requires Commandeck Pro.",
                    duration_ms=0, button_id=button.id,
                ))
                return
            terminal_cmd = self._build_local_terminal_command(
                button.command, run_as_user, working_dir, sudo_password=sudo_password
            )
            run_in_thread(self._run_in_terminal, callback, terminal_cmd, button.id)
            return

        if resolved_id:
            callback(ExecutionResult(
                success=False, return_code=-1,
                stdout="", stderr="SSH execution requires Commandeck Pro.",
                duration_ms=0, button_id=button.id,
            ))
        else:
            run_in_thread(self._run_local, callback, button.command, button.id,
                          run_as_user, working_dir, sudo_password, button.timeout)

    def execute_sync(self, button: CommandButton,
                     machine_id: str | None = None) -> ExecutionResult:
        """Synchronous variant of execute() for headless callers (MCP server).

        Bypasses the thread pool. The caller blocks until the command finishes
        or times out. UI code must continue to use execute() with a callback.
        """
        resolved_id = self._resolve_machine_id(button, machine_id)
        run_as_user, working_dir = self._resolve_profile(button)
        sudo_password = self._get_sudo_password(button) if run_as_user else ""

        if button.execution_mode == "terminal":
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="", stderr="Terminal execution mode is not supported via MCP.",
                duration_ms=0, button_id=button.id,
            )

        if resolved_id:
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="", stderr="SSH execution requires Commandeck Pro.",
                duration_ms=0, button_id=button.id,
            )
        return self._run_local(button.command, button.id,
                               run_as_user, working_dir, sudo_password, button.timeout)

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

    def _run_local(self, command: str, button_id: str = "",
                   run_as_user: str = "", working_dir: str = "",
                   sudo_password: str = "", timeout_override: int = 0) -> ExecutionResult:
        timeout = timeout_override if timeout_override > 0 else self._get_timeout()
        start = time.monotonic()
        _exec_log(f"_run_local: cmd={command!r} timeout={timeout}s thread={_thread_name()}")
        try:
            effective_cmd = command
            stdin_input = None
            if run_as_user:
                if sudo_password:
                    effective_cmd = f"sudo -S -p '' -u {shlex.quote(run_as_user)} bash -c {shlex.quote(command)}"
                    stdin_input = sudo_password + "\n"
                else:
                    effective_cmd = f"sudo -u {shlex.quote(run_as_user)} bash -c {shlex.quote(command)}"
            # Embed `cd` inside the shell command so it works whether the
            # command is dispatched locally or wrapped via flatpak-spawn --host
            # (where the host-side cwd is not inherited from the sandbox).
            if working_dir:
                import sys as _sys2
                if _sys2.platform.startswith("win"):
                    effective_cmd = f'cd /d "{working_dir}" && {effective_cmd}'
                else:
                    effective_cmd = f"cd {shlex.quote(working_dir)} && {effective_cmd}"
            import sys as _sys
            enc = "utf-8"  # explicit utf-8 everywhere; errors="replace" handles bad bytes
            _on_windows = _sys.platform.startswith("win")

            if _on_windows:
                _exec_log(f"  dispatching to _run_local_windows; effective_cmd={effective_cmd!r}")
                return self._run_local_windows(
                    effective_cmd, button_id, stdin_input, timeout, start, enc
                )

            proc = subprocess.run(
                host_shell_argv(effective_cmd),
                capture_output=True,
                text=True,
                encoding=enc,
                errors="replace",
                timeout=timeout,
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

    def _run_local_windows(self, effective_cmd: str, button_id: str,
                           stdin_input, timeout: int, start: float,
                           enc: str) -> ExecutionResult:
        """Run a command on Windows via PowerShell with file-handle output capture.

        Two reasons file-handle inheritance is used (vs subprocess.PIPE or shell
        redirection in the command line):

        1. Wine deadlock — Wine's anonymous-pipe emulation hangs subprocess.run
           when capture_output=True and the child writes to a redirected stdout
           (powershell.exe consistently, cmd.exe with CREATE_NO_WINDOW). File
           handles use the file system, not pipes, so the EOF bug never fires.
        2. Shell quoting — passing `> "path"` inside the command string runs
           into subprocess.list2cmdline + cmd.exe quoting incompatibility: the
           `\\"` escapes Python emits aren't escapes to cmd, so paths become
           garbled and redirection silently fails. Inheriting an opened file
           handle bypasses the shell parser entirely.

        PowerShell is forced into UTF-8 output mode via OutputEncoding so the
        file contents are decodable as UTF-8 (PowerShell 5 otherwise writes
        UTF-16 LE BOM when stdout is redirected).
        """
        import os as _os
        import tempfile as _tempfile
        from commandeck_core.utils.sandbox import is_wine

        _is_wine = is_wine()
        _exec_log(f"_run_local_windows: is_wine={_is_wine} thread={_thread_name()}")

        _out_fd, _out_path = _tempfile.mkstemp(suffix=".out", prefix="rx_")
        _err_fd, _err_path = _tempfile.mkstemp(suffix=".err", prefix="rx_")
        _os.close(_out_fd)
        _os.close(_err_fd)
        _exec_log(f"  tempfiles: out={_out_path!r} err={_err_path!r}")

        ps_cmd = (
            "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); "
            "$OutputEncoding = [System.Text.UTF8Encoding]::new(); "
            + effective_cmd
        )

        # CREATE_NO_WINDOW suppresses the console flash on real Windows. Under
        # Wine it has historically caused pipe EOF issues; file handles avoid
        # pipes so we can keep the flag on both, but to be conservative leave
        # it off under Wine where the console flash is harmless anyway.
        creationflags = 0 if _is_wine else subprocess.CREATE_NO_WINDOW
        _exec_log(f"  ps_cmd={ps_cmd!r}")
        _exec_log(f"  creationflags={creationflags:#x} timeout={timeout}s")

        try:
            with open(_out_path, 'wb') as _out_f, open(_err_path, 'wb') as _err_f:
                _exec_log("  -> subprocess.run(powershell ...) starting")
                proc = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    stdin=(subprocess.PIPE if stdin_input is not None else subprocess.DEVNULL),
                    stdout=_out_f,
                    stderr=_err_f,
                    creationflags=creationflags,
                    timeout=timeout,
                    input=(stdin_input.encode(enc) if stdin_input else None),
                )
                _exec_log(f"  <- subprocess.run returned rc={proc.returncode}")
            with open(_out_path, "r", encoding=enc, errors="replace") as _f:
                _stdout = _f.read()
            with open(_err_path, "r", encoding=enc, errors="replace") as _f:
                _stderr = _f.read()
            _exec_log(f"  read tempfiles: stdout_len={len(_stdout)} stderr_len={len(_stderr)}")
            if _stdout:
                _exec_log(f"  stdout[:200]={_stdout[:200]!r}")
            if _stderr:
                _exec_log(f"  stderr[:200]={_stderr[:200]!r}")
            duration = int((time.monotonic() - start) * 1000)
            _exec_log(f"  returning ExecutionResult(success={proc.returncode == 0}, rc={proc.returncode}, duration={duration}ms)")
            return ExecutionResult(
                success=(proc.returncode == 0),
                return_code=proc.returncode,
                stdout=_stdout,
                stderr=_stderr,
                duration_ms=duration,
                button_id=button_id,
            )
        except subprocess.TimeoutExpired:
            _exec_log(f"  TimeoutExpired after {timeout}s")
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="", stderr=f"Command timed out after {timeout} seconds.",
                duration_ms=timeout * 1000, button_id=button_id,
            )
        except FileNotFoundError as e:
            _exec_log(f"  FileNotFoundError: {e}")
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="",
                stderr=f"powershell.exe not found ({e}). Install Windows PowerShell or add it to PATH.",
                duration_ms=int((time.monotonic() - start) * 1000),
                button_id=button_id,
            )
        except Exception as e:
            import traceback as _tb
            _exec_log(f"  Exception {type(e).__name__}: {e}\n{_tb.format_exc()}")
            return ExecutionResult(
                success=False, return_code=-1,
                stdout="", stderr=f"{type(e).__name__}: {e}",
                duration_ms=int((time.monotonic() - start) * 1000),
                button_id=button_id,
            )
        finally:
            for _p in (_out_path, _err_path):
                try:
                    _os.unlink(_p)
                except OSError:
                    pass

    def _build_local_terminal_command(self, command: str,
                                      run_as_user: str = "",
                                      working_dir: str = "",
                                      sudo_password: str = "") -> str:
        if sys.platform.startswith("win"):
            # PowerShell terminal — run-as-user/sudo are POSIX-only and not
            # applied here. cd via Set-Location with single-quote escaping.
            if working_dir:
                wd = working_dir.replace("'", "''")
                return f"Set-Location -LiteralPath '{wd}'; {command}"
            return command
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
        if not sys.platform.startswith("linux"):
            # macOS (Terminal.app) and Windows (PowerShell) own their native
            # terminal launcher in the PlatformAdapter; the bash/xterm path
            # below is Linux-only.
            from commandeck_core.platform import get_platform
            ok = get_platform().open_in_terminal(command)
            return ExecutionResult(
                success=ok, return_code=0 if ok else -1,
                stdout="",
                stderr="" if ok else "Could not open a terminal window.",
                duration_ms=0, button_id=button_id,
            )
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
                host_argv(terminal + ["bash", "-c", bash_cmd]),
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

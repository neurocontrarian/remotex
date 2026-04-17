import time
from pathlib import Path

import fabric
from fabric import Connection
from paramiko.ssh_exception import (
    AuthenticationException,
    NoValidConnectionsError,
    SSHException,
)

from models.machine import Machine
from services.executor import ExecutionResult


def _get_command_timeout() -> int:
    try:
        import gi
        gi.require_version('Gio', '2.0')
        from gi.repository import Gio
        return Gio.Settings.new('com.github.remotex.RemoteX').get_int('command-timeout')
    except Exception:
        return 30


class SSHService:
    """Wraps Fabric Connection lifecycle for remote command execution."""

    def run_command(self, machine: Machine, command: str, button_id: str = "") -> ExecutionResult:
        """Open a connection, run a command, close it. Returns ExecutionResult."""
        start = time.monotonic()
        timeout = _get_command_timeout()
        conn = self._make_connection(machine)
        try:
            result = conn.run(command, hide=True, warn=True, timeout=timeout)
            return ExecutionResult(
                success=result.ok,
                return_code=result.return_code,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=int((time.monotonic() - start) * 1000),
                button_id=button_id,
            )
        except TimeoutError:
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
        finally:
            conn.close()

    def test_connection(self, machine: Machine) -> tuple[bool, str]:
        """Test SSH connectivity. Returns (success, message)."""
        conn = self._make_connection(machine)
        try:
            result = conn.run("echo remotex-ok", hide=True, timeout=10)
            if result.stdout.strip() == "remotex-ok":
                return True, f"Connected to {machine.host} as {machine.user}"
            return False, f"Unexpected response: {result.stdout.strip()}"
        except AuthenticationException:
            return False, "Authentication failed — check username and SSH key."
        except NoValidConnectionsError:
            return False, f"Could not connect to {machine.host}:{machine.port} — host unreachable."
        except TimeoutError:
            return False, f"Connection to {machine.host} timed out."
        except SSHException as e:
            return False, f"SSH error: {e}"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def _make_connection(self, machine: Machine) -> Connection:
        """Build a Fabric Connection from a Machine config."""
        connect_kwargs = {}
        if machine.identity_file:
            key_path = str(Path(machine.identity_file).expanduser())
            connect_kwargs["key_filename"] = key_path

        return Connection(
            host=machine.host,
            user=machine.user,
            port=machine.port,
            connect_kwargs=connect_kwargs,
            connect_timeout=10,
        )

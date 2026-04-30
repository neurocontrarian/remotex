import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pro.models.machine import Machine
from models.command_button import CommandButton
from models.config import ConfigManager
from services.executor import CommandExecutor, ExecutionResult


def make_executor():
    config = MagicMock(spec=ConfigManager)
    config.load_machines.return_value = []
    return CommandExecutor(config)


def test_run_local_success():
    executor = make_executor()
    result = executor._run_local("echo hello", "btn-1")
    assert result.success is True
    assert result.return_code == 0
    assert "hello" in result.stdout
    assert result.button_id == "btn-1"


def test_run_local_failure():
    executor = make_executor()
    result = executor._run_local("exit 1", "btn-2")
    assert result.success is False
    assert result.return_code == 1


def test_run_local_invalid_command():
    executor = make_executor()
    result = executor._run_local("this_command_does_not_exist_xyz", "btn-3")
    assert result.success is False
    assert result.return_code != 0


def test_run_local_captures_stderr():
    executor = make_executor()
    result = executor._run_local("echo error >&2; exit 1", "btn-4")
    assert result.success is False
    assert "error" in result.stderr


def test_execute_missing_machine():
    executor = make_executor()
    button = CommandButton(name="Test", command="ls", machine_ids=["nonexistent-id"])
    results = []
    executor.execute(button, results.append)

    import time
    time.sleep(0.2)
    assert len(results) == 1
    assert results[0].success is False
    assert "not found" in results[0].stderr


def test_run_remote_delegates_to_ssh_service():
    executor = make_executor()
    machine = Machine(name="Test", host="10.0.0.1", user="root")

    mock_ssh = MagicMock()
    mock_ssh.run_command.return_value = ExecutionResult(
        success=True, return_code=0,
        stdout="remote output", stderr="",
        duration_ms=42, button_id="btn-5",
    )
    executor._ssh = mock_ssh

    result = executor._run_remote("uptime", machine, "btn-5")
    mock_ssh.run_command.assert_called_once_with(machine, "uptime", "btn-5")
    assert result.success is True
    assert result.stdout == "remote output"

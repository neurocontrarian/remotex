import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.command_button import CommandButton
from pro.models.machine import Machine
import pro.mcp_server as mcp_server


# ── helpers ──────────────────────────────────────────────────────────────────

def make_mock_config(buttons=None, machines=None):
    cfg = MagicMock()
    cfg.load_buttons.return_value = buttons or []
    cfg.load_machines.return_value = machines or []
    return cfg


def _btn(name="Test", command="echo hi", **kw):
    return CommandButton(name=name, command=command, **kw)


# ── help ─────────────────────────────────────────────────────────────────────

def test_handle_help_returns_help_text():
    result = mcp_server.handle_help({})
    assert "list_buttons" in result
    assert "create_button" in result
    assert "delete_button" in result   # must document the absence


# ── list_buttons ─────────────────────────────────────────────────────────────

def test_list_buttons_all():
    cfg = make_mock_config(buttons=[_btn("A"), _btn("B")])
    with patch.object(mcp_server, '_config', cfg):
        out = json.loads(mcp_server.handle_list_buttons({}))
    assert len(out) == 2
    assert out[0]["name"] == "A"


def test_list_buttons_category_filter():
    cfg = make_mock_config(buttons=[
        _btn("A", category="Dev"),
        _btn("B", category="Ops"),
    ])
    with patch.object(mcp_server, '_config', cfg):
        out = json.loads(mcp_server.handle_list_buttons({"category": "Dev"}))
    assert len(out) == 1
    assert out[0]["name"] == "A"


# ── get_button ────────────────────────────────────────────────────────────────

def test_get_button_by_id():
    btn = _btn("MyBtn")
    cfg = make_mock_config(buttons=[btn])
    with patch.object(mcp_server, '_config', cfg):
        out = json.loads(mcp_server.handle_get_button({"id": btn.id}))
    assert out["name"] == "MyBtn"


def test_get_button_by_name_case_insensitive():
    btn = _btn("MyBtn")
    cfg = make_mock_config(buttons=[btn])
    with patch.object(mcp_server, '_config', cfg):
        out = json.loads(mcp_server.handle_get_button({"name": "mybtn"}))
    assert out["id"] == btn.id


def test_get_button_not_found():
    cfg = make_mock_config(buttons=[])
    with patch.object(mcp_server, '_config', cfg):
        out = mcp_server.handle_get_button({"id": "does-not-exist"})
    assert out.startswith("Error:")


def test_get_button_no_args():
    cfg = make_mock_config(buttons=[])
    with patch.object(mcp_server, '_config', cfg):
        out = mcp_server.handle_get_button({})
    assert out.startswith("Error:")


# ── create_button ─────────────────────────────────────────────────────────────

def test_create_button_success():
    cfg = make_mock_config()
    with patch.object(mcp_server, '_config', cfg):
        out = json.loads(mcp_server.handle_create_button({"name": "X", "command": "ls"}))
    assert out["created"]["name"] == "X"
    cfg.add_button.assert_called_once()


def test_create_button_missing_name():
    cfg = make_mock_config()
    with patch.object(mcp_server, '_config', cfg):
        out = mcp_server.handle_create_button({"command": "ls"})
    assert out.startswith("Error:")


def test_create_button_missing_command():
    cfg = make_mock_config()
    with patch.object(mcp_server, '_config', cfg):
        out = mcp_server.handle_create_button({"name": "X"})
    assert out.startswith("Error:")


def test_create_button_invalid_machine_id():
    machine = Machine(name="M", host="1.2.3.4", user="u")
    cfg = make_mock_config(machines=[machine])
    with patch.object(mcp_server, '_config', cfg):
        out = mcp_server.handle_create_button({
            "name": "X", "command": "ls",
            "machine_ids": ["bad-uuid-that-does-not-exist"],
        })
    assert out.startswith("Error:")


def test_create_button_valid_machine_id():
    machine = Machine(name="M", host="1.2.3.4", user="u")
    cfg = make_mock_config(machines=[machine])
    with patch.object(mcp_server, '_config', cfg):
        out = json.loads(mcp_server.handle_create_button({
            "name": "X", "command": "ls",
            "machine_ids": [machine.id],
        }))
    assert out["created"]["machine_ids"] == [machine.id]


# ── update_button ─────────────────────────────────────────────────────────────

def test_update_button_success():
    btn = _btn("Old Name")
    cfg = make_mock_config(buttons=[btn])
    with patch.object(mcp_server, '_config', cfg):
        out = json.loads(mcp_server.handle_update_button({"id": btn.id, "name": "New Name"}))
    assert out["updated"]["name"] == "New Name"
    cfg.update_button.assert_called_once()


def test_update_button_missing_id():
    cfg = make_mock_config(buttons=[_btn()])
    with patch.object(mcp_server, '_config', cfg):
        out = mcp_server.handle_update_button({"name": "X"})
    assert out.startswith("Error:")


def test_update_button_not_found():
    cfg = make_mock_config(buttons=[])
    with patch.object(mcp_server, '_config', cfg):
        out = mcp_server.handle_update_button({"id": "ghost-id"})
    assert out.startswith("Error:")


# ── _validate_machine_ids ─────────────────────────────────────────────────────

def test_validate_machine_ids_empty_list_ok():
    cfg = make_mock_config(machines=[])
    with patch.object(mcp_server, '_config', cfg):
        assert mcp_server._validate_machine_ids([]) is None


def test_validate_machine_ids_local_empty_string_ok():
    cfg = make_mock_config(machines=[])
    with patch.object(mcp_server, '_config', cfg):
        assert mcp_server._validate_machine_ids([""]) is None


def test_validate_machine_ids_unknown_returns_error():
    cfg = make_mock_config(machines=[])
    with patch.object(mcp_server, '_config', cfg):
        err = mcp_server._validate_machine_ids(["unknown-id"])
    assert err is not None and err.startswith("Error:")


def test_validate_machine_ids_not_a_list():
    cfg = make_mock_config(machines=[])
    with patch.object(mcp_server, '_config', cfg):
        err = mcp_server._validate_machine_ids("not-a-list")
    assert err is not None and err.startswith("Error:")


# ── MCP disabled gate ─────────────────────────────────────────────────────────

def test_mcp_disabled_tools_list_empty():
    with patch.object(mcp_server, '_is_mcp_enabled', return_value=False):
        responses = []
        with patch.object(mcp_server, '_send', side_effect=responses.append):
            mcp_server._dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    assert responses[0]["result"]["tools"] == []


def test_mcp_disabled_tools_call_returns_error():
    with patch.object(mcp_server, '_is_mcp_enabled', return_value=False):
        responses = []
        with patch.object(mcp_server, '_send', side_effect=responses.append):
            mcp_server._dispatch({
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "help", "arguments": {}},
            })
    assert responses[0]["result"]["isError"] is True


# ── unknown tool ──────────────────────────────────────────────────────────────

# ── execute_button ────────────────────────────────────────────────────────────

class _FakeResult:
    def __init__(self, success=True, return_code=0, stdout="ok", stderr="",
                 duration_ms=42, button_id=""):
        self.success = success
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.button_id = button_id


class _FakeExecutor:
    def __init__(self, result=None):
        self.result = result or _FakeResult()
        self.calls = []

    def execute_sync(self, button, machine_id=None):
        self.calls.append((button.id, machine_id))
        return self.result


def _patch_make_executor(executor):
    """Patch feature_gate.make_executor — imported lazily inside the handler."""
    import feature_gate
    return patch.object(feature_gate, 'make_executor', return_value=executor)


def test_execute_button_global_flag_off():
    btn = _btn(mcp_executable=True)
    cfg = make_mock_config(buttons=[btn])
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=False):
        out = json.loads(mcp_server.handle_execute_button({"id": btn.id}))
    assert "disabled" in out["error"].lower()


def test_execute_button_not_opted_in():
    btn = _btn(mcp_executable=False)
    cfg = make_mock_config(buttons=[btn])
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True):
        out = json.loads(mcp_server.handle_execute_button({"id": btn.id}))
    assert "not enabled for MCP execution" in out["error"]


def test_execute_button_requires_confirmation():
    btn = _btn(mcp_executable=True, confirm_before_run=True)
    cfg = make_mock_config(buttons=[btn])
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True):
        out = json.loads(mcp_server.handle_execute_button({"id": btn.id}))
    assert out["error"] == "requires_confirmation"
    assert out["button"]["command"] == btn.command


def test_execute_button_with_confirmed_runs():
    btn = _btn(mcp_executable=True, confirm_before_run=True)
    cfg = make_mock_config(buttons=[btn])
    fake = _FakeExecutor()
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True), \
         patch.object(mcp_server, '_append_audit_log'), \
         _patch_make_executor(fake):
        out = json.loads(mcp_server.handle_execute_button({
            "id": btn.id, "confirmed": True,
        }))
    assert out["success"] is True
    assert fake.calls == [(btn.id, None)]


def test_execute_button_multi_machine_no_choice():
    machine = Machine(name="M", host="1.2.3.4", user="u")
    btn = _btn(mcp_executable=True, machine_ids=["", machine.id])
    cfg = make_mock_config(buttons=[btn], machines=[machine])
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True):
        out = json.loads(mcp_server.handle_execute_button({"id": btn.id}))
    assert out["error"] == "requires_machine_choice"
    target_ids = [t["id"] for t in out["targets"]]
    assert "" in target_ids
    assert machine.id in target_ids


def test_execute_button_local_success():
    btn = _btn(mcp_executable=True)
    cfg = make_mock_config(buttons=[btn])
    fake = _FakeExecutor(_FakeResult(stdout="hello world"))
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True), \
         patch.object(mcp_server, '_append_audit_log'), \
         _patch_make_executor(fake):
        out = json.loads(mcp_server.handle_execute_button({"id": btn.id}))
    assert out["success"] is True
    assert out["stdout"] == "hello world"
    assert out["machine"] == "local"
    assert fake.calls == [(btn.id, None)]


def test_execute_button_audit_log_appended(tmp_path):
    btn = _btn(mcp_executable=True)
    cfg = make_mock_config(buttons=[btn])
    fake = _FakeExecutor()
    fake_home = tmp_path
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True), \
         patch.object(mcp_server.Path, 'home', return_value=fake_home), \
         _patch_make_executor(fake):
        mcp_server.handle_execute_button({"id": btn.id})
    log = fake_home / '.config' / 'remotex' / '.mcp_executions.log'
    assert log.exists()
    content = log.read_text()
    assert btn.id in content
    assert "exit=0" in content


def test_execute_button_no_args_returns_error():
    cfg = make_mock_config(buttons=[])
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True):
        out = mcp_server.handle_execute_button({})
    assert out.startswith("Error:")


def test_execute_button_not_found():
    cfg = make_mock_config(buttons=[])
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True):
        out = mcp_server.handle_execute_button({"id": "ghost-id"})
    assert out.startswith("Error:")


def test_execute_button_terminal_mode_rejected():
    """Terminal mode is rejected by execute_sync, not by the handler — the error
    surfaces in the result."""
    btn = _btn(mcp_executable=True, execution_mode="terminal")
    cfg = make_mock_config(buttons=[btn])
    fake = _FakeExecutor(_FakeResult(
        success=False, return_code=-1,
        stdout="", stderr="Terminal execution mode is not supported via MCP.",
    ))
    with patch.object(mcp_server, '_config', cfg), \
         patch.object(mcp_server, '_is_mcp_execution_enabled', return_value=True), \
         patch.object(mcp_server, '_append_audit_log'), \
         _patch_make_executor(fake):
        out = json.loads(mcp_server.handle_execute_button({"id": btn.id}))
    assert out["success"] is False
    assert "Terminal" in out["stderr"]


def test_unknown_tool_returns_json_rpc_error():
    with patch.object(mcp_server, '_is_mcp_enabled', return_value=True):
        responses = []
        with patch.object(mcp_server, '_send', side_effect=responses.append):
            mcp_server._dispatch({
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "nonexistent_tool_xyz", "arguments": {}},
            })
    assert "error" in responses[0]

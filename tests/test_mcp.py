import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.command_button import CommandButton
from models.machine import Machine
import mcp_server


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

def test_unknown_tool_returns_json_rpc_error():
    with patch.object(mcp_server, '_is_mcp_enabled', return_value=True):
        responses = []
        with patch.object(mcp_server, '_send', side_effect=responses.append):
            mcp_server._dispatch({
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "nonexistent_tool_xyz", "arguments": {}},
            })
    assert "error" in responses[0]

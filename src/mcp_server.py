#!/usr/bin/env python3
"""
RemoteX MCP Server — config-only, JSON-RPC 2.0 stdio transport.

Exposes 6 tools for reading and writing the RemoteX button/machine config:
  list_buttons, get_button, create_button, update_button,
  list_categories, list_machines

Deletion is intentionally not exposed — buttons must be deleted from the UI.

Add to Claude Desktop (~/.config/Claude/claude_desktop_config.json):
  {
    "mcpServers": {
      "remotex": {
        "command": "python3",
        "args": ["/path/to/remotex/src/mcp_server.py"]
      }
    }
  }
"""

import sys
import json
import os
from pathlib import Path

# Allow importing RemoteX models without a full app install
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.config import ConfigManager
from models.command_button import CommandButton
from models.machine import Machine

_config = ConfigManager()
_MCP_ENABLED_FLAG = Path.home() / '.config' / 'remotex' / '.mcp_enabled'


def _is_mcp_enabled() -> bool:
    return _MCP_ENABLED_FLAG.exists()


# ── Tool definitions ─────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_buttons",
        "description": "List all RemoteX buttons. Optionally filter by category.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filter by category name. Leave empty for all buttons.",
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "get_button",
        "description": "Get a specific button by its ID or name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id":   {"type": "string", "description": "Button UUID"},
                "name": {"type": "string", "description": "Button name (case-insensitive, first match)"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "create_button",
        "description": "Create a new RemoteX button.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name":               {"type": "string",  "description": "Button label"},
                "command":            {"type": "string",  "description": "Shell command to run"},
                "category":           {"type": "string",  "description": "Category name (optional)"},
                "tooltip":            {"type": "string",  "description": "Hover tooltip (optional, defaults to command)"},
                "show_output":        {"type": "boolean", "description": "Show output dialog after execution"},
                "confirm_before_run": {"type": "boolean", "description": "Ask for confirmation before running"},
                "icon_name":          {"type": "string",  "description": "Icon name (optional)"},
                "color":              {"type": "string",  "description": "Background color as hex (#3584e4, optional)"},
                "text_color":         {"type": "string",  "description": "Label text color as hex (#ffffff, optional)"},
                "hide_label":         {"type": "boolean", "description": "Icon-only mode — hide the button text label"},
                "hide_icon":          {"type": "boolean", "description": "Text-only mode — hide the button icon"},
                "machine_ids":        {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Machine UUIDs to run on. Empty list = local. Use list_machines to get UUIDs.",
                },
                "execution_mode":     {"type": "string",  "description": "Output mode: 'silent' (toast only), 'output' (show dialog), 'terminal' (open terminal). Default: 'silent'."},
                "run_as_user":        {"type": "string",  "description": "Run as a different user on remote (e.g. 'root'). Terminal + remote only."},
            },
            "required": ["name", "command"],
            "additionalProperties": False,
        },
    },
    {
        "name": "update_button",
        "description": "Update an existing RemoteX button. Only fields provided are changed. Use get_button first to retrieve the current ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id":                 {"type": "string",  "description": "Button UUID to update (required)"},
                "name":               {"type": "string",  "description": "New button label"},
                "command":            {"type": "string",  "description": "New shell command"},
                "category":           {"type": "string",  "description": "New category name"},
                "tooltip":            {"type": "string",  "description": "New hover tooltip"},
                "show_output":        {"type": "boolean", "description": "Show output dialog after execution"},
                "confirm_before_run": {"type": "boolean", "description": "Ask for confirmation before running"},
                "icon_name":          {"type": "string",  "description": "New icon name"},
                "color":              {"type": "string",  "description": "Background color as hex (#ff0000). Use empty string to remove color."},
                "text_color":         {"type": "string",  "description": "Label text color as hex (#ffffff). Use empty string to reset to theme default."},
                "hide_label":         {"type": "boolean", "description": "Icon-only mode — hide the button text label"},
                "hide_icon":          {"type": "boolean", "description": "Text-only mode — hide the button icon"},
                "machine_ids":        {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Machine UUIDs to run on. Empty list = local only. Use list_machines to get UUIDs.",
                },
                "execution_mode":     {"type": "string",  "description": "Output mode: 'silent', 'output', or 'terminal'."},
                "run_as_user":        {"type": "string",  "description": "Run as a different user on remote. Terminal + remote only."},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    # delete_button intentionally not exposed — deletion requires the RemoteX UI.
    {
        "name": "list_categories",
        "description": "List all category names used by RemoteX buttons (sorted).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "list_machines",
        "description": "List configured SSH machines (name, host, user, port). Private key paths are not returned.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]

# ── Serialisation helpers ────────────────────────────────────────────────────

def _button_to_dict(b: CommandButton) -> dict:
    return {
        "id":                 b.id,
        "name":               b.name,
        "command":            b.command,
        "category":           b.category,
        "tooltip":            b.tooltip,
        "icon_name":          b.icon_name,
        "color":              b.color,
        "text_color":         b.text_color,
        "hide_label":         b.hide_label,
        "hide_icon":          b.hide_icon,
        "show_output":        b.show_output,
        "execution_mode":     b.execution_mode,
        "confirm_before_run": b.confirm_before_run,
        "run_as_user":        b.run_as_user,
        "is_default":         b.is_default,
        "machine_ids":        b.machine_ids,
        "position":           b.position,
    }

def _machine_to_dict(m: Machine) -> dict:
    # Intentionally omit identity_file (path to private key — sensitive)
    return {
        "id":   m.id,
        "name": m.name,
        "host": m.host,
        "user": m.user,
        "port": m.port,
    }

# ── Tool handlers ────────────────────────────────────────────────────────────

def handle_list_buttons(args: dict) -> str:
    category = args.get("category", "")
    buttons = _config.load_buttons()
    if category:
        buttons = [b for b in buttons if b.category == category]
    return json.dumps([_button_to_dict(b) for b in buttons], ensure_ascii=False, indent=2)


def handle_get_button(args: dict) -> str:
    bid  = args.get("id", "")
    name = args.get("name", "")
    if not bid and not name:
        return "Error: provide 'id' or 'name'"
    buttons = _config.load_buttons()
    if bid:
        btn = next((b for b in buttons if b.id == bid), None)
    else:
        btn = next((b for b in buttons if b.name.lower() == name.lower()), None)
    if btn is None:
        return "Error: button not found"
    return json.dumps(_button_to_dict(btn), ensure_ascii=False, indent=2)


def _validate_machine_ids(ids: list) -> str | None:
    if not isinstance(ids, list):
        return "Error: machine_ids must be a list"
    known = {m.id for m in _config.load_machines()} | {""}
    bad = [mid for mid in ids if mid not in known]
    if bad:
        return f"Error: unknown machine IDs {bad} — call list_machines to get valid UUIDs"
    return None


def handle_create_button(args: dict) -> str:
    name    = args.get("name", "").strip()
    command = args.get("command", "").strip()
    if not name or not command:
        return "Error: 'name' and 'command' are required"
    machine_ids = args.get("machine_ids", [])
    err = _validate_machine_ids(machine_ids)
    if err:
        return err
    btn = CommandButton(
        name=name,
        command=command,
        category=           args.get("category", ""),
        tooltip=            args.get("tooltip", ""),
        show_output=        bool(args.get("show_output", False)),
        confirm_before_run= bool(args.get("confirm_before_run", False)),
        icon_name=          args.get("icon_name", "utilities-terminal-symbolic"),
        color=              args.get("color", ""),
        text_color=         args.get("text_color", ""),
        hide_label=         bool(args.get("hide_label", False)),
        hide_icon=          bool(args.get("hide_icon", False)),
        execution_mode=     args.get("execution_mode", ""),
        run_as_user=        args.get("run_as_user", ""),
        machine_ids=        machine_ids,
    )
    _config.add_button(btn)
    return json.dumps({"created": _button_to_dict(btn)}, ensure_ascii=False, indent=2)


def handle_update_button(args: dict) -> str:
    bid = args.get("id", "")
    if not bid:
        return "Error: 'id' is required"
    buttons = _config.load_buttons()
    btn = next((b for b in buttons if b.id == bid), None)
    if btn is None:
        return f"Error: button not found: {bid}"
    for field in ("name", "command", "category", "tooltip", "icon_name", "color",
                  "text_color", "execution_mode", "run_as_user"):
        if field in args:
            setattr(btn, field, args[field])
    for field in ("show_output", "confirm_before_run", "hide_label", "hide_icon"):
        if field in args:
            setattr(btn, field, bool(args[field]))
    if "machine_ids" in args:
        err = _validate_machine_ids(args["machine_ids"])
        if err:
            return err
        btn.machine_ids = args["machine_ids"]
    _config.update_button(btn)
    return json.dumps({"updated": _button_to_dict(btn)}, ensure_ascii=False, indent=2)



def handle_list_categories(args: dict) -> str:
    buttons = _config.load_buttons()
    cats = sorted({b.category for b in buttons if b.category})
    return json.dumps(cats, ensure_ascii=False)


def handle_list_machines(args: dict) -> str:
    machines = _config.load_machines()
    return json.dumps([_machine_to_dict(m) for m in machines], ensure_ascii=False, indent=2)


HANDLERS = {
    "list_buttons":    handle_list_buttons,
    "get_button":      handle_get_button,
    "create_button":   handle_create_button,
    "update_button":   handle_update_button,
    "list_categories": handle_list_categories,
    "list_machines":   handle_list_machines,
}

# ── JSON-RPC 2.0 / MCP protocol ──────────────────────────────────────────────

def _send(obj: dict):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def _send_result(req_id, result):
    _send({"jsonrpc": "2.0", "id": req_id, "result": result})

def _send_error(req_id, code: int, message: str):
    _send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})

def _dispatch(msg: dict):
    method  = msg.get("method", "")
    req_id  = msg.get("id")
    params  = msg.get("params") or {}

    if method == "initialize":
        _send_result(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "remotex", "version": "1.0.0"},
        })
        return

    if method == "notifications/initialized":
        return  # notification — no response

    if method == "ping":
        _send_result(req_id, {})
        return

    if method == "tools/list":
        tools = TOOLS if _is_mcp_enabled() else []
        _send_result(req_id, {"tools": tools})
        return

    if method == "tools/call":
        if not _is_mcp_enabled():
            _send_result(req_id, {
                "content": [{"type": "text", "text":
                    "MCP access is disabled. Enable it in RemoteX → Preferences → Desktop Integration."}],
                "isError": True,
            })
            return
        tool_name = params.get("name", "")
        tool_args = params.get("arguments") or {}
        handler = HANDLERS.get(tool_name)
        if handler is None:
            _send_error(req_id, -32601, f"Unknown tool: {tool_name}")
            return
        try:
            text = handler(tool_args)
        except Exception as exc:
            text = f"Error: {exc}"
        _send_result(req_id, {
            "content": [{"type": "text", "text": text}],
            "isError": text.startswith("Error:"),
        })
        return

    if req_id is not None:
        _send_error(req_id, -32601, f"Method not found: {method}")


def main():
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError as exc:
            _send_error(None, -32700, f"Parse error: {exc}")
            continue
        try:
            _dispatch(msg)
        except Exception as exc:
            _send_error(msg.get("id"), -32603, f"Internal error: {exc}")


if __name__ == "__main__":
    main()

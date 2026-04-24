#!/usr/bin/env python3
"""
RemoteX MCP Server — config-only, JSON-RPC 2.0 stdio transport.

Exposes 16 tools for reading and writing the RemoteX button/machine/profile config:
  list_buttons, get_button, create_button, update_button, delete_button,
  list_categories,
  list_machines, create_machine, update_machine, delete_machine,
  list_profiles, get_profile, create_profile, update_profile, delete_profile,
  help

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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.config import ConfigManager
from models.command_button import CommandButton
from models.machine import Machine
from models.execution_profile import ExecutionProfile

_config = ConfigManager()
_MCP_ENABLED_FLAG = Path.home() / '.config' / 'remotex' / '.mcp_enabled'


def _is_mcp_enabled() -> bool:
    return _MCP_ENABLED_FLAG.exists()


# ── Tool definitions ─────────────────────────────────────────────────────────

TOOLS = [
    # ── Buttons ──────────────────────────────────────────────────────────────
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
                "machine_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Machine UUIDs to run on. Empty list = local. Use list_machines to get UUIDs.",
                },
                "profile_id":         {"type": "string",  "description": "Execution profile UUID (optional). Use list_profiles to get UUIDs."},
                "execution_mode":     {"type": "string",  "description": "Output mode: 'silent' (toast only), 'output' (show dialog), 'terminal' (open terminal). Default: 'silent'."},
                "run_as":             {"type": "string",  "description": "Privilege escalation: 'current' (no sudo, default), 'root' (sudo), or a username string (sudo -u username)."},
                "sudo_password":      {"type": "string",  "description": "Sudo password stored encoded locally. Required for silent/output modes without NOPASSWD. Leave empty for terminal mode (interactive prompt)."},
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
                "machine_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Machine UUIDs to run on. Empty list = local only. Use list_machines to get UUIDs.",
                },
                "profile_id":         {"type": "string",  "description": "Execution profile UUID. Use empty string to remove profile link."},
                "execution_mode":     {"type": "string",  "description": "Output mode: 'silent', 'output', or 'terminal'."},
                "run_as":             {"type": "string",  "description": "Privilege escalation: 'current', 'root', or a username string."},
                "sudo_password":      {"type": "string",  "description": "Sudo password stored encoded locally."},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "delete_button",
        "description": "Delete a RemoteX button by ID. Default buttons (seeded by RemoteX) can also be deleted.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Button UUID to delete"},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    # ── Categories ────────────────────────────────────────────────────────────
    {
        "name": "list_categories",
        "description": "List all category names used by RemoteX buttons (sorted).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    # ── Machines ──────────────────────────────────────────────────────────────
    {
        "name": "list_machines",
        "description": "List configured SSH machines (id, name, host, user, port, icon_name, group). Private key paths are not returned.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "create_machine",
        "description": "Add a new SSH machine. SSH key must be configured separately in the RemoteX UI.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name":      {"type": "string",  "description": "Display name for this machine (e.g. 'Web Server')"},
                "host":      {"type": "string",  "description": "Hostname or IP address"},
                "user":      {"type": "string",  "description": "SSH username"},
                "port":      {"type": "integer", "description": "SSH port (default: 22)"},
                "icon_name": {"type": "string",  "description": "Icon: 'pc-display', 'laptop', 'server', 'router', 'hdd-rack', 'wifi'. Default: 'pc-display'"},
                "group":     {"type": "string",  "description": "Group name for organizing machines (optional)"},
            },
            "required": ["name", "host", "user"],
            "additionalProperties": False,
        },
    },
    {
        "name": "update_machine",
        "description": "Update an existing SSH machine. Only fields provided are changed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id":        {"type": "string",  "description": "Machine UUID to update (required)"},
                "name":      {"type": "string",  "description": "New display name"},
                "host":      {"type": "string",  "description": "New hostname or IP"},
                "user":      {"type": "string",  "description": "New SSH username"},
                "port":      {"type": "integer", "description": "New SSH port"},
                "icon_name": {"type": "string",  "description": "New icon name"},
                "group":     {"type": "string",  "description": "New group name"},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "delete_machine",
        "description": "Delete an SSH machine by ID. Buttons that target this machine will fall back to local execution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Machine UUID to delete"},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    # ── Execution Profiles ────────────────────────────────────────────────────
    {
        "name": "list_profiles",
        "description": "List all execution profiles (reusable run_as + working_dir settings).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "get_profile",
        "description": "Get a specific execution profile by ID or name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id":   {"type": "string", "description": "Profile UUID"},
                "name": {"type": "string", "description": "Profile name (case-insensitive, first match)"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "create_profile",
        "description": "Create a reusable execution profile (sudo user + working directory).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name":         {"type": "string", "description": "Profile name (e.g. 'Web Admin')"},
                "run_as_user":  {"type": "string", "description": "User to run as: '' = current user, 'root' = sudo, any other = sudo -u <user>"},
                "working_dir":  {"type": "string", "description": "Working directory for commands (e.g. '/var/www/html')"},
                "description":  {"type": "string", "description": "Optional description"},
                "sudo_password": {"type": "string", "description": "Sudo password stored encoded locally (optional)"},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "update_profile",
        "description": "Update an existing execution profile. Only fields provided are changed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id":           {"type": "string", "description": "Profile UUID to update (required)"},
                "name":         {"type": "string", "description": "New profile name"},
                "run_as_user":  {"type": "string", "description": "New run_as user"},
                "working_dir":  {"type": "string", "description": "New working directory"},
                "description":  {"type": "string", "description": "New description"},
                "sudo_password": {"type": "string", "description": "New sudo password (empty string to clear)"},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "delete_profile",
        "description": "Delete an execution profile by ID. Buttons linked to this profile keep their other settings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Profile UUID to delete"},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    # ── Help ──────────────────────────────────────────────────────────────────
    {
        "name": "help",
        "description": "Return usage instructions and recommended workflows for the RemoteX MCP server. Call this first if unsure how to proceed.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]

# ── Serialisation helpers ────────────────────────────────────────────────────

def _resolve_run_as(value: str) -> str:
    """Map MCP run_as value to run_as_user field: 'current'→'', 'root'→'root', else username."""
    if not value or value == "current":
        return ""
    return value


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
        "profile_id":         b.profile_id,
        "is_default":         b.is_default,
        "machine_ids":        b.machine_ids,
        "position":           b.position,
    }


def _machine_to_dict(m: Machine) -> dict:
    # identity_file intentionally omitted (path to private key — sensitive)
    return {
        "id":        m.id,
        "name":      m.name,
        "host":      m.host,
        "user":      m.user,
        "port":      m.port,
        "icon_name": m.icon_name,
        "group":     m.group,
    }


def _profile_to_dict(p: ExecutionProfile) -> dict:
    # sudo_password_encoded intentionally omitted
    return {
        "id":               p.id,
        "name":             p.name,
        "run_as_user":      p.run_as_user,
        "working_dir":      p.working_dir,
        "description":      p.description,
        "has_sudo_password": p.has_sudo_password,
    }


# ── Validators ───────────────────────────────────────────────────────────────

def _validate_machine_ids(ids: list) -> str | None:
    if not isinstance(ids, list):
        return "Error: machine_ids must be a list"
    known = {m.id for m in _config.load_machines()} | {""}
    bad = [mid for mid in ids if mid not in known]
    if bad:
        return f"Error: unknown machine IDs {bad} — call list_machines to get valid UUIDs"
    return None


def _validate_profile_id(pid: str) -> str | None:
    if not pid:
        return None
    known = {p.id for p in _config.load_profiles()}
    if pid not in known:
        return f"Error: unknown profile ID '{pid}' — call list_profiles to get valid UUIDs"
    return None


# ── Button handlers ──────────────────────────────────────────────────────────

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


def handle_create_button(args: dict) -> str:
    name    = args.get("name", "").strip()
    command = args.get("command", "").strip()
    if not name or not command:
        return "Error: 'name' and 'command' are required"
    machine_ids = args.get("machine_ids", [])
    err = _validate_machine_ids(machine_ids)
    if err:
        return err
    profile_id = args.get("profile_id", "")
    err = _validate_profile_id(profile_id)
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
        run_as_user=        _resolve_run_as(args.get("run_as", "current")),
        profile_id=         profile_id,
        machine_ids=        machine_ids,
    )
    if args.get("sudo_password"):
        btn.set_sudo_password(args["sudo_password"])
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
                  "text_color", "execution_mode", "profile_id"):
        if field in args:
            setattr(btn, field, args[field])
    if "profile_id" in args:
        err = _validate_profile_id(args["profile_id"])
        if err:
            return err
    if "run_as" in args:
        btn.run_as_user = _resolve_run_as(args["run_as"])
    if "sudo_password" in args:
        btn.set_sudo_password(args["sudo_password"])
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


def handle_delete_button(args: dict) -> str:
    bid = args.get("id", "")
    if not bid:
        return "Error: 'id' is required"
    buttons = _config.load_buttons()
    btn = next((b for b in buttons if b.id == bid), None)
    if btn is None:
        return f"Error: button not found: {bid}"
    _config.delete_button(bid)
    return json.dumps({"deleted": bid, "name": btn.name}, ensure_ascii=False)


# ── Category handlers ────────────────────────────────────────────────────────

def handle_list_categories(args: dict) -> str:
    buttons = _config.load_buttons()
    cats = sorted({b.category for b in buttons if b.category})
    return json.dumps(cats, ensure_ascii=False)


# ── Machine handlers ─────────────────────────────────────────────────────────

def handle_list_machines(args: dict) -> str:
    machines = _config.load_machines()
    return json.dumps([_machine_to_dict(m) for m in machines], ensure_ascii=False, indent=2)


def handle_create_machine(args: dict) -> str:
    name = args.get("name", "").strip()
    host = args.get("host", "").strip()
    user = args.get("user", "").strip()
    if not name or not host or not user:
        return "Error: 'name', 'host', and 'user' are required"
    m = Machine(
        name=name,
        host=host,
        user=user,
        port=int(args.get("port", 22)),
        icon_name=args.get("icon_name", "pc-display"),
        group=args.get("group", ""),
    )
    _config.add_machine(m)
    return json.dumps({"created": _machine_to_dict(m)}, ensure_ascii=False, indent=2)


def handle_update_machine(args: dict) -> str:
    mid = args.get("id", "")
    if not mid:
        return "Error: 'id' is required"
    machines = _config.load_machines()
    m = next((m for m in machines if m.id == mid), None)
    if m is None:
        return f"Error: machine not found: {mid}"
    for field in ("name", "host", "user", "icon_name", "group"):
        if field in args:
            setattr(m, field, args[field])
    if "port" in args:
        m.port = int(args["port"])
    _config.update_machine(m)
    return json.dumps({"updated": _machine_to_dict(m)}, ensure_ascii=False, indent=2)


def handle_delete_machine(args: dict) -> str:
    mid = args.get("id", "")
    if not mid:
        return "Error: 'id' is required"
    machines = _config.load_machines()
    m = next((m for m in machines if m.id == mid), None)
    if m is None:
        return f"Error: machine not found: {mid}"
    _config.delete_machine(mid)
    return json.dumps({"deleted": mid, "name": m.name}, ensure_ascii=False)


# ── Profile handlers ─────────────────────────────────────────────────────────

def handle_list_profiles(args: dict) -> str:
    profiles = _config.load_profiles()
    return json.dumps([_profile_to_dict(p) for p in profiles], ensure_ascii=False, indent=2)


def handle_get_profile(args: dict) -> str:
    pid  = args.get("id", "")
    name = args.get("name", "")
    if not pid and not name:
        return "Error: provide 'id' or 'name'"
    profiles = _config.load_profiles()
    if pid:
        p = next((p for p in profiles if p.id == pid), None)
    else:
        p = next((p for p in profiles if p.name.lower() == name.lower()), None)
    if p is None:
        return "Error: profile not found"
    return json.dumps(_profile_to_dict(p), ensure_ascii=False, indent=2)


def handle_create_profile(args: dict) -> str:
    name = args.get("name", "").strip()
    if not name:
        return "Error: 'name' is required"
    p = ExecutionProfile(
        name=name,
        run_as_user=args.get("run_as_user", ""),
        working_dir=args.get("working_dir", ""),
        description=args.get("description", ""),
    )
    if args.get("sudo_password"):
        p.set_sudo_password(args["sudo_password"])
    _config.add_profile(p)
    return json.dumps({"created": _profile_to_dict(p)}, ensure_ascii=False, indent=2)


def handle_update_profile(args: dict) -> str:
    pid = args.get("id", "")
    if not pid:
        return "Error: 'id' is required"
    profiles = _config.load_profiles()
    p = next((p for p in profiles if p.id == pid), None)
    if p is None:
        return f"Error: profile not found: {pid}"
    for field in ("name", "run_as_user", "working_dir", "description"):
        if field in args:
            setattr(p, field, args[field])
    if "sudo_password" in args:
        p.set_sudo_password(args["sudo_password"])
    _config.update_profile(p)
    return json.dumps({"updated": _profile_to_dict(p)}, ensure_ascii=False, indent=2)


def handle_delete_profile(args: dict) -> str:
    pid = args.get("id", "")
    if not pid:
        return "Error: 'id' is required"
    profiles = _config.load_profiles()
    p = next((p for p in profiles if p.id == pid), None)
    if p is None:
        return f"Error: profile not found: {pid}"
    _config.delete_profile(pid)
    return json.dumps({"deleted": pid, "name": p.name}, ensure_ascii=False)


# ── Help ─────────────────────────────────────────────────────────────────────

_HELP_TEXT = """\
RemoteX MCP — available tools and recommended workflows
========================================================

TOOLS
-----
Buttons:
  help              — Show this guide (no arguments)
  list_buttons      — List all buttons, optionally filtered by category
  get_button        — Get one button by id or name
  create_button     — Create a new button (name + command required)
  update_button     — Patch an existing button by id (only provided fields are changed)
  delete_button     — Delete a button by id
  list_categories   — List all existing category names

Machines (SSH targets):
  list_machines     — List SSH machines (id, name, host, user, port, icon_name, group)
  create_machine    — Add a new SSH machine (name, host, user required)
  update_machine    — Patch a machine by id
  delete_machine    — Delete a machine by id

Execution profiles (reusable run_as + working_dir):
  list_profiles     — List all profiles
  get_profile       — Get one profile by id or name
  create_profile    — Create a profile (name required)
  update_profile    — Patch a profile by id
  delete_profile    — Delete a profile by id

WORKFLOWS
---------
1. Before using machine_ids in create_button or update_button:
   → call list_machines first to get valid UUIDs.
   → machine_ids=[]              means local execution only.
   → machine_ids=["<uuid>"]      means run on that remote machine.
   → machine_ids=["", "<uuid>"]  means ask user to pick (local or remote) at run time.

2. Choosing between get_button and list_buttons:
   → user names the button explicitly ("the button called X", "my X button"):
     use get_button(name="X") directly — it is exact and efficient.
   → you don't know the exact name, or need to search by purpose:
     use list_buttons and scan the results.
   → do NOT call get_button before create_button — it is only for read/update/delete.

3. To avoid duplicate items, always check before creating:
   → categories:  call list_categories first, reuse an existing name if it fits.
   → profiles:    call list_profiles first to check if an equivalent profile exists.
   → machines:    call list_machines first to check if the host is already configured.
   → buttons:     call list_buttons first to check if a button with the same purpose exists.
   Duplicate detection rules (different per type):
   → BUTTONS:  a button is a duplicate only if another button has the EXACT SAME NAME.
               Two buttons may share the same shell command — that is not a duplicate.
               If no button has the same name: create it, even if a similar command exists.
               If the exact name already exists: inform the user and ask.
   → MACHINES: a machine is a duplicate if another machine has the SAME HOST address.
               Name does not matter — check by host (e.g. 192.168.1.50).
   → PROFILES: a profile is a duplicate if another has the same name.
   → CATEGORIES: a category is a duplicate if the same name exists.
   → do NOT silently refuse to create if no true duplicate is found.

4. Explicit updates must always be applied:
   → when the user asks to change a property (color, name, category, etc.),
     apply the change even if the current value looks similar to what was requested.
   → do NOT skip an update because you think the current state is "already correct".

5. Multi-step requests (e.g. "create a profile then create a button using it"):
   → if a required resource (profile, machine) already exists, use it and proceed.
   → do NOT stop to ask about the existing resource unless the user's intent is ambiguous.

5. To link a button to an execution profile:
   → call list_profiles to get the profile UUID.
   → pass profile_id="<uuid>" in create_button or update_button.
   → a profile sets run_as_user and working_dir for all buttons that use it.
   → profile_id can be combined with run_as to add sudo on top of the profile's user.

6. SSH key for a new machine must be configured in the RemoteX UI — create_machine
   stores name/host/user/port only (no private key path accepted via MCP).

7. Execution modes for create_button / update_button:
   → "silent"   — run silently, show a toast notification only.
   → "output"   — open an output dialog showing stdout/stderr.
   → "terminal" — open a terminal window (requires a terminal emulator installed).
   Default is "silent".

8. Privilege escalation (sudo) for create_button / update_button:
   → run_as="current"   — no sudo, run as the logged-in user (default).
   → run_as="root"      — run as root via sudo.
   → run_as="www-data"  — run as a specific user via sudo -u (any username works).
   Provide sudo_password when run_as is not "current", unless NOPASSWD is configured
   or execution_mode is "terminal" (interactive prompt).
   run_as can be combined with profile_id: the profile sets working_dir, run_as sets user.

   DECOMPOSITION RULE — strip context before storing a command:
   → "cd /some/path && cmd"     → command="cmd", use a profile with working_dir="/some/path"
   → "sudo apt update"          → command="apt update", run_as="root"
   → "sudo -u www-data php art" → command="php artisan …", run_as="www-data"
   → "sudo bash" or "sudo -i"   → command="bash", run_as="root", execution_mode="terminal"

NOTES
-----
- Private key paths are never returned by list_machines (security).
- sudo_password_encoded is never returned by any tool (security).
- The MCP server must be enabled in RemoteX → Preferences → Desktop Integration.
"""


def handle_help(args: dict) -> str:
    return _HELP_TEXT


# ── Dispatch table ────────────────────────────────────────────────────────────

HANDLERS = {
    "list_buttons":    handle_list_buttons,
    "get_button":      handle_get_button,
    "create_button":   handle_create_button,
    "update_button":   handle_update_button,
    "delete_button":   handle_delete_button,
    "list_categories": handle_list_categories,
    "list_machines":   handle_list_machines,
    "create_machine":  handle_create_machine,
    "update_machine":  handle_update_machine,
    "delete_machine":  handle_delete_machine,
    "list_profiles":   handle_list_profiles,
    "get_profile":     handle_get_profile,
    "create_profile":  handle_create_profile,
    "update_profile":  handle_update_profile,
    "delete_profile":  handle_delete_profile,
    "help":            handle_help,
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

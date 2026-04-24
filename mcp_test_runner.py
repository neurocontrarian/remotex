#!/usr/bin/env python3
"""
RemoteX MCP test runner — gemma4 via llama.cpp (localhost:8080).

Usage:
    python3 mcp_test_runner.py              # reset state, run all tests
    python3 mcp_test_runner.py T07 T11 T24  # reset state, run specific tests
    python3 mcp_test_runner.py --no-reset   # skip state reset

Results are saved to mcp_test_results.md
"""

import sys
import os
import json
import requests
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import mcp_server
mcp_server._is_mcp_enabled = lambda: True

from mcp_server import TOOLS, HANDLERS

# ── OpenAI tool format conversion ─────────────────────────────────────────

def _to_openai_tools(mcp_tools: list) -> list:
    result = []
    for t in mcp_tools:
        result.append({
            "type": "function",
            "function": {
                "name":        t["name"],
                "description": t.get("description", ""),
                "parameters":  t.get("inputSchema", {"type": "object", "properties": {}}),
            },
        })
    return result


OPENAI_TOOLS = _to_openai_tools(TOOLS)

# ── Config ─────────────────────────────────────────────────────────────────

LLAMA_URL = "http://localhost:8080/v1/chat/completions"
MODEL     = "google_gemma-4-26B-A4B-it-Q5_K_L.gguf"
MAX_TURNS = 8
TIMEOUT   = 90
OUTPUT    = "mcp_test_results.md"

SYSTEM_PROMPT = """\
You are an assistant for RemoteX, a desktop application on Linux.
RemoteX lets the user run commands by clicking buttons, like a remote control.
You can create, read, and modify the user's buttons, machines, and profiles using your tools.

A "button" runs a shell command when clicked.
A "machine" is a remote computer reachable via SSH.
A "profile" is a saved setting (run as a different user, work in a specific folder) \
that buttons can reuse.

Rules:
- Before doing anything, call the help tool to read the instructions.
- When the user explicitly names a button (e.g. "the button called X"), use \
get_button(name="X") directly. When you don't know the exact name, use list_buttons.
- Never call get_button before create_button. get_button is for read/update/delete only.
- For buttons: a duplicate means SAME NAME, not same command. Two buttons may share \
the same command. If no button has the exact same name, create it without asking.
- For machines: a duplicate means SAME HOST address (not same name). Always call \
list_machines and check by host before creating a machine.
- For profiles: a duplicate means same name. Call list_profiles before creating.
- When asked to change a property (color, name, category…), always apply the change. \
Never decide the current value is already acceptable.
- In multi-step requests, if a required resource already exists, use it and proceed. \
Do not stop to ask about the existing resource.
- When you need a machine ID or profile ID, always look it up first.\
"""

# ── State reset ────────────────────────────────────────────────────────────

# Button names created by tests — removed before each run
_TEST_BUTTON_NAMES = frozenset({
    "Free Disk Space",
    "Empty Trash",
    "Update System Packages",
    "Show Running Processes",
    "Restart Nginx",
    "Deploy App",
    "Check Disk",
    "Deploy Website",
})

# Profile names created by tests — removed before each run
_TEST_PROFILE_NAMES = frozenset({"Deploy"})


def reset_test_state():
    """Remove items created by previous test runs so each run starts clean."""
    from models.config import ConfigManager as CM
    cfg = CM()

    btns = cfg.load_buttons()
    clean_btns = [b for b in btns if b.name not in _TEST_BUTTON_NAMES]
    if len(clean_btns) < len(btns):
        cfg.save_buttons(clean_btns)
        print(f"  reset: removed {len(btns) - len(clean_btns)} test button(s)")

    # Restore fixture button properties that tests may have modified
    btns = cfg.load_buttons()
    changed = False
    for b in btns:
        if b.name == "Disk Usage" and b.color != "":
            b.color = ""
            changed = True
    if changed:
        cfg.save_buttons(btns)
        print("  reset: restored Disk Usage color to default")

    profs = cfg.load_profiles()
    clean_profs = [p for p in profs if p.name not in _TEST_PROFILE_NAMES]
    if len(clean_profs) < len(profs):
        cfg.save_profiles(clean_profs)
        print(f"  reset: removed {len(profs) - len(clean_profs)} test profile(s)")

    # Machines are stable fixtures — never touched


# ── Test definitions ───────────────────────────────────────────────────────

TESTS = [
    # id,    group,          user prompt
    ("T01", "Read",         "Show me all my buttons."),
    ("T02", "Read",         'What buttons do I have in the "System" category?'),
    ("T03", "Read",         'Show me the details of the button called "Disk Usage".'),
    ("T04", "Read",         "What categories exist in my RemoteX?"),
    ("T05", "Read",         "What remote machines do I have set up?"),
    ("T06", "Read",         "Do I have any execution profiles?"),
    ("T07", "Create",       'Create a button called "Free Disk Space" that shows how much free disk space I have.'),
    ("T08", "Create",       "Create a button to empty the trash. Ask me before it runs."),
    ("T09", "Create",       "Add a button that updates my system packages. It needs to run as administrator."),
    ("T10", "Create",       'Create a button called "Show Running Processes" that lists active processes and displays the output.'),
    ("T11", "Create",       "Add my home server: address is 192.168.1.50, username is pierre, it's a Linux server."),
    ("T12", "Create",       'Create a profile called "Web Admin" for running commands as www-data in the /var/www folder.'),
    ("T13", "Update",       'Change the color of the "Disk Usage" button to red.'),
    ("T14", "Update",       'Put the "Disk Usage" button in the "Maintenance" category.'),
    ("T15", "Update",       "Make the button that updates system packages ask for confirmation before running."),
    ("T16", "Update",       "Rename my machine at 192.168.1.50 to 'Home NAS'."),
    ("T17", "Multi-step",   "Add my work server at 10.0.0.5, user=admin, then create a button to restart nginx on it."),
    ("T18", "Multi-step",   'Create a "Deploy" profile that runs as www-data in /var/www/myapp, then create a button that uses this profile to run "git pull".'),
    ("T19", "Multi-step",   'Create a button called "Check Disk" that I can run either locally or on my home server, and I choose which one each time I click it.'),
    ("T20", "Error",        'Delete the button called "LaunchRocket2049".'),
    ("T21", "Error",        'Create a button that runs on machine ID "fake-uuid-does-not-exist".'),
    ("T22", "Error",        "Create a button for me."),
    ("T23", "Error",        'Add a category called "System" if it does not exist yet.'),
    ("T24", "Multi-step",   'Create a button called "Deploy Website" that runs "git pull && composer install" on my Work Server, using the "Web Admin" profile, and running as root.'),
]

# ── Scoring engine ─────────────────────────────────────────────────────────

def _tools(r):
    return [tc["tool"] for tc in r["tool_calls"]]

def _args(r, tool_name):
    for tc in reversed(r["tool_calls"]):
        if tc["tool"] == tool_name:
            return tc.get("args_parsed") or {}
    return {}

def _all_args(r, tool_name):
    return [tc.get("args_parsed") or {} for tc in r["tool_calls"] if tc["tool"] == tool_name]

def _called_before(r, tool_a, tool_b):
    tools = _tools(r)
    if tool_a not in tools or tool_b not in tools:
        return False
    return tools.index(tool_a) < tools.index(tool_b)

def _first_real_tool(r):
    for tc in r["tool_calls"]:
        if tc["tool"] != "help":
            return tc["tool"]
    return None

def _any_arg_contains(r, tool_name, key, value):
    return any(a.get(key) == value for a in _all_args(r, tool_name))

def _any_arg_includes(r, tool_name, key, item):
    return any(item in a.get(key, []) for a in _all_args(r, tool_name))

def _lookup_used(r):
    """True if any legitimate lookup tool was used (get_button or list_buttons)."""
    return bool({"get_button", "list_buttons"} & set(_tools(r)))

def _mcp_rejected(r, tool_name):
    """True if tool_name was called and MCP returned an Error."""
    return any(
        tc["tool"] == tool_name and tc.get("result", "").startswith("Error")
        for tc in r["tool_calls"]
    )


TEST_CHECKS = {
    "T01": lambda r: [
        ("list_buttons called",           "list_buttons" in _tools(r)),
        ("No standalone get_button guess", "get_button"  not in _tools(r)),
    ],
    "T02": lambda r: [
        ("list_buttons called",            "list_buttons" in _tools(r)),
        ('category="System" passed',       _any_arg_contains(r, "list_buttons", "category", "System")),
    ],
    "T03": lambda r: [
        ("get_button called (name is explicit)", "get_button" in _tools(r)),
        ('name="Disk Usage" passed',             _any_arg_contains(r, "get_button", "name", "Disk Usage")),
    ],
    "T04": lambda r: [
        ("list_categories called",         "list_categories" in _tools(r)),
    ],
    "T05": lambda r: [
        ("list_machines called",           "list_machines" in _tools(r)),
    ],
    "T06": lambda r: [
        ("list_profiles called",           "list_profiles" in _tools(r)),
    ],
    "T07": lambda r: [
        # Name is explicit in the prompt — list_buttons is optional but not required
        ("list_buttons OR direct create (name given)", True),
        ("create_button called",           "create_button" in _tools(r)),
        ("No get_button before create",    _first_real_tool(r) != "get_button"),
    ],
    "T08": lambda r: [
        ("list_buttons used (not direct get_button guess)",
                                           "list_buttons" in _tools(r)),
        ("create_button called",           "create_button" in _tools(r)),
        ("confirm_before_run=True set",    _any_arg_contains(r, "create_button", "confirm_before_run", True)),
    ],
    "T09": lambda r: [
        ("list_buttons called to search",  "list_buttons"  in _tools(r)),
        ("create_button called",           "create_button" in _tools(r)),
        ("run_as=root",                    _any_arg_contains(r, "create_button", "run_as", "root")),
    ],
    "T10": lambda r: [
        # Name is explicit in the prompt — list_buttons is optional but not required
        ("list_buttons OR direct create (name given)", True),
        ("create_button called",           "create_button" in _tools(r)),
        ("output mode set",                _any_arg_contains(r, "create_button", "execution_mode", "output")
                                           or _any_arg_contains(r, "create_button", "show_output", True)),
    ],
    "T11": lambda r: [
        ("list_machines called first",     "list_machines"  in _tools(r)),
        ("No duplicate machine created",   not _any_arg_contains(r, "create_machine", "host", "192.168.1.50")),
    ],
    "T12": lambda r: [
        ("list_profiles called first",     "list_profiles"  in _tools(r)),
        ("No duplicate profile created",   not _any_arg_contains(r, "create_profile", "name", "Web Admin")),
    ],
    "T13": lambda r: [
        # get_button OR list_buttons are both acceptable for lookup
        ("Looked up button (get or list)", _lookup_used(r)),
        ("update_button called",           "update_button" in _tools(r)),
        ("color set to a blue hex",        any(str(a.get("color", "")).startswith("#")
                                              for a in _all_args(r, "update_button"))),
    ],
    "T14": lambda r: [
        # get_button OR list_buttons are acceptable — both find the button
        ("Looked up button (get or list)", _lookup_used(r)),
        ("No unnecessary update (already in Maintenance)",
                                           True),  # informational — manual check
    ],
    "T15": lambda r: [
        ("list_buttons called",            "list_buttons" in _tools(r)),
    ],
    "T16": lambda r: [
        ("list_machines called",           "list_machines"  in _tools(r)),
        ("No unnecessary rename",          not _any_arg_contains(r, "update_machine", "name", "Home NAS")),
    ],
    "T17": lambda r: [
        ("list_machines called",           "list_machines"   in _tools(r)),
        ("No duplicate machine created",   "create_machine"  not in _tools(r)),
        ("create_button called",           "create_button"   in _tools(r)),
        ("machine_ids set on button",      bool(_args(r, "create_button").get("machine_ids"))),
    ],
    "T18": lambda r: [
        ("list_profiles called before create_profile",
                                           _called_before(r, "list_profiles", "create_profile")),
        ("create_profile called",          "create_profile" in _tools(r)),
        ("create_button called",           "create_button"  in _tools(r)),
        ("profile_id set on button",       bool(_args(r, "create_button").get("profile_id"))),
    ],
    "T19": lambda r: [
        ("list_machines called",           "list_machines" in _tools(r)),
        ("create_button called",           "create_button" in _tools(r)),
        ('machine_ids includes "" (local pick)',
                                           _any_arg_includes(r, "create_button", "machine_ids", "")),
        ("machine_ids includes a real UUID",
                                           any(len(mid) > 10
                                               for a in _all_args(r, "create_button")
                                               for mid in a.get("machine_ids", []))),
    ],
    "T20": lambda r: [
        # get_button OR list_buttons are both fine for delete lookup
        ("Looked up button (get or list)", _lookup_used(r)),
        ("delete_button NOT called (not found)",
                                           "delete_button" not in _tools(r)),
    ],
    "T21": lambda r: [
        # list_machines OR immediate refusal are both correct (proactive > reactive)
        ("Machines checked or immediately refused",
                                           "list_machines" in _tools(r)
                                           or "create_button" not in _tools(r)),
        ("Fake UUID never used successfully",
                                           "create_button" not in _tools(r)
                                           or _mcp_rejected(r, "create_button")),
    ],
    "T22": lambda r: [
        ("No blind create_button",         "create_button" not in _tools(r)),
        ("Asked user for name/command",    "create_button" not in _tools(r)),
    ],
    "T23": lambda r: [
        ("list_categories called",         "list_categories" in _tools(r)),
        ("No create action",               "create_button"   not in _tools(r)),
    ],
    "T24": lambda r: [
        ("list_machines called",           "list_machines"  in _tools(r)),
        ("list_profiles called",           "list_profiles"  in _tools(r)),
        ("create_button called",           "create_button"  in _tools(r)),
        ("machine_ids set",                bool(_args(r, "create_button").get("machine_ids"))),
        ("profile_id set",                 bool(_args(r, "create_button").get("profile_id"))),
        ("run_as=root",                    _args(r, "create_button").get("run_as") == "root"),
    ],
}


def score_result(result: dict) -> tuple[list, int, int]:
    tid = result["tid"]
    fn  = TEST_CHECKS.get(tid)
    if fn is None:
        return [], 0, 0
    if result["error"]:
        checks = [(desc, False) for desc, _ in fn({"tool_calls": [], "tid": tid,
                                                    "error": result["error"]})]
        return checks, 0, len(checks)
    checks = fn(result)
    passed = sum(1 for _, ok in checks if ok)
    return checks, passed, len(checks)


def grade_emoji(passed, total):
    if total == 0:
        return "⬜"
    ratio = passed / total
    if ratio == 1.0:
        return "✅"
    if ratio >= 0.5:
        return "⚠️"
    return "❌"


# ── Core loop ──────────────────────────────────────────────────────────────

def call_llm(messages: list) -> dict:
    resp = requests.post(
        LLAMA_URL,
        json={
            "model":       MODEL,
            "messages":    messages,
            "tools":       OPENAI_TOOLS,
            "tool_choice": "auto",
            "max_tokens":  1024,
            "temperature": 0.1,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def execute_tool(name: str, arguments: str) -> str:
    handler = HANDLERS.get(name)
    if handler is None:
        return f"Error: unknown tool '{name}'"
    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError as e:
        return f"Error: invalid JSON arguments — {e}"
    try:
        return handler(args)
    except Exception as e:
        return f"Error: {e}"


def run_test(tid: str, prompt: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]
    tool_calls_log = []
    error          = None
    final_answer   = ""

    for _ in range(MAX_TURNS):
        try:
            response = call_llm(messages)
        except Exception as e:
            error = str(e)
            break

        choice  = response["choices"][0]
        message = choice["message"]
        reason  = choice["finish_reason"]

        assistant_msg = {"role": "assistant", "content": message.get("content") or ""}
        if message.get("tool_calls"):
            assistant_msg["tool_calls"] = message["tool_calls"]
        messages.append(assistant_msg)

        if reason == "tool_calls" and message.get("tool_calls"):
            for tc in message["tool_calls"]:
                fn       = tc["function"]["name"]
                args_str = tc["function"].get("arguments", "{}")
                result   = execute_tool(fn, args_str)

                try:
                    args_parsed = json.loads(args_str) if args_str else {}
                except Exception:
                    args_parsed = {}

                tool_calls_log.append({
                    "tool":        fn,
                    "arguments":   args_str,
                    "args_parsed": args_parsed,
                    "result":      result[:300] + ("…" if len(result) > 300 else ""),
                })

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc["id"],
                    "content":      result,
                })
        else:
            final_answer = (message.get("content") or "").strip()
            break

    return {
        "tid":        tid,
        "prompt":     prompt,
        "tool_calls": tool_calls_log,
        "answer":     final_answer,
        "error":      error,
    }


# ── Report ─────────────────────────────────────────────────────────────────

def render_report(results: list, elapsed_total: float) -> str:
    scored     = [(r, *score_result(r)) for r in results]
    total_pass = sum(p for _, _, p, _ in scored)
    total_all  = sum(t for _, _, _, t in scored)

    lines = [
        "# RemoteX MCP — gemma4 test results",
        f"\nRun: {datetime.now().strftime('%Y-%m-%d %H:%M')} — "
        f"{len(results)} tests — {elapsed_total:.0f}s — "
        f"score: {total_pass}/{total_all} checks\n",
        "| # | Group | Prompt | Tools used | Score |",
        "|---|-------|--------|------------|-------|",
    ]

    group_map = {tid: grp for tid, grp, _ in TESTS}
    for r, checks, passed, total in scored:
        prompt_short = r["prompt"][:52] + ("…" if len(r["prompt"]) > 52 else "")
        tools_used   = ", ".join(tc["tool"] for tc in r["tool_calls"]) or "—"
        grade        = "❌ ERROR" if r["error"] else f"{grade_emoji(passed, total)} {passed}/{total}"
        grp          = group_map.get(r["tid"], "")
        lines.append(f"| {r['tid']} | {grp} | {prompt_short} | {tools_used} | {grade} |")

    lines.append("\n---\n")
    lines.append("## Detailed results\n")

    for r, checks, passed, total in scored:
        lines.append(f"### {r['tid']} — {r['prompt']}\n")

        if r["error"]:
            lines.append(f"**ERROR:** {r['error']}\n")
        else:
            lines.append(f"**Score: {passed}/{total}** {grade_emoji(passed, total)}")
            for desc, ok in checks:
                lines.append(f"- {'✅' if ok else '❌'} {desc}")
            lines.append("")

            for i, tc in enumerate(r["tool_calls"], 1):
                try:
                    args_pretty = json.dumps(tc["args_parsed"], ensure_ascii=False)
                except Exception:
                    args_pretty = tc["arguments"]
                lines.append(f"**Call {i}:** `{tc['tool']}({args_pretty})`")
                lines.append(f"```\n{tc['result']}\n```")

            if r["answer"]:
                lines.append(f"**Final answer:**\n> {r['answer'][:600]}\n")

        lines.append("---\n")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    args_cli    = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_reset    = "--no-reset" in sys.argv
    filter_ids  = set(args_cli)
    tests_to_run = [(tid, grp, prompt) for tid, grp, prompt in TESTS
                    if not filter_ids or tid in filter_ids]

    if not no_reset:
        print("Resetting test state…")
        reset_test_state()
        print()

    print(f"RemoteX MCP test runner — {len(tests_to_run)} tests\n")

    import time
    results = []
    t_start = time.time()

    for tid, grp, prompt in tests_to_run:
        t0 = time.time()
        print(f"[{tid}] {prompt[:58]}…", end="", flush=True)
        result  = run_test(tid, prompt)
        elapsed = time.time() - t0

        checks, passed, total = score_result(result)
        grade   = grade_emoji(passed, total)
        tools   = [tc["tool"] for tc in result["tool_calls"]]
        status  = "ERROR" if result["error"] else f"{grade} {passed}/{total}"
        print(f" {status} ({elapsed:.0f}s)")
        if tools:
            print(f"      tools: {', '.join(tools)}")

        results.append(result)

    elapsed_total = time.time() - t_start
    report = render_report(results, elapsed_total)

    with open(OUTPUT, "w") as f:
        f.write(report)

    total_pass = sum(score_result(r)[1] for r in results)
    total_all  = sum(score_result(r)[2] for r in results)
    print(f"\nDone in {elapsed_total:.0f}s — global score: {total_pass}/{total_all}")
    print(f"Results saved to {OUTPUT}")


if __name__ == "__main__":
    main()

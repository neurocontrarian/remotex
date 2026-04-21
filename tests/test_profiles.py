import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.execution_profile import ExecutionProfile
from models.command_button import CommandButton
from models.config import ConfigManager


def make_config(tmp_dir):
    config = ConfigManager.__new__(ConfigManager)
    config.CONFIG_DIR = Path(tmp_dir)
    config.MACHINES_FILE = Path(tmp_dir) / 'machines.toml'
    config.BUTTONS_FILE = Path(tmp_dir) / 'buttons.toml'
    config.PROFILES_FILE = Path(tmp_dir) / 'profiles.toml'
    config._ensure_config_dir()
    return config


def test_add_load_profile():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        p = ExecutionProfile(name="As claude-ai", run_as_user="claude-ai",
                             working_dir="/home/projects", description="dev")
        config.add_profile(p)
        loaded = config.load_profiles()
        assert len(loaded) == 1
        assert loaded[0].name == "As claude-ai"
        assert loaded[0].run_as_user == "claude-ai"
        assert loaded[0].working_dir == "/home/projects"
        assert loaded[0].description == "dev"
        assert loaded[0].id == p.id


def test_update_profile():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        p = ExecutionProfile(name="Old Name", run_as_user="user1")
        config.add_profile(p)
        p.name = "New Name"
        config.update_profile(p)
        loaded = config.load_profiles()
        assert loaded[0].name == "New Name"


def test_delete_profile():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        p1 = ExecutionProfile(name="Keep")
        p2 = ExecutionProfile(name="Delete")
        config.add_profile(p1)
        config.add_profile(p2)
        config.delete_profile(p2.id)
        loaded = config.load_profiles()
        assert len(loaded) == 1
        assert loaded[0].name == "Keep"


def test_get_profile_by_id_missing():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        result = config.get_profile_by_id("nonexistent-uuid")
        assert result is None


def test_export_import_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        p = ExecutionProfile(name="Roundtrip", run_as_user="testuser",
                             working_dir="/tmp/test")
        config.add_profile(p)

        archive = Path(tmp) / "backup.rxprofiles"
        config.export_profiles_backup(archive)
        assert archive.exists()

        # Delete original file and reimport
        config.PROFILES_FILE.unlink()
        assert config.load_profiles() == []

        config.import_profiles_backup(archive)
        restored = config.load_profiles()
        assert len(restored) == 1
        assert restored[0].name == "Roundtrip"
        assert restored[0].run_as_user == "testuser"
        assert restored[0].working_dir == "/tmp/test"


def test_resolve_profile_with_profile_id():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        p = ExecutionProfile(name="Profile", run_as_user="alice",
                             working_dir="/srv/app")
        config.add_profile(p)

        from services.executor import CommandExecutor
        executor = CommandExecutor(config)

        button = CommandButton(name="btn", command="ls", profile_id=p.id,
                               run_as_user="ignored")
        run_as_user, working_dir = executor._resolve_profile(button)
        assert run_as_user == "alice"
        assert working_dir == "/srv/app"


def test_resolve_profile_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)

        from services.executor import CommandExecutor
        executor = CommandExecutor(config)

        button = CommandButton(name="btn", command="ls", profile_id="",
                               run_as_user="fallback-user")
        run_as_user, working_dir = executor._resolve_profile(button)
        assert run_as_user == "fallback-user"
        assert working_dir == ""


def test_run_local_with_working_dir():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)

        from services.executor import CommandExecutor
        executor = CommandExecutor(config)

        with patch.object(executor, '_get_timeout', return_value=30):
            result = executor._run_local("pwd", button_id="", run_as_user="",
                                         working_dir=tmp)
        assert result.success
        assert tmp in result.stdout


def test_run_local_with_run_as_user():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)

        from services.executor import CommandExecutor
        executor = CommandExecutor(config)

        captured = {}

        def mock_run(cmd, **kwargs):
            captured['cmd'] = cmd
            return MagicMock(returncode=0, stdout="ok", stderr="")

        with patch.object(executor, '_get_timeout', return_value=30):
            with patch('subprocess.run', side_effect=mock_run):
                executor._run_local("whoami", button_id="", run_as_user="bob",
                                    working_dir="")

        assert "sudo" in captured['cmd']
        assert "bob" in captured['cmd']


def test_build_ssh_command_with_working_dir():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)

        from services.executor import CommandExecutor
        from models.machine import Machine
        executor = CommandExecutor(config)

        machine = Machine(id="m1", name="srv", host="192.168.1.1",
                          user="deploy", port=22)
        cmd = executor._build_ssh_command(machine, "ls", run_as_user="alice",
                                          working_dir="/srv/app")

        # working_dir must be inside the sudo bash -c wrapper
        assert "/srv/app" in cmd
        assert "sudo" in cmd
        # sudo must come AFTER the host specification
        host_pos = cmd.index("192.168.1.1")
        sudo_pos = cmd.index("sudo")
        assert sudo_pos > host_pos

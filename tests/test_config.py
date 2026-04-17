import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.machine import Machine
from models.command_button import CommandButton
from models.config import ConfigManager


def make_config(tmp_dir):
    config = ConfigManager.__new__(ConfigManager)
    config.CONFIG_DIR = Path(tmp_dir)
    config.MACHINES_FILE = Path(tmp_dir) / 'machines.toml'
    config.BUTTONS_FILE = Path(tmp_dir) / 'buttons.toml'
    config._ensure_config_dir()
    return config


def test_load_machines_empty():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        assert config.load_machines() == []


def test_save_and_load_machines():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        machines = [
            Machine(name="Serveur Plex", host="192.168.1.100", user="admin"),
            Machine(name="Staging", host="staging.local", user="deploy", port=2222),
        ]
        config.save_machines(machines)
        loaded = config.load_machines()
        assert len(loaded) == 2
        assert loaded[0].name == "Serveur Plex"
        assert loaded[1].port == 2222


def test_add_and_delete_machine():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        m = Machine(name="Test", host="10.0.0.1", user="root")
        config.add_machine(m)
        assert len(config.load_machines()) == 1
        config.delete_machine(m.id)
        assert len(config.load_machines()) == 0


def test_update_machine():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        m = Machine(name="Old Name", host="10.0.0.1", user="root")
        config.add_machine(m)
        m.name = "New Name"
        config.update_machine(m)
        loaded = config.load_machines()
        assert loaded[0].name == "New Name"


def test_save_and_load_buttons():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        buttons = [
            CommandButton(name="ls", command="ls -la"),
            CommandButton(name="Restart", command="sudo systemctl restart nginx",
                         confirm_before_run=True),
        ]
        config.save_buttons(buttons)
        loaded = config.load_buttons()
        assert len(loaded) == 2
        assert loaded[0].name == "ls"
        assert loaded[1].confirm_before_run is True


def test_buttons_sorted_by_position():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        b1 = CommandButton(name="B", command="b", position=1)
        b2 = CommandButton(name="A", command="a", position=0)
        config.save_buttons([b1, b2])
        loaded = config.load_buttons()
        assert loaded[0].name == "A"
        assert loaded[1].name == "B"


def test_atomic_write_creates_backup():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        m = Machine(name="Test", host="1.1.1.1", user="u")
        config.save_machines([m])
        config.save_machines([m])  # second save creates .bak
        assert (Path(tmp) / 'machines.toml.bak').exists()


def test_add_button_auto_position():
    with tempfile.TemporaryDirectory() as tmp:
        config = make_config(tmp)
        config.add_button(CommandButton(name="A", command="a"))
        config.add_button(CommandButton(name="B", command="b"))
        config.add_button(CommandButton(name="C", command="c"))
        loaded = config.load_buttons()
        abc = sorted([b for b in loaded if b.name in ("A", "B", "C")], key=lambda b: b.position)
        assert len(abc) == 3
        assert [b.name for b in abc] == ["A", "B", "C"]
        assert abc[0].position < abc[1].position < abc[2].position

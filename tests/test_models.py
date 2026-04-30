import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pro.models.machine import Machine
from models.command_button import CommandButton


def test_machine_to_dict_roundtrip():
    m = Machine(name="Serveur Plex", host="192.168.1.100", user="admin", port=2222)
    d = m.to_dict()
    m2 = Machine.from_dict(d)
    assert m2.id == m.id
    assert m2.name == m.name
    assert m2.host == m.host
    assert m2.user == m.user
    assert m2.port == 2222
    assert m2.identity_file == ""


def test_machine_defaults():
    m = Machine(name="Test", host="10.0.0.1", user="root")
    assert m.port == 22
    assert m.identity_file == ""
    assert len(m.id) == 36  # UUID format


def test_machine_unique_ids():
    m1 = Machine(name="A", host="1.1.1.1", user="u")
    m2 = Machine(name="B", host="2.2.2.2", user="u")
    assert m1.id != m2.id


def test_command_button_to_dict_roundtrip():
    b = CommandButton(
        name="Restart Nginx",
        command="sudo systemctl restart nginx",
        machine_ids=["some-uuid"],
        color="#e5a50a",
        confirm_before_run=True,
        show_output=False,
        position=3,
    )
    d = b.to_dict()
    b2 = CommandButton.from_dict(d)
    assert b2.id == b.id
    assert b2.name == b.name
    assert b2.command == b.command
    assert b2.machine_ids == ["some-uuid"]
    assert b2.color == "#e5a50a"
    assert b2.confirm_before_run is True
    assert b2.show_output is False
    assert b2.position == 3


def test_command_button_defaults():
    b = CommandButton(name="ls", command="ls -la")
    assert b.machine_ids == []
    assert b.icon_name == "utilities-terminal-symbolic"
    assert b.color == ""
    assert b.confirm_before_run is False
    assert b.show_output is False
    assert b.position == 0


def test_command_button_backward_compat_machine_id():
    """Old TOML format uses machine_id (str), new format uses machine_ids (list)."""
    old_data = {
        'id': 'btn-1',
        'name': 'Test',
        'command': 'ls',
        'machine_id': 'legacy-uuid',
    }
    b = CommandButton.from_dict(old_data)
    assert b.machine_ids == ['legacy-uuid']


def test_command_button_backward_compat_local():
    """Old local button (machine_id='') becomes machine_ids=[]."""
    old_data = {
        'id': 'btn-2',
        'name': 'Local',
        'command': 'pwd',
        'machine_id': '',
    }
    b = CommandButton.from_dict(old_data)
    assert b.machine_ids == []


def test_command_button_multi_machine():
    """Multi-machine button serializes and deserializes correctly."""
    b = CommandButton(
        name="Deploy",
        command="./deploy.sh",
        machine_ids=["", "uuid-server1", "uuid-server2"],
    )
    d = b.to_dict()
    b2 = CommandButton.from_dict(d)
    assert b2.machine_ids == ["", "uuid-server1", "uuid-server2"]

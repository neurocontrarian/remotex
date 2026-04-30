from dataclasses import dataclass, field
import uuid


@dataclass
class CommandButton:
    name: str
    command: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    machine_ids: list[str] = field(default_factory=list)  # Empty list = local execution
    icon_name: str = "utilities-terminal-symbolic"
    color: str = ""                                    # Hex color or empty for theme default
    confirm_before_run: bool = False
    show_output: bool = False
    position: int = 0                                  # Order in the button grid
    category: str = ""                                 # Category name, empty = uncategorized
    tooltip: str = ""                                  # Custom hover tooltip, empty = show command
    hide_label: bool = False                           # Icon-only mode
    hide_icon: bool = False                            # Text-only mode
    text_color: str = ""                               # Hex color for label text, empty = theme default
    is_default: bool = False                           # True = seeded button, not editable in free tier
    mcp_executable: bool = False                       # True = AI may trigger this button via MCP
    execution_mode: str = ""                           # "": legacy (use show_output); "silent"; "output"; "terminal"
    run_as_user: str = ""                              # sudo -u USER; "root" = sudo without -u; "" = current user
    profile_id: str = ""                               # UUID of ExecutionProfile, "" = none
    sudo_password_encoded: str = ""                    # machine-id XOR encoded sudo password

    def get_sudo_password(self) -> str:
        if not self.sudo_password_encoded:
            return ""
        from services.password_store import decode
        return decode(self.sudo_password_encoded)

    def set_sudo_password(self, password: str) -> None:
        if password:
            from services.password_store import encode
            self.sudo_password_encoded = encode(password)
        else:
            self.sudo_password_encoded = ""

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'command': self.command,
            'machine_ids': self.machine_ids,
            'icon_name': self.icon_name,
            'color': self.color,
            'confirm_before_run': self.confirm_before_run,
            'show_output': self.show_output,
            'execution_mode': self.execution_mode,
            'run_as_user': self.run_as_user,
            'sudo_password_encoded': self.sudo_password_encoded,
            'profile_id': self.profile_id,
            'position': self.position,
            'category': self.category,
            'tooltip': self.tooltip,
            'hide_label': self.hide_label,
            'hide_icon': self.hide_icon,
            'text_color': self.text_color,
            'is_default': self.is_default,
            'mcp_executable': self.mcp_executable,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CommandButton':
        # Backward compat: old format used machine_id (single str)
        machine_ids = data.get('machine_ids', None)
        if machine_ids is None:
            old_id = data.get('machine_id', '')
            machine_ids = [old_id] if old_id else []

        return cls(
            id=data['id'],
            name=data['name'],
            command=data['command'],
            machine_ids=machine_ids,
            icon_name=data.get('icon_name', 'utilities-terminal-symbolic'),
            color=data.get('color', ''),
            confirm_before_run=data.get('confirm_before_run', False),
            show_output=data.get('show_output', False),
            execution_mode=data.get('execution_mode', ''),
            run_as_user=data.get('run_as_user', ''),
            sudo_password_encoded=data.get('sudo_password_encoded', ''),
            profile_id=data.get('profile_id', ''),
            position=data.get('position', 0),
            category=data.get('category', ''),
            tooltip=data.get('tooltip', ''),
            hide_label=data.get('hide_label', False),
            hide_icon=data.get('hide_icon', False),
            text_color=data.get('text_color', ''),
            is_default=data.get('is_default', False),
            mcp_executable=data.get('mcp_executable', False),
        )

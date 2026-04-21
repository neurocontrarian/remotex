from dataclasses import dataclass, field
import uuid


@dataclass
class ExecutionProfile:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_as_user: str = ""
    working_dir: str = ""
    description: str = ""
    sudo_password_encoded: str = ""

    @property
    def has_sudo_password(self) -> bool:
        return bool(self.sudo_password_encoded)

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
            'run_as_user': self.run_as_user,
            'working_dir': self.working_dir,
            'description': self.description,
            'sudo_password_encoded': self.sudo_password_encoded,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ExecutionProfile':
        return cls(
            id=data['id'],
            name=data['name'],
            run_as_user=data.get('run_as_user', ''),
            working_dir=data.get('working_dir', ''),
            description=data.get('description', ''),
            sudo_password_encoded=data.get('sudo_password_encoded', ''),
        )

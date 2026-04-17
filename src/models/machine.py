from dataclasses import dataclass, field
import uuid


@dataclass
class Machine:
    name: str
    host: str
    user: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    port: int = 22
    identity_file: str = ""  # Path to SSH private key
    icon_name: str = "pc-display"  # Bootstrap icon name for this machine

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'host': self.host,
            'user': self.user,
            'port': self.port,
            'identity_file': self.identity_file,
            'icon_name': self.icon_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Machine':
        return cls(
            id=data['id'],
            name=data['name'],
            host=data['host'],
            user=data['user'],
            port=data.get('port', 22),
            identity_file=data.get('identity_file', ''),
            icon_name=data.get('icon_name', 'pc-display'),
        )

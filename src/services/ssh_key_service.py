import subprocess
from pathlib import Path

from models.machine import Machine

KNOWN_KEY_NAMES = ["id_ed25519", "id_rsa", "id_ecdsa", "id_dsa"]


class SSHKeyService:
    """Handles SSH key detection, generation, and deployment to remote machines."""

    def find_existing_keys(self) -> list[Path]:
        """Return all SSH private keys found in ~/.ssh/."""
        ssh_dir = Path.home() / ".ssh"
        found = []
        for name in KNOWN_KEY_NAMES:
            key = ssh_dir / name
            pub = ssh_dir / f"{name}.pub"
            if key.exists() and pub.exists():
                found.append(key)
        return found

    def preferred_key(self) -> Path | None:
        """Return the best available key (ed25519 preferred), or None."""
        keys = self.find_existing_keys()
        return keys[0] if keys else None

    def generate_key(self) -> tuple[bool, str, Path | None]:
        """Generate a new ed25519 key pair. Returns (success, message, key_path)."""
        key_path = Path.home() / ".ssh" / "id_ed25519"
        if key_path.exists():
            return False, "Key already exists at ~/.ssh/id_ed25519.", key_path

        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(mode=0o700, exist_ok=True)

        try:
            subprocess.run(
                ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(key_path)],
                check=True,
                capture_output=True,
            )
            return True, f"Key generated at {key_path}", key_path
        except subprocess.CalledProcessError as e:
            return False, f"ssh-keygen failed: {e.stderr.decode()}", None

    def copy_key_to_machine(self, machine: Machine, password: str, key_path: Path) -> tuple[bool, str]:
        """Copy a public key to the remote machine using password authentication.
        This is the only time a password is used — afterwards, key-based auth takes over.
        """
        pub_key_path = Path(f"{key_path}.pub")
        if not pub_key_path.exists():
            return False, f"Public key not found: {pub_key_path}"

        pub_key = pub_key_path.read_text().strip()

        try:
            import paramiko
        except ImportError:
            return False, "paramiko is not installed. Run: pip install paramiko"

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(
                hostname=machine.host,
                port=machine.port,
                username=machine.user,
                password=password,
                timeout=10,
                allow_agent=False,
                look_for_keys=False,
            )

            # Ensure ~/.ssh exists and append the key to authorized_keys
            commands = (
                "mkdir -p ~/.ssh && "
                "chmod 700 ~/.ssh && "
                f'grep -qxF "{pub_key}" ~/.ssh/authorized_keys 2>/dev/null || '
                f'echo "{pub_key}" >> ~/.ssh/authorized_keys && '
                "chmod 600 ~/.ssh/authorized_keys"
            )
            _, stdout, stderr = client.exec_command(commands)
            exit_code = stdout.channel.recv_exit_status()

            if exit_code != 0:
                return False, f"Failed to write key: {stderr.read().decode()}"

            return True, "SSH key successfully copied. You can now connect without a password."

        except paramiko.AuthenticationException:
            return False, "Authentication failed — incorrect username or password."
        except paramiko.ssh_exception.NoValidConnectionsError:
            return False, f"Could not connect to {machine.host}:{machine.port} — host unreachable."
        except TimeoutError:
            return False, f"Connection to {machine.host} timed out."
        except Exception as e:
            return False, str(e)
        finally:
            client.close()

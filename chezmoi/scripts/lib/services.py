from .common import as_root, have, run


def enable_service(name: str) -> None:
    print(f"Enabling {name} service..." if name == "ollama" else f"Enabling {name}...")
    if run(["systemctl", "--user", "enable", "--now", name], quiet=True, check=False).returncode == 0:
        return
    if as_root(["systemctl", "enable", "--now", name]).returncode == 0:
        return
    print(f"Warning: could not enable {name}")


def enable_services() -> None:
    if not have("systemctl"):
        return

    if have("ollama"):
        enable_service("ollama")

    if have("podman"):
        enable_service("podman.socket")

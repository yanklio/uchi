import os

from .common import APPS_DIR, ENV_FILE, csv_values, die, run, warn
from .tailscale import require_tailscale_access, tailscale_only_mode


def load_env(required: bool = True) -> None:
    if not ENV_FILE.exists():
        if required:
            die(
                f"Missing {ENV_FILE}. Copy homelab/.env.example to homelab/.env and set PIHOLE_PASSWORD."
            )
        return

    mode = ENV_FILE.stat().st_mode & 0o777
    if mode & 0o077:
        warn(f"{ENV_FILE} is mode {mode:o}; tightening to 600")
        run(["chmod", "600", str(ENV_FILE)])

    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ[name.strip()] = value.strip().strip('"').strip("'")


def homelab_apps() -> list[str]:
    apps = csv_values(os.environ.get("HOMELAB_APPS", "glance"))
    return [app for app in apps if app != "pi-hole"]


def validate_apps() -> None:
    for app in homelab_apps():
        if "/" in app or app in {".", ".."}:
            die(f"Invalid app name in HOMELAB_APPS: {app}")
        if not (APPS_DIR / app / "docker-compose.yml").exists():
            die(f"Unknown homelab app: {app}")


def validate_env() -> None:
    validate_apps()

    mode = os.environ.get("HOMELAB_ACCESS_MODE", "lan")
    if mode not in {"lan", "tailscale-only"}:
        die(f"Invalid HOMELAB_ACCESS_MODE: {mode}")

    if os.environ.get("PIHOLE_PASSWORD") == "change_me_to_a_strong_password":
        die("PIHOLE_PASSWORD still uses the example value")

    if tailscale_only_mode():
        require_tailscale_access()

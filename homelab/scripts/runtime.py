import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS_DIR = ROOT / "apps"
ENV_FILE = ROOT / ".env"
DEFAULT_APPS = ["pi-hole", "glance", "open-webui"]


def load_env() -> dict[str, str]:
    env = os.environ.copy()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env.setdefault(key, value)
    env.setdefault("HOMELAB_ACCESS_MODE", "tailscale-only")
    env.setdefault("DHCP_ACTIVE", "false")
    env.setdefault("HOMELAB_APP_BIND", "127.0.0.1")
    env.setdefault("HOMELAB_APPS", ",".join(DEFAULT_APPS))
    return env


def selected_apps(env: dict[str, str]) -> list[str]:
    return [app.strip() for app in env.get("HOMELAB_APPS", "").split(",") if app.strip()]


def compose_cmd(action: str) -> list[str]:
    command = ["podman", "compose"]
    if ENV_FILE.exists():
        command += ["--env-file", str(ENV_FILE)]
    if action == "start":
        return command + ["up", "-d"]
    if action == "stop":
        return command + ["down"]
    if action == "restart":
        return command + ["up", "-d"]
    return command + ["ps"]


def run(command: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> int:
    if env and env.get("HOMELAB_DRY_RUN") == "1":
        where = f" (cwd={cwd})" if cwd else ""
        print("+", " ".join(command) + where)
        return 0
    return subprocess.call(command, cwd=cwd, env=env)


def check(command: list[str]) -> int:
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def require_podman_compose() -> bool:
    return shutil.which("podman") is not None and check(["podman", "compose", "version"]) == 0


def app_dir(app: str) -> Path:
    return APPS_DIR / app


def has_compose_file(app: str) -> bool:
    return (app_dir(app) / "docker-compose.yml").exists()


def run_app_action(app: str, action: str, env: dict[str, str]) -> int:
    if not has_compose_file(app):
        print(f"unknown app or missing compose file: {app}", file=sys.stderr)
        return 1
    scoped_env = env.copy()
    scoped_env["HOMELAB_APPS"] = app
    return run(compose_cmd(action), cwd=app_dir(app), env=scoped_env)


def doctor(env: dict[str, str]) -> int:
    status = 0
    if not shutil.which("podman"):
        print("podman is not installed", file=sys.stderr)
        status = 1
    elif check(["podman", "compose", "version"]) != 0:
        print("podman compose is not available", file=sys.stderr)
        status = 1
    if not ENV_FILE.exists():
        print(f"missing {ENV_FILE}", file=sys.stderr)
        status = 1
    if env.get("DHCP_ACTIVE", "false").lower() == "true":
        print("DHCP_ACTIVE=true; confirm this is intentional before starting Pi-hole")
    for app in selected_apps(env):
        if not has_compose_file(app):
            print(f"unknown app or missing compose file: {app}", file=sys.stderr)
            status = 1
    return status


def operate(action: str, env: dict[str, str]) -> int:
    if not require_podman_compose():
        return 1
    status = 0
    for app in selected_apps(env):
        if not has_compose_file(app):
            print(f"skipping unknown app: {app}", file=sys.stderr)
            status = 1
            continue
        rc = run(compose_cmd(action), cwd=app_dir(app), env=env)
        status = status or rc
    return status

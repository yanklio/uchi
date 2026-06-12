import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS_DIR = ROOT / "apps"
SECRETS_DIR = ROOT / "secrets"
STATE_DIR = ROOT / "state"
STORE_DIR = ROOT / "store"
BACKUPS_DIR = ROOT / "backups"
ENV_FILE = ROOT / ".env"
SECRETS_ENV_FILE = SECRETS_DIR / "homelab.env"
DEFAULT_APPS = ["pi-hole", "glance", "open-webui", "hermes"]


@dataclass(frozen=True)
class AppInfo:
    title: str
    port: int
    path: str = "/"
    state_paths: tuple[Path, ...] = ()
    store_paths: tuple[Path, ...] = ()
    legacy_state_paths: tuple[tuple[Path, Path], ...] = ()


APP_INFO = {
    "pi-hole": AppInfo(
        title="Pi-hole",
        port=8081,
        path="/admin/",
        state_paths=(STATE_DIR / "pi-hole" / "etc-pihole", STATE_DIR / "pi-hole" / "etc-dnsmasq.d"),
        legacy_state_paths=(
            (APPS_DIR / "pi-hole" / "etc-pihole", STATE_DIR / "pi-hole" / "etc-pihole"),
            (APPS_DIR / "pi-hole" / "etc-dnsmasq.d", STATE_DIR / "pi-hole" / "etc-dnsmasq.d"),
        ),
    ),
    "glance": AppInfo(title="Glance", port=8080),
    "open-webui": AppInfo(
        title="Chat",
        port=3000,
        state_paths=(STATE_DIR / "open-webui" / "data",),
        legacy_state_paths=((APPS_DIR / "open-webui" / "data", STATE_DIR / "open-webui" / "data"),),
        store_paths=(
            STORE_DIR / "models" / "sentence-transformers",
            STORE_DIR / "models" / "tiktoken",
            STORE_DIR / "models" / "whisper",
        ),
    ),
    "hermes": AppInfo(
        title="Hermes",
        port=9119,
        state_paths=(STATE_DIR / "hermes" / "data",),
        legacy_state_paths=((APPS_DIR / "hermes" / "data", STATE_DIR / "hermes" / "data"),),
        store_paths=(STORE_DIR / "browser" / "playwright", STORE_DIR / "models" / "hermes"),
    ),
}


def load_env() -> dict[str, str]:
    env = os.environ.copy()
    env_file = SECRETS_ENV_FILE if SECRETS_ENV_FILE.exists() else ENV_FILE
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env.setdefault(key, value)
    env.setdefault("HOMELAB_ACCESS_MODE", "tailscale-only")
    env.setdefault("DHCP_ACTIVE", "false")
    env.setdefault("HOMELAB_APP_BIND", "0.0.0.0")
    env.setdefault("HOMELAB_APPS", ",".join(DEFAULT_APPS))
    env.setdefault("HOMELAB_TAILNET_MAGICDNS_NAME", env.get("HOMELAB_TAILNET_DNS_SUFFIX", "localhost"))
    return env


def selected_apps(env: dict[str, str]) -> list[str]:
    return [app.strip() for app in env.get("HOMELAB_APPS", "").split(",") if app.strip()]


def compose_cmd(action: str) -> list[str]:
    command = ["podman", "compose"]
    env_file = SECRETS_ENV_FILE if SECRETS_ENV_FILE.exists() else ENV_FILE
    if env_file.exists():
        command += ["--env-file", str(env_file)]
    if action == "start":
        return command + ["up", "-d"]
    if action == "stop":
        return command + ["down"]
    if action == "restart":
        return command + ["restart"]
    if action == "recreate":
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


def service_url(app: str, env: dict[str, str]) -> str:
    info = APP_INFO[app]
    host = env.get("HOMELAB_TAILNET_MAGICDNS_NAME") or env.get("HOMELAB_TAILNET_DNS_SUFFIX") or "localhost"
    return f"http://{host}:{info.port}{info.path}"


def urls(env: dict[str, str]) -> int:
    for app in selected_apps(env):
        info = APP_INFO.get(app)
        if info:
            print(f"{info.title}: {service_url(app, env)}")
    return 0


def paths(env: dict[str, str]) -> int:
    print("External backup should include:")
    print(f"  {SECRETS_DIR}")
    print(f"  {STATE_DIR}")
    print("Optional shared store:")
    print(f"  {STORE_DIR}")
    print("\nApp state paths:")
    for app in selected_apps(env):
        info = APP_INFO.get(app)
        if not info:
            continue
        print(f"  {app}:")
        if not info.state_paths:
            print("    (no runtime state paths)")
        for path in info.state_paths:
            print(f"    {path}")
    return 0


def ensure_runtime_dirs(env: dict[str, str]) -> None:
    for path in (SECRETS_DIR, STATE_DIR, STORE_DIR, BACKUPS_DIR):
        path.mkdir(parents=True, exist_ok=True)
    for app in selected_apps(env):
        info = APP_INFO.get(app)
        if not info:
            continue
        for path in info.state_paths + info.store_paths:
            path.mkdir(parents=True, exist_ok=True)


def migrate_state(env: dict[str, str]) -> int:
    status = 0
    for app in selected_apps(env):
        info = APP_INFO.get(app)
        if not info:
            continue
        for source, target in info.legacy_state_paths:
            if not source.exists():
                continue
            if target.exists() and any(target.iterdir()):
                print(f"keeping existing state path, legacy path still present: {target}")
                print(f"  legacy: {source}")
                continue
            if env.get("HOMELAB_DRY_RUN") == "1":
                print(f"+ mv {source} {target}")
                continue
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    target.rmdir()
                source.rename(target)
                print(f"migrated {app} state: {source} -> {target}")
            except PermissionError:
                print(f"permission denied migrating {source}", file=sys.stderr)
                print(f"run: sudo mv {source} {target}", file=sys.stderr)
                status = 1
    return status


def doctor(env: dict[str, str]) -> int:
    status = 0
    if not shutil.which("podman"):
        print("podman is not installed", file=sys.stderr)
        status = 1
    elif check(["podman", "compose", "version"]) != 0:
        print("podman compose is not available", file=sys.stderr)
        status = 1
    if not SECRETS_ENV_FILE.exists() and not ENV_FILE.exists():
        print(f"missing {SECRETS_ENV_FILE}", file=sys.stderr)
        status = 1
    if ENV_FILE.exists() and not ENV_FILE.is_symlink():
        print(f"{ENV_FILE} should be a symlink to {SECRETS_ENV_FILE}", file=sys.stderr)
        status = 1
    if env.get("DHCP_ACTIVE", "false").lower() == "true":
        print("DHCP_ACTIVE=true; confirm this is intentional before starting Pi-hole")
    for app in selected_apps(env):
        if not has_compose_file(app):
            print(f"unknown app or missing compose file: {app}", file=sys.stderr)
            status = 1
        info = APP_INFO.get(app)
        if not info:
            continue
        for path in info.state_paths:
            if not path.exists():
                print(f"missing state path: {path}", file=sys.stderr)
                status = 1
    return status


def operate(action: str, env: dict[str, str]) -> int:
    ensure_runtime_dirs(env)
    if action == "urls":
        return urls(env)
    if action == "paths":
        return paths(env)
    if action == "migrate-state":
        return migrate_state(env)
    if action == "quiesce":
        print("Stopping containers so external backup can take a consistent state snapshot.")
        action = "stop"
    if action == "resume":
        print("Starting containers after external backup/restore.")
        action = "start"
    if env.get("HOMELAB_DRY_RUN") == "1":
        status = 0
        for app in selected_apps(env):
            if not has_compose_file(app):
                print(f"skipping unknown app: {app}", file=sys.stderr)
                status = 1
                continue
            if action == "recreate":
                rc = run(compose_cmd("stop"), cwd=app_dir(app), env=env)
                status = status or rc
            rc = run(compose_cmd(action), cwd=app_dir(app), env=env)
            status = status or rc
        return status

    if not require_podman_compose():
        return 1
    status = 0
    for app in selected_apps(env):
        if not has_compose_file(app):
            print(f"skipping unknown app: {app}", file=sys.stderr)
            status = 1
            continue
        if action == "recreate":
            rc = run(compose_cmd("stop"), cwd=app_dir(app), env=env)
            status = status or rc
        rc = run(compose_cmd(action), cwd=app_dir(app), env=env)
        status = status or rc
    return status

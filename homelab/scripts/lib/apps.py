import os

from .common import (
    APPS_DIR,
    ENV_FILE,
    as_root,
    can_run_as_root_noninteractive,
    have,
    require_podman_compose,
    run,
)
from .env import homelab_apps, load_env
from .tailscale import show_tailscale_access_urls, tailscale_only_mode


def compose_in_app(app: str, args: list[str]) -> None:
    app_dir = APPS_DIR / app
    env_args = ["--env-file", str(ENV_FILE)] if ENV_FILE.exists() else []
    env = os.environ.copy()
    if tailscale_only_mode():
        env["HOMELAB_APP_BIND"] = "127.0.0.1"
    run(["podman", "compose", *env_args, *args], cwd=app_dir, env=env)


def start_rootless_apps() -> None:
    require_podman_compose()
    for app in homelab_apps():
        print(f"Starting {app}...")
        compose_in_app(app, ["up", "-d"])


def stop_rootless_apps() -> None:
    require_podman_compose()
    for app in homelab_apps():
        print(f"Stopping {app}...")
        compose_in_app(app, ["down"])


def show_rootless_containers() -> None:
    print("Rootless containers:", flush=True)
    if have("podman"):
        run(["podman", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
        return
    print("podman is not installed")


def show_rootful_containers() -> None:
    print("\nRootful containers:", flush=True)
    if have("podman") and can_run_as_root_noninteractive():
        as_root(["podman", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
        return
    print("sudo root access or podman is not available")


def show_status() -> None:
    load_env(required=False)
    show_rootless_containers()
    show_rootful_containers()
    print()
    show_tailscale_access_urls()

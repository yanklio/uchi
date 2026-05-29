#!/usr/bin/env python3
import sys

from lib.apps import show_status, start_rootless_apps, stop_rootless_apps
from lib.common import PROGRAM, dry_run
from lib.doctor import doctor
from lib.env import load_env, validate_apps, validate_env
from lib.nginx import configure_nginx
from lib.pihole import start_optional_pihole, start_pihole, stop_pihole
from lib.tailscale import show_tailscale_access_urls


def usage() -> None:
    print(
        f"""Usage: {PROGRAM} [command]

Environment:
  HOMELAB_DRY_RUN=1  Print actions without running them
  DOTFILES_DRY_RUN=1 Alias for HOMELAB_DRY_RUN compatibility

Commands:
  start     Start Pi-hole rootful and rootless apps (default)
  stop      Stop rootless apps and Pi-hole
  restart   Stop, then start the homelab stack
  status    Show rootless and rootful container status
  doctor    Validate tools, env, and app inventory
  pihole    Start/configure only rootful Pi-hole
  nginx     Apply homelab nginx reverse-proxy config
  help      Show this help"""
    )


def start() -> None:
    load_env(required=True)
    validate_env()
    start_optional_pihole()
    start_rootless_apps()
    print("All homelab containers started.")
    show_tailscale_access_urls()


def stop() -> None:
    load_env(required=False)
    validate_apps()
    stop_rootless_apps()
    stop_pihole()
    print("All homelab containers stopped.")


def restart() -> None:
    stop()
    start()


COMMANDS = {
    "start": start,
    "stop": stop,
    "restart": restart,
    "status": show_status,
    "doctor": doctor,
    "pihole": start_pihole,
    "nginx": configure_nginx,
}


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    if command in {"help", "-h", "--help"}:
        usage()
        return 0
    if command not in COMMANDS:
        print(f"Unknown homelab command: {command}\n", file=sys.stderr)
        usage()
        return 2

    if dry_run():
        print("Running homelab command in dry-run mode...")
    result = COMMANDS[command]()
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())

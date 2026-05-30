import json
import os
import socket
import subprocess

from .common import (
    APPS_DIR,
    ENV_FILE,
    as_root,
    csv_values,
    die,
    dry_run,
    have,
    require_podman_compose,
    run,
    truthy,
    warn,
)
from .env import load_env, validate_env
from .tailscale import tailscale_ipv4, tailscale_only_mode


def pihole_dns_enabled() -> bool:
    return truthy(os.environ.get("HOMELAB_ENABLE_PIHOLE_DNS", "false"))


def should_start_pihole() -> bool:
    return not tailscale_only_mode() or pihole_dns_enabled()


def pihole_dns_hosts() -> list[str]:
    if tailscale_only_mode():
        ip = tailscale_ipv4()
        suffix = os.environ.get("HOMELAB_TAILNET_DNS_SUFFIX", socket.gethostname().split(".", 1)[0])
        names = os.environ.get("HOMELAB_TAILNET_DNS_NAMES") or os.environ.get("HOMELAB_APPS", "glance")
    else:
        ip = os.environ.get("HOMELAB_IP", "")
        suffix = os.environ.get("HOMELAB_DOMAIN") or os.environ.get("PIHOLE_DOMAIN", "home")
        names = os.environ.get("HOMELAB_DNS_NAMES", "pihole,glance")
    if not ip:
        die("No IP available for Pi-hole local DNS records")
    return [f"{ip} {name}.{suffix}" for name in csv_values(names)]


def start_optional_pihole() -> None:
    if not should_start_pihole():
        print("Skipping Pi-hole in tailscale-only mode.")
        return
    start_pihole()


def remove_rootless_pihole() -> None:
    print("Stopping rootless Pi-hole if it exists...")
    if dry_run():
        run(["podman", "rm", "-f", "pihole"])
        return
    subprocess.run(
        ["podman", "rm", "-f", "pihole"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def configure_pihole_dns() -> None:
    print("Configuring Pi-hole local DNS records...")
    as_root(
        [
            "podman",
            "exec",
            "pihole",
            "pihole-FTL",
            "--config",
            "dns.hosts",
            json.dumps(pihole_dns_hosts()),
        ],
        quiet=True,
    )


def configure_pihole_dhcp() -> None:
    if tailscale_only_mode():
        print("Skipping Pi-hole DHCP configuration in tailscale-only mode.")
        return
    if not truthy(os.environ.get("DHCP_ACTIVE", "true")):
        return

    print("Configuring Pi-hole DHCP DNS option...")
    value = json.dumps([f"dhcp-option=option:dns-server,{os.environ.get('HOMELAB_IP', '')}"])
    as_root(
        ["podman", "exec", "pihole", "pihole-FTL", "--config", "misc.dnsmasq_lines", value],
        quiet=True,
    )


def enable_podman_restart() -> None:
    if have("systemctl") and (have("sudo") or os.geteuid() == 0):
        as_root(["systemctl", "enable", "--now", "podman-restart.service"], quiet=True, check=False)


def start_pihole() -> None:
    require_podman_compose()
    if not have("sudo") and os.geteuid() != 0:
        die("sudo is required for rootful Pi-hole")
    load_env(required=True)
    if not os.environ.get("PIHOLE_PASSWORD"):
        die(f"PIHOLE_PASSWORD must be set in {ENV_FILE}")
    validate_env()

    pihole_dir = APPS_DIR / "pi-hole"
    if not (pihole_dir / "docker-compose.yml").exists():
        die(f"Missing {pihole_dir / 'docker-compose.yml'}")

    remove_rootless_pihole()
    print(
        "Starting Pi-hole rootful for tailnet DNS only..."
        if tailscale_only_mode()
        else "Starting Pi-hole rootful for DNS/DHCP..."
    )
    as_root(["podman", "compose", "--env-file", str(ENV_FILE), "up", "-d"], cwd=pihole_dir)

    configure_pihole_dns()
    configure_pihole_dhcp()
    enable_podman_restart()
    print("Pi-hole rootful container started.")


def stop_pihole() -> None:
    pihole_dir = APPS_DIR / "pi-hole"
    if not (pihole_dir / "docker-compose.yml").exists():
        return
    require_podman_compose()
    if not have("sudo") and os.geteuid() != 0:
        warn("sudo is not available; skipping rootful Pi-hole stop")
        return
    print("Stopping pi-hole...")
    env_args = ["--env-file", str(ENV_FILE)] if ENV_FILE.exists() else []
    as_root(["podman", "compose", *env_args, "down"], cwd=pihole_dir)

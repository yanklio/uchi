import json
import os
import subprocess
import sys

from .common import ENV_FILE, have, warn
from .env import load_env, validate_env
from .pihole import pihole_dns_enabled, pihole_dns_hosts
from .tailscale import show_tailscale_access_urls, tailscale_ipv4, tailscale_only_mode


def doctor() -> int:
    issues = []
    if ENV_FILE.exists():
        load_env(required=False)
    else:
        issues.append(f"{ENV_FILE} is missing")

    print("Checking homelab prerequisites...")
    if not have("podman"):
        issues.append("podman is not installed")
    elif subprocess.run(["podman", "compose", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        issues.append("podman compose is not available")

    if ENV_FILE.exists():
        try:
            validate_env()
        except SystemExit:
            issues.append("homelab environment is invalid")
        print(f"Access mode: {os.environ.get('HOMELAB_ACCESS_MODE', 'lan')}")

    if not tailscale_only_mode() and not os.environ.get("PIHOLE_PASSWORD"):
        issues.append("PIHOLE_PASSWORD is not set")

    if tailscale_only_mode():
        print(f"Tailscale IPv4: {tailscale_ipv4()}")
        show_tailscale_access_urls()

    if tailscale_only_mode() and pihole_dns_enabled():
        print(f"Tailnet DNS: Pi-hole enabled for {json.dumps(pihole_dns_hosts())}")
        if not os.environ.get("PIHOLE_PASSWORD"):
            issues.append("PIHOLE_PASSWORD is required when HOMELAB_ENABLE_PIHOLE_DNS=true")

    if issues:
        for message in issues:
            warn(message)
        print("Homelab doctor found issues.", file=sys.stderr)
        return 1
    print("Homelab doctor passed.")
    return 0

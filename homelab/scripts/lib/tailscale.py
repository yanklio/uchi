import socket
import subprocess

from .common import die, have, require, run_capture


def tailscale_only_mode() -> bool:
    import os

    return os.environ.get("HOMELAB_ACCESS_MODE", "lan") == "tailscale-only"


def tailscale_ipv4() -> str:
    if not have("tailscale"):
        return ""
    for line in run_capture(["tailscale", "ip", "-4"]).splitlines():
        if line.strip():
            return line.strip()
    return ""


def require_tailscale_access() -> None:
    require("tailscale")
    if subprocess.run(["tailscale", "status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        die("Tailscale is not running or this host is not logged in; run 'tailscale up' first.")
    if not tailscale_ipv4():
        die("No Tailscale IPv4 address found; check 'tailscale status' and 'tailscale ip -4'.")


def show_tailscale_access_urls() -> None:
    if not tailscale_only_mode():
        return
    ip = tailscale_ipv4()
    if not ip:
        return
    host = socket.gethostname().split(".", 1)[0]
    print("Tailscale access:")
    print(f"  http://{ip}/")
    if host:
        print(f"  http://{host}/ (with Tailscale MagicDNS)")

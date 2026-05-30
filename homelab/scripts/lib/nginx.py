import tempfile
from pathlib import Path

from .common import HOMELAB_DIR, as_root, die, dry_run, run
from .env import load_env, validate_env
from .tailscale import tailscale_ipv4, tailscale_only_mode


def nginx_listen_address() -> str:
    return f"{tailscale_ipv4()}:80" if tailscale_only_mode() else "80"


def render_nginx_conf(source: Path, listen: str) -> str:
    rendered = source.read_text()
    rendered = rendered.replace("listen 80 default_server;", f"listen {listen} default_server;")
    return rendered.replace("listen 80;", f"listen {listen};")


def configure_nginx() -> None:
    config_dir = HOMELAB_DIR / "services" / "nginx" / "conf.d"
    if not config_dir.is_dir():
        die(f"Missing nginx config directory: {config_dir}")
    load_env(required=False)
    validate_env()
    listen = nginx_listen_address()

    if dry_run():
        run(["install", "-m", "0644", *[str(path) for path in config_dir.glob("*.conf")], "/etc/nginx/conf.d/"])
        print(f"Nginx reverse proxy listening on {listen}.")
        return

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        rendered_files = []
        for conf in config_dir.glob("*.conf"):
            rendered = tmp_dir / f"dotfiles-{conf.name}"
            rendered.write_text(render_nginx_conf(conf, listen))
            rendered_files.append(rendered)

        as_root(["mkdir", "-p", "/etc/nginx/conf.d"])
        default_site = Path("/etc/nginx/sites-enabled/default")
        if default_site.is_symlink():
            as_root(["rm", str(default_site)])
        elif default_site.exists():
            as_root(["mv", "-n", str(default_site), "/etc/nginx/sites-available/default.disabled"])

        for site in [Path("/etc/nginx/conf.d/default.conf"), Path("/etc/nginx/conf.d/welcome.conf")]:
            if site.exists():
                as_root(["mv", "-n", str(site), f"{site}.disabled"])

        as_root(["rm", "-f", "/etc/nginx/conf.d/home-lab.conf", *[str(path) for path in Path("/etc/nginx/conf.d").glob("dotfiles-*.conf")]])
        for rendered in rendered_files:
            as_root(["install", "-m", "0644", str(rendered), f"/etc/nginx/conf.d/{rendered.name}"])

    as_root(["nginx", "-t"])
    as_root(["systemctl", "enable", "--now", "nginx"])
    as_root(["systemctl", "reload", "nginx"])
    print(f"Nginx reverse proxy listening on {listen}.")

import os
import subprocess
from pathlib import Path

from .common import PACKAGES_DIR, add_post_setup_note, dry_run, have, read_list, run


def install_go_tools() -> None:
    if not have("go"):
        return
    tools = read_list(PACKAGES_DIR / "go.txt")
    if not tools:
        return
    print("Installing Go tools...")
    for tool in tools:
        run(["go", "install", tool])


def install_oh_my_zsh() -> None:
    if not have("curl") or (Path.home() / ".oh-my-zsh").is_dir():
        return
    print("Installing oh-my-zsh...")
    command = "curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh | sh --unattended"
    if dry_run():
        print(f"+ {command}")
        return
    env = {**os.environ, "RUNZSH": "no", "CHSH": "no", "KEEP_ZSHRC": "yes"}
    subprocess.run(command, shell=True, check=True, env=env)


def install_npm_packages() -> None:
    if not have("npm"):
        return
    packages = read_list(PACKAGES_DIR / "npm.txt")
    if not packages:
        return
    print("Installing npm packages...")
    run(["npm", "install", "--global", "--prefix", str(Path.home() / ".local"), *packages])


def install_extra_cli_tools() -> None:
    if not have("curl"):
        return
    for line in read_list(PACKAGES_DIR / "upstream.txt"):
        command_name, display_name, install_url = [*line.split("|"), "", ""][:3]
        if not command_name or have(command_name):
            continue
        print(f"Installing {display_name}...")
        if dry_run():
            print(f"+ curl -fsSL {install_url} | sh")
        else:
            subprocess.run(f"curl -fsSL {install_url} | sh", shell=True, check=True)
        if command_name == "tailscale":
            add_post_setup_note("Tailscale: run 'sudo tailscale up' to complete setup.")


def install_flatpaks() -> None:
    if not have("flatpak"):
        return
    apps = read_list(PACKAGES_DIR / "flatpak.txt")
    if not apps:
        return
    print("Installing Flatpaks...")
    for app in apps:
        if subprocess.run(["flatpak", "info", app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            continue
        if run(["flatpak", "install", "--noninteractive", "--user", "-y", "flathub", app], quiet=True, check=False).returncode != 0:
            print(f"Skipping {app}; install manually if needed.")

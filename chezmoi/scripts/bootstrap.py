#!/usr/bin/env python3
import sys

from lib.common import dry_run, print_post_setup_notes
from lib.desktop import apply_gnome_settings
from lib.packages import install_system_packages
from lib.services import enable_services
from lib.tools import (
    install_extra_cli_tools,
    install_flatpaks,
    install_go_tools,
    install_npm_packages,
    install_oh_my_zsh,
)


def usage() -> None:
    print(
        """Usage: bootstrap.sh [section ...]

Environment:
  DOTFILES_DRY_RUN=1  Print actions without running them

Sections:
  all       Run every bootstrap section (default)
  packages  Install role-based system packages with dnf/apt
  go        Install Go tools
  shell     Install oh-my-zsh
  npm       Install npm global packages
  upstream  Install upstream CLI tools
  flatpak   Install Flatpak apps
  services  Enable user/system services
  gnome     Apply GNOME settings when enabled/detected"""
    )


def run_all() -> None:
    install_system_packages()
    install_go_tools()
    install_oh_my_zsh()
    install_npm_packages()
    install_extra_cli_tools()
    install_flatpaks()
    enable_services()
    apply_gnome_settings()


SECTIONS = {
    "all": run_all,
    "packages": install_system_packages,
    "go": install_go_tools,
    "shell": install_oh_my_zsh,
    "npm": install_npm_packages,
    "upstream": install_extra_cli_tools,
    "flatpak": install_flatpaks,
    "flatpaks": install_flatpaks,
    "services": enable_services,
    "gnome": apply_gnome_settings,
}


def main() -> int:
    sections = sys.argv[1:] or ["all"]
    if sections[0] in {"help", "-h", "--help"}:
        usage()
        return 0

    print("Running bootstrap in dry-run mode..." if dry_run() else "Running bootstrap...")
    for section in sections:
        if section not in SECTIONS:
            print(f"Unknown bootstrap section: {section}\n", file=sys.stderr)
            usage()
            return 2
        SECTIONS[section]()

    print_post_setup_notes()
    print("Bootstrap complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

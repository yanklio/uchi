import os
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
PACKAGES_DIR = SCRIPT_DIR / "packages"
POST_SETUP_NOTES: list[str] = []


def truthy(value: str | None) -> bool:
    return value in {"1", "true", "yes", "on"}


def dry_run() -> bool:
    return truthy(os.environ.get("DOTFILES_DRY_RUN"))


def have(command: str) -> bool:
    return shutil.which(command) is not None


def command_text(args: list[str]) -> str:
    return "+ " + " ".join(subprocess.list2cmdline([arg]) for arg in args)


def run(
    args: list[str], *, quiet: bool = False, check: bool = True
) -> subprocess.CompletedProcess[str]:
    if dry_run():
        print(command_text(args))
        return subprocess.CompletedProcess(args, 0)
    stderr = subprocess.DEVNULL if quiet else None
    return subprocess.run(args, stderr=stderr, check=check)


def as_root(args: list[str]) -> subprocess.CompletedProcess[str]:
    if dry_run() or os.geteuid() == 0:
        return run(args, check=False)
    if not have("sudo"):
        return subprocess.CompletedProcess(args, 1)
    sudo = ["sudo"] if os.isatty(0) else ["sudo", "-n"]
    return run([*sudo, *args], check=False)


def read_list(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def detect_package_manager() -> str | None:
    if have("dnf"):
        return "dnf"
    if have("apt-get"):
        return "apt"
    return None


def is_gnome() -> bool:
    setting = os.environ.get("DOTFILES_GNOME_SETTINGS", "auto")
    if setting in {"1", "true", "yes", "on", "force", "gnome"}:
        return True
    if setting in {"0", "false", "no", "off", "none", "skip"}:
        return False
    desktop = ":".join(
        [
            os.environ.get("XDG_CURRENT_DESKTOP", ""),
            os.environ.get("XDG_SESSION_DESKTOP", ""),
            os.environ.get("DESKTOP_SESSION", ""),
        ]
    )
    return "gnome" in desktop.lower()


def add_post_setup_note(note: str) -> None:
    if note:
        POST_SETUP_NOTES.append(note)


def print_post_setup_notes() -> None:
    if not POST_SETUP_NOTES:
        return
    print("\nPost-setup notes:")
    for note in POST_SETUP_NOTES:
        print(f"- {note}")

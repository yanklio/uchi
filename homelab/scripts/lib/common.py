import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
HOMELAB_DIR = SCRIPT_DIR.parent
APPS_DIR = HOMELAB_DIR / "apps"
ENV_FILE = HOMELAB_DIR / ".env"
PROGRAM = SCRIPT_DIR / "homelab.sh"


def warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def truthy(value: str | None) -> bool:
    return value in {"1", "true", "yes", "on"}


def dry_run() -> bool:
    return truthy(os.environ.get("HOMELAB_DRY_RUN") or os.environ.get("DOTFILES_DRY_RUN"))


def have(command: str) -> bool:
    return shutil.which(command) is not None


def command_text(args: list[str]) -> str:
    return "+ " + " ".join(subprocess.list2cmdline([arg]) for arg in args)


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    quiet: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    if dry_run():
        print(command_text(args))
        return subprocess.CompletedProcess(args, 0, "", "")

    stdout = subprocess.DEVNULL if quiet else None
    return subprocess.run(args, cwd=cwd, env=env, stdout=stdout, text=True, check=check)


def run_capture(args: list[str], *, check: bool = False) -> str:
    result = subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=check
    )
    return result.stdout


def as_root(
    args: list[str],
    *,
    cwd: Path | None = None,
    quiet: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    if os.geteuid() == 0 or dry_run():
        return run(args, cwd=cwd, quiet=quiet, check=check)
    if have("sudo"):
        return run(["sudo", *args], cwd=cwd, quiet=quiet, check=check)
    die("sudo is required")


def can_run_as_root_noninteractive() -> bool:
    if os.geteuid() == 0:
        return True
    if not have("sudo"):
        return False
    return (
        subprocess.run(
            ["sudo", "-n", "true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode
        == 0
    )


def require(command: str) -> None:
    if not have(command):
        die(f"{command} is required")


def require_podman_compose() -> None:
    require("podman")
    result = subprocess.run(
        ["podman", "compose", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode != 0:
        die("podman compose is required")


def csv_values(value: str) -> list[str]:
    return [item.strip() for item in value.replace(",", " ").split() if item.strip()]

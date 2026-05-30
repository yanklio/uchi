from .common import PACKAGES_DIR, as_root, detect_package_manager, is_gnome


def package_enabled(roles: str, managers: str, package_manager: str) -> bool:
    roles = {role.strip() for role in roles.split(",")}
    managers = {manager.strip() for manager in managers.split(",")}
    role_enabled = bool(roles & {"all", "core", "dev"}) or ("desktop" in roles and is_gnome())
    manager_enabled = "all" in managers or package_manager in managers
    return role_enabled and manager_enabled


def collect_packages(package_manager: str) -> list[str]:
    packages = []
    for line in (PACKAGES_DIR / "system.txt").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("|")
        package = parts[0]
        roles = parts[1] if len(parts) > 1 and parts[1] else "all"
        managers = parts[2] if len(parts) > 2 and parts[2] else "all"
        if package_enabled(roles, managers, package_manager):
            packages.append(package)
    return sorted(set(packages))


def install_dnf_packages(packages: list[str]) -> None:
    if as_root(["dnf", "install", "-y", *packages]).returncode != 0:
        print("No TTY available for sudo; skipping Fedora packages.")


def install_apt_packages(packages: list[str]) -> None:
    if as_root(["apt-get", "update"]).returncode != 0:
        print("No TTY available for sudo; skipping Debian/Ubuntu packages.")
        return
    if as_root(["apt-get", "install", "-y", *packages]).returncode != 0:
        print("No TTY available for sudo; skipping Debian/Ubuntu packages.")


def install_system_packages() -> None:
    package_manager = detect_package_manager()
    if not package_manager:
        return

    packages = collect_packages(package_manager)
    if not packages:
        return

    print("Installing system packages...")
    if package_manager == "dnf":
        install_dnf_packages(packages)
        return
    install_apt_packages(packages)

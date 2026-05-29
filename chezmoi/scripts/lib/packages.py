from .common import PACKAGES_DIR, as_root, detect_package_manager, is_gnome


def package_enabled(roles: str, managers: str, package_manager: str) -> bool:
    selected = {role.strip() for role in roles.split(",")}
    supported_managers = {manager.strip() for manager in managers.split(",")}
    role_enabled = bool({"all", "core", "dev"} & selected) or ("desktop" in selected and is_gnome())
    manager_enabled = "all" in supported_managers or package_manager in supported_managers
    return role_enabled and manager_enabled


def collect_packages(package_manager: str) -> list[str]:
    packages = []
    for line in (PACKAGES_DIR / "system.txt").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        package, roles, managers = [*line.split("|"), "all", "all"][:3]
        if package_enabled(roles or "all", managers or "all", package_manager):
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

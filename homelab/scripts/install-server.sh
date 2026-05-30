#!/usr/bin/env bash
set -euo pipefail

dotfiles_dir="${DOTFILES_DIR:-$HOME/Dotfiles}"
chezmoi_source="$dotfiles_dir/chezmoi"
homelab_dir="$dotfiles_dir/homelab"
env_file="$homelab_dir/.env"
package_manager=""

have() {
  command -v "$1" >/dev/null 2>&1
}

require_sudo() {
  if [[ $EUID -eq 0 ]]; then
    return 0
  fi

  if ! have sudo; then
    echo "sudo is required" >&2
    exit 1
  fi
}

install_base_packages() {
  export PATH="$HOME/.local/bin:$PATH"

  if have dnf; then
    package_manager="dnf"
  elif have apt-get; then
    package_manager="apt-get"
  else
    echo "Neither dnf nor apt-get is available; skipping package install."
    return 0
  fi

  echo "Installing homelab packages..."
  case "$package_manager" in
    dnf)
      sudo dnf install -y git curl ca-certificates podman nginx ansible
      ;;
    apt-get)
      sudo apt-get update
      sudo apt-get install -y git curl ca-certificates podman nginx ansible
      ;;
  esac

  if ! have chezmoi; then
    echo "Installing chezmoi..."
    sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "$HOME/.local/bin"
  fi
}

detect_ip() {
  ip -4 route get 1.1.1.1 2>/dev/null | tr ' ' '\n' | awk 'prev == "src" { print; exit } { prev = $0 }'
}

detect_gateway() {
  ip -4 route show default 2>/dev/null | awk '{ print $3; exit }'
}

network_prefix() {
  local ip="$1"
  printf '%s.%s.%s' ${ip//./ }
}

ensure_homelab_env() {
  if [[ -f "$env_file" ]]; then
    chmod 600 "$env_file" 2>/dev/null || true
    echo "Using existing $env_file"
    return 0
  fi

  local ip gateway prefix password old_umask
  ip="$(detect_ip)"
  gateway="$(detect_gateway)"

  [[ -n "$ip" ]] || read -rp "Homelab server IP: " ip
  [[ -n "$gateway" ]] || read -rp "Router/gateway IP: " gateway

  prefix="$(network_prefix "$ip")"

  read -rsp "Pi-hole admin password: " password
  echo

  old_umask="$(umask)"
  umask 077
  {
    printf 'PIHOLE_PASSWORD=%s\n' "$password"
    printf 'DHCP_ACTIVE=true\n'
    printf 'DHCP_START=%s.100\n' "$prefix"
    printf 'DHCP_END=%s.200\n' "$prefix"
    printf 'DHCP_ROUTER=%s\n' "$gateway"
    printf 'DHCP_LEASE_TIME=24h\n'
    printf 'PIHOLE_DOMAIN=home\n'
    printf 'HOMELAB_IP=%s\n' "$ip"
    printf 'HOMELAB_DOMAIN=home\n'
    printf 'HOMELAB_DNS_NAMES=pihole,glance\n'
  } > "$env_file"
  umask "$old_umask"
  chmod 600 "$env_file"
}

apply_dotfiles() {
  echo "Initializing chezmoi..."
  chezmoi init --source="$chezmoi_source"

  echo "Applying dotfiles..."
  chezmoi apply
}

main() {
  require_sudo

  if [[ ! -d "$dotfiles_dir" ]]; then
    echo "Dotfiles repo not found: $dotfiles_dir" >&2
    exit 1
  fi

  install_base_packages
  apply_dotfiles
  ensure_homelab_env

  "$homelab_dir/scripts/homelab.sh" start
  "$homelab_dir/scripts/homelab.sh" nginx

  echo "Homelab server install complete."
  echo "Verify: nslookup glance.home $(grep '^HOMELAB_IP=' "$env_file" | cut -d= -f2-)"
}

main "$@"

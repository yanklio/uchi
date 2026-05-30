#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
homelab_dir="$(cd "$script_dir/.." && pwd)"
dotfiles_dir="${DOTFILES_DIR:-$(cd "$homelab_dir/.." && pwd)}"
playbook="$homelab_dir/ansible/install-server.yml"

have() {
  command -v "$1" >/dev/null 2>&1
}

require_sudo() {
  if [[ $EUID -eq 0 ]]; then
    return 0
  fi

  if ! have sudo; then
    echo "sudo is required to install Ansible." >&2
    exit 1
  fi
}

install_ansible() {
  have ansible-playbook && return 0
  require_sudo

  if have dnf; then
    sudo dnf install -y ansible
  elif have apt-get; then
    sudo apt-get update
    sudo apt-get install -y ansible
  else
    echo "ansible-playbook is required, and neither dnf nor apt-get is available to install it." >&2
    exit 1
  fi
}

main() {
  if [[ ! -d "$dotfiles_dir" ]]; then
    echo "Dotfiles repo not found: $dotfiles_dir" >&2
    exit 1
  fi

  install_ansible
  export DOTFILES_DIR="$dotfiles_dir"
  exec ansible-playbook "$playbook" "$@"
}

main "$@"

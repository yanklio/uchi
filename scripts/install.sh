#!/usr/bin/env bash
set -euo pipefail

dotfiles_repo="${DOTFILES_REPO:-https://github.com/yanklio/dotfiles.git}"
dotfiles_dir="${DOTFILES_DIR:-$HOME/Dotfiles}"
distro="auto"
package_manager=""

export PATH="$HOME/.local/bin:$PATH"

usage() {
  cat <<EOF
Usage: $0 [options]

Installs the minimum dependencies, clones this repository, and applies the
chezmoi dotfiles source. Workstation bootstrap and homelab setup are explicit
follow-up commands.

Options:
  --repo URL         Clone from URL (default: $dotfiles_repo)
  --dir PATH         Clone to PATH (default: $dotfiles_dir)
  --distro NAME      Force package setup for auto, fedora, or debian
  --fedora           Alias for --distro fedora
  --debian           Alias for --distro debian
  --ubuntu           Alias for --distro debian
  -h, --help         Show this help
EOF
}

have() {
  command -v "$1" >/dev/null 2>&1
}

as_root() {
  if [[ $EUID -eq 0 ]]; then
    "$@"
  else
    have sudo || {
      echo "sudo is required" >&2
      exit 1
    }
    sudo "$@"
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --fedora) distro="fedora" ;;
      --debian | --ubuntu) distro="debian" ;;
      --distro)
        [[ $# -ge 2 ]] || { echo "--distro requires a value" >&2; exit 2; }
        distro="$2"
        shift
        ;;
      --distro=*) distro="${1#*=}" ;;
      --repo)
        [[ $# -ge 2 ]] || { echo "--repo requires a value" >&2; exit 2; }
        dotfiles_repo="$2"
        shift
        ;;
      --repo=*) dotfiles_repo="${1#*=}" ;;
      --dir)
        [[ $# -ge 2 ]] || { echo "--dir requires a value" >&2; exit 2; }
        dotfiles_dir="$2"
        shift
        ;;
      --dir=*) dotfiles_dir="${1#*=}" ;;
      --server | --client | --workstation | --gnome | --no-gnome)
        echo "$1 is no longer handled by the dotfiles installer." >&2
        echo "Run chezmoi/scripts/bootstrap.sh for workstation setup or homelab/scripts/install-server.sh for server setup." >&2
        exit 2
        ;;
      -h | --help) usage; exit 0 ;;
      *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
    shift
  done
}

detect_package_manager() {
  case "$distro" in
    auto) ;;
    fedora) package_manager="dnf"; return 0 ;;
    debian | ubuntu) package_manager="apt-get"; return 0 ;;
    *) echo "Unsupported distro: $distro" >&2; exit 2 ;;
  esac

  if have dnf; then
    package_manager="dnf"
  elif have apt-get; then
    package_manager="apt-get"
  else
    echo "Neither dnf nor apt-get is available" >&2
    exit 1
  fi
}

install_base_packages() {
  detect_package_manager

  echo "Installing base packages..."
  case "$package_manager" in
    dnf)
      as_root dnf install -y git curl ca-certificates
      ;;
    apt-get)
      as_root apt-get update
      as_root apt-get install -y git curl ca-certificates
      ;;
  esac
}

install_chezmoi() {
  have chezmoi && return 0

  echo "Installing chezmoi..."
  sh -c "$(curl -fsLS get.chezmoi.io)" -- -b "$HOME/.local/bin"
}

clone_dotfiles() {
  if [[ -d "$dotfiles_dir/.git" ]]; then
    echo "Updating existing dotfiles repo..."
    git -C "$dotfiles_dir" pull --ff-only
    return 0
  fi

  if [[ -e "$dotfiles_dir" ]]; then
    echo "Refusing to overwrite existing path: $dotfiles_dir" >&2
    exit 1
  fi

  echo "Cloning dotfiles..."
  git clone "$dotfiles_repo" "$dotfiles_dir"
}

apply_dotfiles() {
  local chezmoi_source="$dotfiles_dir/chezmoi"

  echo "Initializing chezmoi..."
  chezmoi init --source="$chezmoi_source"

  echo "Applying dotfiles..."
  chezmoi apply
}

next_steps() {
  cat <<EOF

Dotfiles install complete.

Optional follow-up commands:
  Workstation bootstrap: $dotfiles_dir/chezmoi/scripts/bootstrap.sh
  Homelab server setup:  $dotfiles_dir/homelab/scripts/install-server.sh
EOF
}

main() {
  parse_args "$@"
  install_base_packages
  install_chezmoi
  clone_dotfiles
  apply_dotfiles
  next_steps
}

main "$@"

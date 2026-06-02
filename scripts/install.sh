#!/usr/bin/env bash
set -euo pipefail

dotfiles_repo="${DOTFILES_REPO:-https://github.com/yanklio/dot_uchi.git}"
dotfiles_dir="${DOTFILES_DIR:-$HOME/Dotfiles}"
dotfiles_branch="${DOTFILES_BRANCH:-uchi}"
distro="auto"
target=""
package_manager=""

usage() {
  cat <<EOF
Usage: $0 [options]

Install base dependencies, clone/update this repo, and optionally run an
Ansible wrapper.

Options:
  --repo URL            Clone from URL (default: $dotfiles_repo)
  --dir PATH            Clone to PATH (default: $dotfiles_dir)
  --branch NAME         Git branch (default: $dotfiles_branch)
  --target NAME         Run workstation or server after clone
  --distro NAME         Force package setup for auto, fedora, or debian
  -h, --help            Show this help
EOF
}

have() {
  command -v "$1" >/dev/null 2>&1
}

as_root() {
  if [[ $EUID -eq 0 ]]; then
    "$@"
  else
    have sudo || { echo "sudo is required" >&2; exit 1; }
    sudo "$@"
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --distro) distro="${2:?--distro requires a value}"; shift ;;
      --repo) dotfiles_repo="${2:?--repo requires a value}"; shift ;;
      --dir) dotfiles_dir="${2:?--dir requires a value}"; shift ;;
      --branch) dotfiles_branch="${2:?--branch requires a value}"; shift ;;
      --target) target="${2:?--target requires a value}"; shift ;;
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
    dnf) as_root dnf install -y git curl ca-certificates ansible ;;
    apt-get)
      as_root apt-get update
      as_root apt-get install -y git curl ca-certificates ansible python3-apt
      ;;
  esac
}

clone_or_update_repo() {
  if [[ -d "$dotfiles_dir/.git" ]]; then
    echo "Updating existing dotfiles repo..."
    git -C "$dotfiles_dir" fetch --prune origin "$dotfiles_branch"
    git -C "$dotfiles_dir" checkout "$dotfiles_branch"
    git -C "$dotfiles_dir" pull --ff-only origin "$dotfiles_branch"
    return 0
  fi

  if [[ -e "$dotfiles_dir" ]]; then
    echo "Refusing to overwrite existing path: $dotfiles_dir" >&2
    exit 1
  fi

  echo "Cloning dotfiles..."
  git clone --branch "$dotfiles_branch" "$dotfiles_repo" "$dotfiles_dir"
}

run_target() {
  case "$target" in
    "")
      cat <<EOF

Repo ready at $dotfiles_dir.

Next commands:
  Workstation: $dotfiles_dir/scripts/workstation.sh
  Server:      $dotfiles_dir/scripts/server.sh
  Containers:  $dotfiles_dir/scripts/containers.sh start
  Check:       $dotfiles_dir/scripts/check.sh
EOF
      ;;
    workstation | server) "$dotfiles_dir/scripts/$target.sh" ;;
    *) echo "Unknown target: $target" >&2; exit 2 ;;
  esac
}

main() {
  parse_args "$@"
  install_base_packages
  clone_or_update_repo
  run_target
}

main "$@"

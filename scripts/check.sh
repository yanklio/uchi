#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

have() {
  command -v "$1" >/dev/null 2>&1
}

check_shell() {
  echo "Checking shell syntax..."
  bash -n "$root"/scripts/*.sh
  bash -n "$root"/homelab/scripts/*.sh
  bash -n "$root/chezmoi/scripts/bootstrap.sh"
}

check_python() {
  echo "Checking Python syntax..."
  python3 -c 'import pathlib, sys; [compile(path.read_text(), str(path), "exec") for base in sys.argv[1:] for path in pathlib.Path(base).rglob("*.py")]' "$root/homelab/scripts" "$root/chezmoi/scripts"
}

check_homelab_compose() {
  have podman || return 0
  podman compose version >/dev/null 2>&1 || return 0

  echo "Checking homelab compose files..."
  local compose_file app_dir env_arg=()
  [[ -f "$root/homelab/.env.example" ]] && env_arg=(--env-file "$root/homelab/.env.example")

  for compose_file in "$root"/homelab/apps/*/docker-compose.yml; do
    [[ -f "$compose_file" ]] || continue
    app_dir="$(dirname "$compose_file")"
    (cd "$app_dir" && podman compose "${env_arg[@]}" config >/dev/null)
  done
}

check_chezmoi_templates() {
  have chezmoi || {
    echo "chezmoi is not installed; skipping template checks."
    return 0
  }

  echo "Checking chezmoi templates..."
  chezmoi --source="$root/chezmoi" execute-template < "$root/chezmoi/.chezmoi.toml.tmpl" >/dev/null
}

check_chezmoi_diff() {
  have chezmoi || return 0

  echo "Previewing chezmoi diff..."
  chezmoi --source="$root/chezmoi" diff --exclude=scripts >/dev/null
}

check_ansible() {
  have ansible-playbook || {
    echo "ansible-playbook is not installed; skipping playbook syntax checks."
    return 0
  }

  echo "Checking Ansible playbooks..."
  ansible-playbook --syntax-check -i localhost, "$root/homelab/playbook.yml"
}

check_ignored_runtime_state() {
  echo "Checking homelab ignore rules..."
  git -C "$root" check-ignore -q homelab/.env
  git -C "$root" check-ignore -q homelab/apps/pi-hole/etc-pihole/pihole.toml
}

main() {
  check_shell
  check_python
  check_chezmoi_templates
  check_chezmoi_diff
  check_ansible
  check_homelab_compose
  check_ignored_runtime_state
  echo "Checks passed."
}

main "$@"

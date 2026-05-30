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
  [[ ! -f "$root/dotfiles" ]] || bash -n "$root/dotfiles"
}

check_python() {
  echo "Checking Python syntax..."
  python3 -m py_compile "$root"/homelab/scripts/*.py
  for python_file in "$root"/homelab/apps/*/*.py; do
    [[ -f "$python_file" ]] || continue
    python3 -m py_compile "$python_file"
  done
}

check_yaml() {
  have yamllint || return 0
  echo "Checking YAML..."
  yamllint "$root/ansible" "$root/homelab/apps"
}

check_ansible() {
  have ansible-playbook || {
    echo "ansible-playbook is not installed; skipping syntax check."
    return 0
  }

  echo "Checking Ansible syntax..."
  ansible-playbook -i "$root/ansible/hosts.yml" "$root/ansible/site.yml" --syntax-check
}

check_ansible_lint() {
  have ansible-lint || return 0
  echo "Checking Ansible lint..."
  ansible-lint "$root/ansible/site.yml"
}

check_compose() {
  have podman || return 0
  podman compose version >/dev/null 2>&1 || return 0

  echo "Checking compose files..."
  local compose_file app_dir env_arg=()
  [[ -f "$root/homelab/.env.example" ]] && env_arg=(--env-file "$root/homelab/.env.example")

  for compose_file in "$root"/homelab/apps/*/docker-compose.yml; do
    [[ -f "$compose_file" ]] || continue
    app_dir="$(dirname "$compose_file")"
    (cd "$app_dir" && podman compose "${env_arg[@]}" config >/dev/null)
  done
}

main() {
  check_shell
  check_python
  check_yaml
  check_ansible
  check_ansible_lint
  check_compose
  echo "Checks passed."
}

main "$@"

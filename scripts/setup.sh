#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v ansible-playbook >/dev/null 2>&1; then
  echo "ansible-playbook is required. Run scripts/install.sh first." >&2
  exit 1
fi

ansible-playbook -i "$root/ansible/hosts.yml" "$root/ansible/site.yml" --ask-become-pass "$@"

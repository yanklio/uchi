#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ansible-playbook -i "$root/ansible/hosts.yml" "$root/ansible/site.yml" --limit workstation --ask-become-pass "$@"

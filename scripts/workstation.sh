#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$root/scripts/lib.sh"

require_command ansible-playbook "ansible-playbook is required. Run scripts/install.sh first."
run_ansible "$root" workstation --ask-become-pass "$@"

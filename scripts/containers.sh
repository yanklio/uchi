#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$root/scripts/lib.sh"

usage() {
  cat >&2 <<EOF
Usage: $0 start|stop|restart|recreate|status|doctor|urls|paths|migrate-state|quiesce|resume|app <app> [command]
EOF
  exit 2
}

homelab() {
  "$root/homelab/scripts/homelab.sh" "$@"
}

run_privileged_migration() {
  require_command ansible-playbook "ansible-playbook is required. Run scripts/install.sh first."
  run_ansible "$root" server --tags migrate-state --ask-become-pass "$@"
}

run_app_command() {
  local app="${1:-}"
  local command="${2:-list}"
  [[ -n "$app" ]] || usage

  if [[ $# -ge 2 ]]; then
    shift 2
  else
    shift
  fi

  homelab app "$app" "$command" "$@"
}

main() {
  local action="${1:-}"
  [[ -n "$action" ]] || usage
  shift || true

  case "$action" in
    start|stop|restart|recreate|status|doctor|urls|paths|quiesce|resume) homelab "$action" "$@" ;;
    migrate-state) run_privileged_migration "$@" ;;
    app) run_app_command "$@" ;;
    *) usage ;;
  esac
}

main "$@"

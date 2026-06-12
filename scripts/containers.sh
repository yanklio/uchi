#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
action="${1:-}"

if ! command -v ansible-playbook >/dev/null 2>&1; then
  echo "ansible-playbook is required. Run scripts/install.sh first." >&2
  exit 1
fi

case "$action" in
  start) tag="start-containers" ;;
  stop) tag="stop-containers" ;;
  restart) tag="restart-containers" ;;
  recreate) tag="recreate-containers" ;;
  status) tag="status" ;;
  doctor) tag="doctor" ;;
  urls) tag="urls" ;;
  paths) tag="paths" ;;
  migrate-state) tag="migrate-state" ;;
  quiesce) tag="quiesce" ;;
  resume) tag="resume" ;;
  app)
    app="${2:-}"
    command="${3:-list}"
    if [[ -z "$app" ]]; then
      echo "Usage: $0 app <app> [command]" >&2
      exit 2
    fi
    if [[ $# -ge 3 ]]; then
      shift 3
    else
      shift 2
    fi
    ansible-playbook -i "$root/ansible/hosts.yml" "$root/ansible/site.yml" \
      --limit server \
      --tags app-command \
      --extra-vars "homelab_app=$app homelab_app_command=$command" \
      "$@"
    exit 0
    ;;
  *)
    echo "Usage: $0 start|stop|restart|recreate|status|doctor|urls|paths|migrate-state|quiesce|resume|app <app> [command]" >&2
    exit 2
    ;;
esac

shift || true
ansible-playbook -i "$root/ansible/hosts.yml" "$root/ansible/site.yml" --limit server --tags "$tag" "$@"

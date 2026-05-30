#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
action="${1:-}"

case "$action" in
  start) tag="start-containers" ;;
  stop) tag="stop-containers" ;;
  restart) tag="restart-containers" ;;
  status) tag="status" ;;
  doctor) tag="doctor" ;;
  *)
    echo "Usage: $0 start|stop|restart|status|doctor" >&2
    exit 2
    ;;
esac

shift || true
ansible-playbook -i "$root/ansible/hosts.yml" "$root/ansible/site.yml" --limit server --tags "$tag" "$@"

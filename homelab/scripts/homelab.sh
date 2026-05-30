#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
homelab_dir="$(cd "$script_dir/.." && pwd)"
playbook="$homelab_dir/ansible/playbooks/homelab.yml"
command_name="${1:-start}"

case "$command_name" in
  help|-h|--help)
    cat <<USAGE
Usage: $script_dir/homelab.sh [command]

Environment:
  HOMELAB_DRY_RUN=1  Run the Ansible lifecycle playbook in check mode
  DOTFILES_DRY_RUN=1 Alias for HOMELAB_DRY_RUN compatibility

Commands:
  start     Start Pi-hole rootful and rootless apps (default)
  stop      Stop rootless apps and Pi-hole
  restart   Stop, then start the homelab stack
  status    Show rootless and rootful container status
  doctor    Validate tools, env, and app inventory (legacy Python command)
  pihole    Start/configure only rootful Pi-hole
  nginx     Apply homelab nginx reverse-proxy config (legacy Python command)
  help      Show this help
USAGE
    exit 0
    ;;
  doctor|nginx)
    export PYTHONDONTWRITEBYTECODE=1
    exec python3 "$script_dir/homelab.py" "$command_name" "${@:2}"
    ;;
  start|stop|restart|status|pihole)
    ;;
  *)
    echo "Unknown homelab command: $command_name" >&2
    exit 2
    ;;
esac

if ! command -v ansible-playbook >/dev/null 2>&1; then
  echo "ansible-playbook is required for homelab lifecycle commands. Run homelab/scripts/install-server.sh or install Ansible." >&2
  exit 1
fi

ansible_args=("$playbook" --extra-vars "homelab_action=$command_name")
if [[ "${HOMELAB_DRY_RUN:-${DOTFILES_DRY_RUN:-}}" =~ ^(1|true|yes|on)$ ]]; then
  echo "Running homelab command in dry-run mode..."
  ansible_args+=(--check)
fi

exec ansible-playbook "${ansible_args[@]}"

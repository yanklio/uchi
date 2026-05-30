#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
homelab_dir="$(cd "$script_dir/.." && pwd)"
lifecycle_playbook="$homelab_dir/ansible/homelab.yml"
nginx_playbook="$homelab_dir/ansible/site.yml"
command_name="${1:-start}"

usage() {
  cat <<USAGE
Usage: $script_dir/homelab.sh [command]

Environment:
  HOMELAB_DRY_RUN=1  Run Ansible in check mode
  DOTFILES_DRY_RUN=1 Alias for HOMELAB_DRY_RUN compatibility

Commands:
  start     Start Pi-hole rootful and rootless apps (default)
  stop      Stop rootless apps and Pi-hole
  restart   Stop, then start the homelab stack
  status    Show rootless and rootful container status
  pihole    Start/configure only rootful Pi-hole
  nginx     Apply homelab nginx reverse-proxy config
  help      Show this help
USAGE
}

if [[ "$command_name" == "help" || "$command_name" == "-h" || "$command_name" == "--help" ]]; then
  usage
  exit 0
fi

if ! command -v ansible-playbook >/dev/null 2>&1; then
  echo "ansible-playbook is required for homelab commands. Run homelab/scripts/install-server.sh or install Ansible." >&2
  exit 1
fi

ansible_args=()
if [[ "${HOMELAB_DRY_RUN:-${DOTFILES_DRY_RUN:-}}" =~ ^(1|true|yes|on)$ ]]; then
  echo "Running homelab command in dry-run mode..."
  ansible_args+=(--check)
fi

case "$command_name" in
  start|stop|restart|status|pihole)
    exec ansible-playbook "$lifecycle_playbook" --extra-vars "homelab_action=$command_name" "${ansible_args[@]}"
    ;;
  nginx)
    exec ansible-playbook -i localhost, "$nginx_playbook" "${ansible_args[@]}"
    ;;
  *)
    echo "Unknown homelab command: $command_name" >&2
    usage >&2
    exit 2
    ;;
esac

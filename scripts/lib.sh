#!/usr/bin/env bash

have() {
  command -v "$1" >/dev/null 2>&1
}

die() {
  echo "$*" >&2
  exit 1
}

require_command() {
  local command="$1"
  local hint="${2:-$command is required}"

  have "$command" || die "$hint"
}

run_ansible() {
  local root="$1"
  local limit="$2"
  shift 2

  ansible-playbook -i "$root/ansible/hosts.yml" "$root/ansible/site.yml" --limit "$limit" "$@"
}

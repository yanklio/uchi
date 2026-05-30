# Agent Notes

## Repository Shape

- This repository root is `~/Dotfiles`.
- Ansible is the main setup system for both workstation and server setup.
- Dotfiles live in `home/` and are copied into `$HOME` by `ansible/tasks/common.yml`.
- Homelab server/container config lives in `homelab/`.
- Keep the repo small: no Ansible roles, Galaxy dependencies, Vault, or enterprise-style nesting.

## Ansible Flow

- Main playbook: `ansible/site.yml`.
- Inventory: `ansible/hosts.yml` with `workstation` and `server` groups.
- Variables: `ansible/vars.yml`.
- Task files live in `ansible/tasks/`.
- Templates live in `ansible/templates/`.

## Homelab

- Container app definitions live in `homelab/apps/<name>/docker-compose.yml`.
- Container lifecycle goes through `homelab/scripts/homelab.sh`.
- Ansible container tags should call the homelab CLI, not duplicate compose logic.
- Server setup must not auto-start containers.
- `DHCP_ACTIVE` defaults to `false` and `HOMELAB_ACCESS_MODE` defaults to `tailscale-only`.

## Verification

- Run all repository checks with: `scripts/check.sh`.
- If diagnosing manually, check shell syntax with: `bash -n scripts/*.sh homelab/scripts/*.sh`.
- Check Ansible syntax with: `ansible-playbook -i ansible/hosts.yml ansible/site.yml --syntax-check`.

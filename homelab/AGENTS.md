# Agent Notes

## Repository Shape
- This directory is intentionally separate from chezmoi-managed dotfiles.
- Container app definitions live in `apps/<name>/docker-compose.yml`.
- Host service config lives in `services/`; nginx config is applied by the `nginx` Ansible role via `homelab/scripts/homelab.sh nginx` or `ansible/site.yml`.
- Runtime state and secrets belong in ignored paths, especially `homelab/.env` and Pi-hole data directories.

## Script Flow
- `scripts/install-server.sh` is a thin wrapper around `ansible/install-server.yml`.
- `scripts/homelab.sh` is a thin dispatcher for Ansible playbooks and roles.
- Keep homelab implementation in focused Ansible roles under `ansible/roles/`.
- Pi-hole runs rootful because DNS/DHCP require privileged host networking. Other apps run rootless.
- Keep `.env` handling centralized in Ansible role tasks; do not add new ad-hoc parsers.

## Verification
- Run repository checks from the root with `scripts/check.sh`.
- Check homelab shell syntax manually with `bash -n homelab/scripts/*.sh`.
- Use `HOMELAB_DRY_RUN=1 homelab/scripts/homelab.sh start` to inspect lifecycle commands without changing containers.
- Use `ansible-playbook --syntax-check homelab/ansible/homelab.yml` when checking Ansible manually.

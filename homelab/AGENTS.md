# Agent Notes

## Repository Shape

- Container app definitions live in `apps/<name>/docker-compose.yml`.
- Runtime state and secrets belong in ignored paths, especially `homelab/.env`, Pi-hole data directories, and Open WebUI data.
- Nginx is managed by the root Ansible playbook from `ansible/templates/nginx/homelab.conf.j2`.

## Script Flow

- `scripts/homelab.sh` is a thin Python dispatcher wrapper.
- Keep container lifecycle logic in `homelab/scripts/homelab.py`.
- Ansible should trigger the CLI through tags and should not duplicate container logic.
- Pi-hole DHCP must stay disabled unless explicitly configured.

## Verification

- Run repository checks from the root with `scripts/check.sh`.
- Check homelab shell syntax manually with `bash -n homelab/scripts/*.sh`.
- Use `HOMELAB_DRY_RUN=1 homelab/scripts/homelab.sh start` to inspect lifecycle commands without changing containers.

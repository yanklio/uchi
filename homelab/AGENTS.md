# Agent Notes

## Repository Shape
- This directory is intentionally separate from chezmoi-managed dotfiles.
- Container app definitions live in `apps/<name>/docker-compose.yml`.
- Host service config lives in `services/`; nginx config is applied by `homelab/scripts/homelab.sh nginx`.
- Runtime state and secrets belong in ignored paths, especially `homelab/.env` and Pi-hole data directories.

## Script Flow
- `scripts/homelab.sh` is a compatibility wrapper. Keep implementation in focused Python modules under `scripts/lib/`.
- `start-all.sh`, `stop-all.sh`, `restart-all.sh`, `status.sh`, and `start-pihole-rootful.sh` are compatibility wrappers only.
- Pi-hole runs rootful because DNS/DHCP require privileged host networking. Other apps run rootless.
- Keep `.env` handling centralized in `scripts/lib/env.py`; do not parse `.env` directly in new scripts.

## Verification
- Run repository checks from the root with `scripts/check.sh`.
- Check homelab shell syntax manually with `bash -n homelab/scripts/*.sh`.
- Use `HOMELAB_DRY_RUN=1 homelab/scripts/homelab.sh start` to inspect lifecycle commands without changing containers.

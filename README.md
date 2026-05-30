# Dotfiles

Simple Ansible-managed workstation and homelab setup.

## Layout

- `ansible/`: inventory, variables, playbook, tasks, and templates.
- `home/`: dotfiles copied into `$HOME` by Ansible.
- `homelab/apps/`: Podman Compose app definitions.
- `homelab/scripts/`: small homelab CLI used by Ansible container tags.
- `scripts/`: thin wrappers around Ansible.

Ansible is the main setup system for both workstation and server setup. There are no roles, Galaxy dependencies, Vault files, or deep task nesting.

## Workstation

```bash
./scripts/workstation.sh
```

## Server

```bash
./scripts/server.sh
```

Server setup installs packages, writes `homelab/.env`, manages nginx, enables nginx, checks Podman restart support, and runs `homelab/scripts/homelab.sh doctor`.

It does not start containers by default.

## Containers

```bash
./scripts/containers.sh start
./scripts/containers.sh restart
./scripts/containers.sh status
```

Container operations call the existing homelab CLI. Ansible only triggers `homelab/scripts/homelab.sh`; it does not duplicate compose logic.

## Validation

```bash
./scripts/check.sh
```

## Safety Defaults

- Nginx is managed by Ansible from `ansible/templates/nginx/homelab.conf.j2`.
- `HOMELAB_ACCESS_MODE=tailscale-only` is the safe default.
- `DHCP_ACTIVE=false` is the safe default.
- Pi-hole DHCP is only enabled if explicitly set in `ansible/vars.yml`.
- Container image tags are pinned through `ansible/vars.yml` and `homelab/.env`.

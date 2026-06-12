# Dotfiles

Simple Ansible-managed workstation and homelab setup.

## Layout

- `ansible/`: inventory, variables, playbook, tasks, and templates.
- `home/`: dotfiles copied into `$HOME` by Ansible.
- `homelab/apps/`: Podman Compose app definitions.
- `homelab/scripts/`: small homelab CLI used by Ansible container tags.
- `scripts/`: the small set of user entrypoints.

Ansible is the main setup system for both workstation and server setup. There are no roles, Galaxy dependencies, Vault files, or deep task nesting.

## Control Flow

User entrypoints live in `scripts/`. They call Ansible. Ansible applies machine state and calls the homelab CLI only for container lifecycle operations.

```text
scripts/workstation.sh -> ansible/site.yml -> workstation tasks
scripts/server.sh      -> ansible/site.yml -> server tasks
scripts/containers.sh  -> ansible/site.yml tags -> homelab/scripts/homelab.sh -> podman compose
```

The flow is intentionally one-way. `homelab/scripts/homelab.sh` never calls Ansible.

## Workstation

Fresh install or update clone:

```bash
./scripts/install.sh --target workstation
```

Run setup from an existing clone:

```bash
./scripts/workstation.sh
```

Common setup installs dotfiles, shell tooling, npm globals, Go tools, Oh My Zsh, and upstream tools such as Zed, Ollama, and Tailscale when missing. Workstation setup additionally adds Flathub and installs the configured Flatpak apps.

## Server

Fresh install or update clone:

```bash
./scripts/install.sh --target server
```

Run setup from an existing clone:

```bash
./scripts/server.sh
```

Server setup installs packages, writes `homelab/secrets/homelab.env`, links `homelab/.env` for compose compatibility, manages nginx, enables nginx, checks Podman restart support, and runs `homelab/scripts/homelab.sh doctor`.

It does not start containers by default.

## Containers

```bash
./scripts/containers.sh start
./scripts/containers.sh restart
./scripts/containers.sh recreate
./scripts/containers.sh status
./scripts/containers.sh urls
./scripts/containers.sh paths
```

Container operations go through Ansible tags, then Ansible calls the homelab CLI. Ansible does not duplicate compose logic.

App-specific maintenance commands use `app <name> <command>`:

```bash
./scripts/containers.sh app open-webui
./scripts/containers.sh app open-webui reset-data
```

`open-webui reset-data` is registered in `homelab/apps/open-webui/actions.py`. The homelab CLI loads app commands through `homelab/scripts/app_commands.py` and runs compose operations through `homelab/scripts/runtime.py`.

The command stops Open WebUI, moves `homelab/state/open-webui/data` to a timestamped backup directory, creates a fresh data directory, and starts Open WebUI again.

## Homelab State

Tracked Git files define configuration and orchestration. Runtime data and secrets live in stable ignored directories so external backup tools can back them up without understanding app internals:

```text
homelab/secrets/  # credentials and generated environment files
homelab/state/    # persistent app data, externally backed up
homelab/store/    # shared models, browser downloads, and heavyweight caches
homelab/backups/  # manual/export scratch space
```

External backup should include:

```text
homelab/secrets/
homelab/state/
```

`homelab/store/` is optional because it is intended for large reusable caches and model downloads.

After changing compose files or environment values, use `recreate` so containers pick up the new config:

```bash
./scripts/containers.sh recreate
```

When migrating from older app-local data folders, run once before recreating containers:

```bash
./scripts/containers.sh migrate-state
```

For external backup windows:

```bash
./scripts/containers.sh quiesce
# run external backup of homelab/secrets and homelab/state
./scripts/containers.sh resume
```

Recovery on a rebuilt server:

```bash
git clone <repo> ~/Dotfiles
cd ~/Dotfiles
./scripts/server.sh
# restore homelab/secrets and homelab/state with the external backup tool
./scripts/containers.sh doctor
./scripts/containers.sh recreate
./scripts/containers.sh urls
```

## Validation

```bash
./scripts/check.sh
```

## Safety Defaults

- Nginx is managed by Ansible from `ansible/templates/nginx/homelab.conf.j2`.
- `HOMELAB_ACCESS_MODE=tailscale-only` is the safe default.
- `DHCP_ACTIVE=false` is the safe default.
- Pi-hole DHCP is only enabled if explicitly set in `ansible/vars.yml`.
- Pi-hole is included in container operations, but DHCP stays disabled unless explicitly enabled.
- Container image tags are pinned through `ansible/vars.yml` and `homelab/secrets/homelab.env`.

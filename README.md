# Dotfiles

Personal Ansible dotfiles and homelab server roles.

## Layout

- `dot_roles/` - workstation and shell tooling roles
- `server_roles/` - server infrastructure and app roles
- `playbooks/site.yml` - apply the full workstation/server setup
- `playbooks/roles.yml` - run one role by tag
- `playbooks/control.yml` - start, stop, restart, or inspect service containers
- `inventory.yaml` - host inventory

## Common commands

```bash
ansible-playbook playbooks/site.yml
ansible-playbook playbooks/roles.yml --tags node
ansible-playbook playbooks/site.yml --tags server
ansible-playbook playbooks/control.yml -e control_action=status
ansible-playbook playbooks/control.yml -e control_action=restart -e control_app=hermes
```

## Server

The `_server` base role configures Tailscale, Podman, nginx, Cockpit, and a private
`~/share` SFTP file-drop directory. Cockpit listens on port `9090` through
Tailscale only.

Hermes is currently the only managed container app. Its compose file is written to
`~/serve/apps/hermes`; state is stored under `~/serve/state`, and shared caches
under `~/serve/store`.

A full `site.yml` run starts Hermes only. Use `playbooks/control.yml` for manual
container lifecycle operations.

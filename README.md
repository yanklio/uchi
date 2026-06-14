# Dotfiles

Personal Ansible dotfiles and homelab server roles.

## Layout

- `dot_roles/` - workstation and shell tooling roles
- `server_roles/` - homelab service roles
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
ansible-playbook playbooks/control.yml -e control_action=up -e control_app=glance
```

## Server apps

- app compose files are written under `~/serve/apps/<app>`
- app state is stored under `~/serve/state`
- shared caches and model stores are under `~/serve/store`
- nginx service configs are written to `/etc/nginx/conf.d`

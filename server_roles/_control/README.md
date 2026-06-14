# _control

- controls Podman Compose apps in `~/serve/apps`
- supports `status`, `up`, `down`, and `restart`
- targets all app directories by default
- set `control_app=<name>` to target one app

```bash
ansible-playbook playbooks/control.yml -e control_action=status
ansible-playbook playbooks/control.yml -e control_action=restart -e control_app=glance
```

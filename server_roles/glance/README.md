# glance

- writes Glance config and Podman Compose file to `~/serve/apps/glance`
- stores dashboard config in `glance.yml`
- proxies through nginx
- listens on `80` and `8080` by default
- backend container port is bound to `127.0.0.1:18080`

```bash
ansible-playbook playbooks/site.yml --tags glance
ansible-playbook playbooks/control.yml -e control_action=up -e control_app=glance
```

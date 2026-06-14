# hermes

- writes Hermes Podman Compose file to `~/serve/apps/hermes`
- runs `hermes gateway run`
- gateway binds to `127.0.0.1:18642` by default
- dashboard binds to `0.0.0.0:9119` by default
- sets `HERMES_DASHBOARD_INSECURE=1` unless overridden
- optional nginx mode proxies public `9119` to private backend `19119`

```bash
ansible-playbook playbooks/site.yml --tags hermes
ansible-playbook playbooks/control.yml -e control_action=restart -e control_app=hermes
```

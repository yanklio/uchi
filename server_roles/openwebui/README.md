# openwebui

- writes Open WebUI Podman Compose file to `~/serve/apps/open-webui`
- runs with host networking
- app binds to `127.0.0.1:13000` by default
- proxies through nginx on port `3000`
- defaults to Ollama at `http://127.0.0.1:11434`

```bash
ansible-playbook playbooks/site.yml --tags openwebui
ansible-playbook playbooks/control.yml -e control_action=up -e control_app=open-webui
```

# AGENTS

- Keep role documentation short and practical, matching existing `dot_roles/*/README.md` style.
- Prefer `rg` for searches and inspect role defaults/templates before changing behavior.
- Do not revert unrelated user changes in this repository.
- For manual edits, use `apply_patch`.
- Run `ANSIBLE_LOCAL_TEMP=/tmp/ansible-local TMPDIR=/tmp ansible-playbook --syntax-check playbooks/site.yml` after Ansible role changes when possible.
- Server app roles should write compose files into `{{ <role>_app_dir }}/apps/<app>` and leave lifecycle operations to `server_roles/_control`.
- Keep only commonly overridden values in role defaults and document externally reachable ports in each server role README.

# _server

Base server role:

- installs and configures Tailscale, Podman, nginx, and Cockpit through role dependencies
- disables sleep, suspend, and hibernation
- creates `~/share` as a private SFTP file-drop directory

Upload a file over the existing SSH connection:

```bash
sftp gmk-de
put archive.zip share/
```

Override `server_file_drop_dir` to use another path.

Cockpit is available on port `9090` through Tailscale only.

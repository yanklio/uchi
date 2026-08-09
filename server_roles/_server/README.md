# _server

- disables sleep, suspend, and hibernation on server hosts

## Headless networking

Create Wi-Fi connections from root's NetworkManager UI so they are available before
user login:

```bash
sudo nmtui
nmcli -g connection.permissions,connection.autoconnect,802-11-wireless-security.psk-flags connection show "<profile>"
```

A boot-ready profile reports empty permissions, `yes`, and `0` respectively. Wired
Ethernet is preferred for unattended servers.

## Text-mode boot

```bash
sudo systemctl set-default multi-user.target
sudo systemctl enable --now getty@tty1.service
sudo systemctl disable lightdm
```

Start the graphical login only when needed with `sudo systemctl start lightdm`. Restore
graphical boot with `sudo systemctl set-default graphical.target` and
`sudo systemctl enable lightdm`.

After reboot, do not log in locally; verify `tailscale ping gmk-de`, SSH, and Cockpit
at `https://<tailscale-ip>:9090` from another Tailscale device.

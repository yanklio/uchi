from .common import have, is_gnome, run


def apply_gnome_settings() -> None:
    if not have("gsettings") or not is_gnome():
        return

    print("Applying GNOME settings...")
    run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "close", "['<Super>w']"])
    run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "maximize", "['<Super>Up']"])
    run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "begin-resize", "['<Super>BackSpace']"])
    run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "toggle-fullscreen", "['<Shift>F11']"])
    run(["gsettings", "set", "org.gnome.mutter", "dynamic-workspaces", "false"])
    run(["gsettings", "set", "org.gnome.desktop.wm.preferences", "num-workspaces", "6"])

    for i in range(1, 10):
        run(["gsettings", "set", "org.gnome.shell.keybindings", f"switch-to-application-{i}", f"['<Alt>{i}']"])

    for i in range(1, 7):
        run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", f"switch-to-workspace-{i}", f"['<Super>{i}']"])

import importlib.util
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from runtime import APPS_DIR, app_dir, require_podman_compose, run_app_action

AppAction = Callable[[str, str, dict[str, str]], int]
AppCommand = Callable[["AppCommandContext"], int]


@dataclass(frozen=True)
class AppCommandContext:
    app: str
    app_dir: Path
    env: dict[str, str]
    run_app_action: AppAction


def actions_file_for(app: str) -> Path:
    return APPS_DIR / app / "actions.py"


def load_actions_module(app: str) -> ModuleType | None:
    actions_file = actions_file_for(app)
    if not actions_file.exists():
        return None

    module_name = f"homelab_app_actions_{app.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, actions_file)
    if spec is None or spec.loader is None:
        print(f"failed to load app actions: {actions_file}", file=sys.stderr)
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_app_commands(app: str) -> dict[str, AppCommand] | None:
    module = load_actions_module(app)
    if module is None:
        return None

    commands = getattr(module, "COMMANDS", None)
    if not isinstance(commands, dict):
        print(f"app actions must expose COMMANDS dict: {actions_file_for(app)}", file=sys.stderr)
        return None

    for name, command in commands.items():
        if not isinstance(name, str) or not callable(command):
            print(
                f"app command entries must be string names mapped to callables: {actions_file_for(app)}",
                file=sys.stderr,
            )
            return None
    return commands


def run_app_command(app: str, command: str, env: dict[str, str]) -> int:
    app_commands = load_app_commands(app)
    if not app_commands:
        print(f"no app commands registered for: {app}", file=sys.stderr)
        return 2
    if command in {"list", "help"}:
        print(f"Available commands for {app}:")
        for name in sorted(app_commands):
            print(f"  {name}")
        return 0
    handler = app_commands.get(command)
    if not handler:
        commands = ", ".join(sorted(app_commands))
        print(f"unknown command for {app}: {command}. Available: {commands}", file=sys.stderr)
        return 2
    if not require_podman_compose():
        return 1
    context = AppCommandContext(
        app=app,
        app_dir=app_dir(app),
        env=env,
        run_app_action=run_app_action,
    )
    return handler(context)

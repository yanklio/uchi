#!/usr/bin/env python3
import sys

from app_commands import run_app_command
from runtime import doctor, load_env, operate

VALID_ACTIONS = {
    "start",
    "stop",
    "restart",
    "recreate",
    "status",
    "doctor",
    "urls",
    "paths",
    "migrate-state",
    "quiesce",
    "resume",
}


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "app":
        if len(sys.argv) not in {3, 4}:
            print(f"Usage: {sys.argv[0]} app <app> [command]", file=sys.stderr)
            return 2
        env = load_env()
        command = sys.argv[3] if len(sys.argv) == 4 else "list"
        return run_app_command(sys.argv[2], command, env)
    if action not in VALID_ACTIONS:
        print(
            f"Usage: {sys.argv[0]} start|stop|restart|recreate|status|doctor|urls|paths|migrate-state|quiesce|resume|app <app> <command>",
            file=sys.stderr,
        )
        return 2
    env = load_env()
    if action == "doctor":
        return doctor(env)
    return operate(action, env)


if __name__ == "__main__":
    raise SystemExit(main())

from datetime import datetime

from app_commands import AppCommand, AppCommandContext


def reset_data(context: AppCommandContext) -> int:
    data_dir = context.app_dir / "data"
    backup_dir = context.app_dir / f"data.reset-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    status = context.run_app_action(context.app, "stop", context.env)
    if status != 0:
        return status

    if context.env.get("HOMELAB_DRY_RUN") == "1":
        print(f"+ mv {data_dir} {backup_dir}")
        print(f"+ mkdir -p {data_dir}")
    else:
        if data_dir.exists():
            data_dir.rename(backup_dir)
            print(f"Open WebUI data backed up to: {backup_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)

    return context.run_app_action(context.app, "start", context.env)


COMMANDS: dict[str, AppCommand] = {
    "reset-data": reset_data,
}

import subprocess

from app_commands import AppCommandContext


def setup(context: AppCommandContext) -> int:
    command = ["podman", "compose"]
    env_file = context.app_dir.parents[1] / ".env"
    if env_file.exists():
        command += ["--env-file", str(env_file)]
    command += ["run", "--rm", "hermes", "setup"]

    if context.env.get("HOMELAB_DRY_RUN") == "1":
        print("+", " ".join(command) + f" (cwd={context.app_dir})")
        return 0
    return subprocess.call(command, cwd=context.app_dir, env=context.env)


COMMANDS = {
    "setup": setup,
}

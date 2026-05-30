# Dotfiles

Managed with [chezmoi](https://www.chezmoi.io/).

## Quick Start

```bash
git clone https://github.com/yanklio/Dotfiles.git ~/Dotfiles
chezmoi init --source="$HOME/Dotfiles/chezmoi"
chezmoi apply
```

## Personal Data

Non-secret defaults live in `.chezmoidata.toml`. Override Git identity and optional secrets in `~/.config/chezmoi/chezmoi.toml` when needed:

```toml
[data.git]
  name = "Your Name"
  email = "you@example.com"

[data]
  wakatimeApiKey = "your-api-key-here"
```

`dot_gitconfig.tmpl` reads `data.git.*`.

`dot_config/zed/private_settings.json.tmpl` reads `data.wakatimeApiKey`.

`scripts/bootstrap.sh` reads `DOTFILES_GNOME_SETTINGS` from the environment. If unset, it auto-detects GNOME.

## Package Setup

Packages are managed separately from dotfiles in `scripts/packages/`.

Zsh uses `oh-my-zsh` with the `simple` theme, installed by `scripts/bootstrap.sh`.

Run the bootstrap manually:

```bash
./scripts/bootstrap.sh
```

Run selected sections when you do not need the full bootstrap:

```bash
./scripts/bootstrap.sh packages npm flatpak gnome
```

On a fresh Linux machine, the first-run installer stops after `chezmoi apply`. Run `scripts/bootstrap.sh` explicitly when package setup is needed.

`chezmoi apply` only manages dotfiles. Run `scripts/bootstrap.sh` manually when package lists, tools, services, or GNOME settings change.

The bootstrap shell script is a small wrapper around readable Python modules in `scripts/lib/`, detects available tools directly, and supports `DOTFILES_DRY_RUN=1`.

Package lists live in:

- `scripts/packages/system.txt`
- `scripts/packages/go.txt`
- `scripts/packages/npm.txt`
- `scripts/packages/flatpak.txt`
- `scripts/packages/upstream.txt`

`system.txt` uses `package|roles|package-managers`, where roles are `core`, `dev`, or `desktop`, and package managers are `all`, `dnf`, or `apt`.

Repository-only files such as `README.md`, `AGENTS.md`, `docs/`, and `scripts/` are excluded from chezmoi apply by `.chezmoiignore`.

## Npm Packages

CLI tools that are distributed via npm are installed separately into `~/.local`.

Current npm-installed tools:

- `@anthropic-ai/claude-code`
- `opencode-ai`

Run manually:

```bash
./scripts/bootstrap.sh
```

## Daily Use

```bash
# Preview what will change
chezmoi diff

# Apply changes
chezmoi apply

# Edit a managed file
chezmoi edit ~/.config/zsh/.zshrc

# Re-import a file you changed locally
chezmoi re-add ~/.config/zsh/.zshrc
```

## Optional: GNOME Settings

GNOME desktop tweaks are applied by `scripts/bootstrap.sh` when GNOME is detected:
```bash
./scripts/bootstrap.sh
```

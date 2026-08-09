# proton_pass

Reusable Proton Pass secret lookup for other roles. Include `get_secret` with:

- `proton_pass_item`: Proton Pass item title
- `proton_pass_vault`: vault containing the item
- `proton_pass_field`: field containing the secret

The retrieved value is exposed as `proton_pass_secret`.

`pass-cli` is installed by `install.sh` at `~/.local/bin/pass-cli`. Authenticate it
before running a consuming role; the lookup performs a safe authentication preflight.

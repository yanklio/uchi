# zed

- zed editor via curl|sh
- `~/.config/zed/settings.json`
- WakaTime API key loaded through `proton_pass` from the `secret` field of the
  `WakaTime` item in the `Dev` vault

An existing settings file is preserved; only its `api-key` value is replaced.

Override `zed_wakatime_pass_item`, `zed_wakatime_pass_vault`, or
`zed_wakatime_pass_field` when the secret uses a different item title, vault, or
field. Log in with `pass-cli` before running the role.

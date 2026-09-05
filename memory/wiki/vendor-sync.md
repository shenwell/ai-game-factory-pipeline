# Vendor sync

- Run `python scripts/vendor/sync-upstream.py` from repo root; updates `vendor/VENDOR.lock`.
- Do not hand-edit `vendor/` without a file in `vendor/patches/`.
- Kie-only `asset-gen` SKILL: `vendor/patches/asset-gen-SKILL-kie-only.md` applied on sync and init publish.
- After copy, sync strips hardcoded drive-letter defaults from `vendor/godogen/asset-gen/tools/kie_video.py` (project `.env` / `GODOGEN_ROOT`).

Local sources are **siblings of this repo**, not absolute Windows paths:

- `godogen` → `../godogen` or env `GODOGEN_ROOT`
- `godot_cli_control` → `../godot-cli-control` or env `GODOT_CLI_CONTROL_ROOT`

Git sources: gamestudio (clone), game-design (sparse).

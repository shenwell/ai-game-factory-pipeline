# Vendor sync

- Run `python scripts/vendor/sync-upstream.py` from repo root; updates `vendor/VENDOR.lock`.
- Do not hand-edit `vendor/` without a file in `vendor/patches/`.
- Kie-only `asset-gen` SKILL: `vendor/patches/asset-gen-SKILL-kie-only.md` applied on sync and init publish.

Sources (local paths in sync script): godogen, gamestudio (git), game-design (sparse git), godot_cli_control (local).

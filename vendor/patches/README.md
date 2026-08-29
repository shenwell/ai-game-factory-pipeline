# Vendor patches

Applied by `python scripts/vendor/sync-upstream.py` after copy:

- `asset-gen-SKILL-kie-only.md` → `vendor/godogen/asset-gen/SKILL.md`
- `kie_video.py` drive-letter defaults → project `.env` / `GODOGEN_ROOT` (see `_patch_kie_video_env_paths`)

Init publishes skill to `.agents/skills/asset-gen/` — verify no `mcp-kv` in published copy.

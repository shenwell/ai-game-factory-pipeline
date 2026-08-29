# Kie assets (index)

Full recipe: `.agents/skills/asset-gen/SKILL.md` (vendored from godogen, Kie-only patches).

API: https://docs.kie.ai/

Key: `KIE_API_KEY` in project `.env`.

Python tools (in skill `tools/`):

- `asset_gen.py video` — image-to-video / text-to-video
- `asset_gen.py kie-status` — credits check
- `asset_gen.py t2i` — text-to-image via Kie REST
- `asset_gen.py i2i` — image-to-image via Kie REST

Factory client: `src/game_factory/assets/kie/client.py` — ledger sidecars, `unknown_submission` policy.

Do not use mcp-kv or MCP for images.

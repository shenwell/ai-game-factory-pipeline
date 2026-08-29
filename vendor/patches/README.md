# Kie-only patch notes for vendor/godogen/asset-gen/SKILL.md

After sync, apply manually or via future patch script:

- Remove mcp-kv, Gemini, xAI, Tripo3D sections
- Keep Kie video recipe and tools paths
- Point env to project `.env` only

Init publishes skill to `.agents/skills/asset-gen/` — verify no `mcp-kv` in published copy.

---
name: asset-gen
display_name: Asset Generator (Kie-only)
short_description: Generate game images and animated sprites via Kie.ai REST
default_prompt: "Use asset-gen skill to generate Kie images and videos for this game."
allow_implicit_invocation: true
description: |
  Kie.ai-only asset generation for ai-game-factory projects. Images via grok-imagine T2I/I2I;
  video via grok-imagine I2V. Auth: KIE_API_KEY in project `.env`. No MCP, Gemini, xAI, or Tripo3D.
---

# Asset Generator (Kie-only)

Tools live at `${ASSET_GEN_SKILL_DIR}/tools/`. Run from project root. Outputs under `${RUNTIME_ASSET_DIR}/`.

## Models (from game-factory.config.yaml)

| Capability | Default model |
|------------|---------------|
| Text-to-image | `grok-imagine/text-to-image` |
| Image-to-image | `grok-imagine/image-to-image` |
| Reference edit | `nano-banana-pro` |
| Image-to-video | `grok-imagine/image-to-video` |

Confirm spend before the first paid call. `kie-status` checks credits without generating.

## Images

```bash
python ${ASSET_GEN_SKILL_DIR}/tools/asset_gen.py t2i \
  --prompt "full prompt" -o ${RUNTIME_ASSET_DIR}/img/hero.png

python ${ASSET_GEN_SKILL_DIR}/tools/asset_gen.py i2i \
  --prompt "pose change only" --image ref.png -o ${RUNTIME_ASSET_DIR}/img/walk_pose.png
```

## Animated sprites

Recipe: **reference → pose (i2i) → video → frames → loop trim → rembg.**

```bash
python ${ASSET_GEN_SKILL_DIR}/tools/asset_gen.py video \
  --prompt "motion only" --image pose.png --duration 6 -o walk.mp4
```

Timeout after `createTask` is **not** a new job — use `resume`:

```bash
python ${ASSET_GEN_SKILL_DIR}/tools/asset_gen.py resume -o walk.mp4
```

Extract frames with ffmpeg; loop-trim with `tools/find_loop_frame.py`; matte with `tools/rembg_matting.py`.

See `docs/KIE-ASSETS.md` and factory Kie ledger in `.game-factory/jobs/kie-ledger.json`.

# 3D assets

- User-provided GLB: `assets/models/` (see `game-factory.config.yaml` → `assets.models_3d`).
- Blockout: procedural meshes in C# (Godot `MeshInstance3D`, `ArrayMesh`).
- Kie generates **2D references only**; no auto-rigging in v1.1.
- Gate `glb_import` runs on `factory verify full` when `project.dimension: 3d`.

Evidence: list imported GLB paths in task closure notes.

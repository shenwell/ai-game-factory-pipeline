from __future__ import annotations

"""Project-relative path helpers. Config and CLI output must not embed machine roots."""

from pathlib import Path


def relpath(root: Path, path: Path | str) -> str:
    """Return a POSIX path relative to *root*, or the original POSIX form if outside."""
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return candidate.as_posix()


def join_project(root: Path, maybe_rel: Path | str) -> Path:
    """Resolve a CLI/config path against the project root. Absolute inputs are kept."""
    path = Path(maybe_rel)
    if path.is_absolute():
        return path
    return root / path


def under_root(root: Path, rel: Path | str, *, name: str = "path") -> Path:
    """Join a config path that must stay inside the project (no drive-letter / UNC roots)."""
    path = Path(rel)
    if path.is_absolute():
        raise ValueError(f"{name} must be project-relative, got {rel!r}")
    return root / path

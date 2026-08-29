from __future__ import annotations

"""Free asset catalog search and provenance recording."""

import hashlib
import json
from pathlib import Path
from typing import Any

import requests

from game_factory.paths import relpath, under_root

ALLOWED_LICENSES = frozenset({"CC0", "CC-BY-4.0", "CC-BY-3.0", "MIT", "OGA-BY-3.0"})


def provenance_path(project_root: Path) -> Path:
    return project_root / ".game-factory" / "jobs" / "asset-provenance.jsonl"


def catalog_path(project_root: Path) -> Path:
    try:
        from game_factory.config import load_config

        rel = load_config(project_root).get("assets", {}).get("opensource", {}).get("catalog")
        if rel:
            return under_root(project_root, rel, name="assets.opensource.catalog")
    except Exception:
        pass
    installed = project_root / ".game-factory" / "vendor" / "asset-catalog" / "kenney-index.json"
    if installed.exists():
        return installed
    return project_root / "vendor" / "asset-catalog" / "kenney-index.json"


def load_catalog(project_root: Path) -> list[dict[str, Any]]:
    path = catalog_path(project_root)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def search_catalog(project_root: Path, query: str, license_filter: str | None = None) -> list[dict[str, Any]]:
    q = query.lower().strip()
    results = []
    for entry in load_catalog(project_root):
        if license_filter and entry.get("license") != license_filter:
            continue
        hay = f"{entry.get('title','')} {' '.join(entry.get('tags',[]))}".lower()
        if not q or q in hay:
            results.append(entry)
    return results


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record_provenance(project_root: Path, record: dict[str, Any]) -> None:
    path = provenance_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def import_url(
    project_root: Path,
    url: str,
    *,
    license_id: str,
    author: str,
    title: str,
    dest: Path,
) -> dict[str, Any]:
    if license_id not in ALLOWED_LICENSES:
        raise ValueError(f"License not allowed: {license_id}")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    data = resp.content
    checksum = _sha256_bytes(data)
    dest = dest if dest.is_absolute() else project_root / dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    record = {
        "url": url,
        "license": license_id,
        "author": author,
        "title": title,
        "checksum_sha256": checksum,
        "path": relpath(project_root, dest),
    }
    record_provenance(project_root, record)
    return record

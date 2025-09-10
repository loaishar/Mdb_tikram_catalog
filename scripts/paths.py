from paths import resolve_data, open_data
from __future__ import annotations

import os
from pathlib import Path
from typing import Union

# Repo root is one level up from this file
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

# Common subdirectories
SUBDIRS = {
    "batches_products": DATA_DIR / "batches" / "products",
    "batches_offers": DATA_DIR / "batches" / "offers",
    "batches_mongo": DATA_DIR / "batches" / "mongo",
    "batches_misc": DATA_DIR / "batches" / "misc",
    "imports": DATA_DIR / "imports",
    "imports_final": DATA_DIR / "imports" / "final",
    "imports_chunks": DATA_DIR / "imports" / "chunks",
    "imports_ready": DATA_DIR / "imports" / "ready",
    "updates_core": DATA_DIR / "updates" / "core",
    "updates_arabic": DATA_DIR / "updates" / "arabic",
    "status": DATA_DIR / "status",
    "mappings": DATA_DIR / "mappings",
    "tests": DATA_DIR / "tests",
    "raw": DATA_DIR / "raw",
}


def _map_basename(name: str) -> Path:
    """Map a bare filename to its directory under data/ based on naming patterns.

    Falls back to DATA_DIR if no pattern matches.
    """
    n = name
    # Imports core
    if n in {"all_products_import.json", "products_import.json", "offers_import.json", "mongodb_import_batch_1.json"}:
        return SUBDIRS["imports"] / n
    # Status
    if n in {"import_status.json", "offers_import_status.json"}:
        return SUBDIRS["status"] / n
    # Mappings / translations
    if n.startswith("product_id_mapping") or n.startswith("product_mapping"):
        return SUBDIRS["mappings"] / n
    if n.startswith("product_translations"):
        return SUBDIRS["mappings"] / n
    # Updates
    if n.startswith("mongodb_updates") or n.startswith("update_batch_"):
        return SUBDIRS["updates_core"] / n
    if n.startswith("arabic_update_batch_"):
        return SUBDIRS["updates_arabic"] / n
    # Batches
    if n.startswith("products_batch_"):
        return SUBDIRS["batches_products"] / n
    if n.startswith("offers_batch_") or n.startswith("processed_offers_batch_"):
        return SUBDIRS["batches_offers"] / n
    if n.startswith("mongo_batch_"):
        return SUBDIRS["batches_mongo"] / n
    if n == "batch_1_cleaned.json":
        return SUBDIRS["batches_misc"] / n
    # Imports variants
    if n.startswith("import_batch_final_"):
        return SUBDIRS["imports_final"] / n
    if n.startswith("import_chunk_"):
        return SUBDIRS["imports_chunks"] / n
    if n.startswith("ready_for_import_batch_"):
        return SUBDIRS["imports_ready"] / n
    # Tests
    if n.startswith("test_"):
        return SUBDIRS["tests"] / n
    # Raw Excel
    if n.endswith("_shufersal_with_images.xlsx"):
        return SUBDIRS["raw"] / n
    # Default: place directly under data/
    return DATA_DIR / n


def resolve_data(pathlike: Union[str, os.PathLike]) -> str:
    """Resolve a given filename or relative path to the organized data directory.

    - If path is absolute or already exists relative to ROOT_DIR, return as-is.
    - If it's a bare filename, map it to the appropriate data subfolder.
    - Ensure the parent directory exists when used for writing (handled in open_data).
    """
    p = Path(pathlike)
    # Absolute path: leave untouched
    if p.is_absolute():
        return str(p)
    # If given path already exists relative to repo root, keep it
    existing = ROOT_DIR / p
    if existing.exists():
        return str(existing)
    # If it's a simple name (no directory components), map by basename
    if len(p.parts) == 1:
        return str(_map_basename(p.name))
    # Otherwise, treat as relative to DATA_DIR
    return str(DATA_DIR / p)


def open_data(pathlike: Union[str, os.PathLike], mode: str = "r", *args, **kwargs):
    """Open a file under the repo's data directory, auto-creating parent dirs for writes."""
    resolved = Path(resolve_data(pathlike))
    if any(ch in mode for ch in ("w", "a", "+")):
        resolved.parent.mkdir(parents=True, exist_ok=True)
    return open(resolved, mode, *args, **kwargs)

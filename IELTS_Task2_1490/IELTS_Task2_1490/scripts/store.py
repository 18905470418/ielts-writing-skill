"""Tiny JSON item store for collected Task 2 essays."""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "data", "items")


def norm_band(raw: str) -> str | None:
    """Normalise a source-stated band label to a canonical string."""
    if not raw:
        return None
    m = re.search(r"(\d)(?:\.(\d))?", raw)
    if not m:
        return None
    whole, frac = m.group(1), m.group(2)
    return f"{whole}.{frac}" if frac is not None else f"{whole}.0"


def slugify(text: str, limit: int = 60) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:limit].strip("-") or "item"


def add(item: dict, source_key: str) -> str:
    """Write one item; filename is derived from source + a per-essay key.

    The key uses the source URL when present (falling back to the essay text)
    so that two different essays written on the same prompt never collide.
    """
    import hashlib

    os.makedirs(ITEMS, exist_ok=True)
    prompt = item.get("prompt", "")
    unique = "|".join(
        [
            str(item.get("source_url") or item.get("essay") or prompt),
            str(item.get("band_raw") or item.get("band") or ""),
        ]
    )
    h = hashlib.sha1((source_key + "|" + str(unique)).encode()).hexdigest()[:10]
    name = f"{source_key}__{slugify(prompt)}__{h}.json"
    path = os.path.join(ITEMS, name)
    with open(path, "w") as fh:
        json.dump(item, fh, ensure_ascii=False, indent=2)
    return path


def load_all() -> list[dict]:
    if not os.path.isdir(ITEMS):
        return []
    out = []
    for name in sorted(os.listdir(ITEMS)):
        if name.endswith(".json"):
            with open(os.path.join(ITEMS, name)) as fh:
                out.append(json.load(fh))
    return out


def remove_source(source_key: str) -> int:
    """Delete every stored item that belongs to one source key."""
    if not os.path.isdir(ITEMS):
        return 0
    removed = 0
    prefix = source_key + "__"
    for name in os.listdir(ITEMS):
        if name.startswith(prefix) and name.endswith(".json"):
            os.remove(os.path.join(ITEMS, name))
            removed += 1
    return removed

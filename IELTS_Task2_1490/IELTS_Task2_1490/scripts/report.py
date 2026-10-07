#!/usr/bin/env python3
"""Summarise collected items: counts by band, by source, duplicate prompts."""
from __future__ import annotations

import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import load_all  # noqa: E402


def norm_prompt(p: str) -> str:
    p = p.lower()
    p = re.sub(r"[^a-z0-9 ]+", " ", p)
    p = re.sub(r"\s+", " ", p).strip()
    return p


def main() -> int:
    items = load_all()
    print(f"total items: {len(items)}")
    print("\nby band:")
    for band, n in sorted(Counter(i.get("band") for i in items).items(), key=lambda kv: str(kv[0])):
        print(f"  {band}: {n}")
    print("\nby source:")
    for src, n in Counter(i.get("source_name") for i in items).most_common():
        print(f"  {src}: {n}")

    by_source_band: dict[str, Counter] = defaultdict(Counter)
    for i in items:
        by_source_band[i.get("source_name")][i.get("band")] += 1
    print("\nsource x band:")
    for src, c in by_source_band.items():
        print(f"  {src}: " + ", ".join(f"{b}={n}" for b, n in sorted(c.items(), key=lambda kv: str(kv[0]))))

    # duplicate prompts
    groups: dict[str, list[dict]] = defaultdict(list)
    for i in items:
        groups[norm_prompt(i.get("prompt", ""))].append(i)
    dupes = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"\nunique prompts: {len(groups)}   prompts with >1 essay: {len(dupes)}")

    # short essays
    short = [i for i in items if len((i.get("essay") or "").split()) < 120]
    print(f"essays under 120 words: {len(short)}")
    for i in short[:10]:
        print(f"  {i.get('source_name')} {i.get('band')} {len(i.get('essay','').split())}w :: {i.get('prompt','')[:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

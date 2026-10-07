"""Print full essays by id (reading aid for L1/L2 authoring)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import load_enriched  # noqa: E402


def main() -> None:
    ids = sys.argv[1:]
    byid = {r["id"]: r for r in load_enriched()}
    for rid in ids:
        r = byid.get(rid)
        if not r:
            print(f"!! {rid} not found")
            continue
        print("=" * 100)
        print(f"{r['id']} | band {r['band']} | {r['task_type_effective']} | {r['topic']} | {r['source']} | {r['word_count']} words")
        print("Q:", r["question"])
        print("-" * 100)
        print(r["essay"])
        print()


if __name__ == "__main__":
    main()

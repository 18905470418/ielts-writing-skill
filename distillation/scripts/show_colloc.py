"""Print mined collocations for a topic (inspection aid)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "topic-collocations.json"


def main() -> None:
    topics = sys.argv[1:] or ["media", "government", "culture"]
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for t in topics:
        rows = data["topics"].get(t, [])
        print(f"===== {t}: {len(rows)}")
        for r in rows[:40]:
            ex = r["examples"][0]
            print(f"  {r['docs']}d  {r['gram']!r}   [{ex[0]}/{ex[1]}] {ex[2][:120]}")
    print("===== generic")
    for r in data["generic"][:20]:
        ex = r["examples"][0]
        print(f"  {r['docs']}d  {r['gram']!r}   [{ex[0]}] {ex[2][:100]}")


if __name__ == "__main__":
    main()

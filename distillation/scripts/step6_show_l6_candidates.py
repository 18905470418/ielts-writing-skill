"""Compact listing of mined collocations for L6 curation."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "topic-collocations.json"
TOPICS = [
    "education",
    "technology",
    "environment",
    "government",
    "social",
    "crime",
    "culture",
    "health",
    "media",
    "globalization-work",
]


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for t in TOPICS:
        rows = data["topics"].get(t, [])
        print(f"\n===== {t} ({len(rows)})")
        for r in rows[:30]:
            ex = r["examples"][0]
            sent = ex[2].strip()
            m = re.search(r"(?<![a-z])" + re.escape(r["gram"]).replace(r"\\ ", r"\\s+") + r"(?![a-z])", sent, re.I)
            snippet = sent[:110]
            print(f"  [{r['docs']}d] {r['gram']!r} <- {ex[0]}/{ex[1]} | {snippet}")


if __name__ == "__main__":
    main()

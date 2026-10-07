"""Check candidate collocations across band>=8 essays (doc counts + example source)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import load_enriched, short_quote  # noqa: E402


def main() -> None:
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"] and r["band"] >= 8.0]
    phrases = sys.argv[1:]
    for p in phrases:
        pat = r"(?<![a-z])" + re.escape(p).replace(r"\ ", r"\s+") + r"(?![a-z])"
        hits = []
        for r in recs:
            m = re.search(pat, r["essay"], re.I)
            if m:
                s = r["essay"]
                hits.append((r["id"], r["band"], r["topic"], short_quote(s[max(0, m.start() - 60) : m.end() + 100], 170)))
        print(f"===== {p!r}: {len(hits)} docs")
        for h in hits[:6]:
            print("   ", h[0], h[1], h[2], "|", h[3])


if __name__ == "__main__":
    main()

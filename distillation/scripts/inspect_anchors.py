"""Quality inspection for the generated anchor files."""
from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "ielts-writing-scorer" / "references" / "anchors"


def main() -> None:
    for name in ["opinion.md", "discussion.md", "adv-disadv.md", "report.md", "two-part.md"]:
        t = (BASE / name).read_text(encoding="utf-8")
        heads = re.findall(r"^### .+$", t, re.M)
        ids = re.findall(r"^### `(B[^`]+)`", t, re.M)
        dup = [i for i in set(ids) if ids.count(i) > 1]
        print(f"{name}: sections={len(heads)} essays={len(ids)} dups={dup}")
    target = sys.argv[1] if len(sys.argv) > 1 else "B9-OP-005"
    # per-band counts
    for name in ["opinion.md", "discussion.md", "adv-disadv.md", "report.md", "two-part.md"]:
        t = (BASE / name).read_text(encoding="utf-8")
        ids = re.findall(r"^### `(B[^`]+)`", t, re.M)
        counts = {}
        for i in ids:
            m = re.match(r"B(6|65|7|75|8|85|9)-", i)
            band = {"6": "6.0", "65": "6.5", "7": "7.0", "75": "7.5", "8": "8.0", "85": "8.5", "9": "9.0"}[m.group(1)]
            counts[band] = counts.get(band, 0) + 1
        print(f"{name}: per-band {dict(sorted(counts.items()))}")
    t = (BASE / "opinion.md").read_text(encoding="utf-8")
    i = t.find("### `" + target + "`")
    if i < 0:
        # fall back to the first essay block
        m = re.search(r"^### `B[^`]+`", t, re.M)
        if m:
            i = m.start()
    print("\n---- sample block:", target, "----\n")
    print(t[i : i + 4200] if i >= 0 else "not found")


if __name__ == "__main__":
    main()

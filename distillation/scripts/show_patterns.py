"""Print error-pattern statistics (inspection aid)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "error-pattern-stats.json"


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    meta, stats = d["meta"], d["stats"]
    print("mid", meta["mid_n"], "high", meta["high_n"])
    targets = sys.argv[1:]
    for pid, s in sorted(stats.items()):
        if targets and pid not in targets:
            continue
        print(f"{pid:32s} mid {s['in_mid']:4d} high {s['in_high']:4d}")
        for ex in s["examples"][:4]:
            print(f"    [{ex['id']} {ex['band']}] {ex['sentence'][:150]}")


if __name__ == "__main__":
    main()

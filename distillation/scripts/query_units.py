"""Query argument units for a topic (curation helper).

Usage:
  python distillation/scripts/query_units.py --topic education [--band 9] [--max 40]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import DATA_DIR, short_quote  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--band", type=float, default=None)
    ap.add_argument("--max", type=int, default=60)
    args = ap.parse_args()
    units = [json.loads(l) for l in (DATA_DIR / "units.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [u for u in units if u["topic"] == args.topic]
    if args.band is not None:
        rows = [u for u in rows if u["band"] >= args.band]
    print(f"# units: {len(rows)} (topic={args.topic}, band>={args.band})")
    for u in rows[: args.max]:
        print("=" * 90)
        print(f"{u['uid']} | {u['band']:g} | {u['task']} | {u['source']}")
        print("Q:", short_quote(u["question"], 150))
        for s in u["sentences"]:
            print(f"  [{s['tag']}] {short_quote(s['text'], 200)}")


if __name__ == "__main__":
    main()

"""Compact thesis/topic-sentence/conclusion digest for review."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import load_enriched, paragraphs, sentences, short_quote  # noqa: E402


def main() -> None:
    ids = sys.argv[1:]
    recs = {r["id"]: r for r in load_enriched()}
    for rid in ids:
        r = recs.get(rid)
        if not r:
            print("!!", rid, "not found")
            continue
        ps = paragraphs(r["essay"])
        print("=" * 90)
        print(f"{rid} | {r['band']:g} | {r['task_type_effective']} | {r['topic']} | {r['word_count']}w")
        print("Q:", short_quote(r["question"], 160))
        if ps:
            ss = sentences(ps[0])
            print("INTRO:", short_quote(ss[-1] if ss else "", 200))
        for p in ps[1:-1][:3]:
            ss = sentences(p)
            if ss:
                print("BODY-TS:", short_quote(ss[0], 190))
        if len(ps) > 1:
            ss = sentences(ps[-1])
            print("CONC:", short_quote(ss[-1] if ss else "", 180))


if __name__ == "__main__":
    main()

"""Quick reconnaissance over the training split only.

Never touches sample-library/blindtest/.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "sample-library" / "essays.train.jsonl"

BANDS = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]
TASKS = ["opinion", "discussion", "adv-disadv", "report", "two-part"]
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


def load() -> list[dict]:
    recs = []
    with TRAIN.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    assert all(r["split"] == "train" for r in recs), "non-train record found"
    return recs


def main() -> None:
    recs = load()
    print("train records:", len(recs))

    # duplicate detection
    by_essay = collections.Counter(r["essay"] for r in recs)
    dup_essay = [(k, v) for k, v in by_essay.items() if v > 1]
    print("duplicate essay texts (exact):", len(dup_essay), "extra copies:", sum(v - 1 for _, v in dup_essay))

    norm_q = collections.Counter(re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", r["question"].lower())).strip() for r in recs)
    dup_q = [(k, v) for k, v in norm_q.items() if v > 1]
    print("duplicate questions (exact normalized):", len(dup_q))

    # source reliability tiers
    src = collections.Counter(r["source"] for r in recs)
    print("sources:")
    for s, c in src.most_common():
        print(f"  {s}: {c}")

    print("band x source:")
    bs = collections.Counter((r["band"], r["source"]) for r in recs)
    for b in BANDS:
        row = ", ".join(f"{s}:{bs[(b, s)]}" for s in src if bs[(b, s)])
        print(f"  {b}: {row}")

    # train grid
    grid = collections.Counter((r["band"], r["task_type"]) for r in recs)
    print("train band x task:")
    for b in BANDS:
        print("  ", b, {t: grid[(b, t)] for t in TASKS})

    grid_t = collections.Counter((r["band"], r["topic"]) for r in recs)
    thin = []
    for b in BANDS:
        for t in TOPICS:
            c = grid_t[(b, t)]
            if c <= 2:
                thin.append((b, t, c))
    print("thin train topic cells (<=2):", thin)

    # flags
    flagged = [r for r in recs if r["flags"]]
    print("flagged:", [(r["id"], r["flags"]) for r in flagged])

    # weird characters
    weird = collections.Counter()
    for r in recs:
        for ch in r["essay"]:
            o = ord(ch)
            if o > 0x2500 and ch not in "\u2018\u2019\u201c\u201d\u2014\u2013\u2026":
                weird[ch] += 1
    print("unusual chars top:", weird.most_common(12))

    # classification sanity spot checks on question patterns
    mism = []
    for r in recs:
        q = r["question"].lower()
        tt = r["task_type"]
        if "discuss both" in q and tt != "discussion":
            mism.append((r["id"], tt, "discuss both", r["question"][:80]))
        if ("agree or disagree" in q or "to what extent" in q) and tt not in ("opinion",):
            mism.append((r["id"], tt, "agree/extent", r["question"][:80]))
    print("task-type sanity mismatches:", len(mism))
    for m in mism[:25]:
        print("   ", m)

    # source code counts of official subscores in train
    official = [r for r in recs if r["subscores"]]
    print("official subscores in train:", len(official))
    print("official sources:", collections.Counter(r["source"] for r in official))


if __name__ == "__main__":
    sys.exit(main())

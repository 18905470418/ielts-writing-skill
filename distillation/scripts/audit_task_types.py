"""Task-type audit over the training split (review aid for step 1).

Prints every record whose current label disagrees with an intent-based
reading of the question. The reviewed corrections are then frozen in
step1 (see task_type_fix.py).
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import load_train  # noqa: E402

DISCUSS = re.compile(r"discuss\s+both|both\s+(?:of\s+these\s+)?(?:views|sides|opinions)|discuss\s+the\s+(?:two|both)", re.I)
ADV_STRICT = re.compile(
    r"outweigh|advantages?.{0,60}disadvantages?|disadvantages?.{0,60}advantages?|"
    r"positive\s+or\s+negative\s+(?:development|trend|change|step)|"
    r"is\s+(?:this|it)\s+a\s+(?:positive|negative)\s+(?:development|trend|change|step)|"
    r"benefits?.{0,50}(?:drawbacks?|disadvantages?)",
    re.I,
)
OPINION_ASK = re.compile(
    r"agree\s+or\s+disagree|do\s+you\s+(?:agree|disagree)|to\s+what\s+extent|"
    r"what\s+is\s+your\s+(?:opinion|view)|do\s+you\s+think\s+(?:this|it)\s+is|"
    r"is\s+(?:this|it)\s+a\s+(?:good|bad|positive|negative)|what\s+do\s+you\s+think\s+of",
    re.I,
)
EVAL_ASK = re.compile(
    r"agree\s+or\s+disagree|do\s+you\s+(?:agree|disagree)|to\s+what\s+extent|"
    r"what\s+is\s+your\s+(?:opinion|view)|is\s+(?:this|it)\s+a\s+(?:good|bad|positive|negative)|"
    r"positive\s+or\s+negative\s+(?:development|trend|change)",
    re.I,
)
REPORT_ASK = re.compile(
    r"what\s+(?:are\s+)?(?:the\s+)?(?:main\s+)?(?:causes?|reasons?|problems?|effects?|impacts?|factors?)\b|"
    r"what\s+do\s+you\s+think\s+are\s+the\s+(?:causes?|reasons?|problems?|effects?|factors?)|"
    r"why\s+(?:is|are|do|does|has|have|did)\b|why\s+this\b|"
    r"what\s+(?:can|could)\s+be\s+done|what\s+(?:solutions?|measures?|steps?)\b|"
    r"how\s+(?:can|could|might)\s+\w+|what\s+problems?\b|how\s+to\b",
    re.I,
)


def intent_label(q: str) -> tuple[str, str]:
    """Return (label, reason) for the intent-based reading."""
    if DISCUSS.search(q):
        return "discussion", "discuss both"
    if ADV_STRICT.search(q):
        return "adv-disadv", "strict advantages/disadvantages signal"
    o = bool(OPINION_ASK.search(q))
    r = bool(REPORT_ASK.search(q))
    e = bool(EVAL_ASK.search(q))
    if o and r:
        return "two-part", "both opinion and report asks"
    if o:
        return "opinion", "opinion ask"
    if r:
        return "report", "report ask"
    return "opinion", "fallback"


def main() -> None:
    recs = load_train()
    diffs: dict[str, list[dict]] = collections.defaultdict(list)
    for rec in recs:
        if rec["flags"]:
            continue
        lab, why = intent_label(rec["question"])
        if lab != rec["task_type"]:
            diffs[(rec["task_type"], lab)].append({"rec": rec, "why": why})
    total = sum(len(v) for v in diffs.values())
    print(f"records: {len(recs)}, disagreements: {total}")
    for (cur, new), rows in sorted(diffs.items(), key=lambda kv: -len(kv[1])):
        print(f"\n########## {cur} -> {new}: {len(rows)} ##########")
        for row in sorted(rows, key=lambda x: x["rec"]["id"])[:60]:
            rec = row["rec"]
            print(f"--- {rec['id']} | {rec['band']} | {row['why']}")
            print("   ", rec["question"][:240].replace("\n", " "))


if __name__ == "__main__":
    main()

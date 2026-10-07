#!/usr/bin/env python3
"""Flag collected items that look incomplete or contaminated."""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import load_all  # noqa: E402

BAD_ESSAY = re.compile(
    r"(Teacher.?s comment|Click here to see more|Pingback:|Leave a Reply|"
    r"\d+ thoughts on|This essay topic was seen|Save my name, email)",
    flags=re.I,
)
BAND_IN_ESSAY = re.compile(r"\bBand\s*\d(?:\.\d)?\b", flags=re.I)
TASK1 = re.compile(
    r"\b(chart|graph|table|diagram|map|process|bar chart|pie chart|line graph|"
    r"letter|write a letter)\b",
    flags=re.I,
)
GAP = re.compile(r"\s+[.,;]|\(\s*\)|\[\s*\]")


def main() -> int:
    items = load_all()
    problems = {"short": [], "contaminated": [], "band_mention": [], "task1": [], "gap": []}
    for i in items:
        essay = i.get("essay") or ""
        prompt = i.get("prompt") or ""
        words = len(essay.split())
        if words < 150:
            problems["short"].append(i)
        if BAD_ESSAY.search(essay):
            problems["contaminated"].append(i)
        if BAND_IN_ESSAY.search(essay):
            problems["band_mention"].append(i)
        if TASK1.search(prompt) and "letter" not in (i.get("question_type") or "").lower():
            problems["task1"].append(i)
        if GAP.search(essay):
            problems["gap"].append(i)

    for name, lst in problems.items():
        print(f"\n## {name}: {len(lst)}")
        for i in lst[:15]:
            print(f"  [{i.get('band')}] {i.get('source_name')} :: {i.get('prompt','')[:60]}")
            if name == "contaminated":
                m = BAD_ESSAY.search(i["essay"])
                print(f"      ...{i['essay'][max(0,m.start()-80):m.end()+40]!r}")
            if name == "gap":
                m = GAP.search(i["essay"])
                print(f"      ...{i['essay'][max(0,m.start()-80):m.end()+40]!r}")
            if name == "band_mention":
                m = BAND_IN_ESSAY.search(i["essay"])
                print(f"      ...{i['essay'][max(0,m.start()-80):m.end()+40]!r}")
    print(f"\ntotal items: {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

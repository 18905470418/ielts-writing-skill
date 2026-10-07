#!/usr/bin/env python3
"""Collect Task 2 samples from ielts.international (examiner-scored 6.0-8.0)."""
from __future__ import annotations

import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch  # noqa: E402
from store import add, norm_band, remove_source  # noqa: E402

URL = "https://www.ielts.international/ielts-sample-essays"
SOURCE = "ieltsinternational"
SOURCE_NAME = "IELTS International"


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    items = []
    for article in soup.find_all("article"):
        head = article.find("div", recursive=False)
        if not head:
            continue
        head_text = " ".join(head.get_text(" ", strip=True).split())
        m = re.match(r"^Band (\d+(?:\.\d)?)\s", head_text)
        if not m:
            continue
        band_raw = m.group(1)
        qtype = ""
        spans = head.find_all("span")
        if len(spans) >= 2:
            qtype = spans[1].get_text(" ", strip=True)

        qbox = article.find(
            "div", class_=lambda c: c and "rounded-xl" in c and "border-l-4" in c
        )
        prompt = ""
        if qbox:
            qdivs = qbox.find_all("div", recursive=False)
            if len(qdivs) >= 2:
                prompt = " ".join(qdivs[-1].get_text(" ", strip=True).split())

        essay_div = article.find("div", class_=lambda c: c and "space-y-4" in c)
        if not essay_div:
            continue
        paras = [
            " ".join(p.get_text(" ", strip=True).split())
            for p in essay_div.find_all(["p", "div"], recursive=False)
        ]
        paras = [p for p in paras if p]
        essay = "\n\n".join(paras)
        if not prompt or len(essay.split()) < 120:
            continue
        items.append(
            {
                "band": norm_band(band_raw),
                "band_raw": f"Band {band_raw}",
                "prompt": prompt,
                "essay": essay,
                "source_url": URL,
                "source_name": SOURCE_NAME,
                "question_type": qtype,
            }
        )
    return items


def main() -> int:
    removed = remove_source(SOURCE)
    if removed:
        print(f"cleared {removed} stale {SOURCE} items", file=sys.stderr)
    path = fetch(URL)
    if not path:
        print("fetch failed", file=sys.stderr)
        return 1
    html = open(path, encoding="utf-8", errors="ignore").read()
    items = parse(html)
    for item in items:
        add(item, SOURCE)
    print(f"collected {len(items)} essays", file=sys.stderr)
    for i in items:
        print(f"  {i['band']}  {i['prompt'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

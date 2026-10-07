#!/usr/bin/env python3
"""Collect Task 2 samples from cdieltsprep.com (each page: band 6.5 / 7.5 / 9)."""
from __future__ import annotations

import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch  # noqa: E402
from lib_rsc import find_json_objects, rsc_blob  # noqa: E402
from store import add, norm_band, remove_source  # noqa: E402

BASE = "https://www.cdieltsprep.com"
INDEX = BASE + "/writing-samples/task-2"
SOURCE = "cdieltsprep"
SOURCE_NAME = "CD IELTS Prep"


def task2_slugs() -> list[str]:
    path = fetch(INDEX)
    html = open(path, encoding="utf-8", errors="ignore").read()
    soup = BeautifulSoup(html, "lxml")
    slugs = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/writing-samples/") and not re.search(
            r"/writing-samples/(task-|letters)", href
        ):
            slugs.add(href.rsplit("/", 1)[-1])
    return sorted(slugs)


def parse_page(html: str, url: str) -> list[dict]:
    blob = rsc_blob(html)
    items = []
    for sample in find_json_objects(blob, "sample"):
        prompt = (sample.get("prompt") or "").strip()
        if not prompt or "task2" != sample.get("taskKind"):
            continue
        for version in sample.get("versions", []):
            band_raw = version.get("band")
            if band_raw is None:
                continue
            paragraphs = [p.strip() for p in version.get("paragraphs", []) if p and p.strip()]
            if not paragraphs:
                continue
            band = norm_band(str(band_raw))
            items.append(
                {
                    "band": band,
                    "band_raw": f"Band {band_raw}",
                    "prompt": prompt,
                    "essay": "\n\n".join(paragraphs),
                    "source_url": url,
                    "source_name": SOURCE_NAME,
                    "question_type": sample.get("questionType", ""),
                    "topic": sample.get("topic", ""),
                    "title": sample.get("title", ""),
                }
            )
    return items


def main() -> int:
    removed = remove_source(SOURCE)
    if removed:
        print(f"cleared {removed} stale {SOURCE} items", file=sys.stderr)
    slugs = task2_slugs()
    print(f"task-2 slugs: {len(slugs)}", file=sys.stderr)
    total = 0
    for slug in slugs:
        url = f"{BASE}/writing-samples/{slug}"
        path = fetch(url)
        if not path:
            continue
        html = open(path, encoding="utf-8", errors="ignore").read()
        items = parse_page(html, url)
        for item in items:
            add(item, SOURCE)
        total += len(items)
        print(f"{slug}\t{len(items)}")
    print(f"collected {total} essays", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

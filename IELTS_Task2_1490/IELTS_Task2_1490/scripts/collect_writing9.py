#!/usr/bin/env python3
"""Collect Task 2 essays from writing9.com band listings.

writing9 publishes user-submitted essays grouped by the band score its checker
awarded.  Each essay page carries a __NEXT_DATA__ JSON payload with the prompt,
the full essay text and the band number.

Usage:
  python scripts/collect_writing9.py --bands 6,7,8,9 --per-band 100
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch, fetch_many  # noqa: E402
from store import add, load_all, norm_band, remove_source  # noqa: E402

BASE = "https://writing9.com"
SOURCE = "writing9"
SOURCE_NAME = "writing9.com"

SKIP_QUESTION_TYPES = {"letter", "formal letter", "informal letter", "semi-formal letter"}


def listing_urls(band: str, page: int) -> str:
    return f"{BASE}/band/{band}/{page}"


def essay_links(band: str, page: int) -> list[str]:
    path = fetch(listing_urls(band, page))
    if not path:
        return []
    html = open(path, encoding="utf-8", errors="ignore").read()
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/text/"):
            out.append(BASE + href)
    # preserve order, drop duplicates
    return list(dict.fromkeys(out))


def parse_essay(html: str) -> dict | None:
    soup = BeautifulSoup(html, "lxml")
    script = None
    for s in soup.find_all("script", type="application/json"):
        t = s.string or ""
        if '"pageProps"' in t and '"text"' in t:
            script = t
            break
    if not script:
        return None
    try:
        data = json.loads(script)
    except json.JSONDecodeError:
        return None
    text = data.get("props", {}).get("pageProps", {}).get("text")
    if not isinstance(text, dict):
        return None
    return text


def essay_key(text: dict) -> str:
    import hashlib

    raw = (text.get("text") or "").strip().lower()
    return hashlib.sha1(raw.encode()).hexdigest()


def collect_band(
    band: str, want: int, max_pages: int = 200, existing: set[str] | None = None
) -> int:
    got = 0
    seen_ids: set[str] = set(existing or ())
    zero_streak = 0
    for page in range(max_pages):
        links = essay_links(band, page)
        if not links:
            break
        paths = fetch_many(links, workers=8)
        new_on_page = 0
        for url in links:
            if got >= want:
                break
            path = paths.get(url)
            if not path:
                continue
            html = open(path, encoding="utf-8", errors="ignore").read()
            text = parse_essay(html)
            if not text:
                continue
            eid = text.get("_id")
            if not eid or eid in seen_ids:
                continue
            if essay_key(text) in seen_ids:
                continue
            qtype = (text.get("questionType") or "").strip()
            if qtype.lower() in SKIP_QUESTION_TYPES:
                continue
            prompt = (text.get("question") or "").strip()
            essay = (text.get("text") or "").strip()
            band_val = text.get("band")
            if not prompt or not essay or band_val is None:
                continue
            if norm_band(str(band_val)) != norm_band(band):
                continue
            if len(essay.split()) < 150:
                continue
            seen_ids.add(eid)
            seen_ids.add(essay_key(text))
            item = {
                "band": norm_band(str(band_val)),
                "band_raw": f"Band {band_val}",
                "prompt": prompt,
                "essay": essay.replace("\r\n", "\n"),
                "source_url": url,
                "source_name": SOURCE_NAME,
                "question_type": qtype,
                "source_note": "Band score assigned by writing9.com's essay checker.",
            }
            add(item, SOURCE)
            got += 1
            new_on_page += 1
        print(f"  band {band} page {page}: +{new_on_page} (total {got})", file=sys.stderr)
        if got >= want:
            break
        # The listing is ordered newest-first, so the first pages are usually
        # already stored.  Only give up after a long run of pages that add
        # nothing new.
        zero_streak = zero_streak + 1 if new_on_page == 0 else 0
        if zero_streak >= 15:
            break
    return got


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bands", default="6,7,8,9")
    ap.add_argument("--per-band", type=int, default=100)
    ap.add_argument("--max-pages", type=int, default=200)
    ap.add_argument(
        "--targets",
        default=None,
        help="Per-band target counts, e.g. '6:174,6.5:138,8.5:199'. Overrides --bands/--per-band.",
    )
    ap.add_argument(
        "--clean", action="store_true", help="Delete this source's stored items first."
    )
    args = ap.parse_args()

    if args.clean:
        removed = remove_source(SOURCE)
        if removed:
            print(f"cleared {removed} stale {SOURCE} items", file=sys.stderr)

    existing: set[str] = set()
    for item in load_all():
        if item.get("source_name") != SOURCE_NAME:
            continue
        url = item.get("source_url") or ""
        if url:
            existing.add(url.rsplit("/", 1)[-1].split("-")[0])
        essay = (item.get("essay") or "").strip().lower()
        if essay:
            import hashlib

            existing.add(hashlib.sha1(essay.encode()).hexdigest())
    if existing:
        print(f"already stored {len(existing)} keys for {SOURCE_NAME}", file=sys.stderr)

    if args.targets:
        targets = []
        for chunk in args.targets.split(","):
            band, _, count = chunk.partition(":")
            targets.append((band.strip(), int(count)))
    else:
        targets = [(b.strip(), args.per_band) for b in args.bands.split(",")]

    total = 0
    for band, want in targets:
        print(f"collecting band {band} (want {want})", file=sys.stderr)
        got = collect_band(band, want, args.max_pages, existing)
        total += got
        print(f"band {band}: +{got}", file=sys.stderr)
    print(f"collected {total} essays", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

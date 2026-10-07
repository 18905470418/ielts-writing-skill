#!/usr/bin/env python3
"""Collect Task 2 samples from ieltswritingcorrectionservice.com.

Each sample page carries three answers (band 6.5 / 7.5 / 9.0) to one prompt.
"""
from __future__ import annotations

import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch  # noqa: E402
from store import add, norm_band, remove_source  # noqa: E402

BASE = "https://ieltswritingcorrectionservice.com"
INDEX = BASE + "/ielts-task-2-sample"
SOURCE = "iwcs"
SOURCE_NAME = "IELTS Writing Correction Service"


def sample_slugs() -> list[str]:
    path = fetch(INDEX)
    html = open(path, encoding="utf-8", errors="ignore").read()
    soup = BeautifulSoup(html, "lxml")
    slugs = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.match(r"^/ielts-task-2-sample-[a-z0-9-]+$", href):
            slugs.add(href.lstrip("/"))
    return sorted(slugs)


def extract_question(soup: BeautifulSoup) -> str:
    head = soup.find(
        ["h2", "h3"], string=re.compile(r"^\s*(?:The\s+)?(?:Task 2\s+)?(?:Exam\s+)?Question\s*$")
    )
    if not head:
        return ""
    container = head.find_parent("div", class_="page-shell-wide") or head.parent
    text = container.get_text("\n", strip=True)
    text = re.sub(r"^[^\n]*Question\s*", "", text, count=1)
    text = re.sub(r"^\s*Task 2\s*·[^\n]*\n", "", text)
    text = re.split(r"Give reasons for your answer|Write at least 250 words|Spend approximately", text)[0]
    text = text.strip().strip('"').strip()
    return " ".join(text.split())


def parse_page(html: str, url: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    question = extract_question(soup)
    items = []
    for h2 in soup.find_all("h2"):
        label = " ".join(h2.get_text(" ", strip=True).split())
        m = re.match(r"^Band (\d+(?:\.\d)?) (?:answer|response)$", label, flags=re.I)
        if not m:
            continue
        band_raw = m.group(1)
        section = h2.find_parent("div", class_="page-shell-wide")
        if not section:
            continue
        essay_div = None
        for child in section.find_all("div", recursive=False):
            text = " ".join(child.get_text(" ", strip=True).split())
            if len(text) < 400:
                continue
            if re.match(r"^(Examiner comment|Examiner commentary)", text, flags=re.I):
                continue
            essay_div = child
            break
        if essay_div is None:
            continue
        essay = essay_div.get_text("\n", strip=True)
        essay = re.sub(r"\n{2,}", "\n\n", essay).strip()
        if len(essay.split()) < 120:
            continue
        items.append(
            {
                "band": norm_band(band_raw),
                "band_raw": f"Band {band_raw}",
                "prompt": question,
                "essay": essay,
                "source_url": url,
                "source_name": SOURCE_NAME,
                "title": soup.h1.get_text(" ", strip=True) if soup.h1 else "",
            }
        )
    return items


def main() -> int:
    removed = remove_source(SOURCE)
    if removed:
        print(f"cleared {removed} stale {SOURCE} items", file=sys.stderr)
    slugs = sample_slugs()
    print(f"sample slugs: {len(slugs)} -> {slugs}", file=sys.stderr)
    total = 0
    for slug in slugs:
        url = f"{BASE}/{slug}"
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

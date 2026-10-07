#!/usr/bin/env python3
"""Collect Task 2 essays from ielts-blog.com band categories.

IELTS-Blog (Simone Braverman) publishes student essays marked by an IELTS
teacher, filed under Band 5-9 categories.  Each essay page carries the task
prompt and the full essay.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch, fetch_many  # noqa: E402
from store import add, remove_source  # noqa: E402

BASE = "https://www.ielts-blog.com"
CATEGORY = BASE + "/category/ielts-writing-samples/ielts-essays-band-%s/"
SOURCE = "ieltsblog"
SOURCE_NAME = "IELTS-Blog"


def category_links(band: str, max_pages: int) -> list[str]:
    base = CATEGORY % band
    first = fetch(base)
    if not first:
        return []
    soup = BeautifulSoup(open(first, encoding="utf-8", errors="ignore").read(), "lxml")
    last_page = 1
    for a in soup.find_all("a", href=True):
        m = re.search(rf"/ielts-essays-band-{band}/page/(\d+)/", a["href"])
        if m:
            last_page = max(last_page, int(m.group(1)))
    last_page = min(last_page, max_pages)
    urls = [base] + [f"{base}page/{p}/" for p in range(2, last_page + 1)]
    paths = fetch_many(urls, workers=8)

    links: list[str] = []
    seen: set[str] = set()
    for url in urls:
        path = paths.get(url)
        if not path:
            continue
        soup = BeautifulSoup(open(path, encoding="utf-8", errors="ignore").read(), "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if re.search(rf"/ielts-essays-band-{band}/[^/]+/$", href) and href not in seen:
                seen.add(href)
                links.append(href)
    return links


def parse_essay(html: str, url: str, band: str) -> dict | None:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    art = soup.find("article")
    if not art:
        return None

    # IELTS-Blog marks corrections with empty anchors plus a tooltip div that
    # carries the original wording in data-title.  Restore the original words
    # so the essay text stays verbatim.
    tippy = {}
    for d in art.find_all("div", class_="tippy"):
        anchor = (d.get("data-anchor") or "").lstrip("#")
        if anchor:
            tippy[anchor] = d.get("data-title") or ""
    if tippy:
        from bs4 import NavigableString

        for a in art.find_all("a", id=True):
            if a["id"] in tippy:
                a.replace_with(NavigableString(tippy[a["id"]]))
        for d in art.find_all("div", class_="tippy"):
            d.decompose()

    h1 = art.find("h1")
    prompt = ""
    if h1:
        prompt = " ".join(h1.get_text(" ", strip=True).split())
        prompt = re.sub(r"^IELTS Essay,?\s*topic:\s*", "", prompt, flags=re.I).strip()

    paras = [" ".join(p.get_text(" ", strip=True).split()) for p in art.find_all("p")]
    paras = [p for p in paras if p]

    cut_re = re.compile(
        r"^(Click here to see more|This is a good essay|Related posts|Share this|"
        r"Leave a Reply|Simone Braverman is the founder|\d+ thoughts on|Pingback:|"
        r"Teacher’s comment|Teacher's comment|Your email address will not be published|"
        r"Go here for more|No related posts|Save my name, email|Name \*|Email \*|"
        r"Comment \*|Website$)",
        flags=re.I,
    )
    band_comment_re = re.compile(r"\bBand\s*\d(?:\.\d)?\b", flags=re.I)
    essay_word_re = re.compile(r"\b(essay|answer|writing)\b", flags=re.I)
    label_re = re.compile(
        r"^(?:Download the\s+)?(?:(?:Sample|Model)\s+)?(?:Band \d+(?:\.\d)?\s+)?"
        r"(?:Essay|Answer|Response)(?:\s+here)?$",
        flags=re.I,
    )
    meta_re = re.compile(
        r"^(This essay was written on a topic from|This essay topic was seen|"
        r"This is a model response to a Writing Task 2 topic from|"
        r"You should spend about 40 minutes|Give reasons for your answer|"
        r"Write at least 250 words|Write about the following topic)",
        flags=re.I,
    )

    task_re = re.compile(
        r"(To what extent|Do you agree|Discuss both|Discuss\b|What are the|"
        r"advantages and disadvantages|What can we do|Is this a positive|"
        r"Do the advantages|What do you think|What are some|Give reasons for|"
        r"What is your opinion|What are its|Why do|How can|What problems|"
        r"What measures|What solutions|What caused|What are the reasons|"
        r"What do you think)",
        flags=re.I,
    )

    # 1. locate where the essay begins
    start: int | None = None
    label_idx: int | None = None
    for i, text in enumerate(paras):
        if label_re.match(text):
            start = i + 1
            label_idx = i
            break
    if start is None:
        k = 0
        while k < len(paras) and meta_re.match(paras[k]):
            k += 1
        short_title = len(prompt.split()) < 6
        looks_like_prompt = (
            k < len(paras)
            and k < 4
            and len(paras[k].split()) >= 8
            and (task_re.search(paras[k]) or paras[k].rstrip().endswith("?"))
        )
        if short_title and k < len(paras) and len(paras[k].split()) >= 6:
            # The page title is just a topic label; the printed task statement
            # is the paragraph that follows it.
            prompt = paras[k]
            start = k + 1
            while start < len(paras) and start < k + 3:
                text = paras[start]
                is_follow_on = (
                    meta_re.match(text)
                    or text.rstrip().endswith("?")
                    or (task_re.search(text) and len(text.split()) < 45)
                )
                if not is_follow_on:
                    break
                prompt = prompt + " " + text
                start += 1
        elif looks_like_prompt:
            start = k + 1
            prompt = paras[k]
        else:
            from difflib import SequenceMatcher

            best_i, best_r = None, 0.0
            target = prompt.lower()
            for i, text in enumerate(paras):
                r = SequenceMatcher(None, target, text.lower()).ratio()
                if r > best_r:
                    best_r, best_i = r, i
            if best_i is not None and best_r >= 0.45:
                start = best_i + 1
            else:
                start = k

    # Prefer the full task statement printed above a "Sample Essay" label.
    if label_idx is not None:
        collected: list[str] = []
        for j in range(label_idx - 1, -1, -1):
            text = paras[j]
            if meta_re.match(text) or label_re.match(text):
                break
            topic_prefix = re.match(r"^Write about the following topic:?\s*(.*)$", text, flags=re.I)
            if topic_prefix:
                body = topic_prefix.group(1).strip()
                if len(body.split()) >= 6:
                    collected.append(body)
                break
            if re.match(r"^(Give reasons for your answer|You should|Write at least 250 words)", text, flags=re.I):
                continue
            if re.match(r"^(Writing Task 2|Set \d)", text, flags=re.I):
                break
            if len(text.split()) >= 6:
                collected.append(text)
            if len(collected) >= 3:
                break
        if collected:
            candidate = " ".join(reversed(collected)).strip()
            if len(candidate.split()) > len(prompt.split()):
                prompt = candidate
    prompt = re.sub(r"^Write about the following topic:?\s*", "", prompt, flags=re.I).strip()
    prompt = re.split(
        r"\s*(?:You should write at least|You should spend about|"
        r"Give reasons for your answer|Write at least 250 words)",
        prompt,
    )[0].strip()

    # 2. locate where the essay ends (commentary / page furniture)
    end = len(paras)
    for i in range(start, len(paras)):
        text = paras[i]
        if cut_re.match(text) or (band_comment_re.search(text) and essay_word_re.search(text)):
            end = i
            break

    essay_paras = paras[start:end]

    # Drop leftover task-instruction lines and trailing examiner commentary.
    comment_re = re.compile(
        r"\b(essay|writing)\b.{0,200}\b(Band \d|writer|task response|coherence|"
        r"lexical|grammar|score|well-balanced|improvement)",
        flags=re.I,
    )
    cleaned: list[str] = []
    for text in essay_paras:
        if meta_re.match(text):
            continue
        cleaned.append(text)
    while cleaned and comment_re.search(cleaned[-1]):
        cleaned.pop()
    essay_paras = cleaned
    essay = "\n\n".join(essay_paras)
    if not prompt or len(essay.split()) < 120:
        return None
    return {
        "band": f"{band}.0",
        "band_raw": f"Band {band}",
        "prompt": prompt,
        "essay": essay,
        "source_url": url,
        "source_name": SOURCE_NAME,
        "source_note": "Essay marked by an IELTS teacher (IELTS-Blog).",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bands", default="6,7,8,9")
    ap.add_argument("--per-band", type=int, default=100)
    ap.add_argument("--max-pages", type=int, default=80)
    args = ap.parse_args()

    removed = remove_source(SOURCE)
    if removed:
        print(f"cleared {removed} stale {SOURCE} items", file=sys.stderr)
    for band in args.bands.split(","):
        band = band.strip()
        links = category_links(band, args.max_pages)
        print(f"band {band}: {len(links)} candidate links", file=sys.stderr)
        links = links[: args.per_band]
        paths = fetch_many(links, workers=8)
        got = 0
        for url in links:
            path = paths.get(url)
            if not path:
                continue
            html = open(path, encoding="utf-8", errors="ignore").read()
            item = parse_essay(html, url, band)
            if item:
                add(item, SOURCE)
                got += 1
        print(f"band {band}: stored {got}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

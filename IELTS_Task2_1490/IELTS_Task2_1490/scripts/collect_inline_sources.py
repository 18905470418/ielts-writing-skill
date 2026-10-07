#!/usr/bin/env python3
"""Collect Task 2 essays from pages that carry several band-labelled samples:
ieltsprepstudio.com, allthingsielts.com and bandnine.ai.
"""
from __future__ import annotations

import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch  # noqa: E402
from store import add, norm_band, remove_source  # noqa: E402

ANNOTATIONS = {"tr", "cc", "lr", "gra", "gr"}


def clean_paras(container, min_words: int = 120) -> str:
    for span in container.find_all("span"):
        if span.get_text(strip=True).lower() in ANNOTATIONS:
            span.decompose()
    blocks = container.find_all(["p", "li"], recursive=True)
    if not blocks:
        blocks = [container]
    paras = []
    for b in blocks:
        text = " ".join(b.get_text(" ", strip=True).split())
        if text:
            paras.append(text)
    essay = "\n\n".join(paras)
    return essay if len(essay.split()) >= min_words else ""


def collect_ieltsprepstudio() -> list[dict]:
    url = "https://www.ieltsprepstudio.com/blog/ielts-writing-task-2-sample-essays-band-8"
    path = fetch(url)
    if not path:
        return []
    soup = BeautifulSoup(open(path, encoding="utf-8", errors="ignore").read(), "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    article = soup.find("article")
    if not article:
        return []
    children = article.find_all(recursive=False)
    items = []
    for i, child in enumerate(children):
        if child.name != "h2":
            continue
        label = " ".join(child.get_text(" ", strip=True).split())
        m = re.match(r"^Essay \d+:\s*(.+)$", label)
        if not m:
            continue
        qtype = m.group(1).strip()
        qdiv = children[i + 1] if i + 1 < len(children) else None
        ediv = children[i + 2] if i + 2 < len(children) else None
        if not qdiv or not ediv:
            continue
        prompt = " ".join(qdiv.get_text(" ", strip=True).split())
        prompt = re.sub(r"^Question:\s*", "", prompt).strip().strip("“”\"")
        essay = clean_paras(ediv)
        if not prompt or not essay:
            continue
        items.append(
            {
                "band": "8.0",
                "band_raw": "Band 8",
                "prompt": prompt,
                "essay": essay,
                "source_url": url,
                "source_name": "IELTS Prep Studio",
                "question_type": qtype,
            }
        )
    return items


def collect_allthingsielts() -> list[dict]:
    url = "https://allthingsielts.com/ielts-writing/task-2-samples"
    path = fetch(url)
    if not path:
        return []
    soup = BeautifulSoup(open(path, encoding="utf-8", errors="ignore").read(), "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    items = []
    for card in soup.find_all("div", class_="card"):
        head = card.find("h3")
        body = card.find("div", class_="card-body")
        if not head or not body:
            continue
        m = re.search(r"\(Band\s*(\d+(?:\.\d)?)\)", head.get_text(" ", strip=True))
        if not m:
            continue
        band_raw = m.group(1)
        divs = body.find_all("div", recursive=False)
        if len(divs) < 2:
            continue
        prompt = re.sub(r"^Task:\s*", "", " ".join(divs[0].get_text(" ", strip=True).split()))
        essay = clean_paras(divs[1])
        if not prompt or not essay:
            continue
        items.append(
            {
                "band": norm_band(band_raw),
                "band_raw": f"Band {band_raw}",
                "prompt": prompt,
                "essay": essay,
                "source_url": url,
                "source_name": "AllThingsIELTS",
            }
        )
    return items


def collect_bandnine() -> list[dict]:
    url = "https://bandnine.ai/blog/ielts-writing-band-7-sample-essays-examiner-criteria"
    path = fetch(url)
    if not path:
        return []
    soup = BeautifulSoup(open(path, encoding="utf-8", errors="ignore").read(), "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    items = []
    # each Task 2 sample is preceded by an h3 "The prompt" and an h3 "Band N sample response"
    heads = soup.find_all("h3")
    for i, h in enumerate(heads):
        label = " ".join(h.get_text(" ", strip=True).split()).lstrip("# ").strip()
        if not re.match(r"^The prompt$", label, flags=re.I):
            continue
        resp = None
        for h2 in heads[i + 1 :]:
            l2 = " ".join(h2.get_text(" ", strip=True).split()).lstrip("# ").strip()
            if re.match(r"^Band (\d+(?:\.\d)?) sample response$", l2, flags=re.I):
                resp = h2
                break
            if re.match(r"^The prompt$", l2, flags=re.I):
                break
        if not resp:
            continue
        m = re.match(r"^Band (\d+(?:\.\d)?) sample response$", " ".join(resp.get_text(" ", strip=True).split()).lstrip("# ").strip(), flags=re.I)
        band_raw = m.group(1)
        # gather prompt paragraphs between h and resp
        prompt_parts = []
        node = h
        while True:
            node = node.find_next()
            if node is None or node is resp or (node.name == "h3" and node is not h):
                break
            if node.name in ("p", "blockquote") and node.get_text(strip=True):
                prompt_parts.append(" ".join(node.get_text(" ", strip=True).split()))
        prompt = " ".join(prompt_parts).strip().strip("“”\"")
        # essay paragraphs after resp until next h2/h3
        essay_parts = []
        node = resp
        while True:
            node = node.find_next()
            if node is None or node.name in ("h2", "h3"):
                break
            if node.name in ("p", "blockquote") and node.get_text(strip=True):
                essay_parts.append(" ".join(node.get_text(" ", strip=True).split()))
        essay = "\n\n".join(essay_parts)
        if not prompt or len(essay.split()) < 120:
            continue
        # only keep Task 2 (bandnine also shows a Task 1 sample)
        if "chart" in prompt.lower() or "graph" in prompt.lower():
            continue
        items.append(
            {
                "band": norm_band(band_raw),
                "band_raw": f"Band {band_raw}",
                "prompt": prompt,
                "essay": essay,
                "source_url": url,
                "source_name": "Band Nine",
            }
        )
    return items


COLLECTORS = {
    "ieltsprepstudio": collect_ieltsprepstudio,
    "allthingsielts": collect_allthingsielts,
    "bandnine": collect_bandnine,
}


def main() -> int:
    which = sys.argv[1:] or list(COLLECTORS)
    for key in which:
        fn = COLLECTORS.get(key)
        if not fn:
            print(f"unknown collector {key}", file=sys.stderr)
            continue
        removed = remove_source(key)
        if removed:
            print(f"cleared {removed} stale {key} items", file=sys.stderr)
        items = fn()
        for item in items:
            add(item, key)
        print(f"{key}: {len(items)} essays", file=sys.stderr)
        for i in items:
            print(f"  {i['band']}  {i['prompt'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

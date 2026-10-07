#!/usr/bin/env python3
"""Render the final Markdown collection from data/items.

Selects up to 200 essays per band (6.0 / 6.5 / 7.0 / 7.5 / 8.0 / 8.5 / 9.0),
de-duplicates by essay text, spreads the selection across sources and unique
prompts, then appends any remaining inventory, writing
output/ielts_task2_collection.md plus a JSON manifest and per-band index.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import load_all  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "output")

BANDS = ["6.0", "6.5", "7.0", "7.5", "8.0", "8.5", "9.0"]

# source_name -> priority (lower = preferred)
PRIORITY = {
    "IELTS-Blog": 0,
    "IELTS International": 1,
    "IELTS Prep Studio": 2,
    "AllThingsIELTS": 2,
    "Band Nine": 2,
    "CD IELTS Prep": 1,
    "IELTS Writing Correction Service": 1,
    "writing9.com": 9,
}


def norm_text(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def clean_prompt(p: str) -> str:
    """Strip source-side scaffolding that leaked into a few prompt strings."""
    p = " ".join((p or "").split())
    p = re.sub(r"^IELTS\s+(?:Band\s+\d+(?:\.\d)?\s+)?[Ee]ssay,?\s*topic:\s*", "", p)
    p = re.sub(r"^(?:Question|Task)\s*:\s*", "", p, flags=re.I)
    p = re.sub(r"^\d{1,2}\s*[.)]\s*", "", p)
    return p.strip()


TASK1_RE = re.compile(
    r"(the (?:bar|pie|line) chart|the (?:line )?graph|the diagram|the table|"
    r"the (?:two )?maps?\b|the chart below|the graph below|the diagram below|"
    r"write a letter|letter to (?:a|your) friend)",
    flags=re.I,
)


def is_task1(prompt: str) -> bool:
    """Guard against Task 1 material that slipped into a Task 2 listing."""
    return bool(TASK1_RE.search(prompt or ""))


def select(items: list[dict], per_band: int) -> dict[str, list[dict]]:
    chosen: dict[str, list[dict]] = {b: [] for b in BANDS}
    used_essays: set[str] = set()
    for band in BANDS:
        pool = [
            i
            for i in items
            if i.get("band") == band
            and len((i.get("prompt") or "").split()) >= 8
            and not is_task1(i.get("prompt") or "")
        ]
        by_source: dict[str, list[dict]] = defaultdict(list)
        for item in pool:
            by_source[item.get("source_name")].append(item)
        order = sorted(by_source, key=lambda s: PRIORITY.get(s, 5))
        queues = {s: list(by_source[s]) for s in order}
        deferred: list[dict] = []
        seen_prompts: set[str] = set()
        picked: list[dict] = []

        def take(item: dict) -> bool:
            ekey = norm_text(item.get("essay"))
            if not ekey or ekey in used_essays:
                return False
            used_essays.add(ekey)
            picked.append(item)
            return True

        # round 1: round-robin across sources, one unique prompt at a time
        progress = True
        while len(picked) < per_band and progress:
            progress = False
            for src in order:
                if len(picked) >= per_band:
                    break
                queue = queues[src]
                while queue:
                    item = queue.pop(0)
                    pkey = norm_text(item.get("prompt"))
                    if pkey in seen_prompts:
                        deferred.append(item)
                        continue
                    if take(item):
                        seen_prompts.add(pkey)
                        progress = True
                    break
        # round 2: allow repeated prompts, still unique essays
        remaining = [i for src in order for i in queues[src]] + deferred
        for item in remaining:
            if len(picked) >= per_band:
                break
            take(item)
        chosen[band] = picked
    return chosen


def collect_extras(items: list[dict], chosen: dict[str, list[dict]]) -> list[dict]:
    """Everything left in the store once the primary essays are picked."""
    used = {norm_text(i.get("essay")) for band in BANDS for i in chosen[band]}
    extras: list[dict] = []
    for band in BANDS:
        pool = [
            i
            for i in items
            if i.get("band") == band and not is_task1(i.get("prompt") or "")
        ]
        for item in pool:
            ekey = norm_text(item.get("essay"))
            if not ekey or ekey in used:
                continue
            used.add(ekey)
            extras.append(item)
    return extras


def entry_lines(item: dict, number: int) -> list[str]:
    return [
        f"## 第{number:03d}篇",
        "",
        "### 分数",
        "",
        f"Band {item.get('band')}",
        "",
        "### 题目",
        "",
        clean_prompt(item.get("prompt", "")),
        "",
        "### 文章",
        "",
        (item.get("essay") or "").strip(),
        "",
        "### 来源",
        "",
        (item.get("source_url") or "").strip(),
        "",
    ]


def render(chosen: dict[str, list[dict]], extras: list[dict]) -> str:
    lines: list[str] = []
    n = 0
    for band in BANDS:
        for item in chosen[band]:
            n += 1
            lines.extend(entry_lines(item, n))

    primary_counts = {b: len(chosen[b]) for b in BANDS}
    extra_counts = dict(Counter(i.get("band") for i in extras))
    total_counts: Counter = Counter()
    for band in BANDS:
        total_counts[band] += primary_counts[band]
    for band, count in extra_counts.items():
        total_counts[band] += count

    if extras:
        lines.append("# 额外库存")
        lines.append("")
        for item in extras:
            n += 1
            lines.extend(entry_lines(item, n))

    lines.append("```text")
    lines.append("【主体】")
    for b in BANDS:
        lines.append(f"Band {b}：{primary_counts[b]}篇")
    lines.append(f"小计：{sum(primary_counts.values())}篇")
    lines.append("")
    if extras:
        lines.append("【额外库存】")
        for b in BANDS:
            if extra_counts.get(b):
                lines.append(f"Band {b}：{extra_counts[b]}篇")
        lines.append(f"小计：{len(extras)}篇")
        lines.append("")
        lines.append("【合计】")
        for b in BANDS:
            if total_counts.get(b):
                lines.append(f"Band {b}：{total_counts[b]}篇")
    lines.append(f"总计：{n}篇")
    lines.append("```")
    return "\n".join(lines)


def write_index(
    chosen: dict[str, list[dict]], extras: list[dict], md_path: str, csv_path: str
) -> None:
    """Write a per-band index (Markdown table + CSV) of the whole corpus."""
    lines: list[str] = ["# IELTS Task 2 采集清单（按分数段）", ""]
    rows: list[tuple[int, str, str, str, str, int]] = []
    n = 0

    def add_band_section(title: str, items: list[dict]) -> None:
        nonlocal n
        if not items:
            return
        lines.append(f"## {title}（{len(items)} 篇）")
        lines.append("")
        lines.append("| 编号 | 题目 | 来源 |")
        lines.append("| --- | --- | --- |")
        for item in items:
            n += 1
            prompt = clean_prompt(item.get("prompt"))
            short = prompt if len(prompt) <= 120 else prompt[:119] + "…"
            lines.append(
                f"| {n:03d} | {short.replace('|', chr(92) + '|')} | {item.get('source_url', '')} |"
            )
            rows.append(
                (
                    n,
                    item.get("band", ""),
                    prompt,
                    item.get("source_url", ""),
                    item.get("source_name", ""),
                    len((item.get("essay") or "").split()),
                )
            )
        lines.append("")

    for band in BANDS:
        add_band_section(f"主体 · Band {band}", chosen[band])
    by_band_extras: dict[str, list[dict]] = defaultdict(list)
    for item in extras:
        by_band_extras[item.get("band")].append(item)
    for band in BANDS:
        add_band_section(f"额外库存 · Band {band}", by_band_extras.get(band, []))

    with open(md_path, "w") as fh:
        fh.write("\n".join(lines))
    with open(csv_path, "w") as fh:
        import csv as _csv

        writer = _csv.writer(fh)
        writer.writerow(["no", "band", "prompt", "source_url", "source_name", "word_count"])
        for no, band, prompt, url, src, wc in rows:
            writer.writerow([no, band, prompt, url, src, wc])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-band", type=int, default=200)
    ap.add_argument("--out", default=os.path.join(OUT_DIR, "ielts_task2_collection.md"))
    args = ap.parse_args()

    items = load_all()
    exact = [i for i in items if i.get("band") in BANDS]
    chosen = select(exact, args.per_band)
    extras = collect_extras(items, chosen)
    os.makedirs(OUT_DIR, exist_ok=True)
    md = render(chosen, extras)
    with open(args.out, "w") as fh:
        fh.write(md)
    write_index(
        chosen,
        extras,
        os.path.join(OUT_DIR, "index_by_band.md"),
        os.path.join(OUT_DIR, "index_by_band.csv"),
    )

    manifest = {
        "counts": {b: len(chosen[b]) for b in BANDS},
        "total": sum(len(v) for v in chosen.values()),
        "extras": dict(Counter(i.get("band") for i in extras)),
        "extras_total": len(extras),
        "grand_total": sum(len(v) for v in chosen.values()) + len(extras),
        "by_source": {
            b: dict(Counter(i.get("source_name") for i in chosen[b])) for b in BANDS
        },
        "available": dict(Counter(i.get("band") for i in exact)),
    }
    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

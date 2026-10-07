"""Semantic duplicate check for L5 entries and exact duplicate check for L6.

Writes reports/duplicate-check.md (informational; used by the manual audit).
"""
from __future__ import annotations

import collections
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import REFS_DIR, REPORT_DIR, STOPWORDS, content_tokens, short_quote, write_text  # noqa: E402


def parse_l5() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for p in sorted((REFS_DIR / "viewpoint-bank").glob("*.md")):
        entries = []
        for block in re.split(r"\n- \*\*\[", p.read_text(encoding="utf-8"))[1:]:
            code = block.split("]", 1)[0]
            claim_m = re.search(r"观点：(.*?)\*\*", block, re.S)
            chain_m = re.search(r"- 展开：(.+)", block)
            entries.append(
                {
                    "code": code,
                    "claim": (claim_m.group(1) if claim_m else "").strip(),
                    "chain": (chain_m.group(1) if chain_m else "").strip(),
                }
            )
        out[p.stem] = entries
    return out


def parse_l6() -> list[dict]:
    rows = []
    for p in sorted((REFS_DIR / "topic-vocab").glob("*.md")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| L6-"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 7:
                rows.append({"code": cells[0], "topic": p.stem, "gram": cells[1]})
    return rows


def main() -> None:
    l5 = parse_l5()
    l6 = parse_l6()
    lines = ["# 重复检查报告（L5 语义 / L6 精确）", ""]
    flag_pairs: list[tuple[float, str, str, dict, dict]] = []
    topic_flags: dict[str, int] = {}
    for topic, entries in l5.items():
        # IDF-weighted cosine over claim+chain content tokens
        vecs = []
        for e in entries:
            toks = [t for t in content_tokens(e["claim"] + " " + e["chain"]) if t not in STOPWORDS and len(t) > 2]
            vecs.append(collections.Counter(toks))
        df = collections.Counter()
        for c in vecs:
            df.update(c.keys())
        total = max(1, len(entries))
        norm_vecs = []
        for c in vecs:
            v = {t: (1 + math.log(n)) * math.log(total / (1 + df[t])) for t, n in c.items()}
            nrm = math.sqrt(sum(x * x for x in v.values())) or 1.0
            norm_vecs.append({t: x / nrm for t, x in v.items()})
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                inter = set(norm_vecs[i]) & set(norm_vecs[j])
                sim = sum(norm_vecs[i][t] * norm_vecs[j][t] for t in inter)
                if sim >= 0.55:
                    flag_pairs.append((sim, topic, f"{entries[i]['code']}~{entries[j]['code']}", entries[i], entries[j]))
                    topic_flags[topic] = topic_flags.get(topic, 0) + 1
    flag_pairs.sort(reverse=True)

    lines.append(f"- L5 条目合计 {sum(len(v) for v in l5.values())}；疑似重复对（相似度 ≥0.55）{len(flag_pairs)} 对。")
    lines.append(f"- L6 条目合计 {len(l6)}；精确重复词伙 {sum(c-1 for c in collections.Counter(r['gram'].lower() for r in l6).values() if c > 1)} 例。")
    lines.append("")
    lines.append("## 主题内 L5 疑似重复率（对数 / 条目数）")
    lines.append("")
    lines.append("| 主题 | 条目数 | 疑似重复对 | 比例 |")
    lines.append("|---|---:|---:|---:|")
    for topic, entries in l5.items():
        n = len(entries)
        f = topic_flags.get(topic, 0)
        lines.append(f"| {topic} | {n} | {f} | {(f/n if n else 0):.0%} |")
    lines.append("")
    lines.append("## 相似度最高的 20 对（供人工判定是否合并）")
    lines.append("")
    for sim, topic, codes, a, b in flag_pairs[:20]:
        lines.append(f"- **{sim:.2f}** [{topic}] `{codes}`")
        lines.append(f"  - A: {short_quote(a['claim'], 110)}")
        lines.append(f"  - B: {short_quote(b['claim'], 110)}")
    lines.append("")
    dup_grams = [g for g, c in collections.Counter(r["gram"].lower() for r in l6).items() if c > 1]
    lines.append("## L6 精确重复词伙")
    lines.append("")
    if dup_grams:
        for g in sorted(dup_grams):
            where = ", ".join(f"{r['topic']}:{r['code']}" for r in l6 if r["gram"].lower() == g)
            lines.append(f"- `{g}` → {where}")
    else:
        lines.append("（无）")
    write_text(REPORT_DIR / "duplicate-check.md", "\n".join(lines) + "\n")
    print("L5 pairs:", len(flag_pairs), "L6 exact dups:", len(dup_grams))


if __name__ == "__main__":
    main()

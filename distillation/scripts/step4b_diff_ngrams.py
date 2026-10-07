"""Mid-band vs high-band n-gram doc-frequency differences (L3/L4 mining aid)."""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import DATA_DIR, STOPWORDS, load_enriched, ngrams, tokens, write_text  # noqa: E402


def main() -> None:
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"]]
    mid = [r for r in recs if 6.0 <= r["band"] <= 7.5]
    high = [r for r in recs if r["band"] >= 8.0]

    def df_map(rs):
        df: dict[tuple, int] = collections.Counter()
        for r in rs:
            seen = set()
            toks = tokens(r["essay"])
            for n in (2, 3, 4):
                for g in ngrams(toks, n):
                    if g[0] in STOPWORDS or g[-1] in STOPWORDS:
                        continue
                    if sum(1 for t in g if t in STOPWORDS) > n - 2:
                        continue
                    seen.add(g)
            df.update(seen)
        return df

    df_mid, df_high = df_map(mid), df_map(high)
    rows_mid = []
    rows_high = []
    for g, c in df_mid.items():
        if c < 10:
            continue
        h = df_high.get(g, 0)
        rate_m, rate_h = c / len(mid), h / len(high)
        rows_mid.append((rate_m - rate_h, rate_m, rate_h, " ".join(g)))
    for g, c in df_high.items():
        if c < 10:
            continue
        m = df_mid.get(g, 0)
        rate_m, rate_h = m / len(mid), c / len(high)
        rows_high.append((rate_h - rate_m, rate_m, rate_h, " ".join(g)))
    rows_mid.sort(reverse=True)
    rows_high.sort(reverse=True)

    lines = ["# 6–7.5 vs 8+ 词串差频（文档频率）", ""]
    lines.append(f"- 中档 {len(mid)} 篇；高分 {len(high)} 篇。")
    lines.append("- 仅保留两组中出现≥10 篇的词串（2–4 gram），按文档频率差排序。")
    lines.append("")
    lines.append("## 中档显著偏高的词串（潜在失分模式/套话）")
    lines.append("")
    lines.append("| 词串 | 中档频率 | 高分频率 | 差值 |")
    lines.append("|---|---:|---:|---:|")
    for d, rm, rh, gram in rows_mid[:150]:
        lines.append(f"| {gram} | {rm:.1%} | {rh:.1%} | {d:+.1%} |")
    lines.append("")
    lines.append("## 高分显著偏高的词串（潜在加分表达）")
    lines.append("")
    lines.append("| 词串 | 中档频率 | 高分频率 | 差值 |")
    lines.append("|---|---:|---:|---:|")
    for d, rm, rh, gram in rows_high[:150]:
        lines.append(f"| {gram} | {rm:.1%} | {rh:.1%} | {d:+.1%} |")
    write_text(DATA_DIR.parent / "reports" / "ngram-diff.md", "\n".join(lines) + "\n")
    print("wrote ngram-diff.md")
    print("mid top:", [r[3] for r in rows_mid[:30]])
    print("high top:", [r[3] for r in rows_high[:30]])


if __name__ == "__main__":
    main()

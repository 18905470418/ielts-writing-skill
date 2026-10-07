"""Step 3 (quantitative track) - corpus features, collocation mining and the
per-band distribution table handed to Task 3.

Outputs
-------
distillation/data/features.train.csv          per-essay quantitative features
distillation/data/topic-collocations.json     candidate collocations per topic (L6 input)
distillation/reports/feature-distribution.md  各档分布区间表 + 相邻档差值
distillation/data/feature-distribution.csv    machine-readable version
"""
from __future__ import annotations

import collections
import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import (  # noqa: E402
    BANDS,
    DATA_DIR,
    REPORT_DIR,
    TOPICS,
    build_vocab_df,
    collocation_density,
    compute_features,
    extract_collocations,
    load_enriched,
    quantiles,
    write_csv,
    write_json,
    write_text,
)

FEATURES = [
    ("word_count", "词数"),
    ("paragraph_count", "段数"),
    ("avg_sentence_length", "平均句长（词）"),
    ("sentence_len_sd", "句长标准差"),
    ("long_sentence_ratio", "长句(>25词)占比"),
    ("simple_ratio", "简单句占比*"),
    ("compound_ratio", "并列句占比*"),
    ("complex_ratio", "复杂句占比*"),
    ("subordinate_density", "从属结构密度(/100词)"),
    ("connector_density", "显性连接词密度(/100词)"),
    ("connector_variety", "连接词种类数"),
    ("mechanical_connector_density", "机械连接词密度(/100词)"),
    ("reference_density", "指代词密度(/100词)"),
    ("reference_chain_max", "最长指代链（句）"),
    ("ttr250", "前250词类符形符比"),
    ("long_word_ratio", "长词(>=7字母)占比"),
    ("awl_ratio", "学术词表命中率"),
    ("rare_token_ratio", "语料级罕见词占比"),
    ("question_keyword_coverage", "题干关键词字面覆盖率"),
    ("mechanism_hits", "机制解释标记数"),
    ("example_hits", "例证标记数"),
    ("implication_count", "推论/回扣标记数"),
    ("specific_example_count", "具体例证数"),
    ("proper_noun_count", "专有名词数"),
    ("numeric_count", "数字/数据点数"),
    ("template_hits", "模板句命中数"),
    ("people_count", "people 出现次数"),
    ("colloc_density", "主题词伙密度(/100词)"),
]


def spearman(xs: list[float], ys: list[float]) -> float:
    def rank(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        return ranks

    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def main() -> None:
    recs = load_enriched()
    corpus = [r for r in recs if not r["excluded_from_distillation"]]
    vocab_df = build_vocab_df(recs)

    # ---------- collocation mining over 8+ samples
    high = [r for r in corpus if r["band"] >= 8.0]
    print(f"collocation corpus: {len(high)} essays (band >= 8)")
    topic_docs = collections.Counter(r["topic"] for r in high)
    min_docs_map = {t: (2 if topic_docs[t] < 30 else 3) for t in TOPICS}
    print("per-topic 8+ docs:", dict(topic_docs), "min_docs:", min_docs_map)
    colloc = extract_collocations(high, min_docs=3, min_docs_map=min_docs_map)
    # keep top 150 per topic by docs
    compact = {"meta": {"corpus": "train band>=8", "docs": len(high), "min_docs": 3}, "topics": {}, "generic": {}}
    for t in TOPICS:
        rows = sorted(colloc["topics"][t].values(), key=lambda x: (-x["docs"], -len(x["gram"])))[:150]
        compact["topics"][t] = rows
    compact["generic"] = sorted(colloc["generic"].values(), key=lambda x: (-x["docs"], -len(x["gram"])))[:120]
    write_json(DATA_DIR / "topic-collocations.json", compact)
    print("collocation candidates:", {t: len(compact["topics"][t]) for t in TOPICS})

    # top grams per topic for density feature
    top_grams = {t: [r["gram"] for r in compact["topics"][t][:60]] for t in TOPICS}
    generic_grams = [r["gram"] for r in compact["generic"][:60]]

    # ---------- per-essay features
    rows = []
    for rec in corpus:
        feats = compute_features(rec, vocab_df, len(recs))
        feats["reliability_tier"] = rec["reliability_tier"]
        grams = top_grams.get(rec["topic"], []) + generic_grams
        feats["colloc_density"] = collocation_density(rec["essay"], grams)
        rows.append(feats)

    header = ["id", "band", "task_type", "topic", "source", "reliability_tier"] + [f for f, _ in FEATURES]
    out_rows = []
    for f in rows:
        vals = [f["id"], f["band"], f["task_type"], f["topic"], f["source"], f.get("reliability_tier", "")]
        vals += [f[key] for key, _ in FEATURES]
        out_rows.append(vals)
    write_csv(DATA_DIR / "features.train.csv", header, out_rows)

    # ---------- distribution table
    lines: list[str] = []
    A = lines.append
    A("# 任务二 · 定量特征各档分布区间表（交付任务三）")
    A("")
    A(f"> 语料：训练集 {len(corpus)} 篇（剔除 7 条 suspected-offtask），盲测集未使用。")
    A("> 口径：* 标记的句式为启发式分类（简单/并列/复杂），其余见 `distillation/scripts/distill_lib.py`。")
    A("> 用途：评分期交叉验证的**辅助信号**，不作独立判分依据（任务三 §1.5）。")
    A("")
    A("## 1. 各档分布区间（P25 / 中位数 / P75）")
    A("")
    header_cells = "| 指标 | " + " | ".join(f"{b}" for b in BANDS) + " | ρ(与分数) |"
    A(header_cells)
    A("|---|" + "---:|" * (len(BANDS) + 1))
    dist_rows = []
    for key, label in FEATURES:
        cells = []
        byband = []
        for b in BANDS:
            vals = [f[key] for f in rows if f["band"] == b]
            q25, med, q75 = quantiles(vals, (0.25, 0.5, 0.75))
            byband.append((b, q25, med, q75, len(vals)))
            dist_rows.append([key, label, b, round(q25, 3), round(med, 3), round(q75, 3), round(statistics.mean(vals), 3), len(vals)])
            cells.append(f"{q25:.2f}/{med:.2f}/{q75:.2f}")
        xs = [f[key] for f in rows]
        ys = [f["band"] for f in rows]
        rho = spearman(xs, ys)
        A(f"| {label} | " + " | ".join(cells) + f" | {rho:+.2f} |")
    A("")
    A("> 说明：中位数栏内为 `P25/中位数/P75`。ρ 为 Spearman 秩相关系数（|ρ|<0.15 视为噪声级）。")
    A("")
    A("## 2. 相邻分数档的中位数差值（哪 0.5 分差在哪）")
    A("")
    pairs = list(zip(BANDS[:-1], BANDS[1:]))
    A("| 指标 | " + " | ".join(f"{a}→{b}" for a, b in pairs) + " |")
    A("|---|" + "---:|" * len(pairs))
    for key, label in FEATURES:
        meds = {}
        for b in BANDS:
            vals = [f[key] for f in rows if f["band"] == b]
            meds[b] = statistics.median(vals)
        cells = []
        for a, b in pairs:
            d = meds[b] - meds[a]
            cells.append(f"{d:+.2f}")
        A(f"| {label} | " + " | ".join(cells) + " |")
    A("")
    A("## 3. 强信号摘要（|ρ|≥0.20）")
    A("")
    strong = []
    for key, label in FEATURES:
        xs = [f[key] for f in rows]
        ys = [f["band"] for f in rows]
        rho = spearman(xs, ys)
        if abs(rho) >= 0.20:
            strong.append((abs(rho), label, rho))
    for _, label, rho in sorted(strong, reverse=True):
        A(f"- {label}（ρ={rho:+.2f}）")
    A("")
    A("## 4. 任务三复检触发建议")
    A("")
    A("- 若判分结论为 7.5，但「复杂句占比 / 从属结构密度」落在 6.5 档区间且「错误代理指标」")
    A("  高于 7 分档 P75，则触发复检一次（回看锚点比对）；")
    A("- 若判分结论为 8+，但「具体例证数 = 0」且「机制解释标记数」低于 7 分档 P25，则触发 TR 复检；")
    A("- 若 TR 判分主要依据「题干关键词字面覆盖率」而结论偏高：高分样本存在系统性改写题干、")
    A("  字面覆盖率反而偏低的现象（见《偏差记录表》§6），该指标只用于低覆盖预警，不用于高分确认。")
    A("")
    write_text(REPORT_DIR / "feature-distribution.md", "\n".join(lines) + "\n")
    write_csv(
        DATA_DIR / "feature-distribution.csv",
        ["feature", "label", "band", "p25", "median", "p75", "mean", "n"],
        dist_rows,
    )

    print("features rows:", len(rows))
    print("wrote feature-distribution.md / .csv / features.train.csv / topic-collocations.json")


if __name__ == "__main__":
    main()

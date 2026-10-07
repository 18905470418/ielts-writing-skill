"""Step 2 - blind (descriptor-operationalised) scoring + deviation record.

The scorer only sees text features. Band labels are stripped before scoring
and only joined back afterwards for the comparison table, so every score is
produced without knowledge of the true band.

Outputs
-------
distillation/data/blind-scores.csv         per-essay scores vs truth
distillation/reports/deviation-record.md   《偏差记录表》
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
    TASKS,
    blind_module_scores,
    build_vocab_df,
    compute_features,
    load_enriched,
    round_half,
    short_quote,
    write_csv,
    write_text,
)

MODULES = ["TR", "CC", "LR", "GRA"]


def quantile(vals: list[float], q: float) -> float:
    vals = sorted(vals)
    if not vals:
        return float("nan")
    if q <= 0:
        return vals[0]
    if q >= 1:
        return vals[-1]
    pos = q * (len(vals) - 1)
    lo, hi = int(pos), int(pos) + 1
    if hi >= len(vals):
        return vals[-1]
    frac = pos - lo
    return vals[lo] * (1 - frac) + vals[hi] * frac


def main() -> None:
    recs = load_enriched()
    vocab_df = build_vocab_df(recs)
    rows = []
    for rec in recs:
        if rec["excluded_from_distillation"]:
            continue
        feats = compute_features(rec, vocab_df, len(recs))
        blind = blind_module_scores(feats)
        blind_total = round_half(statistics.mean(blind.values()))
        official = rec["subscores_source"] == "official"
        subs = rec["subscores"]
        row = {
            "id": rec["id"],
            "band_true": rec["band"],
            "task_type": rec["task_type_effective"],
            "topic": rec["topic"],
            "source": rec["source"],
            "reliability_tier": rec["reliability_tier"],
            "word_count": feats["word_count"],
            "blind_TR": blind["TR"],
            "blind_CC": blind["CC"],
            "blind_LR": blind["LR"],
            "blind_GRA": blind["GRA"],
            "blind_total": blind_total,
            "delta_total": blind_total - rec["band"],
            "subscores_source": rec["subscores_source"],
            "true_TR": subs["TR"],
            "true_CC": subs["CC"],
            "true_LR": subs["LR"],
            "true_GRA": subs["GRA"],
            "delta_TR": blind["TR"] - subs["TR"],
            "delta_CC": blind["CC"] - subs["CC"],
            "delta_LR": blind["LR"] - subs["LR"],
            "delta_GRA": blind["GRA"] - subs["GRA"],
            "coverage": round(feats["question_keyword_coverage"], 3),
            "ttr250": round(feats["ttr250"], 3),
            "rare_ratio": round(feats["rare_token_ratio"], 4),
            "subord_density": round(feats["subordinate_density"], 2),
            "connector_density": round(feats["connector_density"], 2),
            "template_hits": feats["template_hits"],
        }
        rows.append(row)

    header = list(rows[0].keys())
    write_csv(
        DATA_DIR / "blind-scores.csv",
        header,
        [[r[h] for h in header] for r in rows],
    )

    # ---------------- aggregates
    def agg(rs):
        n = len(rs)
        exact = sum(1 for r in rs if r["delta_total"] == 0) / n
        within_half = sum(1 for r in rs if abs(r["delta_total"]) <= 0.5) / n
        within_one = sum(1 for r in rs if abs(r["delta_total"]) <= 1.0) / n
        over = sum(1 for r in rs if r["delta_total"] > 0) / n
        under = sum(1 for r in rs if r["delta_total"] < 0) / n
        mean = statistics.mean(r["delta_total"] for r in rs)
        return n, exact, within_half, within_one, over, under, mean

    lines: list[str] = []
    A = lines.append
    A("# 任务二 · 第 2 步双向标注对账 ——《偏差记录表》")
    A("")
    A("> 对账对象：训练集 1186 篇（剔除 7 条 `suspected-offtask`）。")
    A("> 独立评分方：`blind_module_scores`（官方 Band Descriptor 的操作化规则评分器，")
    A("> 只读文本特征，评分时剥离 id/band/subscores，完成后才与真实分数对账）。")
    A("> 明细：`distillation/data/blind-scores.csv`（每篇四维预评分、总分、偏差与特征）。")
    A("")
    A("## 1. 评分器操作化口径（摘要）")
    A("")
    A("| 维度 | 观察点（全部可实现为文本特征） |")
    A("|---|---|")
    A("| TR | 立场句是否出现/位置；题干关键词覆盖率；主体段是否含机制解释（because/leads to...）与例证标记；段数与词数 |")
    A("| CC | 段落数与均衡；显性连接词密度与种类；段落开头是否重复；指代链长度；连续短句检测 |")
    A("| LR | 前 250 词类符/形符比；长词占比；学术词表命中率；语料级罕见词（拼写错误代理）；模板句与 people 密度 |")
    A("| GRA | 平均句长与句长标准差；从属结构密度；run-on/粘连检测；词数达标 |")
    A("")
    A("该评分器是课堂式规则代理，不是考官；它的价值在于把「官方措辞 vs 文章实际特征」的落差显性化。")
    A("")
    A("## 2. 总分对账总表")
    A("")
    A("| 子集 | 篇数 | 完全一致 | 误差≤0.5 | 误差≤1.0 | 判高率 | 判低率 | 平均偏差(估-真) |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|")
    subsets: list[tuple[str, list[dict]]] = [("全体", rows)]
    subsets += [(f"Band {b}", [r for r in rows if r["band_true"] == b]) for b in BANDS]
    subsets += [(f"题型 {t}", [r for r in rows if r["task_type"] == t]) for t in TASKS]
    for name, rs in subsets:
        n, exact, wh, wo, over, under, mean = agg(rs)
        A(f"| {name} | {n} | {exact:.0%} | {wh:.0%} | {wo:.0%} | {over:.0%} | {under:.0%} | {mean:+.2f} |")
    A("")
    A("## 3. 模块级对账")
    A("")
    A("### 3.1 与 22 条官方小分对账（唯一有真实四维小分的子集）")
    A("")
    official_rows = [r for r in rows if r["subscores_source"] == "official"]
    A("| 模块 | 平均偏差(估-真) | 误差≤0.5 占比 | 误差≥1.0 篇数 | 方向 |")
    A("|---|---:|---:|---:|---|")
    for d in MODULES:
        vals = [r[f"delta_{d}"] for r in official_rows]
        mean = statistics.mean(vals)
        wh = sum(1 for v in vals if abs(v) <= 0.5) / len(vals)
        big = sum(1 for v in vals if abs(v) >= 1.0)
        direction = "无系统偏差" if abs(mean) < 0.15 else ("系统性判高" if mean > 0 else "系统性判低")
        A(f"| {d} | {mean:+.2f} | {wh:.0%} | {big} | {direction} |")
    A("")
    A("### 3.2 全训练集模块偏差（对反向标注小分，仅供参考）")
    A("")
    A("| 模块 | 平均偏差(估-标注) | 误差≤0.5 占比 | 说明 |")
    A("|---|---:|---:|---|")
    for d in MODULES:
        vals = [r[f"delta_{d}"] for r in rows]
        mean = statistics.mean(vals)
        wh = sum(1 for v in vals if abs(v) <= 0.5) / len(vals)
        A(f"| {d} | {mean:+.2f} | {wh:.0%} | 反向标注由同一评分器校准而来，此项只用于检查标注内部一致性 |")
    A("")
    A("## 4. 判高 / 判低最大的样本（各 15 篇，供人工复核）")
    A("")

    def row_line(r):
        return (
            f"| {r['id']} | {r['band_true']} | {r['blind_total']} | {r['delta_total']:+.1f} | "
            f"{r['task_type']} | {r['word_count']} | {r['coverage']:.2f} | {r['ttr250']:.2f} | "
            f"{r['rare_ratio']:.3f} | {r['template_hits']} |"
        )

    A("### 4.1 判高 Top 15")
    A("")
    A("| id | 真分 | 预评 | 偏差 | 题型 | 词数 | 关键词覆盖 | TTR | 罕见词率 | 模板命中 |")
    A("|---|---:|---:|---:|---|---:|---:|---:|---:|---:|")
    for r in sorted(rows, key=lambda x: -x["delta_total"])[:15]:
        A(row_line(r))
    A("")
    A("### 4.2 判低 Top 15")
    A("")
    A("| id | 真分 | 预评 | 偏差 | 题型 | 词数 | 关键词覆盖 | TTR | 罕见词率 | 模板命中 |")
    A("|---|---:|---:|---:|---|---:|---:|---:|---:|---:|")
    for r in sorted(rows, key=lambda x: x["delta_total"])[:15]:
        A(row_line(r))
    A("")
    A("## 5. 偏差结构（按分数段 × 模块，官方小分子集）")
    A("")
    A("| 分数档 | 篇数 | TR | CC | LR | GRA |")
    A("|---|---:|---:|---:|---:|---:|")
    for b in BANDS:
        rs = [r for r in official_rows if r["band_true"] == b]
        if not rs:
            continue
        cells = []
        for d in MODULES:
            cells.append(f"{statistics.mean(r[f'delta_{d}'] for r in rs):+.2f}")
        A(f"| {b} | {len(rs)} | " + " | ".join(cells) + " |")
    A("")
    A("## 6. 判定落差归因（基于 20 篇人工复核）")
    A("")
    A("### 6.1 判高的机制：公式化完成度被计数型规则奖励")
    A("")
    A("- 典型样本 `B6-ADV-002`（真 6.0 / 预评 8.5）：结构完整、连接词齐全、")
    A("  「This is mainly because → For example → As a result」三段式反复出现，")
    A("  但例证全是假设性泛例（\"an employee may have to work longer hours\"），两个主体段未提供新信息；")
    A("  计数型 TR/GRA 把「标记齐全」误当作「论证充分」。")
    A("- 典型样本 `B6-OP-006`（真 6.0 / 预评 8.5）：TTR 0.79、字面覆盖 0.81，词汇与结构表面分高；")
    A("  但开头直接复述题干（疑似套用题目原句），论点停留在「艺术减压、有助职业」的常识层。")
    A("- 结论：**「完整但泛化」是 6.0–6.5 的典型形态，必须用 L2 锚点比对才能与 7+ 区分**；")
    A("  单纯的特征计数会把这类文章推到 8+。")
    A("")
    A("### 6.2 判低的机制：高分文刻意违反「字面覆盖 + 标记密度」假设")
    A("")
    A("- 典型样本 `B9-OP-005`（真 9.0 / 预评 6.0）：关键概念全部改写（字面覆盖 0.39），")
    A("  引言即引入 harm principle 作为分析框架，几乎不用 because/for example；")
    A("  连接词密度仅 1.05/100 词——恰是 9.0 档的特征（全档中位 2.55）。")
    A("- 典型样本 `B9-REP-002`（真 9.0 / 预评 6.0）：报告类 9.0 用「Three things have shifted at once」")
    A("  组织因果，而非 what are the causes 的字面复述；覆盖 0.29 被误判为回应不足。")
    A("- 典型样本 `B9-DIS-004`（真 9.0 / 预评 6.5）：官方评语称其以「pessimists / optimists / decisive variable」")
    A("  三层框架重构题目；计数型规则只看到低连接词密度与低字面覆盖。")
    A("- 结论：**Band 8+ 的文本特征与 6–7 档相反**——改写题干、少用标记、低连接词密度；")
    A("  任何把这些指标当作正向证据的规则都会系统性判低高档。")
    A("")
    A("### 6.3 官方措辞 → 操作化代理 → 落差 → L1 修订对照")
    A("")
    A("| 官方措辞 | 本步操作化代理 | 观察到的落差 | L1 采用的修订 |")
    A("|---|---|---|---|")
    A("| addresses all parts | 题干实词字面覆盖率 | 8+ 档改写题干 → 覆盖率反而低，被误判未回应 | §0.2 覆盖率只作「低覆盖预警」；TR 用概念回应检查 |")
    A("| extends and supports main ideas | because/for example 标记计数 | 公式化 6.0 文被高估；标记少的 9.0 文被低估 | L1-TR-6.2 检查「例证后是否推进」；L1-TR-9.1 重构框架 |")
    A("| uses cohesive devices | 显性连接词密度与种类 | 连接词越多越像高分，但语料相关性为负（ρ=−0.36） | L1-CC-6.1 / 75.1；密度只作复检信号 |")
    A("| uses a variety of complex structures | 复杂句占比 / 从属结构密度 | 与总分几乎不相关（ρ≤0.11） | L1-GRA-7.2：不得按复杂句数量定档 |")
    A("| error-free | 语料级罕见词 / 正则扫描 | 抓不到中式搭配，且把主题专名当噪声 | L3 增加负迁移标签；GRA 以锚点比对为主 |")
    A("")
    A("### 6.4 对 L1 的直接启示")
    A("")
    A("1. 所有「数量型」特征必须配合至少一条「质量型」判别操作（如展开检查：解释后是否推进）；")
    A("2. 连接词密度只作为辅助信号，评分以段间语义推进检查为主；")
    A("3. 词表类信号只用于 LR 复检，不单独触发降档；")
    A("4. 半分档必须依靠「稳定性」判别（段落间波动、错误出现的分布），而非整体均值；")
    A("5. 计数型预评分与规则结论冲突时以规则与 L2 锚点为准（任务三 §1.5 的复检机制同理）。")
    A("")
    A("## 7. 人工复核记录（20 篇）")
    A("")
    A("复核明细（判高 10 篇 + 判低 10 篇，含逐篇结论与代表性原文片段）：")
    A("见 `distillation/reports/deviation-review.md`；本节 6.1/6.2 引用的三篇深度个案")
    A("（`B6-ADV-002`、`B6-OP-006`、`B9-OP-005`、`B9-REP-002`、`B9-DIS-004`）均在其中。")
    A("")
    write_text(REPORT_DIR / "deviation-record.md", "\n".join(lines) + "\n")

    # quick console summary
    n, exact, wh, wo, over, under, mean = agg(rows)
    print(f"rows: {n}")
    print(f"exact: {exact:.1%}  within0.5: {wh:.1%}  within1.0: {wo:.1%}")
    print(f"over: {over:.1%}  under: {under:.1%}  mean: {mean:+.2f}")
    print("wrote:", DATA_DIR / "blind-scores.csv")
    print("wrote:", REPORT_DIR / "deviation-record.md")


if __name__ == "__main__":
    main()

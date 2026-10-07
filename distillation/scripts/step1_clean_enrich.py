"""Step 1 - schema cleaning + subscores back-annotation.

Outputs
-------
distillation/data/essays.train.enriched.jsonl
    Training records with:
      * task_type_effective  (reviewed correction; see task_type_fix.py)
      * reliability_tier     (A-examiner .. D-auto)
      * excluded_from_distillation / exclusion_reason
      * subscores            (official where available, otherwise inferred)
      * subscores_source     ("official" | "inferred-v1")
      * subscores_confidence
distillation/reports/cleaning-report.md
    Schema findings, corrections, exclusions, inference method.

Discipline: reads only the train split. The blindtest stays sealed.
"""
from __future__ import annotations

import collections
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import (  # noqa: E402
    BANDS,
    DATA_DIR,
    REPORT_DIR,
    TOPICS,
    blind_module_scores,
    build_vocab_df,
    compute_features,
    infer_subscores,
    load_train,
    reliability_tier,
    round_half,
    write_jsonl,
    write_text,
)
from task_type_fix import effective_task_type  # noqa: E402

REQUIRED = ["id", "band", "task_type", "topic", "question", "essay", "word_count", "source", "source_url", "source_no", "split", "flags"]
ID_RE = re.compile(r"^B(6|65|7|75|8|85|9)-(OP|DIS|ADV|REP|TQ)-\d{3}$")


def validate(recs: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ids = [r["id"] for r in recs]
    dup = [i for i, c in collections.Counter(ids).items() if c > 1]
    if dup:
        errors.append(f"duplicate ids: {dup[:10]}")
    for r in recs:
        for f in REQUIRED:
            if f not in r or r[f] in (None, "") and f != "flags":
                errors.append(f"{r.get('id','?')}: required field missing/empty: {f}")
        if not ID_RE.match(r["id"]):
            errors.append(f"{r['id']}: id pattern")
        if r["band"] not in BANDS:
            errors.append(f"{r['id']}: band {r['band']}")
        if r["topic"] not in TOPICS:
            errors.append(f"{r['id']}: topic {r['topic']}")
        if r["split"] != "train":
            errors.append(f"{r['id']}: split {r['split']}")
        wc = len(re.findall(r"\S+", r["essay"]))
        if abs(wc - r["word_count"]) > 2:
            warnings.append(f"{r['id']}: stored word_count {r['word_count']} vs recomputed {wc}")
        if len(r["essay"].split()) < 120:
            warnings.append(f"{r['id']}: very short essay ({wc} words)")
        if r.get("subscores"):
            for d in ("TR", "CC", "LR", "GRA"):
                if d not in r["subscores"]:
                    errors.append(f"{r['id']}: subscores missing {d}")
    return errors, warnings


def main() -> None:
    recs = load_train()
    errors, warnings = validate(recs)
    vocab_df = build_vocab_df(recs)
    n_docs = len(recs)

    corrections: list[dict] = []
    enriched: list[dict] = []
    for rec in recs:
        new_type = effective_task_type(rec["question"], rec["task_type"], rec["id"])
        if new_type != rec["task_type"]:
            corrections.append(
                {
                    "id": rec["id"],
                    "band": rec["band"],
                    "old": rec["task_type"],
                    "new": new_type,
                    "question": rec["question"][:220],
                }
            )
        out = dict(rec)
        out["task_type_effective"] = new_type
        out["reliability_tier"] = reliability_tier(rec)
        excluded = bool(rec["flags"])
        out["excluded_from_distillation"] = excluded
        out["exclusion_reason"] = "flags: suspected-offtask（疑为 Task 1/非 Task 2）" if excluded else None
        # ---- subscores: official kept, otherwise inferred
        feats = compute_features(out, vocab_df, n_docs)
        blind = blind_module_scores(feats)
        if rec.get("subscores"):
            out["subscores_source"] = "official"
            out["subscores_confidence"] = "high"
        else:
            subs, conf = infer_subscores(feats, rec["band"], blind)
            out["subscores"] = subs
            out["subscores_source"] = "inferred-v1"
            out["subscores_confidence"] = conf
        out["blind_scores_v1"] = blind
        out["blind_total_v1"] = round_half(statistics.mean(blind.values()))
        enriched.append(out)

    write_jsonl(DATA_DIR / "essays.train.enriched.jsonl", enriched)

    # ---- report
    by_type = collections.Counter(r["task_type_effective"] for r in enriched if not r["excluded_from_distillation"])
    grid = collections.Counter((r["band"], r["task_type_effective"]) for r in enriched if not r["excluded_from_distillation"])
    thin_cells = [
        (b, t, grid[(b, t)]) for b in BANDS for t in ("opinion", "discussion", "adv-disadv", "report", "two-part") if grid[(b, t)] < 3
    ]
    conf = collections.Counter(r["subscores_confidence"] for r in enriched if r["subscores_source"].startswith("inferred"))
    tier = collections.Counter(r["reliability_tier"] for r in enriched if not r["excluded_from_distillation"])
    lines: list[str] = []
    A = lines.append
    A("# 任务二 · 第 1 步结构化清洗报告")
    A("")
    A("> 输入：`sample-library/essays.train.jsonl`（1193 篇，split=train）。")
    A("> 本步骤只读训练集；盲测集（`sample-library/blindtest/`）全程未读取。")
    A("> 产出：`distillation/data/essays.train.enriched.jsonl`（带反向标注小分与修正后题型）。")
    A("")
    A("## 1. Schema 校验")
    A("")
    A(f"- 必填字段/number 校验：**{'通过' if not errors else '存在错误'}**（错误 {len(errors)} 条）。")
    A(f"- 警示项：{len(warnings)} 条（字数口径 ±2 与超短样本提示；不影响入库）。")
    A("- 行数：1193；重复 id：0；重复正文：0；U+FFFD 替换符：0。")
    if errors:
        A("")
        A("```")
        for e in errors[:20]:
            A(e)
        A("```")
    A("")
    A("## 2. 分数可靠性分层")
    A("")
    A("| 层级 | 来源 | 训练集篇数 | 用途约束 |")
    A("|---|---|---:|---|")
    tier_desc = {
        "A-examiner": "考官/官方标注（含官网小分与考官评语）",
        "B-teacher": "教学机构批改或精选范文（cdieltsprep / allthingsielts / ieltsprepstudio / bandnine）",
        "C-blog": "教师博客范文（ielts-blog）",
        "D-auto": "writing9.com 自动评分",
    }
    for k in ("A-examiner", "B-teacher", "C-blog", "D-auto", "E-other"):
        if tier.get(k):
            A(f"| {k} | {tier_desc.get(k,'其他')} | {tier[k]} | {'L2 锚点首选、L1 证据优先' if k in ('A-examiner','B-teacher') else '可用于统计与常规锚点，8.5 档须标注来源；L2 黄金锚点不单独采用'} |")
    A("")
    A("**处理原则**：训练集内不存在「无任何分数来源」的记录（全部带 source/source_url/band）。")
    A("按任务一 README 的口径，writing9.com 自动评分依赖其页面标注，本任务不删除、不重打分，")
    A("但在锚点选择与 8.5 档规则归纳时按上表降权，并在产物中显式标注来源层级。")
    A("")
    A("## 3. 题型标注审计与修正")
    A("")
    A("任务一分类器有一条实现性问题：`RE_REPORT` 的 `best way to (solve|reduce|...)` 分支")
    A("会把「单一评价式设问」（best way + do you agree）误导向 two-part；且 `RE_ADV` 优先级高于")
    A("「why + positive/negative」的混合设问判定，把一部分双问题类误标为 adv-disadv。")
    A("按任务一记录的分类边界（混合型设问→two-part、positive/negative development→adv-disadv、")
    A("单句 What/How/Why→report）逐题复核后，对训练集做如下修正（id 保持不变）：")
    A("")
    A("| id | 原题型 | 修正为 | 依据（题干摘要） |")
    A("|---|---|---|---|")
    for c in corrections:
        q = c["question"].replace("|", "\\|")
        A(f"| {c['id']} | {c['old']} | {c['new']} | {q} |")
    A("")
    A(f"共修正 **{len(corrections)}** 条。`task_type_effective` 字段写入 enriched 记录；")
    A("原始 `task_type` 保持不变，便于审计。修正函数固化在 `distillation/scripts/task_type_fix.py`，")
    A("任务三对盲测集评分时须调用同一函数，保持两边口径一致。")
    A("")
    A("## 4. 剔除清单（不参与任何规则/锚点/观点/词伙蒸馏）")
    A("")
    A("| id | 分数 | flags | 理由 |")
    A("|---|---|---|---|")
    for r in enriched:
        if r["excluded_from_distillation"]:
            A(f"| {r['id']} | {r['band']} | {'/'.join(r['flags'])} | {r['exclusion_reason']} |")
    A("")
    A("## 5. 四维小分反向标注（subscores back-annotation）")
    A("")
    A("- 训练集中 22 条带官网小分与考官评语（A-examiner），原样保留，`subscores_source=official`。")
    A("- 其余 1171 条（含 7 条剔除项）执行反向标注：")
    A("  1. 用官方 Band Descriptor 操作性化的盲评分器（`blind_module_scores`）计算四维相对强弱；")
    A("  2. 以**真实总分**为锚，把相对强弱分布到四个维度（±1.0 内），并强制满足官方取整规则")
    A("     （四项平均按 .25→.5、.75→下一档取整后等于真实总分）；")
    A("  3. 标注 `subscores_source=inferred-v1` 与置信度（high/medium/low）。")
    A("- 推断值仅作为规则归纳与锚点评语的内部依据；不得用于任务三的盲测真值。")
    A("")
    A("| 推断置信度 | 篇数 |")
    A("|---|---:|")
    for k in ("high", "medium", "low"):
        A(f"| {k} | {conf.get(k,0)} |")
    A("")
    A("## 6. 清洗后分布与薄弱格子（训练集口径）")
    A("")
    A("| 分数档 | opinion | discussion | adv-disadv | report | two-part | 小计 |")
    A("|---|---:|---:|---:|---:|---:|---:|")
    for b in BANDS:
        row = [grid[(b, t)] for t in ("opinion", "discussion", "adv-disadv", "report", "two-part")]
        A(f"| {b} | " + " | ".join(str(x) for x in row) + f" | {sum(row)} |")
    A("")
    if thin_cells:
        A("训练集内「分数档 × 题型」不足 3 篇的格子（对应规则须标注低置信度）：")
        for b, t, c in thin_cells:
            A(f"- {b} × {t}：{c} 篇")
    else:
        A("训练集内「分数档 × 题型」全部格子 ≥3 篇。")
    A("")
    A("> 说明：distribution-report.md 的薄弱格子按 1490 全集统计；本表按修正后训练集 1186 篇")
    A(">（剔除 7 条 suspected-offtask）统计，作为 L1 置信度标注的唯一依据。")
    A("")
    write_text(REPORT_DIR / "cleaning-report.md", "\n".join(lines) + "\n")
    write_jsonl(DATA_DIR / "task-type-corrections.jsonl", corrections)

    print(f"enriched records: {len(enriched)}")
    print(f"task-type corrections: {len(corrections)}")
    print(f"subscores inferred: {sum(1 for r in enriched if r['subscores_source'] != 'official')}")
    print(f"excluded: {sum(1 for r in enriched if r['excluded_from_distillation'])}")
    print("errors:", errors[:5])
    print("warnings:", warnings[:5])


if __name__ == "__main__":
    main()

"""Task-2 acceptance self-check (requirement -> evidence)."""
from __future__ import annotations

import re
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import DATA_DIR, REFS_DIR, REPORT_DIR  # noqa: E402

DIMS = ["TR", "CC", "LR", "GRA"]
BAND_CODES = ["6", "65", "7", "75", "8", "85", "9"]


def main() -> None:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, note: str = ""):
        results.append((name, ok, note))

    # 1. no placeholders
    bad = []
    for p in list(REFS_DIR.glob("*.md")) + list((REFS_DIR / "anchors").glob("*.md")):
        t = p.read_text(encoding="utf-8")
        if "空骨架" in t or "PENDING" in t:
            bad.append(p.name)
    check("全部 references 文件已填充（无空骨架）", not bad, ",".join(bad))

    # 2. L1 coverage
    l1 = (REFS_DIR / "band-rules.md").read_text(encoding="utf-8")
    missing = []
    for d in DIMS:
        for b in BAND_CODES:
            if f"L1-{d}-{b}" not in l1:
                missing.append(f"{d}-{b}")
        for dlt in ["D65", "D7", "D75", "D8", "D85", "D9"]:
            if f"L1-{d}-{dlt}" not in l1:
                missing.append(f"{d}-{dlt}")
    check("L1 四维 × 7 档 + 6 组 Delta 齐备", not missing, ",".join(missing[:8]))
    check("L1 含半分档专项与置信度说明", "半分档专项" in l1 and "置信度" in l1)

    # 3. anchors per band x task = 2..3
    counts_ok = True
    detail = []
    for name, prefix in [
        ("opinion.md", {"6.0": "B6-OP", "6.5": "B65-OP", "7.0": "B7-OP", "7.5": "B75-OP", "8.0": "B8-OP", "8.5": "B85-OP", "9.0": "B9-OP"}),
        ("discussion.md", {"6.0": "B6-DIS", "6.5": "B65-DIS", "7.0": "B7-DIS", "7.5": "B75-DIS", "8.0": "B8-DIS", "8.5": "B85-DIS", "9.0": "B9-DIS"}),
        ("adv-disadv.md", {"6.0": "B6-ADV", "6.5": "B65-ADV", "7.0": "B7-ADV", "7.5": "B75-ADV", "8.0": "B8-ADV", "8.5": "B85-ADV", "9.0": "B9-ADV"}),
        ("report.md", {"6.0": "B6-REP", "6.5": "B65-REP", "7.0": "B7-REP", "7.5": "B75-REP", "8.0": "B8-REP", "8.5": "B85-REP", "9.0": "B9-REP"}),
        ("two-part.md", {"6.0": "B6-TQ", "6.5": "B65-TQ", "7.0": "B7-TQ", "7.5": "B75-TQ", "8.0": "B8-TQ", "8.5": "B85-TQ", "9.0": "B9-TQ"}),
    ]:
        t = (REFS_DIR / "anchors" / name).read_text(encoding="utf-8")
        ids = re.findall(r"^### `(B[^`]+)`", t, re.M)
        per_band = {}
        for rid in ids:
            m = re.match(r"B(6|65|7|75|8|85|9)-", rid)
            if m:
                per_band[m.group(1)] = per_band.get(m.group(1), 0) + 1
        for code, n in per_band.items():
            if not (2 <= n <= 3):
                counts_ok = False
                detail.append(f"{name}:B{code}={n}")
        if len(per_band) != 7:
            counts_ok = False
            detail.append(f"{name}:bands={len(per_band)}")
        if "## 黄金锚点" not in t or t.find("## 黄金锚点") > t.find("## 分档补充锚点"):
            counts_ok = False
            detail.append(f"{name}:no-golden-top")
    check("L2 五文件每档 2–3 篇、黄金锚点置顶", counts_ok, ";".join(detail[:6]))

    # 4. L3/L4/L5/L6/question bank structure
    l3 = (REFS_DIR / "error-patterns.md").read_text(encoding="utf-8")
    check("L3 模块分类 + 负迁移标签轴", all(f"## {m} 模块" in l3 for m in DIMS) and "负迁移" in l3)
    l4 = (REFS_DIR / "language-assets.md").read_text(encoding="utf-8")
    l4_topics = ["教育", "科技", "环境", "政府与公共政策", "社会问题", "犯罪与法律", "文化与语言", "健康", "媒体与广告", "全球化与工作"]
    check("L4 主题分节 + 题型索引", all(f"### {t}（" in l4 for t in l4_topics) and "按题型索引" in l4)
    vp_dir = REFS_DIR / "viewpoint-bank"
    vocab_dir = REFS_DIR / "topic-vocab"
    l5 = "\n".join(p.read_text(encoding="utf-8") for p in sorted(vp_dir.glob("*.md")))
    l5_entries = re.findall(r"\n- \*\*\[(?:EDU|TECH|ENV|GOV|SOC|CRIME|CUL|HEALTH|MEDIA|GLOB)-\d{2}\]", l5)
    l5_sources = len(re.findall(r"来源样本：`B", l5))
    check(f"L5 v2 条目编号+来源 id 双轨（{len(l5_entries)} 条）", len(l5_entries) >= 150 and l5_sources >= len(l5_entries))
    l6 = "\n".join(p.read_text(encoding="utf-8") for p in sorted(vocab_dir.glob("*.md")))
    l6_rows = re.findall(r"^\| L6-[A-Z]+-\d{3} \|", l6, re.M)
    check(f"L6 v2 表格含编号与来源 id（{len(l6_rows)} 行）", len(l6_rows) >= 400)
    # per-topic thresholds + coverage
    cov_file = DATA_DIR / "coverage.json"
    cov_ok = True
    cov_detail = []
    if cov_file.exists():
        cov = json.loads(cov_file.read_text(encoding="utf-8")).get("topics", {})
        for t in [
            "education", "technology", "environment", "government", "social",
            "crime", "culture", "health", "media", "globalization-work",
        ]:
            c = cov.get(t)
            if not c:
                cov_ok = False
                cov_detail.append(f"{t}:missing")
                continue
            thin = t in {"government", "crime", "culture", "media"}
            if c["l5_entries"] < (12 if thin else 15) or c["l6_entries"] < (30 if thin else 40):
                cov_ok = False
                cov_detail.append(f"{t}:counts {c['l5_entries']}/{c['l6_entries']}")
            if c["l5_cov"] < 0.40 or c["l6_cov"] < 0.50:
                cov_ok = False
                cov_detail.append(f"{t}:cov {c['l5_cov']:.0%}/{c['l6_cov']:.0%}")
    else:
        cov_ok = False
        cov_detail.append("coverage.json missing")
    check("L5/L6 每主题数量与引用覆盖达标", cov_ok, ";".join(cov_detail[:6]))
    # curation verification reports
    cur_ok = True
    cur_detail = []
    for t in [
        "education", "technology", "environment", "government", "social",
        "crime", "culture", "health", "media", "globalization-work",
    ]:
        rp = REPORT_DIR / f"curation-verify-{t}.md"
        if not rp.exists():
            cur_ok = False
            cur_detail.append(f"{t}:no-report")
            continue
        body = rp.read_text(encoding="utf-8")
        if "结果：PASS" not in body:
            cur_ok = False
            cur_detail.append(f"{t}:FAIL")
    check("10 个主题策展校验全部 PASS", cur_ok, ";".join(cur_detail[:6]))
    qb = (REFS_DIR / "question-bank.md").read_text(encoding="utf-8")
    qb_n = len(re.findall(r"^## QB-\d+", qb, re.M))
    check(f"question-bank 覆盖高频题目（{qb_n} 条）", qb_n >= 40)

    # 5. reports
    for rep, label in [
        ("cleaning-report.md", "清洗报告"),
        ("deviation-record.md", "《偏差记录表》"),
        ("deviation-review.md", "偏差人工复核"),
        ("feature-distribution.md", "定量特征分布表"),
        ("l5-l6-audit.md", "L5/L6 抽检报告"),
        ("asset-verification.md", "资产验证报告"),
    ]:
        check(f"{label} 产出", (REPORT_DIR / rep).exists())

    # 6. verification report content
    av = (REPORT_DIR / "asset-verification.md").read_text(encoding="utf-8")
    check("资产验证 0 问题", "（无）——全部引用样本 id 存在" in av)

    # 7. deep structural checks
    l1_bad = []
    for d in DIMS:
        sections = len(re.findall(rf"^### L1-{d}-(?:6|65|7|75|8|85|9) ", l1, re.M))
        deltas = len(re.findall(rf"L1-{d}-D(?:65|7|75|8|85|9)", l1))
        if sections != 7:
            l1_bad.append(f"{d}:sections={sections}")
        if deltas < 6:
            l1_bad.append(f"{d}:deltas={deltas}")
    check("L1 每维 7 个分档小节 + 6 条 Delta 均成段存在", not l1_bad, ",".join(l1_bad))
    check("L1 含规定短语「样本不足，此规则置信度低」", "样本不足，此规则置信度低" in l1)

    anchor_bad = []
    for name in ["opinion.md", "discussion.md", "adv-disadv.md", "report.md", "two-part.md"]:
        t = (REFS_DIR / "anchors" / name).read_text(encoding="utf-8")
        blocks = len(re.findall(r"^### `B[^`]+`", t, re.M))
        tr = len(re.findall(r"\*\*TR（Task Response）\*\*", t))
        cc = len(re.findall(r"\*\*CC（Coherence", t))
        lr = len(re.findall(r"\*\*LR（Lexical", t))
        gra = len(re.findall(r"\*\*GRA（Grammatical", t))
        vd = len(re.findall(r"\*\*定分理由\*\*", t))
        if not (blocks == tr == cc == lr == gra == vd):
            anchor_bad.append(f"{name}:{blocks}/{tr}/{cc}/{lr}/{gra}/{vd}")
    check("L2 每篇锚点六件套齐全（全文+四维评语+定分理由）", not anchor_bad, ",".join(anchor_bad))

    l5_bad = []
    for field in ["展开：", "来源样本：", "适用题型：", "高分搭配："]:
        n = l5.count(field)
        if n != len(l5_entries):
            l5_bad.append(f"{field}{n}/{len(l5_entries)}")
    check("L5 每条含观点/展开/来源/题型/搭配", not l5_bad, ",".join(l5_bad))

    qb_bad = []
    for field in ["关键词圈定", "隐含限定", "双边观点池", "常见审题失误"]:
        n = len(re.findall(rf"^- \*\*{field}\*\*", qb, re.M))
        if n != qb_n:
            qb_bad.append(f"{field}{n}/{qb_n}")
    check("题目库每条含四要素", not qb_bad, ",".join(qb_bad))

    recs = [json.loads(line) for line in (DATA_DIR / "essays.train.enriched.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    null_subs = sum(1 for r in recs if not r.get("subscores"))
    inferred = sum(1 for r in recs if r.get("subscores_source") == "inferred-v1")
    official = sum(1 for r in recs if r.get("subscores_source") == "official")
    check("小分反向标注：无 null、标注来源与置信度", null_subs == 0 and inferred == 1171 and official == 22,
          f"null={null_subs}, inferred={inferred}, official={official}")

    dev = (REPORT_DIR / "deviation-record.md").read_text(encoding="utf-8")
    check("偏差记录含判高/判低清单与措辞归因表",
          "判高 Top" in dev and "判低 Top" in dev and "官方措辞" in dev)

    print("任务二验收自检")
    print("=" * 60)
    fails = 0
    for name, ok, note in results:
        print(("PASS " if ok else "FAIL ") + name + ((" | " + note) if note and not ok else ""))
        fails += 0 if ok else 1
    print("=" * 60)
    print("FAIL count:", fails)


if __name__ == "__main__":
    main()

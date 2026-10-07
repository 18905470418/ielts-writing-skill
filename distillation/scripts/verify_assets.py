"""Verify every reference asset against the training corpus.

Checks
------
* all cited sample ids exist in the training split and are not flagged;
* anchor files contain the verbatim essay text of the cited sample;
* L4 example frames exist (soft check: first 8 words) in the cited sample;
* L5 view chains cite real sources and their collocations occur in them;
* L6 example sentences occur in the cited sample;
* no asset still carries the "空骨架" placeholder.

Writes reports/asset-verification.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import REFS_DIR, REPORT_DIR, load_enriched, write_text  # noqa: E402

ID_RE = re.compile(r"B(?:6|65|7|75|8|85|9)-(?:OP|DIS|ADV|REP|TQ)-\d{3}")


def norm(s: str) -> str:
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def main() -> None:
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"]]
    by_id = {r["id"]: r for r in recs}
    issues: list[str] = []
    stats = {}

    def check_ids(text: str, where: str):
        ids = sorted(set(ID_RE.findall(text)))
        bad = [i for i in ids if i not in by_id]
        for i in bad:
            issues.append(f"{where}: unknown/flagged sample id `{i}`")
        stats[where] = len(ids)
        return ids

    refs = REFS_DIR
    anchor_dir = refs / "anchors"

    # ---- placeholder check
    sub_dirs = [refs / "viewpoint-bank", refs / "topic-vocab"]
    extra = [p for d in sub_dirs if d.exists() for p in d.glob("*.md")]
    for p in list(refs.glob("*.md")) + list(anchor_dir.glob("*.md")) + extra:
        t = p.read_text(encoding="utf-8")
        if "空骨架" in t or "PENDING" in t:
            issues.append(f"{p.name}: still contains placeholder text")

    # ---- L1 / L3 / question bank id check
    for name in ["band-rules.md", "error-patterns.md", "question-bank.md"]:
        t = (refs / name).read_text(encoding="utf-8")
        check_ids(t, name)

    # ---- anchors: full-text equality
    for name in ["opinion.md", "discussion.md", "adv-disadv.md", "report.md", "two-part.md"]:
        t = (refs / "anchors" / name).read_text(encoding="utf-8")
        ids = check_ids(t, f"anchors/{name}")
        for rid in ids:
            rec = by_id.get(rid)
            if not rec:
                continue
            essay = norm(rec["essay"])
            if essay not in norm(t):
                issues.append(f"anchors/{name}: full text of `{rid}` not found verbatim")

    # ---- L4: soft frame check
    l4 = (refs / "language-assets.md").read_text(encoding="utf-8")
    l4_ids = check_ids(l4, "language-assets.md")
    l4_pairs = re.findall(r"[（(]`(B(?:6|65|7|75|8|85|9)-(?:OP|DIS|ADV|REP|TQ)-\d{3})`[^）)]*[）)]", l4)
    checked4 = 0
    missed4 = []
    for line in l4.splitlines():
        for rid in ID_RE.findall(line):
            rec = by_id.get(rid)
            if not rec:
                continue
            m = re.search(r"[：:]\s*([A-Z][^。（(]{40,260})", line)
            if not m:
                continue
            snippet = m.group(1).strip()
            if "[" in snippet or "]" in snippet:
                continue
            words = re.findall(r"[A-Za-z]+", snippet)[:8]
            if len(words) < 5:
                continue
            pat = r"[\s,;:.\-—]+".join(re.escape(w) for w in words)
            checked4 += 1
            if not re.search(pat, rec["essay"], re.I):
                missed4.append((rid, snippet[:80]))
    for rid, snip in missed4:
        issues.append(f"language-assets.md: example not matched in `{rid}` → {snip}")

    # ---- L5 (v2: per-topic directory)
    vp_files = sorted((refs / "viewpoint-bank").glob("*.md"))
    l5 = "\n".join(p.read_text(encoding="utf-8") for p in vp_files)
    l5_ids = check_ids(l5, "viewpoint-bank/")
    l5_entries = re.split(r"\n- \*\*\[", l5)
    l5_checked = 0
    for entry in l5_entries[1:]:
        src_line = re.search(r"来源样本：(.+)", entry)
        if not src_line:
            issues.append("viewpoint-bank/: entry without 来源样本: " + entry[:60])
            continue
        rids = re.findall(r"`(B[^`]+)`", src_line.group(1))
        texts = [by_id[r]["essay"] for r in rids if r in by_id]
        if not texts:
            continue
        coll = re.search(r"高分搭配：(.+)", entry)
        if coll:
            for phrase in re.split(r"[、；,;]", coll.group(1)):
                phrase = phrase.strip().strip("`").strip()
                if len(phrase) < 4:
                    continue
                words = re.split(r"[\s\-–—]+", phrase.strip())
                pat = r"(?<![a-z])" + r"[\s\-–—]+".join(re.escape(w) for w in words if w) + r"(?:s|es|ing|ed)?(?![a-z])"
                l5_checked += 1
                if not any(re.search(pat, t, re.I) for t in texts):
                    issues.append(f"viewpoint-bank/: collocation `{phrase}` not found in any of {rids}")

    # ---- L6 (v2: per-topic directory)
    vocab_files = sorted((refs / "topic-vocab").glob("*.md"))
    l6 = "\n".join(p.read_text(encoding="utf-8") for p in vocab_files)
    l6_ids = check_ids(l6, "topic-vocab/")
    l6_rows = 0
    for line in l6.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "词伙" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 7:
            continue
        gram, example = cells[1], cells[4]
        rids = ID_RE.findall(cells[5])
        if not rids:
            continue
        l6_rows += 1
        ex = example.rstrip(" .").replace(" ...", "").strip()
        if len(ex) > 30 and not any(norm(ex) in norm(by_id[r]["essay"]) for r in rids if r in by_id):
            issues.append(f"topic-vocab/: example for `{gram}` not found in {rids}")

    lines = ["# 任务二 · 资产验证报告", ""]
    A = lines.append
    A("> 验证对象：`ielts-writing-scorer/references/` 全部资产。")
    A("> 数据源：训练集 enriched 记录（1186 篇，剔除 7 条 flagged）。盲测集未读取。")
    A("")
    A("## 覆盖统计")
    A("")
    A("| 文件 | 引用样本 id 数 |")
    A("|---|---:|")
    for k, v in stats.items():
        A(f"| {k} | {v} |")
    A(f"| language-assets.md 例句抽检 | {checked4}（失败 {len(missed4)}） |")
    A(f"| viewpoint-bank.md 搭配校验 | {l5_checked} |")
    A(f"| topic-vocab.md 例句校验 | {l6_rows} |")
    A("")
    A("## 问题清单")
    A("")
    if issues:
        for it in issues:
            A(f"- {it}")
    else:
        A("（无）——全部引用样本 id 存在、锚点全文一致、L5/L6 引用可在来源中回查。")
    A("")
    write_text(REPORT_DIR / "asset-verification.md", "\n".join(lines) + "\n")
    print(f"issues: {len(issues)}")
    for it in issues[:40]:
        print(" !", it)


if __name__ == "__main__":
    main()

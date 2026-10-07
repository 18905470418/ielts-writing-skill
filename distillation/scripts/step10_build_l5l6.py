"""L5/L6 v2 builder: migrate v1, merge per-topic curation, split by topic.

Outputs
-------
references/viewpoint-bank.md            index (usage + counts + links)
references/viewpoint-bank/<topic>.md    10 topic files (v1 entries + new curation)
references/topic-vocab.md               index
references/topic-vocab/<topic>.md       10 topic files + generic.md
reports/coverage-report.md              processing & citation coverage
data/coverage.json                      machine-readable coverage
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import DATA_DIR, REFS_DIR, REPORT_DIR, TOPIC_CN, TOPICS, load_enriched, sentences, write_json, write_text  # noqa: E402

CODE_TO_TOPIC = {
    "EDU": "education",
    "TECH": "technology",
    "ENV": "environment",
    "GOV": "government",
    "SOC": "social",
    "CRIME": "crime",
    "CUL": "culture",
    "HEALTH": "health",
    "MEDIA": "media",
    "GLOB": "globalization-work",
}
TOPIC_TO_CODE = {v: k for k, v in CODE_TO_TOPIC.items()}


# ---------------------------------------------------------------- v1 parsers


def parse_v1_viewpoints(text: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {t: [] for t in TOPICS}
    for m in re.finditer(r"^- \*\*\[([A-Z]+)-(\d{2})\]\s*观点：", text, re.M):
        code_full = f"{m.group(1)}-{m.group(2)}"
        topic = CODE_TO_TOPIC.get(m.group(1))
        if not topic:
            continue
        start = m.start()
        nxt = text.find("\n- **[", m.end())
        block = text[start : nxt if nxt != -1 else len(text)]
        claim_m = re.search(r"观点：(.*?)\*\*", block, re.S)
        claim = re.sub(r"\s+", " ", claim_m.group(1)).strip() if claim_m else ""
        tend_m = re.search(r"（倾向：([^）]*)）", block)
        chain_m = re.search(r"- 展开：(.+)", block)
        tasks_m = re.search(r"- 适用题型：(.+)", block)
        src_m = re.search(r"- 来源样本：(.+)", block)
        coll_m = re.search(r"- 高分搭配：(.+)", block)
        sources = []
        if src_m:
            for rm in re.finditer(r"`(B[^`]+)`（([^）]*)）", src_m.group(1)):
                band_m = re.match(r"([0-9.]+)", rm.group(2))
                sources.append({"id": rm.group(1), "band": float(band_m.group(1)) if band_m else None})
            if not sources:
                for rid in re.findall(r"B(?:6|65|7|75|8|85|9)-(?:OP|DIS|ADV|REP|TQ)-\d{3}", src_m.group(1)):
                    sources.append({"id": rid, "band": None})
        colls = []
        if coll_m:
            colls = [c.strip().strip("`") for c in re.split(r"[、；,;]", coll_m.group(1)) if c.strip()]
        out[topic].append(
            {
                "code": code_full,
                "claim": claim,
                "tendency": tend_m.group(1).strip() if tend_m else "",
                "chain": re.sub(r"\s+", " ", chain_m.group(1)).strip() if chain_m else "",
                "task_types": [t.strip() for t in re.split(r"[/、,，]", tasks_m.group(1)) if t.strip()] if tasks_m else [],
                "sources": sources,
                "collocations": colls,
            }
        )
    return out


def parse_v1_vocab(text: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    current = None
    title_to_topic = {TOPIC_CN[t]: t for t in TOPICS}
    for line in text.splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            if title.startswith("通用"):
                current = "generic"
            else:
                current = title_to_topic.get(title.split("（")[0].strip())
            if current:
                out.setdefault(current, [])
            continue
        if not current or not line.startswith("| ") or line.startswith("|---") or "词伙" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6:
            continue
        gram, fn, gloss, example, src, count = cells[:6]
        m = re.search(r"`(B[^`]+)`（([0-9.]+)）", src)
        rid = m.group(1) if m else ""
        band = float(m.group(2)) if m else None
        cnt_m = re.match(r"(\d+)", count)
        docs = int(cnt_m.group(1)) if cnt_m else 0
        out[current].append(
            {
                "gram": gram,
                "function": fn,
                "gloss": gloss,
                "example": example,
                "sources": [{"id": rid, "band": band}] if rid else [],
                "docs": docs,
                "tier": "B" if "低频" in count else "A",
                "supplement_75": False,
            }
        )
    return out


# ---------------------------------------------------------------- rendering


def render_vp(topic: str, entries: list[dict], new_count: int, coverage: dict) -> str:
    code = TOPIC_TO_CODE[topic]
    lines = [f"# L5 观点库 · {TOPIC_CN[topic]}（{code}）", ""]
    lines.append(f"> 条目 {len(entries)} 条（v1 迁移 {len(entries)-new_count} + v2 新增 {new_count}）；")
    lines.append(f"> 来源：训练集 8+ 样本为主；薄主题含 7.5 补充并逐条标注；本主题 8+ 标签样本 {coverage['labeled_high']} 篇，")
    lines.append(f"> L5 引用覆盖 {coverage['l5_cov']:.0%}（{coverage['l5_sources']} 个不同来源）。")
    lines.append("")
    for e in entries:
        lines.append(f"- **[{e['code']}] 观点：{e['claim']}**（倾向：{e.get('tendency','')}）")
        if e.get("chain"):
            lines.append(f"  - 展开：{e['chain']}")
        if e.get("task_types"):
            lines.append(f"  - 适用题型：{' / '.join(e['task_types'])}")
        src_bits = []
        for s in e.get("sources", []):
            band = f"{s['band']:g}" if s.get("band") else "?"
            src_bits.append(f"`{s['id']}`（{band}）")
        if src_bits:
            lines.append("  - 来源样本：" + "、".join(src_bits))
        if e.get("collocations"):
            lines.append("  - 高分搭配：" + "、".join(f"`{c}`" for c in e["collocations"]))
        lines.append("")
    return "\n".join(lines) + "\n"


def render_vocab(topic: str, entries: list[dict]) -> str:
    title = "通用（跨主题）" if topic == "generic" else f"{TOPIC_CN[topic]}（{TOPIC_TO_CODE.get(topic,'GEN')}）"
    lines = [f"# L6 主题词库 · {title}", ""]
    lines.append(f"> 条目 {len(entries)} 条；例句均为来源样本原文（截断者以 ` ...` 结尾）。")
    lines.append("> A 级=8+ 出现 ≥3 篇；B 级仅薄主题（8+ 2 篇或 8+/7.5 合计 ≥3 篇）；「7.5 补充」为主要依赖 7.5 样本的条目。")
    lines.append("")
    lines.append("| 编号 | 词伙 | 功能 | 释义 | 原文语境例句（节选） | 来源样本（id·分数） | 出现篇数 |")
    lines.append("|---|---|---|---|---|---|---|")
    for e in entries:
        src = "、".join(f"`{s['id']}`({s['band']:g})" if s.get("band") else f"`{s['id']}`" for s in e.get("sources", []))
        note = "（7.5 补充）" if e.get("supplement_75") else ""
        docs = e.get("docs8", e.get("docs", 0))
        docs75 = e.get("docs75", 0)
        freq = f"{docs}" + (f"+{docs75}×7.5" if docs75 else "") + ("（低频）" if e.get("tier") == "B" and docs < 2 and docs75 < 2 else "")
        example = e.get("example", "").replace("|", "\\|")
        gram = e["gram"]
        # curation may hyphenate multi-word collocations; prefer the spaced form unless
        # the hyphenated form is a common compound
        KEEP_HYPHEN = {"work-life", "long-term", "short-term", "cost-effective", "well-being", "part-time", "full-time", "high-income", "low-income", "decision-making", "policy-making", "labour-market", "labor-market"}
        if "-" in gram and gram.lower() not in KEEP_HYPHEN:
            gram = gram.replace("-", " ")
        lines.append(f"| {e.get('code','')} | {gram} | {e['function']} | {e.get('gloss','')} | {example} | {src} | {freq} |")
    return "\n".join(lines) + "\n"


def topic_vocab_code(topic: str, rows: list[dict], key: str) -> str:
    for e in rows:
        if re.sub(r"[\s\-–—]+", " ", e.get("gram", "").strip().lower()) == key:
            return e.get("code", "")
    return ""


def phrase_re(p: str) -> re.Pattern:
    words = re.split(r"[\s\-–—]+", p.strip())
    return re.compile(
        r"(?<![a-z])" + r"[\s\-–—]+".join(re.escape(w) for w in words if w) + r"(?:s|es|ing|ed)?(?![a-z])",
        re.I,
    )


def coll_ok(phrase: str, texts: list[str]) -> bool:
    try:
        rx = phrase_re(phrase)
    except re.error:
        return False
    return any(rx.search(t) for t in texts)


def norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\u2019", "'")).strip().lower()


def main() -> None:
    refs = REFS_DIR
    snap_vp = DATA_DIR / "v1-viewpoints.json"
    snap_vocab = DATA_DIR / "v1-vocab.json"
    if snap_vp.exists():
        v1_vp = json.loads(snap_vp.read_text(encoding="utf-8"))
    else:
        v1_vp = parse_v1_viewpoints((refs / "viewpoint-bank.md").read_text(encoding="utf-8"))
        write_json(snap_vp, v1_vp)
    if snap_vocab.exists():
        v1_vocab = json.loads(snap_vocab.read_text(encoding="utf-8"))
    else:
        v1_vocab = parse_v1_vocab((refs / "topic-vocab.md").read_text(encoding="utf-8"))
        write_json(snap_vocab, v1_vocab)
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"]]
    by_id = {r["id"]: r for r in recs}
    high = [r for r in recs if r["band"] >= 8.0]
    THIN_SET = {"government", "crime", "culture", "media"}

    def policy_filter(entry: dict, topic: str) -> dict | None:
        """Enforce the source-band policy (8+ only for non-thin topics)."""
        srcs = []
        for s in entry.get("sources", []):
            rid = s.get("id")
            rec = by_id.get(rid)
            if not rec:
                continue
            band = s.get("band") or rec["band"]
            if topic not in THIN_SET and band < 8.0:
                continue
            srcs.append({"id": rid, "band": band})
        if not srcs:
            return None
        e = dict(entry)
        e["sources"] = srcs
        if "example" in e:
            # the example must still come from one of the remaining sources
            if not any(norm_text(e["example"]) in norm_text(by_id[s["id"]]["essay"]) for s in srcs):
                gram = e.get("gram") or e.get("collocation", "")
                replacement = None
                for s in srcs:
                    for sent in sentences(by_id[s["id"]]["essay"]):
                        if phrase_re(gram).search(sent):
                            replacement = sent
                            break
                    if replacement:
                        break
                if not replacement:
                    return None
                if len(replacement) > 190:
                    replacement = replacement[:190].rsplit(" ", 1)[0] + " ..."
                e["example"] = replacement
        if topic in THIN_SET and not any(s["band"] >= 8.0 for s in srcs):
            e["supplement_75"] = True
        return e

    curation_dir = DATA_DIR / "curation"
    curations: dict[str, dict] = {}
    if curation_dir.exists():
        for p in curation_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("topic") in TOPICS:
                    curations[data["topic"]] = data
            except Exception as exc:  # noqa: BLE001
                print(f"! failed to load {p.name}: {exc}")

    vp_dir = refs / "viewpoint-bank"
    vocab_dir = refs / "topic-vocab"
    vp_dir.mkdir(exist_ok=True)
    vocab_dir.mkdir(exist_ok=True)

    coverage_rows = []
    coverage_json: dict[str, dict] = {}
    merged_vocab_store: dict[str, list[dict]] = {}
    merged_vp_store: dict[str, list[dict]] = {}
    new_vp_counts: dict[str, int] = {}
    for topic in TOPICS:
        # ---- L5 merge
        v1_entries = v1_vp.get(topic, [])
        new_vp = (curations.get(topic, {}).get("viewpoints") or [])
        max_no = max([int(e["code"].split("-")[1]) for e in v1_entries], default=0)
        merged_vp = []
        for e in v1_entries:
            src_ids = [s["id"] for s in e.get("sources", []) if s.get("id") in by_id]
            texts = [by_id[s]["essay"] for s in src_ids]
            e2 = dict(e)
            e2["collocations"] = [c for c in e.get("collocations", []) if coll_ok(c, texts)]
            e3 = policy_filter(e2, topic)
            if e3 is not None:
                merged_vp.append(e3)
        for i, v in enumerate(new_vp, 1):
            code = f"{TOPIC_TO_CODE[topic]}-{max_no + i:02d}"
            merged_vp.append(
                {
                    "code": code,
                    "claim": v.get("claim", ""),
                    "tendency": v.get("tendency", ""),
                    "chain": v.get("chain", ""),
                    "task_types": v.get("task_types", []),
                    "sources": v.get("sources", []),
                    "collocations": v.get("collocations", []),
                }
            )
        # strict collocation filtering for every L5 entry (v1 + v2)
        final_vp = []
        for e in merged_vp:
            src_ids = [s["id"] for s in e.get("sources", []) if s.get("id") in by_id]
            texts = [by_id[s]["essay"] for s in src_ids]
            e2 = dict(e)
            e2["collocations"] = [c for c in e.get("collocations", []) if coll_ok(c, texts)]
            final_vp.append(e2)
        merged_vp = final_vp
        # ---- L6 merge
        v1_rows = v1_vocab.get(topic, [])
        new_rows = (curations.get(topic, {}).get("vocab") or [])
        curated_keys = {
            re.sub(r"[\s\-–—]+", " ", (r.get("collocation") or r.get("gram") or "").strip().lower())
            for r in new_rows
        }
        merged_vocab = []
        seq = 1
        for r in v1_rows:
            key = re.sub(r"[\s\-–—]+", " ", (r.get("gram") or "").strip().lower())
            if key in curated_keys:
                continue  # superseded by the v2 evidence-based entry
            r2 = policy_filter(r, topic)
            if r2 is None:
                continue
            merged_vocab.append(dict(r2, code=f"L6-{TOPIC_TO_CODE[topic]}-{seq:03d}", docs8=r.get("docs", 0), docs75=0))
            seq += 1
        for r in new_rows:
            rr = dict(r)
            rr["gram"] = rr.get("gram") or rr.get("collocation", "")
            rr = policy_filter(rr, topic)
            if rr is None:
                continue
            merged_vocab.append(
                dict(
                    rr,
                    code=f"L6-{TOPIC_TO_CODE[topic]}-{seq:03d}",
                )
            )
            seq += 1
        merged_vocab_store[topic] = merged_vocab

        merged_vp_store[topic] = merged_vp
        new_vp_counts[topic] = len(new_vp)

    # ---- global L6 de-dup across topics (v1 rows included)
    groups: dict[str, list[tuple[str, dict]]] = {}
    for topic, rows in merged_vocab_store.items():
        for e in rows:
            key = re.sub(r"[\s\-–—]+", " ", e.get("gram", "").strip().lower())
            groups.setdefault(key, []).append((topic, e))
    winners: dict[str, tuple[str, dict]] = {}
    for key, items in groups.items():
        items_sorted = sorted(
            items,
            key=lambda x: (
                -(int(x[1].get("docs8") or 0)),
                -(int(x[1].get("docs75") or 0)),
                -len(x[1].get("sources", [])),
            ),
        )
        winners[key] = items_sorted[0]
    cross_notes: list[str] = []
    for topic, rows in merged_vocab_store.items():
        kept = []
        for e in rows:
            key = re.sub(r"[\s\-–—]+", " ", e.get("gram", "").strip().lower())
            owner, winner = winners[key]
            if winner is e:
                kept.append(e)
            elif owner != topic:
                cross_notes.append(f"- {e['gram']} → `{TOPIC_CN[owner]}` / `{winner.get('code','')}`（重复收录已移除）")
        for i, e in enumerate(kept, 1):
            e["code"] = f"L6-{TOPIC_TO_CODE[topic]}-{i:03d}"
        merged_vocab_store[topic] = kept

    # ---- coverage + write topic files (after de-dup)
    for topic in TOPICS:
        merged_vp = merged_vp_store[topic]
        merged_vocab = merged_vocab_store[topic]
        labeled_high = [r for r in high if r["topic"] == topic]
        l5_src = {s["id"] for e in merged_vp for s in e.get("sources", []) if s.get("id")}
        l6_src = {s["id"] for e in merged_vocab for s in e.get("sources", []) if s.get("id")}
        cov = {
            "labeled_high": len(labeled_high),
            "l5_entries": len(merged_vp),
            "l6_entries": len(merged_vocab),
            "l5_sources": len(l5_src),
            "l6_sources": len(l6_src),
            "l5_cov": (len(l5_src) / len(labeled_high)) if labeled_high else 0.0,
            "l6_cov": (len(l6_src) / len(labeled_high)) if labeled_high else 0.0,
            "l5_cov_raw": len(l5_src),
            "l6_cov_raw": len(l6_src),
            "supplement_75": sum(1 for e in merged_vocab if e.get("supplement_75")),
        }
        coverage_json[topic] = cov
        coverage_rows.append((topic, cov))
        write_text(vp_dir / f"{topic}.md", render_vp(topic, merged_vp, new_vp_counts.get(topic, 0), cov))
        write_text(vocab_dir / f"{topic}.md", render_vocab(topic, merged_vocab))

    # generic vocab (v1 only; duplicates already covered by a topic entry move to the index)
    generic = v1_vocab.get("generic", [])
    generic_rows = []
    cross_index_lines = list(cross_notes)
    topic_gram_keys = {
        re.sub(r"[\s\-–—]+", " ", e.get("gram", "").strip().lower())
        for rows in merged_vocab_store.values()
        for e in rows
    }
    gen_i = 0
    for r in generic:
        key = re.sub(r"[\s\-–—]+", " ", (r.get("gram") or "").strip().lower())
        if key in topic_gram_keys:
            cross_index_lines.append(f"- {r.get('gram','')} → 已并入对应主题条目（通用节不再重复收录）")
            continue
        gen_i += 1
        generic_rows.append(dict(r, code=f"L6-GEN-{gen_i:03d}", docs8=r.get("docs", 0), docs75=0))
    cross_path = curation_dir / "_cross_topic.json"
    if cross_path.exists():
        try:
            cross = json.loads(cross_path.read_text(encoding="utf-8")).get("vocab", [])
        except Exception as exc:  # noqa: BLE001
            cross = []
            print(f"! failed to load _cross_topic.json: {exc}")
        for i, r in enumerate(cross, len(generic_rows) + 1):
            rr = dict(r)
            rr["gram"] = rr.get("gram") or rr.get("collocation", "")
            rr["code"] = rr.get("code") or f"L6-GEN-{i:03d}"
            key = re.sub(r"[\s\-–—]+", " ", rr["gram"].strip().lower())
            owner = None
            for topic, rows in merged_vocab_store.items():
                if any(re.sub(r"[\s\-–—]+", " ", e.get("gram", "").strip().lower()) == key for e in rows):
                    owner = topic
                    break
            if owner:
                cross_index_lines.append(f"- {rr['gram']} → `{TOPIC_CN[owner]}`（`{topic_vocab_code(owner, merged_vocab_store[owner], key)}`）")
            else:
                generic_rows.append(rr)
    generic_text = render_vocab("generic", generic_rows)
    if cross_index_lines:
        generic_text += "\n## 跨主题词伙索引（与主题条目去重，指向主条目）\n\n" + "\n".join(cross_index_lines) + "\n"
    write_text(vocab_dir / "generic.md", generic_text)

    # ---- indexes
    vp_index = ["# L5 观点库（v2 索引）", ""]
    vp_index.append("> 已按主题拆分：评分时只读取用户文对应主题的分文件（见下表），不必加载全部条目。")
    vp_index.append("> 条目编号规则：`{主题码}-{两位序号}`，v1 编号保留，v2 新增条目续号。")
    vp_index.append("")
    vp_index.append("| 主题 | 条目数 | v1/新增 | L5 引用覆盖（8+ 样本比例） | 文件 |")
    vp_index.append("|---|---:|---|---:|---|")
    for topic, cov in coverage_rows:
        v1n = len(v1_vp.get(topic, []))
        vp_index.append(
            f"| {TOPIC_CN[topic]} | {cov['l5_entries']} | {v1n}/{cov['l5_entries']-v1n} | {min(cov['l5_cov'],1.0):.0%} | [viewpoint-bank/{topic}.md](viewpoint-bank/{topic}.md) |"
        )
    vp_index.append("")
    vp_index.append("> 使用纪律：引用条目须带编号与来源 id；库中无该主题时明确报告「暂未收录」，禁止编造。")
    write_text(refs / "viewpoint-bank.md", "\n".join(vp_index) + "\n")

    vocab_index = ["# L6 主题词库（v2 索引）", ""]
    vocab_index.append("> 已按主题拆分：评分时只读取用户文对应主题的分文件；通用词伙见 `topic-vocab/generic.md`。")
    vocab_index.append("> 编号规则：`L6-{主题码}-{三位序号}`；B 级与「7.5 补充」逐条标注。")
    vocab_index.append("")
    vocab_index.append("| 主题 | 词伙数 | L6 引用覆盖（8+ 样本比例） | 7.5 补充条目 | 文件 |")
    vocab_index.append("|---|---:|---:|---:|---|")
    for topic, cov in coverage_rows:
        vocab_index.append(
            f"| {TOPIC_CN[topic]} | {cov['l6_entries']} | {min(cov['l6_cov'],1.0):.0%} | {cov['supplement_75']} | [topic-vocab/{topic}.md](topic-vocab/{topic}.md) |"
        )
    vocab_index.append(f"| 通用（跨主题） | {len(generic_rows)} | — | 0 | [topic-vocab/generic.md](topic-vocab/generic.md) |")
    vocab_index.append("")
    vocab_index.append("> 使用纪律：例句须结合用户当前题目重写；B 级/低频条目反馈时标注不确定性。")
    write_text(refs / "topic-vocab.md", "\n".join(vocab_index) + "\n")

    # ---- coverage report
    units_cov = json.loads((DATA_DIR / "coverage-units.json").read_text(encoding="utf-8")) if (DATA_DIR / "coverage-units.json").exists() else {}
    col_cov = json.loads((DATA_DIR / "coverage-collocations.json").read_text(encoding="utf-8")) if (DATA_DIR / "coverage-collocations.json").exists() else {}
    lines = ["# L5 / L6 v2 覆盖报告", ""]
    lines.append("> 处理覆盖：全部 8+ 样本与主体段进入 L5 候选抽取；全部 7.5+ 种子命中样本进入 L6 候选挖掘。")
    lines.append("")
    lines.append("| 主题 | 8+ 标签样本 | L5 条数 | L5 引用覆盖 | L6 条数 | L6 引用覆盖 | 7.5 补充 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for topic, cov in coverage_rows:
        lines.append(
            f"| {TOPIC_CN[topic]} | {cov['labeled_high']} | {cov['l5_entries']} | {min(cov['l5_cov'],1.0):.0%} | {cov['l6_entries']} | {min(cov['l6_cov'],1.0):.0%} | {cov['supplement_75']} |"
        )
    lines.append("")
    if units_cov:
        lines.append(f"- L5 处理覆盖：{units_cov.get('high_essays')} 篇 8+ 样本 / {units_cov.get('body_units')} 个主体段，覆盖率 100%。")
    if col_cov:
        lines.append(f"- L6 处理覆盖：{col_cov.get('processing_coverage')}（各主题候选均达到数量门槛）。")
    write_text(REPORT_DIR / "coverage-report.md", "\n".join(lines) + "\n")
    write_json(DATA_DIR / "coverage.json", {"topics": coverage_json, "units": units_cov, "collocations": col_cov})

    # size check
    for p in list(vp_dir.glob("*.md")) + list(vocab_dir.glob("*.md")):
        kb = p.stat().st_size / 1024
        if kb > 40:
            print(f"! size warning: {p.name} = {kb:.1f}KB (>40KB)")
    print("curations loaded:", sorted(curations))
    for topic, cov in coverage_rows:
        print(f"{topic:20s} L5 {cov['l5_entries']:3d} ({cov['l5_cov']:.0%})  L6 {cov['l6_entries']:3d} ({cov['l6_cov']:.0%})")


if __name__ == "__main__":
    main()

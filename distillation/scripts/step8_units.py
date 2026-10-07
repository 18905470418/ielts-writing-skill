"""L5 v2 - full-corpus argument-unit extraction (all band>=8 essays).

Outputs
-------
data/units.jsonl                  one record per body-paragraph argument unit
data/units-clusters.json          de-duplicated clusters per topic
data/coverage-units.json          processing coverage per topic/essay
reports/units-<topic>[-partN].md  curation digests (split when large)
reports/units-manifest.json       digest file list per topic
"""
from __future__ import annotations

import collections
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import (  # noqa: E402
    DATA_DIR,
    EXAMPLE_RE,
    IMPLICATION_RE,
    MECHANISM_RE,
    POSITION_RE,
    REPORT_DIR,
    STOPWORDS,
    TOPICS,
    content_tokens,
    load_enriched,
    paragraphs,
    reliability_tier,
    sentences,
    short_quote,
    tokens,
    write_json,
    write_jsonl,
    write_text,
)

RELIABILITY_RANK = {"A-examiner": 0, "B-teacher": 1, "C-blog": 2, "D-auto": 3, "E-other": 4}
MAX_DIGEST_CHARS = 36000


def tag_sentence(s: str, index: int, total: int) -> str:
    if POSITION_RE.search(s):
        return "stance"
    if EXAMPLE_RE.search(s):
        return "example"
    if MECHANISM_RE.search(s) or IMPLICATION_RE.search(s):
        return "mechanism"
    if index == 0:
        return "topic"
    if index >= total - 1:
        return "linkback"
    return "explain"


def main() -> None:
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"]]
    high = [r for r in recs if r["band"] >= 8.0]
    units: list[dict] = []
    per_essay: dict[str, int] = {}
    for rec in high:
        paras = paragraphs(rec["essay"])
        if len(paras) >= 3:
            body = paras[1:-1]
        elif len(paras) == 2:
            body = paras[1:]
        else:
            body = paras[:1]
        n = 0
        for pi, p in enumerate(body):
            sents = sentences(p)
            if not sents:
                continue
            sents = [s for s in sents if len(re.findall(r"[A-Za-z]+", s)) >= 4]
            if not sents:
                continue
            n += 1
            tagged = [(s, tag_sentence(s, i, len(sents))) for i, s in enumerate(sents)]
            units.append(
                {
                    "uid": f"{rec['id']}#{pi + 1}",
                    "id": rec["id"],
                    "band": rec["band"],
                    "topic": rec["topic"],
                    "task": rec["task_type_effective"],
                    "source": rec["source"],
                    "reliability": reliability_tier(rec),
                    "question": rec["question"],
                    "para_index": pi + 1,
                    "sentences": [{"text": s, "tag": t} for s, t in tagged],
                    "text": " ".join(s for s, _ in tagged),
                }
            )
        per_essay[rec["id"]] = n
    write_jsonl(DATA_DIR / "units.jsonl", units)

    # ---------------- clustering (IDF-weighted cosine, greedy)
    cluster_output: dict[str, list[dict]] = {}
    for topic in TOPICS:
        topic_units = [u for u in units if u["topic"] == topic]
        # document frequency of tokens across units
        df = collections.Counter()
        unit_tokens: dict[str, collections.Counter] = {}
        for u in topic_units:
            c = collections.Counter(t for t in content_tokens(u["text"]) if t not in STOPWORDS and len(t) > 2)
            unit_tokens[u["uid"]] = c
            df.update(c.keys())
        total = max(1, len(topic_units))
        vecs: dict[str, dict[str, float]] = {}
        for uid, c in unit_tokens.items():
            vec = {t: (1 + math.log(n)) * math.log(total / (1 + df[t])) for t, n in c.items()}
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            vecs[uid] = {t: v / norm for t, v in vec.items()}
        # reliable-first ordering: higher band, then more reliable source
        ordered = sorted(
            topic_units,
            key=lambda u: (-u["band"], RELIABILITY_RANK.get(u["reliability"], 9), u["id"]),
        )
        clusters: list[dict] = []
        for u in ordered:
            vec = vecs[u["uid"]]
            best = None
            best_sim = 0.0
            for cl in clusters:
                rv = vecs[cl["rep"]]
                inter = set(vec) & set(rv)
                cos = sum(vec[t] * rv[t] for t in inter)
                union = set(vec) | set(rv)
                jac = len(inter) / max(1, len(union))
                sim = 0.6 * cos + 0.4 * jac
                if sim > best_sim:
                    best_sim, best = sim, cl
            if best is not None and best_sim >= 0.62:
                best["members"].append(u["uid"])
                if u["id"] not in [s["id"] for s in best["sources"]] and len(best["sources"]) < 3:
                    best["sources"].append({"id": u["id"], "band": u["band"]})
                continue
            clusters.append(
                {
                    "cluster": f"{topic[:3].upper()}-{len(clusters)+1:03d}",
                    "rep": u["uid"],
                    "id": u["id"],
                    "band": u["band"],
                    "task": u["task"],
                    "question": u["question"],
                    "sources": [{"id": u["id"], "band": u["band"]}],
                    "sentences": u["sentences"],
                    "members": [u["uid"]],
                    "similarity": round(best_sim, 3),
                }
            )
        cluster_output[topic] = clusters
    write_json(DATA_DIR / "units-clusters.json", cluster_output)

    # ---------------- digests (split when large)
    manifest: dict[str, list[str]] = {}
    for topic in TOPICS:
        clusters = cluster_output[topic]
        lines = [f"# L5 v2 论证单元候选 · {topic}", ""]
        lines.append(f"> 源：训练集 band>=8 样本；本主题聚簇 {len(clusters)} 个（摘要展示前 {min(120, len(clusters))} 个）。")
        lines.append("> 每簇给代表句链（主题句/机制/例证/回扣，最多 4 句）与合并来源；编号仅用于引用。")
        lines.append("> 完整候选可用 `distillation/scripts/query_units.py --topic " + topic + "` 检索。")
        lines.append("")
        buf: list[str] = []
        part = 1
        files: list[str] = []

        def flush():
            nonlocal buf, part
            if not buf:
                return
            name = f"units-{topic}.md" if part == 1 else f"units-{topic}-part{part}.md"
            path = REPORT_DIR / name
            write_text(path, "\n".join(lines + buf) + "\n")
            files.append(name)
            buf = []

        for cl in clusters[:120]:
            block = [f"### {cl['cluster']} · {cl['id']} · {cl['band']:g} · {cl['task']}"]
            block.append(f"- 题目：{short_quote(cl['question'], 120)}")
            by_tag: dict[str, str] = {}
            for s in cl["sentences"]:
                by_tag.setdefault(s["tag"], s["text"])
            order = [t for t in ("stance", "topic", "mechanism", "example", "linkback", "explain") if t in by_tag]
            for tag in order[:4]:
                block.append(f"- [{tag}] {short_quote(by_tag[tag], 150)}")
            block.append("- 合并来源：" + "、".join(f"{s['id']}({s['band']:g})" for s in cl["sources"]))
            block.append("")
            if sum(len(x) + 1 for x in buf) + sum(len(x) + 1 for x in block) > MAX_DIGEST_CHARS:
                flush()
                part += 1
            buf.extend(block)
        flush()
        manifest[topic] = files
    write_json(REPORT_DIR / "units-manifest.json", manifest)

    # ---------------- coverage
    topic_essays = collections.Counter(r["topic"] for r in high)
    topic_units = collections.Counter(u["topic"] for u in units)
    covered = collections.defaultdict(set)
    for u in units:
        covered[u["topic"]].add(u["id"])
    per_essay_rows = {rid: n for rid, n in per_essay.items()}
    zero_unit = [rid for rid, n in per_essay_rows.items() if n == 0]
    coverage = {
        "high_essays": len(high),
        "body_units": len(units),
        "per_essay": per_essay_rows,
        "zero_unit_essays": zero_unit,
        "topics": {
            t: {
                "high_essays": topic_essays[t],
                "essays_with_units": len(covered.get(t, set())),
                "units": topic_units[t],
                "clusters": len(cluster_output[t]),
            }
            for t in TOPICS
        },
    }
    coverage["processing_coverage"] = len(per_essay_rows) == len(high) and not zero_unit
    write_json(DATA_DIR / "coverage-units.json", coverage)

    print("essays:", len(high), "units:", len(units))
    print("clusters:", {t: len(cluster_output[t]) for t in TOPICS})
    print("digest files:", {t: manifest[t] for t in TOPICS})
    print("processing coverage 100%:", coverage["processing_coverage"])


if __name__ == "__main__":
    main()

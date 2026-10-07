"""Step 4 - evidence extraction for L2-L6 and the question bank.

Outputs (all under distillation/)
--------------------------------
data/error-pattern-stats.json         L3 detector statistics + examples
data/language-frame-candidates.json   L4 sentence-frame candidates
data/question-clusters.json           fuzzy question clusters (>=2 essays)
data/golden-groups.json               same-question multi-band control groups
data/anchor-candidates.json           typical anchor candidates per band x task
reports/viewpoint-digest.md           L5 reading digest (band>=8, by topic)
reports/error-pattern-digest.md       L3 reading digest
reports/language-frame-digest.md      L4 reading digest
reports/question-cluster-digest.md    question-bank reading digest
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import (  # noqa: E402
    BANDS,
    DATA_DIR,
    PATTERNS,
    REPORT_DIR,
    TASKS,
    TOPICS,
    compute_features,
    detect_document_patterns,
    load_enriched,
    paragraphs,
    reliability_tier,
    sentences,
    short_quote,
    write_json,
    write_text,
)

RELIABILITY_RANK = {"A-examiner": 0, "B-teacher": 1, "C-blog": 2, "D-auto": 3, "E-other": 4}

TYPICAL_FEATURES = [
    "word_count",
    "paragraph_count",
    "avg_sentence_length",
    "ttr250",
    "subordinate_density",
    "connector_density",
]

FRAMES = {
    "让步转折": [
        r"^(?:While|Although|Though|Even though|Despite|In spite of|Admittedly)\b",
        r"\bIt is true that\b.{0,160}\b(?:but|however|yet|nevertheless)\b",
    ],
    "因果机制": [
        r"\bThis is (?:largely |mainly |partly )?because\b",
        r"\b(?:This|It) (?:stems|arises|results) from\b",
        r"\bThe (?:root cause|underlying reason|main reason)\b",
        r"\b(?:because of|due to|owing to)\b[^.!?]{0,80}$",
    ],
    "例证具体化": [
        r"\bFor example,? (?!many|most|some)\w+",
        r"\bA case in point is\b",
        r"\bTo illustrate\b",
        r"\bTake [^.]{2,40} as an example\b",
    ],
    "条件与建议": [
        r"\bIf (?:governments?|policymakers?|authorities|individuals?|schools?|parents?)\b",
        r"\bUnless\b",
        r"\bProvided that\b",
        r"\b(?:One|The most effective) way to\b",
        r"\b(?:Governments?|Policymakers?|Authorities) should\b",
    ],
    "结果推进": [
        r"\bAs a result\b",
        r"\bConsequently\b",
        r"\bThis leads to\b",
        r"\bwhich in turn\b",
        r"\bthereby\b",
    ],
    "对比澄清": [
        r"\bBy contrast\b",
        r"\bWhereas\b",
        r"\bUnlike\b",
        r"\bCompared with\b",
        r"\bon the other hand\b",
    ],
    "重新框定": [
        r"\bWhat this (?:misses|overlooks|ignores)\b",
        r"\bThe (?:real|deeper|central) (?:issue|question|problem)\b",
        r"\bIt is not (?:merely|simply|just)\b",
        r"\bRather than\b",
    ],
    "立场句": [
        r"\bI (?:believe|argue|would argue|am convinced|firmly believe)\b",
        r"\bIn my (?:view|opinion)\b",
        r"\bThis essay will\b",
        r"\bMy (?:position|view) is\b",
    ],
}


def union_find_clusters(recs: list[dict]) -> list[list[dict]]:
    """Fuzzy question clustering (content-token Jaccard >= 0.75)."""
    STOP = set(
        "a an the of to in on for and or but with by is are was were be been being that this these those it its as at from their they people some many more most other others than then do does did not no also can could should would may might will shall have has had if when while which who whom whose what how why there here about into over under between among during without within across per each both all any such only even much less least very same own so too either neither nor".split()
    )

    def tset(q: str) -> set[str]:
        return {t for t in re.sub(r"[^a-z0-9 ]", " ", q.lower()).split() if t not in STOP}

    toks = {r["id"]: tset(r["question"]) for r in recs}
    parent = {r["id"]: r["id"] for r in recs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    buckets: dict[tuple, list[str]] = collections.defaultdict(list)
    for rid, t in toks.items():
        if t:
            buckets[(min(t), len(t) // 3)].append(rid)
    for rid, t in toks.items():
        if not t:
            continue
        for rid2 in buckets[(min(t), len(t) // 3)]:
            if rid2 <= rid:
                continue
            t2 = toks[rid2]
            inter = len(t & t2)
            if inter / max(1, len(t | t2)) >= 0.75:
                union(rid, rid2)
    groups: dict[str, list[dict]] = collections.defaultdict(list)
    byid = {r["id"]: r for r in recs}
    for rid in toks:
        groups[find(rid)].append(byid[rid])
    return [g for g in groups.values() if len(g) >= 2]


def main() -> None:
    recs = load_enriched()
    corpus = [r for r in recs if not r["excluded_from_distillation"]]
    vocab_proxy = None  # features for typicality are computed without vocab_df

    # ---------------- error patterns
    print("error pattern scan ...")
    stats: dict[str, dict] = {}
    mid = [r for r in corpus if 6.0 <= r["band"] <= 7.5]
    high = [r for r in corpus if r["band"] >= 8.0]
    for r in corpus:
        found = detect_document_patterns(r)
        for pid, hits in found.items():
            s = stats.setdefault(pid, {"docs": 0, "in_mid": 0, "in_high": 0, "examples": [], "bands": []})
            s["docs"] += 1
            s["bands"].append(r["band"])
            if r["band"] <= 7.5:
                s["in_mid"] += 1
            else:
                s["in_high"] += 1
            if len(s["examples"]) < 12 and hits:
                sent, match = hits[0]
                s["examples"].append({"id": r["id"], "band": r["band"], "task": r["task_type_effective"], "match": match, "sentence": short_quote(sent, 220)})
    meta = {"mid_n": len(mid), "high_n": len(high)}
    write_json(DATA_DIR / "error-pattern-stats.json", {"meta": meta, "stats": stats})

    lines: list[str] = []
    A = lines.append
    A("# L3 错误模式统计摘要（6–7.5 vs 8+）")
    A("")
    A(f"> 中档样本（6–7.5）：{len(mid)} 篇；高分样本（8+）：{len(high)} 篇。")
    A("> 命中率 = 命中篇数 / 该组篇数。示例优先取中档样本。")
    A("")
    A("| 模式 | 模块 | 中档命中率 | 高分命中率 | 差值 | 负迁移 |")
    A("|---|---|---:|---:|---:|---|")
    for pid, spec in PATTERNS.items():
        s = stats.get(pid)
        if not s:
            continue
        mid_rate = s["in_mid"] / len(mid)
        high_rate = s["in_high"] / len(high)
        A(f"| {spec['name']} (`{pid}`) | {spec['module']} | {mid_rate:.1%} | {high_rate:.1%} | {mid_rate-high_rate:+.1%} | {'是' if spec['negative_transfer'] else '否'} |")
    A("")
    for pid, spec in PATTERNS.items():
        s = stats.get(pid)
        if not s:
            continue
        A(f"## {spec['name']} (`{pid}`)")
        A("")
        A(f"- 触发信号：{spec['signal']}")
        A(f"- 修复策略：{spec['fix']}")
        A(f"- 中档命中：{s['in_mid']}/{len(mid)}（{s['in_mid']/len(mid):.1%}）；高分命中：{s['in_high']}/{len(high)}（{s['in_high']/len(high):.1%}）")
        for ex in s["examples"][:6]:
            A(f"  - `{ex['id']}`（{ex['band']}）: “{ex['sentence']}”")
        A("")
    write_text(REPORT_DIR / "error-pattern-digest.md", "\n".join(lines) + "\n")

    # ---------------- language frames
    print("language frame scan ...")
    frames: dict[str, dict[str, list[dict]]] = {f: collections.defaultdict(list) for f in FRAMES}
    for r in high:
        sents = sentences(r["essay"])
        for fam, pats in FRAMES.items():
            if len(frames[fam]["_all"]) >= 40:
                pass
            hit = None
            for s in sents:
                if any(re.search(p, s, re.I) for p in pats):
                    hit = s
                    break
            if hit and len(frames[fam][r["topic"]]) < 4 and len(frames[fam]["_all"]) < 60:
                item = {"id": r["id"], "band": r["band"], "task": r["task_type_effective"], "sentence": short_quote(hit, 260)}
                frames[fam][r["topic"]].append(item)
                frames[fam]["_all"].append(item)
    write_json(DATA_DIR / "language-frame-candidates.json", {f: {k: v for k, v in d.items() if k != "_all"} for f, d in frames.items()})
    lines = ["# L4 句式框架候选（8+ 样本，按主题采样）", ""]
    for fam, d in frames.items():
        lines.append(f"## {fam}")
        lines.append("")
        for topic, items in d.items():
            if topic == "_all":
                continue
            for it in items[:2]:
                lines.append(f"- [`{it['id']}` {it['band']}/{topic}] {it['sentence']}")
        lines.append("")
    write_text(REPORT_DIR / "language-frame-digest.md", "\n".join(lines) + "\n")

    # ---------------- viewpoint digest (L5 reading material)
    print("viewpoint digest ...")
    lines = ["# L5 观点库原始语料（band>=8，按主题）", "", "> 每个语段给出主题句 + 展开句（截断），用于人工归纳观点链条。", ""]
    digest_index = {}
    for topic in TOPICS:
        pool = [r for r in corpus if r["topic"] == topic and r["band"] >= 8.0]
        pool.sort(key=lambda r: (-r["band"], RELIABILITY_RANK.get(r["reliability_tier"], 9)))
        chosen = []
        seen_q = set()
        for r in pool:
            key = re.sub(r"\W+", " ", r["question"].lower())[:60]
            if key in seen_q:
                continue
            seen_q.add(key)
            chosen.append(r)
            if len(chosen) >= 10:
                break
        digest_index[topic] = [r["id"] for r in chosen]
        lines.append(f"## {topic}（{TOPICS.index(topic)+1}/10）")
        lines.append("")
        for r in chosen:
            paras = paragraphs(r["essay"])
            body = paras[1:-1] if len(paras) >= 3 else paras[1:]
            lines.append(f"### `{r['id']}` · {r['band']} · {r['task_type_effective']} · {r['source']}")
            lines.append(f"- Q: {short_quote(r['question'], 180)}")
            for p in body[:2]:
                sents = sentences(p)
                for s in sents[:3]:
                    lines.append(f"  - {short_quote(s, 200)}")
            lines.append("")
    write_text(REPORT_DIR / "viewpoint-digest.md", "\n".join(lines) + "\n")
    write_json(DATA_DIR / "viewpoint-digest-index.json", digest_index)

    # ---------------- question clusters
    print("question clustering ...")
    clustered = union_find_clusters(corpus)
    clusters = []
    for g in clustered:
        bands = sorted({r["band"] for r in g})
        types = sorted({r["task_type_effective"] for r in g})
        representative = max(g, key=lambda r: len(r["question"]))
        clusters.append(
            {
                "size": len(g),
                "bands": bands,
                "task_types": types,
                "ids": [r["id"] for r in sorted(g, key=lambda x: (x["band"], x["id"]))],
                "question": representative["question"],
                "members": [
                    {
                        "id": r["id"],
                        "band": r["band"],
                        "task": r["task_type_effective"],
                        "topic": r["topic"],
                        "source": r["source"],
                        "coverage": round(compute_features(r)["question_keyword_coverage"], 3),
                    }
                    for r in sorted(g, key=lambda x: (x["band"], x["id"]))
                ],
            }
        )
    clusters.sort(key=lambda c: (-c["size"], -len(c["bands"])))
    write_json(DATA_DIR / "question-clusters.json", clusters)
    lines = ["# 题目聚类摘要（训练集）", "", f"> 模糊聚类（Jaccard≥0.75）后共 {len(clusters)} 个多篇题目簇；下表按篇数排序。", ""]
    for c in clusters[:60]:
        lines.append(f"## {c['size']} 篇 · bands {c['bands']} · {c['task_types']}")
        lines.append(f"- Q: {short_quote(c['question'], 220)}")
        lines.append(f"- ids: {', '.join(c['ids'])}")
        low = [m for m in c["members"] if m["band"] <= 7.0]
        if low:
            low.sort(key=lambda m: m["coverage"])
            lines.append(f"- 低覆盖样本（审题失误候选）: " + "; ".join(f"{m['id']}(cov {m['coverage']})" for m in low[:3]))
        lines.append("")
    write_text(REPORT_DIR / "question-cluster-digest.md", "\n".join(lines) + "\n")

    # ---------------- golden groups
    golden = [
        c
        for c in clusters
        if len(c["bands"]) >= 3 and c["size"] >= 3
    ]
    golden.sort(key=lambda c: (-len(c["bands"]), -c["size"]))
    write_json(DATA_DIR / "golden-groups.json", golden)

    # ---------------- anchor candidates
    print("anchor candidates ...")
    feats = {}
    for r in corpus:
        feats[r["id"]] = compute_features(r, vocab_proxy)
    band_stats = {}
    for key in TYPICAL_FEATURES:
        per_band = {}
        for b in BANDS:
            vals = [feats[r["id"]][key] for r in corpus if r["band"] == b]
            per_band[b] = (statistics.mean(vals), statistics.pstdev(vals) or 1.0)
        band_stats[key] = per_band
    anchors = {}
    for b in BANDS:
        for t in TASKS:
            cell = [r for r in corpus if r["band"] == b and r["task_type_effective"] == t and 200 <= feats[r["id"]]["word_count"] <= 400 and feats[r["id"]]["paragraph_count"] >= 3]
            ranked = []
            for r in cell:
                z = []
                for key in TYPICAL_FEATURES:
                    mean, sd = band_stats[key][b]
                    z.append(abs((feats[r["id"]][key] - mean) / sd))
                typicality = statistics.mean(z)
                rel = RELIABILITY_RANK.get(r["reliability_tier"], 9)
                score = rel * 0.35 + typicality
                ranked.append((score, r))
            ranked.sort(key=lambda x: x[0])
            anchors[f"{b}|{t}"] = [
                {
                    "id": r["id"],
                    "band": r["band"],
                    "topic": r["topic"],
                    "source": r["source"],
                    "reliability": r["reliability_tier"],
                    "typicality": round(sc, 3),
                    "word_count": feats[r["id"]]["word_count"],
                }
                for sc, r in ranked[:6]
            ]
    write_json(DATA_DIR / "anchor-candidates.json", anchors)

    print("done")


if __name__ == "__main__":
    main()

"""L6 v2 - expanded collocation candidate mining (8+ primary, 7.5 supplement).

Outputs
-------
data/l6-candidates.json        per-topic candidate list (canonical gram, docs, example)
data/coverage-collocations.json processing coverage per topic
reports/l6-candidates-<topic>.md compact curation digests
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import (  # noqa: E402
    DATA_DIR,
    REPORT_DIR,
    STOPWORDS,
    TOPIC_CN,
    TOPIC_SEEDS,
    TOPICS,
    load_enriched,
    sentences,
    short_quote,
    write_json,
    write_text,
)

THIN_TOPICS = {"government", "crime", "culture", "media"}
MAX_DIGEST_LINES = 170

FUNCTION_RULES = [
    (re.compile(r"\b(should|must|need|invest|protect|reduce|increase|improve|promote|regulate|prohibit|guarantee|fund|subsidi|tax)\b", re.I), "措施建议"),
    (re.compile(r"\b(cause|causes|due|result|effect|impact|cost|costs|rates|growth|degradation|emissions|gap|decline|lead)\b", re.I), "原因结果"),
    (re.compile(r"\b(important|significant|effective|essential|beneficial|harmful|positive|negative|valuable|critical)\b", re.I), "评价判断"),
]


def classify(gram: str) -> str:
    for rx, label in FUNCTION_RULES:
        if rx.search(gram):
            return label
    return "观点表达"


def norm_token(t: str) -> str:
    t = t.lower()
    if t.endswith("'s"):
        t = t[:-2]
    for a, b in (
        ("behaviour", "behavior"),
        ("labour", "labor"),
        ("organisation", "organization"),
        ("organise", "organize"),
        ("programme", "program"),
        ("centre", "center"),
        ("defence", "defense"),
        ("analyse", "analyze"),
    ):
        if a in t:
            t = t.replace(a, b)
    if len(t) > 4 and t.endswith("ies"):
        return t[:-3] + "y"
    if len(t) > 4 and t.endswith(("ses", "xes", "zes", "ches", "shes")):
        return t[:-2]
    if len(t) > 4 and t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    if len(t) > 5 and t.endswith("ing"):
        base = t[:-3]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base
    if len(t) > 4 and t.endswith("ed"):
        base = t[:-2]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base
    return t


def main() -> None:
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"]]
    pool_recs = [r for r in recs if r["band"] >= 7.5]
    high = [r for r in recs if r["band"] >= 8.0]

    # tokenise once
    cache: dict[str, dict] = {}
    for rec in pool_recs:
        raw = re.findall(r"[A-Za-z][A-Za-z'\-]*", rec["essay"].lower())
        cache[rec["id"]] = {
            "norm": [norm_token(t) for t in raw],
            "surface": raw,
            "sents": sentences(rec["essay"]),
        }

    candidates: dict[str, dict[tuple, dict]] = {t: {} for t in TOPICS}
    coverage: dict[str, dict] = {}
    pool_counts: dict[str, int] = {}

    for topic in TOPICS:
        seed_re = re.compile(
            "|".join(rf"(?<![a-z]){re.escape(s)}[a-z]*(?![a-z])" for s in sorted(TOPIC_SEEDS[topic], key=len, reverse=True)),
            re.I,
        )
        wide = [r for r in pool_recs if seed_re.search(r["essay"])]
        pool_counts[topic] = len(wide)
        for rec in wide:
            c = cache[rec["id"]]
            norm, surface, sents = c["norm"], c["surface"], c["sents"]
            is_high = rec["band"] >= 8.0
            seen: set[tuple] = set()
            for n in (2, 3, 4, 5):
                for i in range(len(norm) - n + 1):
                    ng = norm[i : i + n]
                    if all(t in STOPWORDS for t in ng):
                        continue
                    if sum(1 for t in ng if t in STOPWORDS) > n - 2:
                        continue
                    if len(" ".join(ng)) < 8:
                        continue
                    if not seed_re.search(" ".join(ng)):
                        continue
                    key = tuple(t for t in ng if t not in STOPWORDS)
                    if len(key) < 2:
                        continue
                    if key in seen:
                        continue
                    seen.add(key)
                    surf = " ".join(surface[j] for j in range(i, i + n))
                    sent = next((s for s in sents if all(w in s.lower() for w in key[: min(2, len(key))])), "")
                    entry = candidates[topic].setdefault(
                        key,
                        {"variants": collections.Counter(), "docs8": 0, "docs75": 0, "examples8": [], "examples75": []},
                    )
                    entry["variants"][surf] += 1
                    if is_high:
                        entry["docs8"] += 1
                        if len(entry["examples8"]) < 3 and sent:
                            entry["examples8"].append({"id": rec["id"], "band": rec["band"], "sentence": sent})
                    else:
                        entry["docs75"] += 1
                        if len(entry["examples75"]) < 2 and sent:
                            entry["examples75"].append({"id": rec["id"], "band": rec["band"], "sentence": sent})

    out: dict[str, list[dict]] = {}
    for topic in TOPICS:
        rows = []
        for g, e in candidates[topic].items():
            docs8, docs75 = e["docs8"], e["docs75"]
            if docs8 >= 3:
                tier = "A"
            elif topic in THIN_TOPICS and (docs8 == 2 or (docs8 >= 1 and docs75 >= 2) or docs75 >= 2):
                tier = "B"
            else:
                continue
            seed_hits = sum(
                1 for t in g if any(re.match(rf"{re.escape(s)}[a-z]*$", t) for s in TOPIC_SEEDS[topic])
            )
            surface = e["variants"].most_common(1)[0][0]
            examples = e["examples8"] or e["examples75"]
            ex = sorted(examples, key=lambda x: -x["band"])[0] if examples else None
            rows.append(
                {
                    "gram": surface,
                    "norm": " ".join(g),
                    "docs8": docs8,
                    "docs75": docs75,
                    "tier": tier,
                    "supplement_75": docs8 < 2 and docs75 >= 2,
                    "seed_hits": seed_hits,
                    "function": classify(surface),
                    "example": ex,
                }
            )
        # rank: docs8 desc, tier, seed hits, length desc; drop subsumed short grams
        rows.sort(key=lambda r: (-r["docs8"], r["tier"], -r["seed_hits"], -len(r["norm"].split()), r["gram"]))
        kept: list[dict] = []
        for r in rows:
            toks = r["norm"].split()
            subsumed = False
            for k in kept:
                kt = k["norm"].split()
                if len(kt) > len(toks) and all(t in kt for t in toks) and k["docs8"] >= r["docs8"]:
                    subsumed = True
                    break
            if not subsumed:
                kept.append(r)
        out[topic] = kept[:220]
        # coverage: essays that contribute at least one kept candidate
        contributing = set()
        for r in out[topic]:
            if r["example"]:
                contributing.add(r["example"]["id"])
        coverage[topic] = {
            "pool_essays_seed": pool_counts[topic],
            "high_essays_labeled": sum(1 for r in high if r["topic"] == topic),
            "candidates": len(out[topic]),
            "tierA": sum(1 for r in out[topic] if r["tier"] == "A"),
            "tierB": sum(1 for r in out[topic] if r["tier"] == "B"),
            "supplement_75": sum(1 for r in out[topic] if r["supplement_75"]),
            "example_source_essays": len(contributing),
            "processing_ok": len(out[topic]) >= (30 if topic in THIN_TOPICS else 40),
        }
    write_json(DATA_DIR / "l6-candidates.json", out)
    coverage["processing_coverage"] = all(coverage[t]["processing_ok"] for t in TOPICS)
    write_json(DATA_DIR / "coverage-collocations.json", coverage)

    # digests
    for topic in TOPICS:
        lines = [f"# L6 v2 词伙候选 · {TOPIC_CN[topic]}（{topic}）", ""]
        lines.append(
            f"> 主题标签下 8+ 样本 {coverage[topic]['high_essays_labeled']} 篇；"
            f"种子命中池 {coverage[topic]['pool_essays_seed']} 篇（7.5+）；候选 {coverage[topic]['candidates']} 条"
            f"（A 级 {coverage[topic]['tierA']}，B 级 {coverage[topic]['tierB']}，7.5 补充 {coverage[topic]['supplement_75']}）。"
        )
        lines.append("> 每行：词伙 | 8+篇数 | 7.5篇数 | 档级 | 功能 | 例句来源")
        lines.append("")
        by_fn: dict[str, list[dict]] = collections.defaultdict(list)
        for r in out[topic]:
            by_fn[r["function"]].append(r)
        for fn in ["措施建议", "原因结果", "评价判断", "观点表达"]:
            rows = by_fn.get(fn, [])
            if not rows:
                continue
            lines.append(f"## {fn}（{len(rows)}）")
            lines.append("")
            for r in rows[:60]:
                ex = r["example"]
                ex_txt = short_quote(ex["sentence"], 130) if ex else ""
                src = f"{ex['id']}({ex['band']:g})" if ex else "-"
                lines.append(f"- {r['gram']} | 8+:{r['docs8']} | 7.5:{r['docs75']} | {r['tier']} | {src} | {ex_txt}")
            lines.append("")
        write_text(REPORT_DIR / f"l6-candidates-{topic}.md", "\n".join(lines[:MAX_DIGEST_LINES]) + "\n")

    print("candidates:", {t: len(out[t]) for t in TOPICS})
    print("coverage processing OK:", coverage["processing_coverage"])


if __name__ == "__main__":
    main()

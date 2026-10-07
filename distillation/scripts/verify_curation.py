"""Validate a per-topic curation JSON against the corpus and plan thresholds.

Usage:
  python distillation/scripts/verify_curation.py --topic education
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import DATA_DIR, REPORT_DIR, TOPICS, load_enriched, write_text  # noqa: E402

THIN_TOPICS = {"government", "crime", "culture", "media"}
FUNCTIONS = {"观点表达", "原因结果", "措施建议", "评价判断"}
TASKS = {"opinion", "discussion", "adv-disadv", "report", "two-part"}


def norm(s: str) -> str:
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"[\s\-–—]+", " ", s)
    return s.strip().lower()


def phrase_re(p: str) -> re.Pattern:
    words = re.split(r"[\s\-–—]+", p.strip())
    pat = r"[\s\-–—]+".join(re.escape(w) for w in words if w) + r"(?:s|es|ing|ed)?"
    return re.compile(pat, re.I)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    args = ap.parse_args()
    topic = args.topic
    path = DATA_DIR / "curation" / f"{topic}.json"
    results: list[tuple[bool, str]] = []
    fails: list[str] = []

    def check(ok: bool, msg: str):
        results.append((ok, msg))
        if not ok:
            fails.append(msg)

    if topic not in TOPICS:
        print("unknown topic", topic)
        sys.exit(2)
    if not path.exists():
        print("missing curation file:", path)
        sys.exit(2)

    data = json.loads(path.read_text(encoding="utf-8"))
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"]]
    by_id = {r["id"]: r for r in recs}
    high_labeled = [r for r in recs if r["band"] >= 8.0 and r["topic"] == topic]
    thin = topic in THIN_TOPICS

    check(data.get("topic") == topic, f"topic field == {topic}")
    viewpoints = data.get("viewpoints") or []
    vocab = data.get("vocab") or []
    check(len(viewpoints) >= (12 if thin else 15), f"L5 count {len(viewpoints)} >= {12 if thin else 15}")
    check(len(viewpoints) <= 20, f"L5 count {len(viewpoints)} <= 20")
    check(len(vocab) >= (30 if thin else 40), f"L6 count {len(vocab)} >= {30 if thin else 40}")
    check(len(vocab) <= 60, f"L6 count {len(vocab)} <= 60")

    l5_sources: set[str] = set()
    for i, v in enumerate(viewpoints, 1):
        tag = f"L5[{i}]"
        claim = (v.get("claim") or "").strip()
        chain = (v.get("chain") or "").strip()
        tasks = v.get("task_types") or []
        sources = v.get("sources") or []
        colls = v.get("collocations") or []
        check(bool(claim), f"{tag} claim non-empty")
        check("→" in chain or "->" in chain, f"{tag} chain uses arrows")
        check(bool(tasks) and set(tasks) <= TASKS, f"{tag} task_types valid")
        check(1 <= len(sources) <= 3, f"{tag} sources 1..3")
        for s in sources:
            rid = s.get("id", "")
            rec = by_id.get(rid)
            check(bool(rec), f"{tag} source exists: {rid}")
            if rec:
                l5_sources.add(rid)
        check(1 <= len(colls) <= 6, f"{tag} collocations 1..6")
        texts = [by_id[s["id"]]["essay"] for s in sources if s.get("id") in by_id]
        for c in colls:
            ok = any(phrase_re(c).search(t) for t in texts)
            check(ok, f"{tag} collocation in sources: {c!r}")

    strong = 0
    l6_sources: set[str] = set()
    for i, r in enumerate(vocab, 1):
        tag = f"L6[{i}]"
        gram = (r.get("collocation") or "").strip()
        fn = r.get("function")
        gloss = (r.get("gloss") or "").strip()
        sources = r.get("sources") or []
        example = (r.get("example") or "").strip()
        tier = r.get("tier")
        docs8 = int(r.get("docs8") or 0)
        docs75 = int(r.get("docs75") or 0)
        check(bool(gram) and len(gram) >= 6, f"{tag} collocation present")
        check(fn in FUNCTIONS, f"{tag} function valid: {fn!r}")
        check(bool(gloss), f"{tag} gloss non-empty")
        check(1 <= len(sources) <= 3, f"{tag} sources 1..3")
        check(tier in ("A", "B"), f"{tag} tier A/B")
        valid_src = [s for s in sources if s.get("id") in by_id]
        for s in sources:
            check(s.get("id") in by_id, f"{tag} source exists: {s.get('id')}")
            if s.get("id") in by_id:
                l6_sources.add(s["id"])
        check(len(example) >= 30, f"{tag} example length")
        clean = example.replace(" ...", "").strip()
        ok_ex = any(norm(clean) in norm(by_id[s["id"]]["essay"]) for s in valid_src)
        check(ok_ex, f"{tag} example verbatim in source")
        check(any(phrase_re(gram).search(by_id[s["id"]]["essay"]) for s in valid_src), f"{tag} gram in source")
        if tier == "A":
            check(docs8 >= 3, f"{tag} tier A docs8>=3 (got {docs8})")
        if tier == "B":
            check(thin, f"{tag} tier B only for thin topics")
            check(docs8 >= 2 or docs8 + docs75 >= 3, f"{tag} tier B evidence (8+{docs8}, 7.5+{docs75})")
        if (docs8 >= 2 or docs8 + docs75 >= 3) if thin else (docs8 + docs75 >= 3):
            strong += 1

    ratio = strong / max(1, len(vocab))
    check(ratio >= 0.80, f"strong-evidence ratio {ratio:.0%} >= 80%")
    l5_cov = len(l5_sources) / max(1, len(high_labeled))
    l6_cov = len(l6_sources) / max(1, len(high_labeled))
    check(l5_cov >= 0.40, f"L5 source coverage {l5_cov:.0%} >= 40% (of {len(high_labeled)} essays)")
    check(l6_cov >= 0.50, f"L6 source coverage {l6_cov:.0%} >= 50%")

    lines = [f"# 策展校验 · {topic}", ""]
    for ok, msg in results:
        lines.append(("PASS " if ok else "FAIL ") + msg)
    lines.append("")
    lines.append(f"结果：{'PASS' if not fails else 'FAIL'}（{len(results)-len(fails)}/{len(results)}）")
    write_text(REPORT_DIR / f"curation-verify-{topic}.md", "\n".join(lines) + "\n")
    print(f"{topic}: {'PASS' if not fails else 'FAIL'} ({len(results)-len(fails)}/{len(results)})")
    for f in fails[:25]:
        print("  !", f)
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()

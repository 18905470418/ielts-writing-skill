"""Preprocess curation JSONs before the final build:

1. L5 collocations: normalise hyphens, verify against cited sources, attach an
   extra same-topic 8+ source when the phrase exists elsewhere, drop unverifiable.
2. L6 rows: normalise grams, fix tier A/B by evidence, drop unsupported rows.
3. Global de-duplication: the same collocation kept once (highest evidence);
   cross-topic duplicates are consolidated into data/curation/_cross_topic.json
   for the generic section.

Writes cleaned curation files (originals backed up) + reports/curation-preprocess.md.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import DATA_DIR, REPORT_DIR, TOPICS, load_enriched, write_json, write_text  # noqa: E402

THIN = {"government", "crime", "culture", "media"}
KEEP_HYPHEN = {"work-life", "long-term", "short-term", "cost-effective", "well-being", "part-time", "full-time", "high-income", "low-income", "decision-making", "policy-making"}


def phrase_re(p: str) -> re.Pattern:
    words = re.split(r"[\s\-–—]+", p.strip())
    return re.compile(r"[\s\-–—]+".join(re.escape(w) for w in words if w) + r"(?:s|es|ing|ed)?", re.I)


def display_form(s: str) -> str:
    if "-" in s and s.lower() not in KEEP_HYPHEN:
        return s.replace("-", " ")
    return s


def main() -> None:
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"]]
    by_id = {r["id"]: r for r in recs}
    high_by_topic: dict[str, list[dict]] = {t: [r for r in recs if r["topic"] == t and r["band"] >= 8.0] for t in TOPICS}

    cur_dir = DATA_DIR / "curation"
    backup = cur_dir / "backup"
    backup.mkdir(exist_ok=True)
    files = sorted(p for p in cur_dir.glob("*.json") if p.name != "_cross_topic.json")

    log: list[str] = []
    data: dict[str, dict] = {}
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("topic") not in TOPICS:
            continue
        topic = d["topic"]
        shutil.copy2(p, backup / p.name)
        # ---- L5 cleaning
        new_vp = []
        for v in d.get("viewpoints", []):
            src_ids = [s["id"] for s in v.get("sources", []) if s.get("id") in by_id]
            texts = {sid: by_id[sid]["essay"] for sid in src_ids}
            kept_colls = []
            for c in v.get("collocations", []):
                c2 = display_form(c)
                if any(phrase_re(c2).search(t) for t in texts.values()):
                    kept_colls.append(c2)
                    continue
                # try to attach one more same-topic 8+ source that contains it
                found = None
                for r in high_by_topic.get(topic, []):
                    if r["id"] in src_ids:
                        continue
                    if phrase_re(c2).search(r["essay"]):
                        found = r
                        break
                if found and len(v.get("sources", [])) < 3:
                    v.setdefault("sources", []).append({"id": found["id"], "band": found["band"]})
                    kept_colls.append(c2)
                    log.append(f"{topic} L5 {v.get('claim','')[:24]}...：为 `{c2}` 增补来源 {found['id']}")
                else:
                    log.append(f"{topic} L5 丢弃无来源词伙 `{c}`")
            v["collocations"] = kept_colls
            if v.get("sources"):
                new_vp.append(v)
            else:
                log.append(f"{topic} L5 丢弃无有效来源条目：{v.get('claim','')[:40]}")
        d["viewpoints"] = new_vp
        # ---- L6 cleaning
        new_vocab = []
        for r in d.get("vocab", []):
            r["collocation"] = display_form(r.get("collocation", ""))
            docs8, docs75 = int(r.get("docs8") or 0), int(r.get("docs75") or 0)
            r["supplement_75"] = docs8 < 2 and docs75 >= 2
            if r.get("tier") == "A" and docs8 < 3:
                if topic in THIN and (docs8 >= 2 or docs8 + docs75 >= 3):
                    r["tier"] = "B"
                    log.append(f"{topic} L6 `{r['collocation']}`：A→B（8+{docs8}/7.5+{docs75}）")
                else:
                    log.append(f"{topic} L6 丢弃不达 A 级的条目 `{r['collocation']}`（8+{docs8}/7.5+{docs75}）")
                    continue
            if r.get("tier") == "B" and topic not in THIN and docs8 < 3:
                log.append(f"{topic} L6 丢弃非薄主题 B 级条目 `{r['collocation']}`")
                continue
            if r.get("sources"):
                new_vocab.append(r)
            else:
                log.append(f"{topic} L6 丢弃无来源条目 `{r['collocation']}`")
        d["vocab"] = new_vocab
        data[topic] = d

    # ---- global de-dup (keep the strongest evidence; consolidate cross-topic)
    groups: dict[str, list[tuple[str, dict]]] = {}
    for topic in TOPICS:
        for r in data.get(topic, {}).get("vocab", []):
            key = re.sub(r"[\s\-–—]+", " ", r["collocation"].strip().lower())
            groups.setdefault(key, []).append((topic, r))
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
    cross: dict[str, dict] = {}
    for topic in TOPICS:
        if topic not in data:
            continue
        kept = []
        for r in data.get(topic, {}).get("vocab", []):
            key = re.sub(r"[\s\-–—]+", " ", r["collocation"].strip().lower())
            owner_topic, winner = winners[key]
            if winner is r:
                kept.append(r)
                continue
            if owner_topic != topic:
                base = cross.setdefault(key, dict(winner))
                merged = base.setdefault("sources", list(winner.get("sources", [])))
                for s in r.get("sources", []):
                    if len(merged) < 3 and s not in merged:
                        merged.append(s)
                base["docs8"] = max(int(base.get("docs8") or 0), int(r.get("docs8") or 0))
                base["docs75"] = max(int(base.get("docs75") or 0), int(r.get("docs75") or 0))
                log.append(f"跨主题重复 `{r['collocation']}`：保留 {owner_topic}，合并 {topic}")
            else:
                log.append(f"{topic} 主题内重复 `{r['collocation']}`：保留证据最强的一条")
        data[topic]["vocab"] = kept

    # write cleaned files
    for topic, d in data.items():
        write_json(cur_dir / f"{topic}.json", d)
    cross_rows = []
    seq = 0
    for key, r in cross.items():
        rr = dict(r)
        seq += 1
        rr["collocation"] = display_form(rr.get("collocation", ""))
        rr["code"] = f"L6-GEN-{100+seq:03d}"
        cross_rows.append(rr)
    write_json(cur_dir / "_cross_topic.json", {"topic": "generic", "vocab": cross_rows})

    lines = ["# 策展预处理报告", "", f"- 处理主题 {len(data)} 个；跨主题去重 {len(cross_rows)} 条；调整/丢弃 {len(log)} 项。", ""]
    lines += log[:200]
    write_text(REPORT_DIR / "curation-preprocess.md", "\n".join(lines) + "\n")
    print(f"topics {len(data)}, cross-topic {len(cross_rows)}, adjustments {len(log)}")


if __name__ == "__main__":
    main()

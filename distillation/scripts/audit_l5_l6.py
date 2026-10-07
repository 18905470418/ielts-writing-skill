"""Draw the 10% audit sample for L5/L6 and emit a review pack."""
from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import REFS_DIR, REPORT_DIR, load_enriched, paragraphs, sentences, short_quote, write_text  # noqa: E402

ID_RE = re.compile(r"B(?:6|65|7|75|8|85|9)-(?:OP|DIS|ADV|REP|TQ)-\d{3}")


def main() -> None:
    recs = {r["id"]: r for r in load_enriched() if not r["excluded_from_distillation"]}
    items: list[dict] = []
    for p in sorted((REFS_DIR / "viewpoint-bank").glob("*.md")):
        topic = p.stem
        text = p.read_text(encoding="utf-8")
        for entry in re.split(r"\n- \*\*\[", text)[1:]:
            code = entry.split("]", 1)[0]
            m = re.search(r"来源样本：`(B[^`]+)`", entry)
            if not m:
                continue
            items.append(
                {"kind": "L5", "topic": topic, "code": code, "id": m.group(1), "claim": short_quote(entry.split("**（倾向", 1)[0], 220)}
            )
    for p in sorted((REFS_DIR / "topic-vocab").glob("*.md")):
        topic = p.stem
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|") or line.startswith("|---") or "词伙" in line:
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 7:
                continue
            m = ID_RE.search(cells[5])
            if not m:
                continue
            items.append({"kind": "L6", "topic": topic, "code": cells[0], "id": m.group(0), "claim": cells[3]})

    rng = random.Random(20261007)
    # stratified: up to 2 per (kind, topic) -> ~40 items, at least 30
    sample: list[dict] = []
    groups: dict[tuple, list[dict]] = {}
    for it in items:
        groups.setdefault((it["kind"], it["topic"]), []).append(it)
    for key, rows in sorted(groups.items()):
        sample.extend(rng.sample(rows, min(2, len(rows))))
    if len(sample) < 30:
        pool = [i for i in items if i not in sample]
        sample.extend(rng.sample(pool, min(len(pool), 30 - len(sample))))
    sample.sort(key=lambda x: (x["kind"], x["topic"], x["id"], x["code"]))

    lines = ["# L5 / L6 质量抽检包（分层 ≥30 条）", "", f"> 总条目 {len(items)}；抽样 {len(sample)} 条（按主题 × L5/L6 分层）；随机种子 20261007。", ""]
    for i, it in enumerate(sample, 1):
        rec = recs.get(it["id"])
        lines.append(f"## AUD-{i:02d} · {it['kind']} · {it['topic']} · `{it['code']}` ← `{it['id']}`")
        lines.append("")
        lines.append(f"- 库内内容：{it['claim']}")
        if rec:
            body = paragraphs(rec["essay"])
            excerpt = " ".join(body[1:3]) if len(body) > 2 else rec["essay"]
            lines.append(f"- 原文相关段（节选）：{short_quote(excerpt, 420)}")
            lines.append(f"- 来源：{rec['source']} · Band {rec['band']:g} · {rec['task_type_effective']} · {rec['topic']}")
        lines.append("")
    write_text(REPORT_DIR / "l5-l6-audit-pack.md", "\n".join(lines) + "\n")
    print("items:", len(items), "sample:", len(sample))


if __name__ == "__main__":
    main()

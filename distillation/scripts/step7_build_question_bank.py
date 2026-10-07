"""Build question-bank.md from fuzzy question clusters (train only)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import (  # noqa: E402
    DATA_DIR,
    REFS_DIR,
    TOPIC_CN,
    load_enriched,
    paragraphs,
    sentences,
    short_quote,
    write_text,
)

L5_LINKS = {
    "education": ["EDU-01", "EDU-02", "EDU-04"],
    "technology": ["TECH-01", "TECH-02", "TECH-03"],
    "environment": ["ENV-01", "ENV-02", "ENV-04"],
    "government": ["GOV-01", "GOV-03", "GOV-04"],
    "social": ["SOC-01", "SOC-04", "SOC-05"],
    "crime": ["CRIME-01", "CRIME-02", "CRIME-03"],
    "culture": ["CUL-01", "CUL-02", "CUL-03"],
    "health": ["HEALTH-01", "HEALTH-02", "HEALTH-04"],
    "media": ["MEDIA-01", "MEDIA-03", "MEDIA-05"],
    "globalization-work": ["GLOB-01", "GLOB-03", "GLOB-05"],
}

QUALIFIERS = [
    ("only", "only（排他限定）"),
    ("best", "best（最优断言）"),
    ("most important", "most important（最高级）"),
    ("the main", "the main（主因/主渠道）"),
    ("always", "always（全称）"),
    ("never", "never（全称）"),
    ("all ", "all（全量）"),
    ("in some countries", "in some countries（范围限定）"),
    ("in many countries", "in many countries（范围限定）"),
    ("young people", "young people（对象限定）"),
    ("children", "children（对象限定）"),
    ("should", "should（规范性主张）"),
    ("outweigh", "outweigh（比较结构）"),
    ("to what extent", "to what extent（程度限定）"),
    ("positive or negative", "positive/negative（评价方向）"),
]


def qualifiers(q: str) -> list[str]:
    ql = q.lower()
    return [label for key, label in QUALIFIERS if key in ql]


def aspect_pool(q: str, task_types: list[str]) -> tuple[str, str]:
    """Return (side A, side B) descriptions appropriate for the task type."""
    text = re.sub(r"\s+", " ", q).strip()
    if "discussion" in task_types:
        m = re.search(
            r"(some people[^?]{10,220}?)[,.;]?\s*(?:while|whereas)\s*(others?[^?]{10,220})(?:\?|$)",
            text,
            re.I,
        )
        if m:
            return short_quote(m.group(1), 160), short_quote(m.group(2), 160)
        m = re.search(r"(some people[^?]{10,200}?)[,.;]?\s*(?:others?[^?]{10,200}?)(?:\?|$)", text, re.I)
        if m:
            return short_quote(m.group(1), 160), "题干后半部分的对立主张"
        return "A 方：题干前半部分主张", "B 方：题干后半部分主张"
    if "two-part" in task_types:
        asks = [s.strip(" .") for s in re.split(r"\?", text) if s.strip(" .")]
        if len(asks) >= 2:
            return f"设问 1：{short_quote(asks[0], 150)}", f"设问 2：{short_quote(asks[1], 150)}"
        m = re.search(r"(.{10,200}?)\s*,?\s*and\s+(is it.{5,120})$", text, re.I)
        if m:
            return f"设问 1：{short_quote(m.group(1), 150)}", f"设问 2：{short_quote(m.group(2), 150)}"
        return "设问 1：题干第一个问题", "设问 2：题干第二个问题"
    if "adv-disadv" in task_types:
        return "收益方（advantages / positive）", "成本方（disadvantages / negative）"
    if "report" in task_types:
        return "原因 / 问题机制", "措施 / 建议"
    return "支持题干主张", "反对或限定题干主张（有条件同意）"


def keywords(q: str, k: int = 7) -> list[str]:
    from distill_lib import content_tokens

    seen = []
    for t in content_tokens(q):
        if len(t) > 3 and t not in seen:
            seen.append(t)
    return seen[:k]


def mistake_case(members: list[dict], recs: dict) -> str:
    lows = [m for m in members if m["band"] <= 6.5 and m.get("coverage", 1.0) <= 0.45]
    if not lows:
        return "（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）"
    lows.sort(key=lambda m: m.get("coverage", 1))
    m = lows[0]
    rec = recs.get(m["id"])
    if not rec:
        return ""
    paras = paragraphs(rec["essay"])
    intro = sentences(paras[0])[:2] if paras else []
    quote = short_quote(" ".join(intro), 170)
    return f"`{m['id']}`（{m['band']}，关键词覆盖 {m.get('coverage',0):.0%}）开头：「{quote}」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。"


def main() -> None:
    clusters = json.loads((DATA_DIR / "question-clusters.json").read_text(encoding="utf-8"))
    recs = {r["id"]: r for r in load_enriched()}
    selected = [c for c in clusters if c["size"] >= 3]
    lines: list[str] = []
    A = lines.append
    A("# 题目解析库（审题要点）")
    A("")
    A("> **层级**：增强项 · 题目解析（服务于「审题前置」）。")
    A("> **来源**：任务二从训练集聚类（模糊聚类 Jaccard≥0.75）后整理；每题给出真实样本 id。")
    A("> **加载时机**：评分流程最前端的「审题前置」：先按题目关键词/题型检索；未命中时现场生成审题要点并追加回本库。")
    A(f"> **覆盖**：训练集内出现 ≥3 篇的题目簇 {len(selected)} 个（另有多篇簇收录于 `distillation/data/question-clusters.json`）。")
    A("")
    A("## 使用说明")
    A("")
    A("1. 每条的「隐含限定」是 TR 的第一证据：未回应限定词时 TR 封顶 6.5（参见 `band-rules.md` L1-TR-6.3 / 65.3 / 75.3）。")
    A("2. 「常见审题失误」列出该题真实低档样本的覆盖缺口；反馈时对照用户作文逐项检查。")
    A("3. 「双边观点池」给出可展开维度与 L5 观点库入口；引用时须带 L5 编号。")
    A("4. 运行时遇到库中未收录的题目：按同一格式现场生成（标注 `source: runtime-generated` 与日期）并追加。")
    A("")
    for i, c in enumerate(selected, 1):
        q = c["question"]
        task = "/".join(c["task_types"])
        topics = sorted({recs[m["id"]]["topic"] for m in c["members"] if m["id"] in recs})
        topic_cn = "、".join(TOPIC_CN.get(t, t) for t in topics)
        kw = keywords(q)
        qls = qualifiers(q)
        sa, sb = aspect_pool(q, c["task_types"])
        A(f"## QB-{i:03d}｜{short_quote(q, 130)}")
        A("")
        A(f"- **指纹**：题型 {task}；主题 {topic_cn}；样本 {c['ids'][0]} 等 {c['size']} 篇")
        A(f"- **关键词圈定**：{', '.join('`'+k+'`' for k in kw)}")
        if qls:
            A(f"- **隐含限定**：{'；'.join(qls)}。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。")
        else:
            A("- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。")
        A(f"- **双边观点池**：A——{sa}；B——{sb}。可展开维度见 L5 条目 {', '.join(L5_LINKS.get(topics[0], []) if topics else [])}。")
        A(f"- **常见审题失误**：{mistake_case(c['members'], recs)}")
        dist_cells = []
        for m in c["members"]:
            dist_cells.append(f"{m['band']:g}·`{m['id']}`")
        A("- **样本分布**：" + "；".join(dist_cells))
        A("")
    write_text(REFS_DIR / "question-bank.md", "\n".join(lines) + "\n")
    print("entries:", len(selected))


if __name__ == "__main__":
    main()

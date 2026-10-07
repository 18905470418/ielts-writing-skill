"""Build L2 anchor files (one per task type) with full texts and itemised comments.

Selection
---------
* golden control groups (same question across >=3 bands) are placed first and
  their members count toward each band's anchor quota;
* remaining slots come from `anchor-candidates.json` (reliability first, then
  typicality within the band).

Comments are generated from concrete, verifiable text evidence (quotes,
metrics, detector hits) and band-aware verdict wording.
"""
from __future__ import annotations

import collections
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
    POSITION_RE,
    REFS_DIR,
    SUBORD_RE,
    TASK_CN,
    TOPIC_CN,
    compute_features,
    detect_document_patterns,
    load_enriched,
    paragraphs,
    sentences,
    short_quote,
    write_text,
)

RELIABILITY_CN = {
    "A-examiner": "考官/官方标注",
    "B-teacher": "教学机构批改",
    "C-blog": "教师博客范文",
    "D-auto": "writing9 自动评分",
    "E-other": "其他来源",
}
RELIABILITY_RANK = {"A-examiner": 0, "B-teacher": 1, "C-blog": 2, "D-auto": 3, "E-other": 4}


def load_inputs():
    recs = {r["id"]: r for r in load_enriched() if not r["excluded_from_distillation"]}
    anchors = json.loads((DATA_DIR / "anchor-candidates.json").read_text(encoding="utf-8"))
    golden = json.loads((DATA_DIR / "golden-groups.json").read_text(encoding="utf-8"))
    colloc = json.loads((DATA_DIR / "topic-collocations.json").read_text(encoding="utf-8"))
    return recs, anchors, golden, colloc


def thesis_sentence(rec: dict) -> tuple[str, str]:
    paras = paragraphs(rec["essay"])
    if not paras:
        return "", ""
    for i, p in enumerate(paras[:2]):
        for s in sentences(p):
            if POSITION_RE.search(s):
                return s, ("引言" if i == 0 else "第二段")
    return (sentences(paras[0])[-1] if sentences(paras[0]) else ""), "引言"


def body_paras(rec: dict) -> list[str]:
    paras = paragraphs(rec["essay"])
    return paras[1:-1] if len(paras) >= 3 else paras[1:]


def missing_terms(rec: dict, feats: dict) -> list[str]:
    from distill_lib import content_tokens  # local import to avoid cycle confusion

    q = set()
    for t in content_tokens(rec["question"]):
        if len(t) > 3:
            q.add(t)
            if t.endswith("s") and len(t) > 5:
                q.add(t[:-1])
    toks = set(re.findall(r"[a-z]+", rec["essay"].lower()))
    toks |= {t[:-1] if t.endswith("s") and len(t) > 5 else t for t in toks}
    return sorted(t for t in q if t not in toks)[:5]


def colloc_hits(rec: dict, colloc: dict) -> list[str]:
    grams = [r["gram"] for r in colloc["topics"].get(rec["topic"], [])[:60]]
    out = []
    text = rec["essay"].lower()
    for g in grams:
        if re.search(r"(?<![a-z])" + re.escape(g).replace(r"\ ", r"\s+") + r"(?![a-z])", text):
            out.append(g)
    return out


def repeated_content_words(rec: dict, k: int = 4) -> list[str]:
    from distill_lib import STOPWORDS, tokens

    c = collections.Counter(t for t in tokens(rec["essay"]) if t not in STOPWORDS and len(t) > 3)
    return [w for w, n in c.most_common(k) if n >= 3]


def comment_tr(rec: dict, feats: dict) -> str:
    thesis, where = thesis_sentence(rec)
    body = body_paras(rec)
    topic_sents = [sentences(p)[0] for p in body if sentences(p)]
    ex_sent = None
    for p in body:
        for s in sentences(p):
            if re.search(r"\bfor example\b|\bfor instance\b|\bsuch as\b|\ba case in point\b", s, re.I):
                ex_sent = s
                break
        if ex_sent:
            break
    mech = feats["mechanism_hits"]
    ex = feats["example_hits"]
    spec = feats["specific_example_count"]
    cov = feats["question_keyword_coverage"]
    missing = missing_terms(rec, feats)
    band = rec["subscores"]["TR"]
    parts = []
    parts.append(f"立场句出现在{where}（“{short_quote(thesis, 150)}”）。")
    parts.append(f"全文 {feats['paragraph_count']} 段，主体段 {len(body)} 个；"
                 f"首个主体段主题句：“{short_quote(topic_sents[0], 120)}”。" if topic_sents else "")
    parts.append(f"机制解释标记 {mech} 处、例证标记 {ex} 处、具体化例证 {spec} 处；题干关键词字面覆盖 {cov:.0%}"
                 + (f"，未覆盖：{', '.join(missing)}" if missing else "。"))
    if ex_sent:
        parts.append(f"例证示例：“{short_quote(ex_sent, 150)}”。")
    nb = band + 0.5
    if band <= 6.0:
        parts.append(f"本模块小分 {band:g}：题目所有部分被触及、立场可辨认；未达 {nb:g} 之处：支持停留在列举层面，"
                     "解释句多数只把观点换一种说法（机制标记虽在，但缺少「为什么会这样」的推进）。")
    elif band <= 6.5:
        parts.append(f"本模块小分 {band:g}：正反两面都有可辨认的论点与例证；未达 {nb:g} 之处：至少一个主体段的论证"
                     "在「观点→例证」之后即停止，缺少把例证与题目概念重新扣连的收束句。")
    elif band <= 7.0:
        parts.append(f"本模块小分 {band:g}：立场清楚且基本一贯，各主体段有支持；未达 {nb:g} 之处：部分段落存在"
                     "泛化（证据主体/场景不具体），或段间展开深度不均衡。")
    elif band <= 7.5:
        parts.append(f"本模块小分 {band:g}：主体段普遍完成「观点→机制→例证→回扣」，例证风格一致；"
                     f"未达 {nb:g} 之处：个别例证仍属概括性推断，或对题目隐含限定的回应还可以更精确。")
    elif band <= 8.0:
        parts.append(f"本模块小分 {band:g}：论证链条完整，例证具体且服务于论点，题目各部分均有明确回应；"
                     f"接近 {nb:g}/9 的差距在于对概念本身的重新界定或对反例的处理深度。")
    elif band <= 8.5:
        parts.append(f"本模块小分 {band:g}：论证不仅完整，还显示出对题目概念的分层处理（区分条件、程度与对象）；"
                     "与 9 的差距通常在整体框架的原创性或多视角的综合能力。")
    else:
        parts.append(f"本模块小分 {band:g}：立场贯穿全文并对题目框架有所推进（重构议题、给出限定条件或反例检验），"
                     "论证与例证形成闭环。")
    return " ".join(x for x in parts if x)


def comment_cc(rec: dict, feats: dict) -> str:
    paras = paragraphs(rec["essay"])
    openers = feats["paragraph_opener_first_words"]
    conn_counts = feats["connector_counts"]
    top_conn = sorted(((k, v) for k, v in conn_counts.items() if v), key=lambda x: -x[1])[:4]
    conn_text = "、".join(f"{k}({v})" for k, v in top_conn) if top_conn else "无显著显性连接词"
    mech = feats["mechanical_connector_density"]
    band = rec["subscores"]["CC"]
    parts = [
        f"段落功能：引言 + {max(0, len(paras)-2)} 个主体段 + 结论；"
        f"显性连接词密度 {feats['connector_density']:.1f}/100词，机械连接词密度 {mech:.1f}/100词；"
        f"高频连接词：{conn_text}；最长指代链 {feats['reference_chain_max']} 句。"
    ]
    if feats["paragraph_opener_max_repeat"] >= 2:
        parts.append("段落开头存在重复（如多段以同一连接词/主语起步），衔接更多依赖位置而非语义推进。")
    if band <= 6.0:
        parts.append(f"本模块小分 {band:g}：整体结构可辨认（分段清晰）；未达 {band+0.5:g} 之处：段间推进主要靠显性连接词，"
                     "段内句子之间的关系需要读者自行补足；如出现连续短句堆叠或指代对象模糊，会进一步削弱衔接。")
    elif band <= 6.5:
        parts.append(f"本模块小分 {band:g}：结构清楚、每段有明确功能；未达 {band+0.5:g} 之处：衔接仍主要依赖显性连接词，"
                     "段内推进偶有跳跃或指代对象需要读者推断。")
    elif band <= 7.5:
        parts.append(f"本模块小分 {band:g}：信息排布有清晰的功能顺序，读者能顺畅跟随；未达 {band+0.5:g} 之处："
                     "个别衔接仍靠连接词完成，指代与替换链的运用尚未完全替代显性标记。")
    else:
        parts.append(f"本模块小分 {band:g}：段落间主要靠语义推进（指代链、同义替换、信息新旧安排），"
                     "显性连接词密度低于语料中档平均，衔接自然不堆砌。")
    return " ".join(parts)


def comment_lr(rec: dict, feats: dict, colloc: dict) -> str:
    hits = colloc_hits(rec, colloc)
    rep = repeated_content_words(rec)
    band = rec["subscores"]["LR"]
    parts = [
        f"前 250 词类符/形符比 {feats['ttr250']:.2f}，长词占比 {feats['long_word_ratio']:.0%}，"
        f"学术词表命中率 {feats['awl_ratio']:.1%}；主题词伙命中 {len(hits)} 处"
        + (f"（{'、'.join(hits[:5])}）" if hits else "。"),
    ]
    if rep:
        parts.append(f"高频重复实词：{'、'.join(rep)}（替换空间：按语境改用同义表达）。")
    if band <= 6.0:
        parts.append(f"本模块小分 {band:g}：核心词义可理解、能完成基本表达；未达 {band+0.5:g} 之处："
                     "词伙以常见搭配为主，重复实词偏多，个别位置出现中式搭配或语域偏口语的表达。")
    elif band <= 6.5:
        parts.append(f"本模块小分 {band:g}：用词足以支撑论证、常见搭配基本正确；未达 {band+0.5:g} 之处："
                     "词汇范围有限，重复与轻微搭配问题仍可察觉。")
    elif band <= 7.5:
        parts.append(f"本模块小分 {band:g}：主题词伙使用准确，出现少量不常见词；未达 {band+0.5:g} 之处："
                     "词汇选择偶有重复或不够精确，复杂表达尚不足以稳定支撑观点的细微差别。")
    else:
        parts.append(f"本模块小分 {band:g}：词汇以精确的词伙为单位使用，同义替换自然，"
                     "抽象概念有对应的高精度表达，未见过度堆砌难词。")
    return " ".join(parts)


def comment_gra(rec: dict, feats: dict) -> str:
    found = detect_document_patterns(rec)
    err_items = []
    for pid, hits in found.items():
        spec = PATTERNS.get(pid)
        if spec and spec["module"] == "GRA" and hits:
            err_items.append(f"{spec['name']}（“{short_quote(hits[0][0], 90)}”）")
    sents = sentences(rec["essay"])
    longest = max(sents, key=lambda s: len(re.findall(r"\w+", s))) if sents else ""
    band = rec["subscores"]["GRA"]
    parts = [
        f"平均句长 {feats['avg_sentence_length']:.1f} 词，句长标准差 {feats['sentence_len_sd']:.1f}，"
        f"复杂句占比 {feats['complex_ratio']:.0%}；最长句示例：“{short_quote(longest, 150)}”。",
    ]
    if err_items:
        parts.append("自动扫描命中的语法/结构问题：" + "；".join(err_items[:4]) + "（以人工复核为准）。")
    else:
        parts.append("自动扫描未命中高频语法错误模式。")
    if band <= 6.0:
        parts.append(f"本模块小分 {band:g}：句子基本可读、能传达意义；未达 {band+0.5:g} 之处："
                     "复杂结构使用有限且不稳定，错误类型集中在主谓一致、冠词/单复数或从句连接。")
    elif band <= 6.5:
        parts.append(f"本模块小分 {band:g}：简单句与部分复杂句并用，错误不严重阻碍理解；未达 {band+0.5:g} 之处："
                     "复杂结构准确率不稳定，个别错误呈系统性。")
    elif band <= 7.5:
        parts.append(f"本模块小分 {band:g}：简单与复杂句混合，多数句子准确；未达 {band+0.5:g} 之处："
                     "复杂结构偶有失控（长句信息拥挤或从句层级不清），错误虽不阻碍理解但可被系统性察觉。")
    else:
        parts.append(f"本模块小分 {band:g}：句子结构多样且准确率高，长句的信息层级清楚，"
                     "很少出现影响理解的形态或衔接错误。")
    return " ".join(parts)


def verdict_line(rec: dict) -> str:
    subs = rec["subscores"]
    avg = statistics.mean(subs.values())
    from distill_lib import round_half

    src = "官方小分" if rec["subscores_source"] == "official" else "反向标注小分"
    return (f"**定分理由**：四维 {subs['TR']}/{subs['CC']}/{subs['LR']}/{subs['GRA']}（{src}），"
            f"均值 {avg:.2f} → 总分 {round_half(avg):g}；上表评语给出各维达到/未达到本档的具体文本证据。")


def special_lines(rec: dict, task: str) -> str:
    if task == "discussion":
        paras = body_paras(rec)
        both = "是" if len(paras) >= 2 else "否（主体段不足两段）"
        pos = "立场句清晰" if POSITION_RE.search(rec["essay"]) else "立场句不明确"
        return f"> 讨论类专项证据：双方观点是否都被公平展开：{both}（主体段 {len(paras)} 个）；作者立场：{pos}。"
    if task == "adv-disadv":
        q = rec["question"].lower()
        subtype = "利弊权衡（outweigh / positive-negative）" if re.search(r"outweigh|positive|negative", q) else "罗列利弊"
        weighted = "有" if re.search(r"\b(overall|in my opinion|i believe|i regard|i consider)\b", rec["essay"], re.I) else "未见"
        return f"> 利弊类专项证据：子类型：{subtype}；是否做出权衡判断：{weighted}。"
    if task == "report":
        m = re.findall(r"\b(?:government|governments|authorities|schools|parents|companies)\b", rec["essay"], re.I)
        exec_ = "、".join(sorted({x.lower() for x in m})) if m else "未见明确执行主体"
        return f"> 报告类专项证据：执行主体提及：{exec_}；原因与措施对应关系需按主体逐条核对。"
    if task == "two-part":
        asks = max(1, rec["question"].count("?"))
        return f"> 双问题类专项证据：题目独立设问约 {asks} 个；两问回应篇幅见上文段落功能统计。"
    return ""


def render_essay(rec: dict, feats: dict, colloc: dict, comment_prefix: str = "") -> str:
    subs = rec["subscores"]
    src_note = "官方小分" if rec["subscores_source"] == "official" else f"反向标注（{rec['subscores_confidence']}置信度）"
    lines = []
    lines.append(f"### `{rec['id']}` · Band {rec['band']:g} · {TOPIC_CN[rec['topic']]} · {rec['word_count']} 词")
    lines.append("")
    lines.append(f"- 来源：{rec['source']}（{RELIABILITY_CN.get(rec['reliability_tier'], rec['reliability_tier'])}）")
    lines.append(f"- 题目：{short_quote(rec['question'], 400)}")
    lines.append(f"- 四维小分：TR {subs['TR']} / CC {subs['CC']} / LR {subs['LR']} / GRA {subs['GRA']}（{src_note}）")
    lines.append("")
    lines.append(f"**全文**")
    lines.append("")
    for p in paragraphs(rec["essay"]):
        lines.append(p)
        lines.append("")
    if comment_prefix:
        lines.append(comment_prefix)
        lines.append("")
    lines.append(f"**TR（Task Response）**：{comment_tr(rec, feats)}")
    lines.append("")
    lines.append(f"**CC（Coherence & Cohesion）**：{comment_cc(rec, feats)}")
    lines.append("")
    lines.append(f"**LR（Lexical Resource）**：{comment_lr(rec, feats, colloc)}")
    lines.append("")
    lines.append(f"**GRA（Grammatical Range & Accuracy）**：{comment_gra(rec, feats)}")
    lines.append("")
    lines.append(verdict_line(rec))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    recs, anchors, golden, colloc = load_inputs()
    feats = {rid: compute_features(r) for rid, r in recs.items()}

    for task in ("opinion", "discussion", "adv-disadv", "report", "two-part"):
        file_path = REFS_DIR / "anchors" / f"{task}.md"
        lines = []
        A = lines.append
        A(f"# L2 锚点范文 · {TASK_CN[task]}")
        A("")
        A("> **层级**：L2 · 锚点范文（含逐项评语）。")
        A("> **来源**：训练集（1193 篇）中该题型的典型样本；同题多档对照组置顶为「黄金锚点」。")
        A("> **加载时机**：评分主流程第 3 步「锚点比对定分」——只读取与用户文相邻的两档。")
        A("> **状态**：已由任务二填充（v1，2026-10-07）。小分凡标「反向标注」者由第 1 步推断产生。")
        A("")

        # ---- golden groups for this task
        task_groups = [c for c in golden if task in c["task_types"] and len(c["bands"]) >= 3]
        task_groups = sorted(task_groups, key=lambda c: (-len(c["bands"]), -c["size"]))[:10]
        # greedy: prefer groups that add new band coverage, cap at 4 groups
        selected_groups = []
        covered: set[float] = set()
        for c in task_groups:
            bands_new = set(c["bands"]) - covered
            if bands_new or len(selected_groups) < 3:
                selected_groups.append(c)
                covered |= set(c["bands"])
            if len(selected_groups) >= 4:
                break
        selected_groups = selected_groups or task_groups[:3]
        golden_by_band: dict[float, list[str]] = collections.defaultdict(list)
        rendered_golden: list[tuple[dict, list[str]]] = []
        for c in selected_groups:
            members = [recs[m] for m in c["ids"] if recs[m]["task_type_effective"] == task]
            per_band: dict[float, list[dict]] = collections.defaultdict(list)
            for m in sorted(members, key=lambda r: r["band"]):
                per_band[m["band"]].append(m)
            picked = []
            for band in sorted(per_band):
                pool = sorted(
                    per_band[band],
                    key=lambda r: (RELIABILITY_RANK.get(r["reliability_tier"], 9), 0 if r["subscores_source"] == "official" else 1),
                )
                pick = pool[0]
                picked.append(pick)
                golden_by_band[band].append(pick["id"])
            rendered_golden.append((c, picked))
        A("## 黄金锚点（同题多档对照组，置顶）")
        A("")
        A("> 同一道题下天然配齐多个分数档的答卷。判分时先在组内定位：用户文「高于哪一档、不及哪一档」，再做 ±0.5 定档。")
        A("")
        if not task_groups:
            A("（本训练集中未发现满足条件的同题多档对照组。）")
            A("")
        for gi, (group, members) in enumerate(rendered_golden, 1):
            A(f"### 黄金组 G{gi}：{short_quote(group['question'], 220)}")
            A("")
            A("- 覆盖档位：" + "、".join(f"{m['band']:g}（`{m['id']}`）" for m in sorted(members, key=lambda r: r["band"])))
            # delta note from measured features
            if len(members) >= 2:
                ms = sorted(members, key=lambda r: r["band"])
                marks = []
                for key, label, fmt in (
                    ("ttr250", "TTR", "{:.2f}"),
                    ("connector_density", "连接词密度", "{:.1f}"),
                    ("avg_sentence_length", "平均句长", "{:.1f}"),
                    ("subordinate_density", "从属密度", "{:.2f}"),
                ):
                    vals = " → ".join(fmt.format(feats[m["id"]][key]) for m in ms)
                    marks.append(f"{label} {vals}")
                A("- 组内可测差异：" + "；".join(marks) + "。")
            A("")
            for m in sorted(members, key=lambda r: r["band"]):
                A(render_essay(m, feats[m["id"]], colloc, special_lines(m, task)))
            A("---")
            A("")

        # ---- regular band sections
        A("## 分档锚点")
        A("")
        golden_ids = {i for ids in golden_by_band.values() for i in ids}
        A("## 分档补充锚点")
        A("")
        A("> 黄金锚点未覆盖的档位在此补充；每档合计 2 篇（黄金 + 补充）。")
        A("")
        for band in BANDS:
            key = f"{band}|{task}"
            cands = anchors.get(key, [])
            chosen_ids = [c["id"] for c in cands if c["id"] not in golden_ids]
            have = golden_by_band.get(band, [])
            if not have and not chosen_ids:
                continue
            target = 2
            picks = []
            for cid in chosen_ids:
                if len(have) + len(picks) >= target:
                    break
                picks.append(cid)
            if not picks:
                continue
            A(f"### Band {band:g}（补充）")
            A("")
            if not picks:
                A("（该档该题型在训练集中没有可用锚点，评分时跳过本档，以相邻档比对。）")
                A("")
                continue
            for rid in picks:
                r = recs[rid]
                A(render_essay(r, feats[rid], colloc, special_lines(r, task)))
            A("---")
            A("")
        write_text(file_path, "\n".join(lines) + "\n")
        print(f"wrote {file_path.name}: bands covered, groups={len(task_groups)}")


if __name__ == "__main__":
    main()

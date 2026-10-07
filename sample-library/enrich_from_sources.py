#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""enrich_from_sources.py -- 任务一·样本库增强(可选前置步骤)

源语料正集缺单项分与考官评语。其中两家来源的官网页面本身带有
结构化四维小分与考官点评:
  - ieltswritingcorrectionservice.com (6 个主题页, 覆盖样本库 18 条)
  - ielts.international/ielts-sample-essays (单页, 覆盖样本库 10 条)
本脚本抓取并解析这些页面, 产出 enrichment.json, 供 build_sample_library.py
在入库时回填 question(仅缺失的 6 条)、subscores、examiner_comment。
页面缓存于 _cache/, 重复运行不重复请求。匹配不上的一律跳过并打印警告,
不做任何猜测性回填。
"""

import html as html_mod
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "_cache"
COLLECTION = HERE.parent / "IELTS_Task2_1490" / "IELTS_Task2_1490" / "ielts_task2_collection.md"

IWCS_SLUGS = ["society", "environment", "health", "work", "technology", "education"]
II_URL = "https://www.ielts.international/ielts-sample-essays"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch(url: str, cache_name: str) -> str:
    CACHE.mkdir(exist_ok=True)
    p = CACHE / cache_name
    if p.exists():
        return p.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    p.write_text(data, encoding="utf-8")
    time.sleep(1.0)
    return data


def text_lines(raw_html: str):
    t = re.sub(r"<script.*?</script>", "", raw_html, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", raw_html, flags=re.S)
    txt = html_mod.unescape(re.sub(r"<[^>]+>", "\n", t))
    return [l.strip() for l in txt.split("\n") if l.strip()]


def norm(t: str) -> str:
    return " ".join(t.split())


def parse_iwcs(raw_html: str):
    """返回 {'question': str, 'answers': [{band, subscores, essay_key, comment}]}"""
    lines = text_lines(raw_html)
    out = {"question": None, "answers": []}
    marks = [i for i, l in enumerate(lines)
             if re.fullmatch(r"Band \d(?:\.\d)? (?:answer|Response)", l)]
    # 题目: 三种版式的题目标记之后、首个答案块之前,
    # 剔除题型标注行与考试指令行, 剩余行以空格拼合(题干可能跨行)
    q_idx = next((i for i, l in enumerate(lines)
                  if l in ("Task 2 Question", "The Question", "The Exam Question")), None)
    if q_idx is not None and marks:
        q_lines = []
        for l in lines[q_idx + 1:marks[0]]:
            if l.startswith("Task 2 ·") or re.match(
                    r"(?i)(give reasons|write at least|spend approximately|"
                    r"you should spend)", l):
                continue
            q_lines.append(l)
        if q_lines:
            out["question"] = norm(" ".join(q_lines))

    end_markers = ("How the bands compare", "What pushes your score",
                   "Criterion-by-criterion comparison", "What pushes your band up")
    label_map = {
        "TR": "TR", "Task Response": "TR",
        "CC": "CC", "Coherence & Cohesion": "CC", "Coherence and Cohesion": "CC",
        "LR": "LR", "Lexical Resource": "LR",
        "GRA": "GRA", "Grammatical Range": "GRA",
        "Grammatical Range and Accuracy": "GRA", "Grammatical Range & Accuracy": "GRA",
    }
    labels_alt = "|".join(re.escape(k) for k in sorted(label_map, key=len, reverse=True))
    for k, i in enumerate(marks):
        end = marks[k + 1] if k + 1 < len(marks) else len(lines)
        block = lines[i:end]
        j = 0
        scores = {}
        while j < len(block):
            m_inline = re.fullmatch(rf"({labels_alt})\s*:\s*(\d(?:\.\d)?)", block[j])
            if m_inline:
                scores[label_map[m_inline.group(1)]] = float(m_inline.group(2))
                j += 1
                continue
            if j < len(block) - 1 and block[j] in label_map \
                    and re.fullmatch(r"\d(\.\d)?", block[j + 1]):
                scores[label_map[block[j]]] = float(block[j + 1])
                j += 2
                continue
            if block[j].startswith("Overall "):
                break
            j += 1
        if len(scores) != 4:
            continue
        c_idx = next((n for n, l in enumerate(block)
                      if re.fullmatch(r"Examiner comment(ary)?:?", l)), None)
        if c_idx is None:
            continue
        essay_lines = [l for l in block[j + 1:c_idx]
                       if not l.startswith("·") and not re.fullmatch(r"Band \d(\.\d)?", l)]
        tail = block[c_idx + 1:]
        stop = next((n for n, l in enumerate(tail)
                     if l.startswith(end_markers)), len(tail))
        comment = " ".join(tail[:stop])
        band = float(re.fullmatch(r"Band (\d(?:\.\d)?) (?:answer|Response)", block[0]).group(1))
        out["answers"].append({
            "band": band,
            "subscores": {"TR": scores["TR"], "CC": scores["CC"],
                          "LR": scores["LR"], "GRA": scores["GRA"]},
            "essay_key": norm(" ".join(essay_lines))[:120],
            "comment": comment,
        })
    return out


def parse_ii(raw_html: str):
    """返回 [{question, band, subscores, comment}]"""
    lines = text_lines(raw_html)
    blocks = []
    i = 0
    while i < len(lines):
        if lines[i] == "Question" and i + 1 < len(lines):
            q = lines[i + 1]
            j = i + 2
            scores, overall, comment = {}, None, None
            while j < len(lines) and lines[j] != "Question":
                if lines[j] in ("Task Response", "Coherence and Cohesion",
                                "Lexical Resource", "Grammatical Range and Accuracy") \
                        and j + 1 < len(lines) and re.fullmatch(r"\d(\.\d)?", lines[j + 1]):
                    key = {"Task Response": "TR", "Coherence and Cohesion": "CC",
                           "Lexical Resource": "LR",
                           "Grammatical Range and Accuracy": "GRA"}[lines[j]]
                    scores[key] = float(lines[j + 1])
                    j += 2
                    continue
                if lines[j] == "Overall Band" and j + 1 < len(lines):
                    overall = float(lines[j + 1])
                    j += 2
                    continue
                if lines[j] == "Examiner Commentary" and j + 1 < len(lines):
                    comment = lines[j + 1]
                j += 1
            if len(scores) == 4 and overall is not None:
                blocks.append({"question": q, "band": overall,
                               "subscores": scores, "comment": comment})
            i = j
        else:
            i += 1
    return blocks


def parse_collection_brief(path: Path):
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^## 第(\d+)篇\s*$", text)
    entries = []
    for i in range(1, len(blocks), 2):
        no = int(blocks[i])
        body = blocks[i + 1]
        m = re.match(
            r"(?s).*?### 分数\s*\n\s*Band\s*([\d.]+)\s*\n+### 题目\s*\n(.*?)\n+### 文章\s*\n(.*?)\n+### 来源\s*\n\s*(\S+)",
            body)
        entries.append({"no": no, "band": float(m.group(1)),
                        "question": m.group(2).strip(),
                        "essay": m.group(3).strip(), "url": m.group(4)})
    return entries


def main():
    entries = parse_collection_brief(COLLECTION)
    enrich = {}

    # IWCS: 每页三篇不同档答案, 用 band + 正文前缀匹配
    iwcs_pages = {}
    for slug in IWCS_SLUGS:
        url = f"https://ieltswritingcorrectionservice.com/ielts-task-2-sample-{slug}"
        iwcs_pages[url] = parse_iwcs(fetch(url, f"iwcs_{slug}.html"))
    for e in entries:
        if "ieltswritingcorrectionservice" not in e["url"]:
            continue
        page = iwcs_pages.get(e["url"])
        if not page:
            continue
        key = norm(e["essay"])[:120]
        cand = [a for a in page["answers"] if a["band"] == e["band"]]
        hit = next((a for a in cand if a["essay_key"][:80] == key[:80]), None)
        if hit is None and len(cand) == 1:
            hit = cand[0]
        if hit is None:
            print(f"[iwcs] 未匹配: 第{e['no']}篇 band={e['band']} {e['url']}")
            continue
        rec = {"subscores": hit["subscores"], "examiner_comment": hit["comment"]}
        if not e["question"] and page["question"]:
            rec["question"] = page["question"]
        elif e["question"] and page["question"] \
                and norm(e["question"])[:60] != norm(page["question"])[:60]:
            print(f"[iwcs] 题目不一致(保留原值): 第{e['no']}篇")
        enrich[str(e["no"])] = rec

    # ielts.international: 用题目文本匹配
    ii_blocks = parse_ii(fetch(II_URL, "ii_sample_essays.html"))
    for e in entries:
        if "ielts.international" not in e["url"]:
            continue
        qkey = norm(e["question"])[:60]
        hit = next((b for b in ii_blocks if norm(b["question"])[:60] == qkey), None)
        if hit is None:
            print(f"[ii] 未匹配: 第{e['no']}篇 {qkey[:60]}")
            continue
        if hit["band"] != e["band"]:
            print(f"[ii] 总分不一致(以样本库为准): 第{e['no']}篇 lib={e['band']} page={hit['band']}")
        enrich[str(e["no"])] = {"subscores": hit["subscores"],
                                "examiner_comment": hit["comment"]}

    out = HERE / "enrichment.json"
    out.write_text(json.dumps(enrich, ensure_ascii=False, indent=1), encoding="utf-8")
    n_q = sum(1 for r in enrich.values() if "question" in r)
    print(f"enrichment.json: {len(enrich)} 条 (含补题 {n_q} 条)")


if __name__ == "__main__":
    main()

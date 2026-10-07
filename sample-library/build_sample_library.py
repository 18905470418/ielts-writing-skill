#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_sample_library.py -- 任务一·样本库建设

输入: IELTS_Task2_1490 正集 ielts_task2_collection.md(1490 篇, 唯一权威来源)
产出:
  essays.train.jsonl        训练集 (~80%, 按分数档×题型分层)
  blindtest/essays.blindtest.jsonl  盲测集 (~20%, 物理隔离, 只读封存)
  ledger.csv                采样台账 (全部 1490 条元数据, 不含正文)
  distribution-report.md    分布盘点报告 (7 档 × 5 题型 × 10 主题)

说明:
- 源数据只有总分, 无单项分/考官评语 -> subscores / examiner_comment 一律 null,
  按任务约定留待任务二反向标注补齐。
- task_type / topic 由规则分类器自动标注 (见 classify_* 函数), 局限写入盘点报告。
- 分类与切分全程确定性 (固定随机种子), 可复现。
"""

import csv
import io
import json
import os
import random
import re
import stat
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLLECTION = ROOT / "IELTS_Task2_1490" / "IELTS_Task2_1490" / "ielts_task2_collection.md"
OUT = ROOT / "sample-library"
BLIND_DIR = OUT / "blindtest"
ENRICHMENT = OUT / "enrichment.json"

SEED = 20261007
BLIND_RATIO = 0.2

BANDS = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]
TASK_TYPES = ["opinion", "discussion", "adv-disadv", "report", "two-part"]
TOPICS = ["education", "technology", "environment", "government", "social",
          "crime", "culture", "health", "media", "globalization-work"]

BAND_CODE = {6.0: "B6", 6.5: "B65", 7.0: "B7", 7.5: "B75", 8.0: "B8", 8.5: "B85", 9.0: "B9"}
TYPE_CODE = {"opinion": "OP", "discussion": "DIS", "adv-disadv": "ADV", "report": "REP", "two-part": "TQ"}


# ---------------------------------------------------------------- 解析

def parse_collection(path: Path):
    """解析 collection.md -> [{source_no, band, question, essay, source_url}]"""
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^## 第(\d+)篇\s*$", text)
    # blocks[0] 是前言; 之后成对出现 (编号, 正文块)
    entries = []
    for i in range(1, len(blocks), 2):
        no = int(blocks[i])
        body = blocks[i + 1]
        m = re.match(
            r"(?s).*?### 分数\s*\n\s*Band\s*([\d.]+)\s*\n+### 题目\s*\n(.*?)\n+### 文章\s*\n(.*?)\n+### 来源\s*\n\s*(\S+)",
            body)
        if not m:
            raise ValueError(f"第{no}篇解析失败")
        band, question, essay, url = m.groups()
        entries.append({
            "source_no": no,
            "band": float(band),
            "question": question.strip(),
            "essay": essay.strip(),
            "source_url": url.strip(),
        })
    return entries


# ---------------------------------------------------------------- 题型分类

RE_DISCUSSION = re.compile(
    r"discuss\s+both|both\s+(of\s+these\s+)?(views|sides|opinions)|"
    r"discuss\s+the\s+(two|both)|both\s+points?\s+of\s+view|"
    r"discuss\s+these\s+(two\s+)?(views|opinions)", re.I)

RE_ADV = re.compile(
    r"advantages?.{0,40}(and|or|&).{0,40}disadvantages?|disadvantages?.{0,40}(and|or).{0,40}advantages?|"
    r"outweigh|positive\s+or\s+negative\s+(development|trend|change)|"
    r"is\s+(this|it)\s+a\s+(positive|negative)\s+(development|trend|step|change)|"
    r"(positive|negative)\s+development|benefits?.{0,30}(and|or).{0,30}(drawbacks?|disadvantages?)|"
    r"do\s+the\s+(advantages|benefits)\s+of|more\s+(advantages|benefits)\s+than|"
    r"(advantages|benefits)\s+(of|in)\b.{0,60}\?|merits?\s+and\s+demerits?|"
    r"pros\s+and\s+cons|do\s+you\s+think\s+(the\s+)?(advantages|benefits)",
    re.I)

RE_OPINION = re.compile(
    r"agree\s+or\s+disagree|to\s+what\s+extent\s+(do\s+you|did\s+you)\s+(agree|disagree)|"
    r"do\s+you\s+(agree|disagree)|what\s+is\s+your\s+(opinion|view)|"
    r"what\s+do\s+you\s+think|give\s+your\s+(own\s+)?opinion|"
    r"do\s+you\s+think\s+(this|it|that)\s+is|to\s+what\s+extent.{0,30}agree|"
    r"how\s+far\s+(do\s+you|would\s+you)\s+(agree|disagree)|"
    r"express\s+your\s+opinion|in\s+your\s+opinion.{0,40}\?|"
    r"what\s+are\s+your\s+(opinions|views|thoughts)", re.I)

RE_REPORT = re.compile(
    r"(causes?|reasons?|factors?).{0,80}(solutions?|measures?|steps?|ways?|effects?|impacts?|deal|tackle|address|overcome|reduce|solve)|"
    r"(solutions?|measures?).{0,60}(causes?|reasons?|problems?)|"
    r"what\s+(are\s+)?(the\s+)?(causes?|reasons?|problems?|effects?|impacts?)\b|"
    r"why\s+(is|does|do|has|have|are)\s+this|why\s+this\s+(is|has)\s+(happening|the\s+case)|"
    r"what\s+problems?\s+(does|do|can|could|might|may|will)|"
    r"how\s+(can|could|should|to)\s+(we|governments?|this|it|society|they)?\s*\w*\s*(solve|address|tackle|deal\s+with|overcome|reduce|prevent|combat|handle|cope)|"
    r"problems?\s+(and|&)\s+solutions?|causes?\s+(and|&)\s+(solutions?|effects?)|"
    r"what\s+(measures?|steps?)\s+(can|could|should)|"
    r"best\s+way\s+to\s+(solve|reduce|deal|tackle|address|improve|tackle|ensure|encourage|protect)|"
    r"what\s+can\s+(be\s+done|we\s+do|governments?\s+do)|"
    r"explain\s+(some\s+of\s+)?the\s+(reasons?|causes?)|"
    r"what\s+factors?\s+(contribute|lead|cause)|"
    r"(increasing|growing|worsening|rising|declining|increasingly).{0,60}(why|what\s+are\s+the\s+(causes?|reasons?))",
    re.I)

RE_SUGGEST_MEASURE = re.compile(
    r"suggest\s+(some\s+)?(solutions?|measures?|ways?)|"
    r"what\s+(solutions?|measures?)\s+(would|can|could)\s+you\s+suggest|"
    r"how\s+(can|could)\s+(this|these)\s+(problem|issue|situation|trend)s?", re.I)


def classify_task_type(q: str) -> str:
    n_q = q.count("?")
    if RE_DISCUSSION.search(q):
        return "discussion"
    if RE_ADV.search(q):
        return "adv-disadv"
    has_opinion = bool(RE_OPINION.search(q))
    has_report = bool(RE_REPORT.search(q)) or bool(RE_SUGGEST_MEASURE.search(q))
    if has_opinion and has_report:
        return "two-part"          # 混合型(如 why + agree) 归入双问题类
    if has_opinion:
        return "opinion"
    if has_report:
        return "report"
    if n_q >= 2:
        return "two-part"
    # 单句直接问句(What/How/Why 开头且不含观点词)按报告类处理
    if re.search(r"(?i)^(what|how|why)\b", q.strip()) or re.search(r"[?.!]\s*(what|how|why)\s", q, re.I):
        return "report"
    return "opinion"               # 兜底: 观点类是 IELTS 默认题型


# ---------------------------------------------------------------- 主题分类
# 每主题: (强关键词权重3, 弱关键词权重1); 取总分最高者, 平分看关键词出现位置更早者

TOPIC_RULES = {
    "education": (
        r"\b(schools?|students?|teachers?|teaching|universit\w+|colleges?|education\w*|academic\w*|"
        r"curricul\w+|homework|tuition|graduat\w+|classrooms?|lessons?|exams?|examinations?|degrees?|"
        r"pupils?|kindergarten|scholarship\w*|campus|lectures?|subjects?|coursework|literacy|"
        r"primary\s+school|secondary\s+school|high\s+school|homeschool|tuition\s+fees?|phd|"
        r"study\s+abroad|studying\s+abroad|gap\s+year|vocational)\b",
        r"\b(learn|learning|studying|study|educated|knowledge|skills?\s+development)\b"),
    "technology": (
        r"\b(technolog\w+|computers?|internet|online|smartphones?|mobile\s+phones?|"
        r"artificial\s+intelligence|\bai\b|robots?|robotics|automation|automated|digital|screens?|"
        r"e-books?|ebooks?|self-driving|driverless|algorithms?|apps?\b|cyber|virtual\s+reality|"
        r"video\s+games?|computer\s+games?|gaming|gadgets?|wi-fi|data\s+privacy)\b",
        r"\b(machines?|devices?|electronic\w*|innovation\w*|science|scientific|scientists?|research)\b"),
    "environment": (
        r"\b(environment\w*|pollution|pollutants?|climate|global\s+warming|emissions?|carbon|"
        r"fossil\s+fuels?|renewable|greenhouse|recycl\w+|plastics?|deforestation|"
        r"endangered|extinction|extinct|wildlife|zoos?|animal\s+(rights|testing|welfare)|"
        r"biodiversity|sustainab\w+|natural\s+resources?|air\s+quality|waste\s+disposal|"
        r"litter|ecosystems?|habitats?|species|conservation|solar\s+energy|"
        r"environmental\s+problems?)\b",
        r"\b(animals?|waste|energy\s+sources?|nature|planet|greenery|parks?\s+and)\b"),
    "government": (
        r"\b(governments?|taxes?|taxation|taxpayers?|public\s+(money|funds?|spending|services?|sector)|"
        r"policies|policy|state[-\s]funded|budgets?|subsid\w+|welfare|pensions?|"
        r"space\s+(research|programmes?|exploration)|military|defen[cs]e|foreign\s+aid|"
        r"voting|elections?|politicians?|public\s+transport\s+funding|ministers?|"
        r"public\s+transport|"
        r"free\s+(healthcare|education)\s+.{0,30}(government|state|public))\b",
        r"\b(authorities|bans?\b|funding|funded|laws?\s+(to|that|banning)|regulations?|citizens?)\b"),
    "social": (
        r"\b(elderly|older\s+people|ageing\s+population|aging\s+population|pensioners?|"
        r"poverty|inequality|homeless\w*|housing|charity|charities|volunteer\w*|community\s+service|"
        r"unemployment|gender|women'?s\s+rights|sexism|discrimination|happiness|"
        r"social\s+(problems?|issues?|isolation)|loneliness|family\s+(life|values?)|"
        r"single\s+parent|divorce|birth\s+rates?|overpopulation|population\s+growth|"
        r"quality\s+of\s+life|standard\s+of\s+living|retire\w*|childcare|parenting)\b",
        r"\b(society|community|families|neighbourhoods?|neighborhoods?|children|young\s+people|"
        r"teenagers?|elderly\s+people|cities|urban|rural|money|salary|success|famous|"
        r"population|leisure|free\s+time|hobbies|hobby|traffic|congestion|road\s+safety|"
        r"bicycles?|bikes?|cycling|driving|drivers?|vehicles?|commut\w+|renting|rent\s|"
        r"owning\s+a\s+(home|house|flat)|property|properties|flats?|houses?|homes?|live\s+alone|"
        r"living\s+alone|personal\s+life|daily\s+lives)\b"),
    "crime": (
        r"\b(crimes?|criminals?|prisons?|prisoners?|offenders?|offences?|punish\w*|jails?|"
        r"death\s+penalty|capital\s+punishment|police|courts?|juvenile\s+delinquen\w*|"
        r"sentenc\w*|reoffend\w*|deterren\w*|deters?\b|theft|burglar\w*|shoplifting|"
        r"cybercrime|fraud|violent\s+crime|crime\s+rates?|commit\s+\w*\s*crimes?|lawbreakers?)\b",
        r"\b(laws?|illegal|legal|victims?|rehabilitation)\b"),
    "culture": (
        r"\b(cultur\w+|traditions?|traditional|heritage|museums?|languages?|foreign\s+language|"
        r"second\s+language|minority\s+language|customs?|festivals?|arts?\b|art\s+galleries|"
        r"music\s+(industry|festivals?)|handicrafts?|indigenous|mother\s+tongue|"
        r"global\s+language|english\s+(as\s+a\s+)?(global|international|world)\s+language|"
        r"historical\s+(sites?|buildings?)|monuments?)\b",
        r"\b(history|historical|customs|arts?\s+and\s+crafts|bilingual|multilingual)\b"),
    "health": (
        r"\b(health|healthy|healthcare|diets?|dieting|obesity|obese|overweight|exercise|"
        r"diseases?|medical|doctors?|hospitals?|fast\s+food|junk\s+food|sugar|smoking|smokers?|"
        r"mental\s+health|medicines?|illness(es)?|vaccin\w*|patients?|physical\s+activity|"
        r"life\s+expectancy|nutrition|nutritious|stress(ful)?|stress\s+levels?|cancer|"
        r"public\s+health|sedentary)\b",
        r"\b(sport(s)?\b|fitness|wellbeing|well-being|cure|treatment|epidemic|sleep|"
        r"food|cooking|meals?|restaurants?|gyms?)\b"),
    "media": (
        r"\b(media|advertis\w*|adverts?\b|ads?\b|news(papers?)?|television|\btv\b|"
        r"social\s+media|celebrit\w*|famous\s+people|the\s+press|journalis\w*|reporters?|"
        r"reality\s+(tv|shows?)|broadcast\w*|films?\s+industry|movies?|censorship|"
        r"fake\s+news|influencers?|magazines?|violence\s+on\s+(tv|television))\b",
        r"\b(news\s+reports?|films?|movies|watching\s+tv|radio)\b"),
    "globalization-work": (
        r"\b(globali[sz]\w*|global\s+(economy|trade|village)|international\s+(trade|business|companies|tourism)|"
        r"workplaces?|employees?|employers?|working\s+(hours?|week|conditions|from\s+home)|"
        r"remote\s+work(ing)?|telework\w*|careers?|job\s+(satisfaction|security|market|opportunities)|"
        r"unemploy\w*|multinational|outsourc\w*|imports?|exports?|consumer\s+goods|"
        r"work-life\s+balance|overtime|salaries|wages|retirement\s+age|"
        r"tourism|tourists?|immigra\w*|emigra\w*|migration|brain\s+drain)\b",
        r"\b(jobs?|work\b|working|business(es)?|compan\w+|economy|economic|factories|"
        r"international|abroad|rich\s+countries|poor\s+countries|developing\s+countries|"
        r"developed\s+countries|global|consumer\w*|shopping|shops?|supermarkets?|buying|goods|"
        r"products?|leaders?|leadership|managers?|management|price)\b"),
}

TOPIC_PRIORITY = ["crime", "health", "environment", "education", "media", "culture",
                  "technology", "government", "globalization-work", "social"]


def classify_topic(q: str):
    best, best_score, best_pos = None, 0, 10 ** 9
    for topic in TOPIC_PRIORITY:          # 先遍历者平分优先
        strong, weak = TOPIC_RULES[topic]
        score, first = 0, None
        for weight, pat in ((3, strong), (1, weak)):
            for m in re.finditer(pat, q, re.I):
                score += weight
                if first is None:
                    first = m.start()
        if score > best_score or (score == best_score and score > 0 and first is not None and first < best_pos):
            best, best_score, best_pos = topic, score, (first if first is not None else 10 ** 9)
    return (best or "social"), best_score  # 兜底: 社会问题是最宽口径


# Task 1 / 书信题泄漏检测(源语料过滤残留的少量非 Task2 题)
RE_OFFTASK = re.compile(
    r"summari[sz]e|the\s+(chart|table|diagram|map|plans?|picture|graph)s?\s+(below|show)|"
    r"write\s+an?\s+(letter|email)|bar\s+chart|pie\s+chart|line\s+graph|"
    r"write\s+to\s+(your|the)\s+\w+\s+(explaining|to)", re.I)

# 源采集时混入题目的 Task 1 指令样板句(剥除后还原真实 Task 2 题干)
RE_T1_BOILER = re.compile(
    r"\s*Summari[sz]e\s+the\s+information\s+by\s+selecting\s+and\s+reporting\s+the\s+main\s+"
    r"features,?\s*(and\s+make\s+comparisons\s+where\s+relevant)?\s*\.?\s*", re.I)


def _norm(t: str) -> str:
    return " ".join(t.split())


def _halfdup_span(t: str):
    """若 t 为同一文本重复两次(允许中间有空白), 返回保留一半后的文本, 否则返回 None"""
    n = _norm(t)
    L, h = len(n), len(n) // 2
    for off in range(-3, 4):
        a, b = n[:h + off].strip(), n[h + off:].strip()
        if a and a == b:
            # 原始文本按段落切: 优先保留含段落结构的一半
            paras = t.split("\n\n")
            if len(paras) > 1 and _norm(paras[0]) == _norm("\n\n".join(paras[1:])):
                return "\n\n".join(paras[1:]).strip()
            if len(paras) > 1 and _norm("\n\n".join(paras[:-1])) == _norm(paras[-1]):
                return "\n\n".join(paras[:-1]).strip()
            return a
    return None


def clean_entry(e, stats):
    q = RE_T1_BOILER.sub("", e["question"])
    if q != e["question"]:
        stats["t1_boiler"] += 1
        e["question"] = q.strip()
    for field in ("question", "essay"):
        dedup = _halfdup_span(e[field])
        if dedup is not None:
            stats[f"{field}_halfdup"] += 1
            e[field] = dedup
    return e


# ---------------------------------------------------------------- 切分

def stratified_split(records):
    """按 分数档 × 题型 分层抽 20% 进盲测集, 总量向 round(n*0.2) 对齐"""
    rng = random.Random(SEED)
    by_band = defaultdict(list)
    for r in records:
        by_band[r["band"]].append(r)

    for band, group in by_band.items():
        target = round(len(group) * BLIND_RATIO)
        cells = defaultdict(list)
        for r in group:
            cells[r["task_type"]].append(r)
        for cell in cells.values():
            rng.shuffle(cell)

        picked = []
        for cell in cells.values():
            k = max(1, round(len(cell) * BLIND_RATIO)) if len(cell) >= 3 else 1
            picked.extend(cell[:k])
        # 微调至目标数: 多了退回, 少了从剩余补
        picked_set = {id(r) for r in picked}
        rest = [r for cell in cells.values() for r in cell if id(r) not in picked_set]
        rng.shuffle(rest)
        while len(picked) > target:
            rest.append(picked.pop())
        while len(picked) < target and rest:
            picked.append(rest.pop())
        for r in picked:
            r["split"] = "blindtest"
    return records


# ---------------------------------------------------------------- 盲测封存

def set_readonly(path: Path, ro: bool):
    """Windows 用 os.chmod(stat.S_IREAD/S_IWRITE) 控制只读属性; 其他平台去/加写位"""
    if not path.exists():
        return
    if os.name == "nt":
        os.chmod(path, stat.S_IREAD if ro else stat.S_IWRITE)
    else:
        mode = path.stat().st_mode
        path.chmod((mode & ~0o222) if ro else (mode | 0o200))


# ---------------------------------------------------------------- 主流程

def main():
    entries = parse_collection(COLLECTION)
    assert len(entries) == 1490, f"解析得到 {len(entries)} 条, 期望 1490"

    clean_stats = Counter()
    entries = [clean_entry(e, clean_stats) for e in entries]

    # 可选增强: 回填 iwcs / ielts.international 官网的四维小分与考官评语
    enrich = {}
    if ENRICHMENT.exists():
        enrich = json.loads(ENRICHMENT.read_text(encoding="utf-8"))

    # 来源标注: 从 URL 提取站点名
    def source_name(url):
        m = re.search(r"https?://(?:www\.)?([^/]+)", url)
        return m.group(1) if m else url

    topic_zero = 0
    n_enriched = n_qfill = 0
    for e in entries:
        en = enrich.get(str(e["source_no"]))
        if en:
            if not e["question"].strip() and en.get("question"):
                e["question"] = en["question"]
                n_qfill += 1
            n_enriched += 1
        e["subscores"] = (en or {}).get("subscores")
        e["examiner_comment"] = (en or {}).get("examiner_comment")
        e["task_type"] = classify_task_type(e["question"])
        e["topic"], tscore = classify_topic(e["question"])
        e["topic_auto_zero"] = (tscore == 0)
        topic_zero += (tscore == 0)
        e["word_count"] = len(e["essay"].split())
        e["source"] = source_name(e["source_url"])
        e["split"] = "train"
        e["flags"] = ["suspected-offtask"] if RE_OFFTASK.search(e["question"]) else []

    entries = stratified_split(entries)

    # 赋 ID: B{分数}-{题型}-{序号}, 序号按原始篇号排序
    counters = defaultdict(int)
    for e in sorted(entries, key=lambda x: x["source_no"]):
        key = (e["band"], e["task_type"])
        counters[key] += 1
        e["id"] = f"{BAND_CODE[e['band']]}-{TYPE_CODE[e['task_type']]}-{counters[key]:03d}"

    # 写 JSONL
    OUT.mkdir(exist_ok=True)
    BLIND_DIR.mkdir(exist_ok=True)

    def to_record(e):
        return {
            "id": e["id"],
            "band": e["band"],
            "subscores": e["subscores"],  # 源数据多数无单项分; 有官网小分者已回填
            "task_type": e["task_type"],
            "topic": e["topic"],
            "question": e["question"],
            "essay": e["essay"],
            "word_count": e["word_count"],
            "examiner_comment": e["examiner_comment"],
            "source": e["source"],
            "source_url": e["source_url"],
            "source_no": e["source_no"],
            "split": e["split"],
            "flags": e["flags"],
        }

    ordered = sorted(entries, key=lambda x: x["id"])
    n_train = n_blind = 0
    set_readonly(BLIND_DIR / "essays.blindtest.jsonl", False)   # 重跑前解除封存
    with open(OUT / "essays.train.jsonl", "w", encoding="utf-8") as ftr, \
         open(BLIND_DIR / "essays.blindtest.jsonl", "w", encoding="utf-8") as fbl:
        for e in ordered:
            line = json.dumps(to_record(e), ensure_ascii=False)
            if e["split"] == "train":
                ftr.write(line + "\n"); n_train += 1
            else:
                fbl.write(line + "\n"); n_blind += 1
    # 盲测集物理隔离: 独立目录 + 只读封存(含目录说明文件)
    for p in (BLIND_DIR / "essays.blindtest.jsonl", BLIND_DIR / "README.md"):
        set_readonly(p, True)

    # 采样台账 (仅元数据)
    with open(OUT / "ledger.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "band", "task_type", "topic", "split", "word_count",
                    "subscores", "flags", "source", "source_no", "source_url"])
        for e in sorted(entries, key=lambda x: x["source_no"]):
            sub = e["subscores"]
            sub_s = "/".join(f"{k}{sub[k]:g}" for k in ("TR", "CC", "LR", "GRA")) if sub else ""
            w.writerow([e["id"], e["band"], e["task_type"], e["topic"], e["split"],
                        e["word_count"], sub_s, ";".join(e["flags"]),
                        e["source"], e["source_no"], e["source_url"]])

    n_off = sum(1 for e in entries if e["flags"])
    write_report(entries, n_train, n_blind, topic_zero, n_off, clean_stats,
                 n_enriched, n_qfill)
    print(f"OK: total={len(entries)} train={n_train} blind={n_blind} "
          f"topic_zero_hits={topic_zero} offtask={n_off} clean={dict(clean_stats)} "
          f"enriched={n_enriched} question_filled={n_qfill}")


# ---------------------------------------------------------------- 盘点报告

def write_report(entries, n_train, n_blind, topic_zero, n_off, clean_stats,
                 n_enriched, n_qfill):
    cnt = Counter((e["band"], e["task_type"], e["topic"]) for e in entries)
    bt = Counter((e["band"], e["task_type"]) for e in entries)
    bp = Counter((e["band"], e["topic"]) for e in entries)
    band_total = Counter(e["band"] for e in entries)
    type_total = Counter(e["task_type"] for e in entries)
    topic_total = Counter(e["topic"] for e in entries)
    split_band = Counter((e["band"], e["split"]) for e in entries)

    L = []
    A = L.append
    A("# 样本库分布盘点报告\n")
    A("> 任务一 §2.1/§2.4 交付物。语料: `IELTS_Task2_1490/ielts_task2_collection.md`(1490 篇)。")
    A("> 题型/主题由 `build_sample_library.py` 规则分类器自动标注(基于题目文本),")
    A("> 未逐篇人工复核; 任务二蒸馏时若发现误标, 直接在 JSONL 中修正并回写台账。\n")

    A("## 1. 总量与切分\n")
    A("| 分数档 | 总数 | 训练集 | 盲测集 |")
    A("|---|---:|---:|---:|")
    for b in BANDS:
        A(f"| {b} | {band_total[b]} | {split_band[(b,'train')]} | {split_band[(b,'blindtest')]} |")
    A(f"| **合计** | **{sum(band_total.values())}** | **{n_train}** | **{n_blind}** |")
    A(f"\n切分方式: 分数档 × 题型分层随机(种子 {SEED}), 盲测占比 {BLIND_RATIO:.0%}; "
      "盲测集物理隔离于 `blindtest/` 并设只读, 仅供任务三使用。\n")

    A("## 2. 分数档 × 题型 透视(理想值: 每档每题型约 40 篇)\n")
    A("| 分数档 | " + " | ".join(TASK_TYPES) + " | 小计 |")
    A("|---|" + "---:|" * len(TASK_TYPES) + "---:|")
    for b in BANDS:
        row = [str(bt[(b, t)]) for t in TASK_TYPES]
        A(f"| {b} | " + " | ".join(row) + f" | {band_total[b]} |")
    A("| **合计** | " + " | ".join(str(type_total[t]) for t in TASK_TYPES) +
      f" | **{sum(band_total.values())}** |\n")

    A("## 3. 分数档 × 主题 透视(要求: 每档至少覆盖 8 个主题)\n")
    A("| 分数档 | " + " | ".join(TOPICS) + " | 覆盖主题数 |")
    A("|---|" + "---:|" * len(TOPICS) + "---:|")
    for b in BANDS:
        row = [str(bp[(b, t)]) for t in TOPICS]
        cov = sum(1 for t in TOPICS if bp[(b, t)] > 0)
        flag = "" if cov >= 8 else "  ⚠️不足"
        A(f"| {b} | " + " | ".join(row) + f" | {cov}/10{flag} |")
    A("| **合计** | " + " | ".join(str(topic_total[t]) for t in TOPICS) + " | |\n")

    A("## 4. 薄弱格子清单(7档 × 5题型 × 10主题 全网格)\n")
    A("规则: 格子样本数 = 0 记 **空缺**, 1–2 记 **薄弱**; "
      "任务二在对应规则上须标注「样本不足, 此规则置信度低」, 并据此定向补样。\n")
    A("| 分数档 | 题型 | 空缺主题 | 薄弱主题(篇数) |")
    A("|---|---|---|---|")
    weak_cells = 0
    for b in BANDS:
        for t in TASK_TYPES:
            empty = [p for p in TOPICS if cnt[(b, t, p)] == 0]
            weak = [f"{p}({cnt[(b,t,p)]})" for p in TOPICS if 0 < cnt[(b, t, p)] < 3]
            weak_cells += len(empty) + len(weak)
            A(f"| {b} | {t} | {', '.join(empty) if empty else '—'} | "
              f"{', '.join(weak) if weak else '—'} |")
    full = len(BANDS) * len(TASK_TYPES) * len(TOPICS)
    A(f"\n全网格共 {full} 格, 空缺+薄弱合计 {weak_cells} 格 "
      f"(健康格子占比 {(full-weak_cells)/full:.1%})。\n")

    A("## 5. 数据质量注记\n")
    A("- **分数可靠性**: 沿用源语料 README 警告——8.5 档 199/200 来自 writing9.com 自动评分,"
      " 6.5/7.5 半分档亦以自动评分为主; 任务二蒸馏 L1/L2 时应对 8.5 档锚点从严甄选。")
    A(f"- **单项分/考官评语**: 源语料正集缺失; 已从 IWCS(18 条)与 IELTS International(10 条)"
      f" 官网回填四维小分与考官评语共 {n_enriched} 条(小分与总分官方取整规则 100% 吻合),"
      f" 并据官网补回缺失题目 {n_qfill} 条; 其余 1462 条 `subscores`/`examiner_comment` 为 null,"
      " 待任务二反向标注。复现方式: `python enrich_from_sources.py && python build_sample_library.py`。")
    A(f"- **疑似非 Task 2 泄漏**: {n_off} 篇题目疑似 Task 1 图表/书信题(源语料过滤残留),"
      " 已在 JSONL 与台账 `flags` 列标注 `suspected-offtask`; 任务二蒸馏与任务三抽测时应剔除。")
    A(f"- **入库清洗**: 剥除题目中混入的 Task 1 指令样板句 {clean_stats['t1_boiler']} 处; "
      f"修正题目半串重复 {clean_stats['question_halfdup']} 处、正文半串重复 "
      f"{clean_stats['essay_halfdup']} 处(采集器拼接瑕疵, 清洗动作确定性可复现)。")
    A(f"- **主题零命中兜底**: {topic_zero} 篇题目未命中任何主题关键词, 已归入 social; "
      "清单见台账筛选 `topic=social` 且低频主题交叉复核。")
    A("- **题型分类边界**: 混合型设问(如 why + agree)统一归入 two-part; "
      "「positive/negative development」归入 adv-disadv; 单句 What/How/Why 直接问句归入 report。")
    A("- **每档每题型理想 40 篇**: 实际分布见第 2 节, report 与 two-part 普遍偏低,"
      " 补样优先级: two-part > report > adv-disadv。\n")

    (OUT / "distribution-report.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    main()

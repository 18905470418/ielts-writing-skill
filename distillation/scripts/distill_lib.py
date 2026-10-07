"""Shared utilities for the Task-2 distillation pipeline.

Only ever reads ``sample-library/essays.train.jsonl`` (plus pipeline-derived
files under ``distillation/``). The blindtest split is never opened here.
"""
from __future__ import annotations

import collections
import csv
import json
import math
import random
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = ROOT / "sample-library" / "essays.train.jsonl"
DISTILL = ROOT / "distillation"
DATA_DIR = DISTILL / "data"
REPORT_DIR = DISTILL / "reports"
REFS_DIR = ROOT / "ielts-writing-scorer" / "references"
ANCHOR_DIR = REFS_DIR / "anchors"

BANDS = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]
HALF_BANDS = [6.5, 7.5, 8.5]
TASKS = ["opinion", "discussion", "adv-disadv", "report", "two-part"]
TASK_CN = {
    "opinion": "观点类",
    "discussion": "讨论类",
    "adv-disadv": "利弊类",
    "report": "报告类",
    "two-part": "双问题类",
}
TASK_CODE = {"opinion": "OP", "discussion": "DIS", "adv-disadv": "ADV", "report": "REP", "two-part": "TQ"}
BAND_CODE = {6.0: "B6", 6.5: "B65", 7.0: "B7", 7.5: "B75", 8.0: "B8", 8.5: "B85", 9.0: "B9"}

TOPICS = [
    "education",
    "technology",
    "environment",
    "government",
    "social",
    "crime",
    "culture",
    "health",
    "media",
    "globalization-work",
]
TOPIC_CN = {
    "education": "教育",
    "technology": "科技",
    "environment": "环境",
    "government": "政府与公共政策",
    "social": "社会问题",
    "crime": "犯罪与法律",
    "culture": "文化与语言",
    "health": "健康",
    "media": "媒体与广告",
    "globalization-work": "全球化与工作",
}
TOPIC_CODE = {
    "education": "EDU",
    "technology": "TECH",
    "environment": "ENV",
    "government": "GOV",
    "social": "SOC",
    "crime": "CRIME",
    "culture": "CUL",
    "health": "HEALTH",
    "media": "MEDIA",
    "globalization-work": "GLOB",
}

# Seed lexicons used to keep mined collocations anchored to their topic.
TOPIC_SEEDS: dict[str, list[str]] = {
    "education": [
        "school", "student", "teach", "learn", "educat", "univers", "college", "academic", "curricul",
        "classroom", "homework", "tuition", "degree", "exam", "literacy", "vocational", "scholarship",
        "kindergarten", "pupil", "lecture", "subject", "coursework", "skill", "knowledge",
    ],
    "technology": [
        "technolog", "computer", "internet", "online", "smartphone", "mobile", "digital", "artificial",
        "robot", "automat", "algorithm", "screen", "app", "cyber", "virtual", "device", "gadget",
        "software", "hardware", "data", "privacy", "electronic",
    ],
    "environment": [
        "environment", "climate", "emission", "pollution", "carbon", "waste", "recycl", "sustain",
        "energy", "fossil", "green", "conservation", "wildlife", "ecosystem", "plastic", "deforest",
        "habitat", "renewable", "global warming", "air quality", "natural resource",
    ],
    "government": [
        "government", "public", "policy", "tax", "subsid", "regulat", "law", "legislat", "funding",
        "infrastructure", "council", "ministry", "state", "welfare", "authorit", "transport", "public service",
        "public money", "public spending", "municipal", "citizen",
    ],
    "social": [
        "societ", "social", "communit", "population", "urban", "rural", "family", "children", "elderly",
        "poverty", "inequal", "lifestyle", "city", "citizen", "generation", "young people", "living standard",
        "wellbeing", "well-being", "public transport", "housing", "neighbour", "neighbor", "ageing", "aging",
    ],
    "crime": [
        "crime", "criminal", "prison", "offend", "law", "police", "sentence", "punish", "recidiv",
        "rehabilitat", "justice", "court", "deter", "victim", "penal", "custody", "juvenile",
        "law break", "lawbreak", "offence", "offense",
    ],
    "culture": [
        "cultur", "tradition", "heritage", "museum", "art", "language", "histor", "custom", "identity",
        "craft", "music", "festival", "tourism", "ancestor", "ritual", "monument", "native",
    ],
    "health": [
        "health", "medical", "disease", "obes", "diet", "exercise", "mental", "physical", "doctor",
        "hospital", "patient", "lifestyle", "nutrition", "fitness", "overweight", "illness", "medicine",
        "wellbeing", "well-being", "healthcare", "health care", "smoking", "alcohol",
    ],
    "media": [
        "media", "news", "televis", "newspaper", "advertis", "journal", "broadcast", "press",
        "information", "platform", "online", "social media", "publicity", "headline", "viewer", "audience",
        "campaign", "content",
    ],
    "globalization-work": [
        "global", "international", "work", "employ", "job", "career", "business", "trade", "econom",
        "migrat", "remote", "office", "labour", "labor", "unemploy", "multinational", "outsource",
        "workplace", "company", "industry", "wage", "salary", "profession", "workforce", "work-life",
    ],
}


def topic_seed_re(topic: str) -> re.Pattern:
    seeds = sorted(TOPIC_SEEDS[topic], key=len, reverse=True)
    pats = []
    for s in seeds:
        s = re.escape(s).replace(r"\ ", r"\s+")
        pats.append(rf"(?<![a-z]){s}[a-z]*(?![a-z])")
    return re.compile("|".join(pats), re.I)


def _all_seed_re() -> re.Pattern:
    pats = []
    for s in sorted({s for v in TOPIC_SEEDS.values() for s in v}, key=len, reverse=True):
        esc = re.escape(s).replace("\\ ", "\\s+")
        pats.append("(?<![a-z])" + esc + "[a-z]*(?![a-z])")
    return re.compile("|".join(pats), re.I)


ALL_SEED_RE = _all_seed_re()

# ---------------------------------------------------------------- loading


def load_train(include_flagged: bool = True) -> list[dict]:
    """Load the training split; asserts the physical split discipline."""
    recs: list[dict] = []
    with TRAIN_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec["split"] != "train":
                raise RuntimeError(f"non-train record in train file: {rec['id']}")
            recs.append(rec)
    if not include_flagged:
        recs = [r for r in recs if not r["flags"]]
    return recs


def load_enriched() -> list[dict]:
    path = DATA_DIR / "essays.train.enriched.jsonl"
    if path.exists():
        recs = []
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    recs.append(json.loads(line))
        return recs
    return load_train()


def is_distillable(rec: dict) -> bool:
    """Flagged (suspected Task-1) records are excluded from all assets."""
    return not rec.get("flags")


def effective_task_type(rec: dict) -> str:
    """Task type after the reviewed corrections recorded in step 1."""
    return rec.get("task_type_effective") or rec["task_type"]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- text utils

_ABBREV = ["e.g.", "i.e.", "etc.", "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "St.", "vs.", "U.S.", "U.K.", "No."]


def paragraphs(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = re.split(r"\n\s*\n", text)
    out = []
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip()
        if p:
            out.append(p)
    return out


def sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.replace("\r", " ").replace("\n", " ")).strip()
    if not text:
        return []
    protected = text
    for i, ab in enumerate(_ABBREV):
        protected = protected.replace(ab, ab.replace(".", "\u2022"))
    chunks = re.split(r"(?<=[.!?])\s+(?=[\"'(\[]?[A-Z0-9])", protected)
    out: list[str] = []
    for ch in chunks:
        ch = ch.replace("\u2022", ".").strip()
        if not ch:
            continue
        # A trailing fragment without terminal punctuation still counts.
        out.append(ch)
    # merge ultra-short orphans (e.g. leftover quote marks)
    merged: list[str] = []
    for s in out:
        if len(s) < 3 and merged:
            merged[-1] += " " + s
        else:
            merged.append(s)
    return merged


TOKEN_RE = re.compile(r"[a-z]+(?:['\u2019][a-z]+)*")


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


STOPWORDS = set(
    """
    a an the and or but if while whereas although though because since unless until when whenever where wherever
    of to in on at by for with about into over under between among during without within across per
    is are was were be been being am do does did done doing have has had having
    can could should would may might must will shall
    i me my mine we us our ours you your yours he him his she her hers it its they them their theirs
    this that these those such there here who whom whose which what when why how
    not no nor none neither either also too very more most much many few less least
    than then so such both each every all any some other others another same own only just still yet even
    as from up down out off again once ever never always often sometimes usually rather quite
    one two three four five first second third next last
    s t d ll re ve m
    """.split()
)


def content_tokens(text: str) -> list[str]:
    return [t for t in tokens(text) if t not in STOPWORDS and len(t) > 1]


def ngrams(seq: list[str], n: int):
    for i in range(len(seq) - n + 1):
        yield tuple(seq[i : i + n])


def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def short_quote(s: str, max_len: int = 130) -> str:
    """Trim a sentence to a safe markdown-inline quote."""
    s = norm_space(s)
    if len(s) <= max_len:
        return s
    cut = s[:max_len]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:") + " ..."


def round_half(x: float) -> float:
    """IELTS rounding: .25 -> up to .5, .75 -> up to next integer."""
    return math.floor(x * 2 + 0.5) / 2


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def quantiles(values: list[float], qs=(0.0, 0.25, 0.5, 0.75, 1.0)) -> list[float]:
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return [float("nan")] * len(qs)
    out = []
    for q in qs:
        if q <= 0:
            out.append(vals[0])
            continue
        if q >= 1:
            out.append(vals[-1])
            continue
        pos = q * (len(vals) - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            out.append(vals[lo])
        else:
            frac = pos - lo
            out.append(vals[lo] * (1 - frac) + vals[hi] * frac)
    return out


# ---------------------------------------------------------------- vocabularies

# A compact Academic Word List subset (headwords). Used only as an auxiliary
# lexical-range signal; documented in feature-distribution.md.
AWL = set(
    """
    abstract academy access accommodate accompany accumulate accurate achieve acknowledge acquire adapt adequate
    adjacent adjust administration advocate affect aggregate allocate alter alternative ambiguous amend analyse
    analysis annual anticipate apparent append appreciate approach appropriate approximate arbitrary area aspect
    assemble assess assign assume attach attain attitude attribute authority automate available aware benefit bias
    brief capable capacity category cease challenge channel chapter chart chemical circumstance cite civil clarify
    classic clause code coherent coincide collapse colleague commence comment commission commit commodity
    communicate community compatible compensate compile complement complex component compound comprehensive
    comprise compute conceive concentrate concept conclude concurrent conduct confer confine confirm conflict
    conform consent consequence considerable consist constant constitute constrain construct consult consume
    contact contemporary context contract contradict contrary contrast contribute controversy convene converse
    convert convince cooperate coordinate core corporate correspond cycle data debate decade decline deduce
    define demonstrate denote deny derive design despite detect deviate device devote differentiate dimension
    diminish discrete discriminate displace display dispose distinct distort distribute diverse document
    domestic dominate draft dramatic duration dynamic economy edit element eliminate emerge emphasis empirical
    enable encounter enforce enhance enormous ensure entity environment equate equip equivalent erode establish
    estimate ethical evaluate evident evolve exceed exclude expand explicit exploit expose external extract
    facilitate factor feature federal fee file final finance finite flexible fluctuate focus format formula
    framework function fundamental gender generate generation global goal grant guarantee guideline hypothesis
    identify ideology illustrate implement imply impose incentive incidence incline income incorporate indicate
    inevitable infer inhibit initial initiate innovate input inspect instance institute instruct integrate
    integrity intense interact interpret interval intervene intrinsic investigate invoke involve isolate issue
    item job journal justify label labour layer lecture legal legislation levy liberal license link locate logic
    maintain major manipulate mature maximize mechanism media mediate method migrate military minimal minimize
    ministry minor mode modify monitor motive mutual negate negotiate network neutral nevertheless norm
    normalise notion objective obtain occupy occur offset ongoing option orient outcome overall overlap
    participate perceive percent period persist perspective phase phenomenon policy portion pose positive
    potential practitioner precede precise predict preliminary presume prevail primary principle prior priority
    proceed process professional prohibit project promote proportion prospect protocol publish purchase pursue
    qualitative quote radical random range ratio rational react recover refine regime region register regulate
    reinforce reject relax release relevant reluctance rely remove require research reside resolve resource
    respond restore restrain restrict retain reveal revenue reverse revise revolution rigid role route scenario
    scheme scope sector secure seek select sequence series shift significant similar simulate site so-called sole
    somewhat source specific specify sphere stable statistic status straightforward strategy stress structure
    submit subordinate subsequent subsidy substitute successor suffice sufficient sum summary supplement survey
    survive suspend sustain symbol target task team technical technique technology temporary tense terminate
    text theme theory thereby thesis topic trace tradition transfer transform transit transmit trend trigger
    ultimate undergo underlie undertake uniform unify unique utilize valid vary vehicle version via violate
    virtual visible vision visual volume welfare whereas widespread
    """.split()
)

TEMPLATE_PHRASES = [
    "in this modern era",
    "in this day and age",
    "every coin has two sides",
    "in a nutshell",
    "as far as i am concerned",
    "it is undeniable that",
    "last but not least",
    "with the development of",
    "nowadays more and more",
    "in this essay i will",
    "this essay will discuss",
    "in the contemporary society",
    "with the rapid development of",
    "it is a controversial issue",
    "there is a heated debate",
    "first and foremost",
]

MECHANISM_MARKERS = [
    "because",
    "due to",
    "owing to",
    "this means",
    "as a result",
    "leads to",
    "lead to",
    "results in",
    "result in",
    "causes",
    "cause",
    "so that",
    "in that way",
    "by doing",
    "through this",
    "the reason is",
    "this is largely because",
    "consequently",
    "therefore",
    "thus",
    "hence",
]

EXAMPLE_MARKERS = [
    "for example",
    "for instance",
    "such as",
    "a case in point",
    "to illustrate",
    "take",
    "consider",
    "namely",
]

IMPLICATION_MARKERS = [
    "this means",
    "this shows",
    "this suggests",
    "in other words",
    "which is why",
    "it is therefore",
    "the result is",
    "as a consequence",
    "what this reveals",
]

SUBORDINATORS = [
    "although",
    "though",
    "even though",
    "even if",
    "while",
    "whereas",
    "because",
    "since",
    "unless",
    "until",
    "whenever",
    "wherever",
    "despite",
    "in spite of",
    "so that",
    "provided that",
    "as long as",
    "which",
    "who",
    "whom",
    "whose",
    "that",
    "whether",
]

CONNECTIVES = {
    "additive": [
        "furthermore",
        "moreover",
        "in addition",
        "additionally",
        "besides",
        "what is more",
        "similarly",
        "likewise",
        "also",
    ],
    "contrast": [
        "however",
        "nevertheless",
        "nonetheless",
        "on the contrary",
        "in contrast",
        "whereas",
        "although",
        "despite",
        "in spite of",
        "on the other hand",
        "yet",
        "but",
    ],
    "cause": [
        "because",
        "since",
        "due to",
        "owing to",
        "therefore",
        "thus",
        "hence",
        "consequently",
        "as a result",
        "for this reason",
    ],
    "example": ["for example", "for instance", "such as", "to illustrate", "namely", "a case in point"],
    "sequence": [
        "firstly",
        "first of all",
        "secondly",
        "thirdly",
        "finally",
        "lastly",
        "next",
        "then",
    ],
    "conclusion": ["in conclusion", "to conclude", "to sum up", "in summary", "overall"],
}

MECHANICAL_CONNECTIVES = [
    "firstly",
    "first of all",
    "secondly",
    "thirdly",
    "finally",
    "lastly",
    "moreover",
    "furthermore",
    "in addition",
    "on the one hand",
    "on the other hand",
    "in conclusion",
    "to sum up",
]

POSITION_RE = re.compile(
    r"\b(?:i\s+(?:believe|think|agree|disagree|feel|would\s+argue|am\s+convinced)|"
    r"in\s+my\s+(?:opinion|view)|my\s+(?:opinion|view)\s+is|from\s+my\s+perspective|"
    r"personally\s*,?\s*i|this\s+essay\s+will\s+argue|i\s+am\s+of\s+the\s+(?:opinion|view))\b",
    re.I,
)


def compile_multiword(items: list[str]) -> re.Pattern:
    pats = sorted({re.escape(i).replace(r"\ ", r"\s+") for i in items if i}, key=len, reverse=True)
    return re.compile(r"(?<![a-z])(?:" + "|".join(pats) + r")(?![a-z])", re.I)


CONN_RE = {k: compile_multiword(v) for k, v in CONNECTIVES.items()}
MECH_CONN_RE = compile_multiword(MECHANICAL_CONNECTIVES)
MECHANISM_RE = compile_multiword(MECHANISM_MARKERS)
EXAMPLE_RE = compile_multiword(EXAMPLE_MARKERS)
IMPLICATION_RE = compile_multiword(IMPLICATION_MARKERS)
SUBORD_RE = compile_multiword(SUBORDINATORS)
TEMPLATE_RE = compile_multiword(TEMPLATE_PHRASES)


# ---------------------------------------------------------------- error patterns


def _p(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.I)


PATTERNS: dict[str, dict] = {
    # ---- TR
    "TR-template-opening": {
        "module": "TR",
        "name": "模板化开头",
        "negative_transfer": True,
        "signal": "开头使用可套用任何题目的万能句（in this modern era / with the development of ...）",
        "fix": "把万能句换成对本题具体概念的重述：点出争议点 + 双方立场 + 自己的回应方向。",
        "regex": TEMPLATE_RE,
    },
    "TR-generic-example": {
        "module": "TR",
        "name": "例证停留在常识层",
        "negative_transfer": False,
        "signal": "例证只有 for example, many people ... 式泛化，没有具体主体、场景或数据",
        "fix": "给例证加上具体主体与情境（谁、在哪里、什么条件下发生了变化），并解释它如何证明论点。",
        "regex": _p(r"for\s+(?:example|instance)\s*,?\s*(?:many|most|some|a\s+lot\s+of)\s+(?:people|students|children|countries|governments)"),
    },
    "TR-unaddressed-question": {
        "module": "TR",
        "name": "题目关键词未回应",
        "negative_transfer": False,
        "signal": "题干核心实词/限定词在全文覆盖率低，或只回应了题目的一半",
        "fix": "先圈定题干实词与限定词，逐段核对回应位置，缺哪一块补哪一块的论证。",
        "regex": None,  # computed from question coverage
    },
    "TR-one-sided-discussion": {
        "module": "TR",
        "name": "讨论题只展开一方",
        "negative_transfer": False,
        "signal": "discuss both views 题目中一方观点只被提及而未展开",
        "fix": "给被冷落的一方独立段落：观点 → 机制 → 例证 → 回扣，再给出自己的取舍理由。",
        "regex": None,
    },
    # ---- CC
    "CC-mechanical-connectors": {
        "module": "CC",
        "name": "连接词机械化",
        "negative_transfer": True,
        "signal": "段落开头反复 Firstly / Secondly / Moreover；显性连接词密度过高且集中在段首",
        "fix": "删除可由语义自然衔接的连接词，用指代链与同义替换推进（this policy / such measures / that shift）。",
        "regex": MECH_CONN_RE,
    },
    "CC-paragraph-opener-repeat": {
        "module": "CC",
        "name": "段落开头重复",
        "negative_transfer": False,
        "signal": "两个以上段落用同一词/同一句式开头",
        "fix": "改用不同的信息起点：一段从原因切入，一段从结果或反例切入。",
        "regex": None,
    },
    "CC-short-sentence-run": {
        "module": "CC",
        "name": "连续短句堆叠",
        "negative_transfer": False,
        "signal": "连续 3 句以上均为 12 词以内的短句，句间无明确逻辑推进",
        "fix": "把关系最近的短句合并为从句或分词结构，或补一句解释句说明前句的意义。",
        "regex": None,
    },
    "CC-dangling-reference": {
        "module": "CC",
        "name": "指代断裂",
        "negative_transfer": False,
        "signal": "句首 this/they/it 指代前文不明确或跨段跳跃",
        "fix": "把代词换成具体名词（this policy / these conditions），或补一个限定短语明确指向。",
        "regex": _p(r"(?:^|[.!?]\s+)this\s+(?:is|has|can|will|would|means|causes|makes)\b"),
    },
    # ---- LR
    "LR-unlearn-knowledge": {
        "module": "LR",
        "name": "搭配错误：learn knowledge",
        "negative_transfer": True,
        "signal": "learn knowledge / study knowledge（中文『学习知识』直译）",
        "fix": "acquire / gain / obtain knowledge。",
        "regex": _p(r"\b(?:learn|learning|study|studying|studied)\s+(?:some\s+|much\s+|a\s+lot\s+of\s+)?knowledge\b"),
    },
    "LR-make-crime": {
        "module": "LR",
        "name": "搭配错误：make crime",
        "negative_transfer": True,
        "signal": "make crime / make mistakes in collocation（中文『犯罪』直译）",
        "fix": "commit a crime / engage in criminal activity。",
        "regex": _p(r"\bmake\s+(?:a\s+)?(?:crime|crimes)\b(?!\s+(?:fiction|novels?|dramas?|shows?|stories|rates?))"),
    },
    "LR-verb-prep": {
        "module": "LR",
        "name": "搭配错误：多余介词",
        "negative_transfer": True,
        "signal": "discuss about / emphasize on / mention about / research about 等动词冗余介词",
        "fix": "删去多余介词：discuss sth / emphasise sth / mention sth / research sth。",
        "regex": _p(r"\b(?:discuss(?:ed|ing)?\s+about|mention(?:ed|ing)?\s+about|explain(?:ed|ing)?\s+about)\b"),
    },
    "LR-open-light": {
        "module": "LR",
        "name": "中式直译：open the light",
        "negative_transfer": True,
        "signal": "open the light / open the TV / close the light 等动宾直译",
        "fix": "turn on the light / turn on the TV / turn off the light。",
        "regex": _p(r"\b(?:open|close|opened|closed)\s+(?:the\s+)?(?:light|lights|tv|television|computer)\b"),
    },
    "LR-vague-intensifier": {
        "module": "LR",
        "name": "词汇贫乏：very + 形容词",
        "negative_transfer": False,
        "signal": "very important / very big / very good 等高密度模糊强化",
        "fix": "换成精确形容词（crucial / pivotal / substantial / detrimental），或直接用量化信息替代。",
        "regex": _p(r"\bvery\s+(?:important|big|good|bad|much|many|serious|difficult|easy)\b"),
    },
    "LR-a-lot-of": {
        "module": "LR",
        "name": "语域不当：a lot of",
        "negative_transfer": False,
        "signal": "学术语域中反复使用 a lot of / lots of / kids / stuff 等口语表达",
        "fix": "a considerable number of / numerous / children / material 等学术表达。",
        "regex": _p(r"\b(?:a\s+lot\s+of|lots\s+of|kids|stuff|things\s+like)\b"),
    },
    "LR-more-and-more": {
        "module": "LR",
        "name": "重复用词：more and more",
        "negative_transfer": False,
        "signal": "more and more 反复出现，且全文重复使用同一名词",
        "fix": "an increasing number of / a growing proportion of / rising。",
        "regex": _p(r"\bmore\s+and\s+more\b"),
    },
    "LR-people-overuse": {
        "module": "LR",
        "name": "重复用词：people",
        "negative_transfer": False,
        "signal": "people 在全文出现次数过多，缺少同义替换（individuals / citizens / residents / the public）",
        "fix": "按语境替换为 individuals / citizens / residents / employees / the public。",
        "regex": None,
    },
    # ---- GRA
    "GRA-although-but": {
        "module": "GRA",
        "name": "从句误用：although ... but",
        "negative_transfer": True,
        "signal": "although/though 与 but 在同一句连用（中文『虽然……但是……』负迁移）",
        "fix": "二选一：Although X, Y. / X, but Y。",
        "regex": _p(
            r"\b(?:although|though)\b(?![^.!?]{0,90}\b(?:no|any|little|nothing|anything)\s+choice\s+but\b)"
            r"[^.!?]{0,120}?\bbut\b(?!\s+also\b)"
        ),
    },
    "GRA-there-be": {
        "module": "GRA",
        "name": "there be 滥用",
        "negative_transfer": True,
        "signal": "there is/are 反复使用，且多为无信息量的存在句",
        "fix": "改写成实义主语结构：Many governments face ... / This trend produces ...。",
        "regex": _p(r"\bthere\s+(?:is|are|was|were)\b"),
    },
    "GRA-sva": {
        "module": "GRA",
        "name": "主谓一致",
        "negative_transfer": True,
        "signal": "复数主语 + is/was/has/does、第三人称单数主语 + are/were/have/do",
        "fix": "主谓一致：People are / The government has / They have / It is。",
        "regex": _p(
            r"\b(?:people|students|children|parents|governments|individuals|countries|companies|they|we)\s+(?:is|was|has|does)\b|"
            r"\b(?:he|she|it)\s+(?:are|were|have|do)\b|"
            r"\bthere\s+(?:is|was)\s+(?:many|several|a\s+number\s+of|a\s+lot\s+of|lots\s+of)\b|"
            r"\bthere\s+(?:are|were)\s+(?:much|a\s+great\s+deal\s+of)\b"
        ),
    },
    "GRA-modal-form": {
        "module": "GRA",
        "name": "情态动词后接错形",
        "negative_transfer": True,
        "signal": "should to / can to / must to / can able to / should can 等",
        "fix": "情态动词后接动词原形：should take / can help / must be。",
        "regex": _p(r"\b(?:should|can|could|must|may|might|will|would)\s+(?:to\s+\w+|able\s+to)\b"),
    },
    "GRA-double-comparative": {
        "module": "GRA",
        "name": "双重比较级",
        "negative_transfer": True,
        "signal": "more better / more easier / more happier 等",
        "fix": "better / easier / happier。",
        "regex": _p(r"\bmore\s+(?:better|easier|happier|worse|higher|lower|bigger|smaller|cheaper|faster)\b"),
    },
    "GRA-countability": {
        "module": "GRA",
        "name": "不可数名词复数化",
        "negative_transfer": True,
        "signal": "informations / advices / equipments / knowledges / researches / evidences 等",
        "fix": "information / advice / equipment / knowledge / research / evidence（不可数）。",
        "regex": _p(r"\b(?:informations|advices|equipments|knowledges|researches|evidences|homeworks|moneys)\b"),
    },
    "GRA-one-of": {
        "module": "GRA",
        "name": "one of the + 单数",
        "negative_transfer": True,
        "signal": "one of the + 单数名词（one of the reason）",
        "fix": "one of the + 复数名词（one of the reasons）。",
        "regex": _p(
            r"\bone\s+of\s+the\s+(?:(?:main|major|most\s+important|biggest|primary|principal|key|common|important|serious)\s+)?"
            r"(?:reason|problem|cause|factor|issue|benefit|advantage|disadvantage|student|country|person|company|way)(?![a-z])"
        ),
    },
    "GRA-run-on": {
        "module": "GRA",
        "name": "run-on 句",
        "negative_transfer": False,
        "signal": "单句超过 45 词、含多个并列谓词却只用逗号连接",
        "fix": "按意群拆分，或补上从属连词/分号建立层级。",
        "regex": None,
    },
    "GRA-comma-splice": {
        "module": "GRA",
        "name": "标点：逗号粘连",
        "negative_transfer": False,
        "signal": "逗号连接两个独立句且用 however/therefore 作连接词（缺分号或另起句）",
        "fix": "; however, ... / . Therefore, ...。",
        "regex": _p(r",\s*(?:however|therefore|thus|moreover|furthermore)\s+(?!,)[a-z]"),
    },
    "GRA-fragment": {
        "module": "GRA",
        "name": "句子残缺",
        "negative_transfer": False,
        "signal": "Because/Although 引导的从句单独成句（无主句）",
        "fix": "补主句或把从句并入完整句子。",
        "regex": _p(r"(?:^|[.!?]\s+)(?:because|although|though|while|if)\b[^.!?]*$"),
    },
    "GRA-article-gov": {
        "module": "GRA",
        "name": "冠词缺失：Government should",
        "negative_transfer": True,
        "signal": "句首 Government/Technology/Education 等单数可数名词无冠词",
        "fix": "The government should ... / Technology（不可数泛指可无冠词）。",
        "regex": _p(r"(?:^|[.!?]\s+)(?:government|country|school|university|student|child|company)\s+(?:should|must|can|has|is|needs)"),
    },
}


def sentence_hits(text: str, regex: re.Pattern | None) -> list[tuple[str, str]]:
    """Return (sentence, matched-text) pairs for a pattern."""
    if regex is None:
        return []
    out = []
    for s in sentences(text):
        m = regex.search(s)
        if m:
            out.append((s, m.group(0)))
    return out


def detect_document_patterns(rec: dict) -> dict[str, list[tuple[str, str]]]:
    """Detect sentence-level patterns for one essay."""
    text = rec["essay"]
    found: dict[str, list[tuple[str, str]]] = {}
    for pid, spec in PATTERNS.items():
        hits = sentence_hits(text, spec.get("regex"))
        if hits:
            found[pid] = hits
    # document-level patterns
    feat = base_text_stats(text)
    if feat["mech_connector_paragraph_openers"] >= 2 or feat["mechanical_connector_density"] >= 2.0:
        found["CC-mechanical-connectors"] = [
            (opener, opener) for opener in feat["paragraph_openers"] if MECH_CONN_RE.search(opener)
        ] or found.get("CC-mechanical-connectors", [])
    else:
        found.pop("CC-mechanical-connectors", None)
    tb = len(re.findall(r"\bthere\s+(?:is|are|was|were)\b", text, re.I))
    if tb >= max(3, feat["word_count"] / 120):
        found["GRA-there-be"] = found.get("GRA-there-be", [])
    else:
        found.pop("GRA-there-be", None)
    if feat["short_sentence_run"]:
        found["CC-short-sentence-run"] = [(" ".join(feat["short_sentence_run_example"]), "short-run")]
    if feat["run_on"]:
        found["GRA-run-on"] = [(feat["run_on"][0], "run-on")]
    if feat["people_count"] >= max(6, feat["word_count"] / 40):
        found["LR-people-overuse"] = []
    return found


# ---------------------------------------------------------------- base stats


def base_text_stats(text: str) -> dict:
    paras = paragraphs(text)
    sents = sentences(text)
    toks = tokens(text)
    wc = len(toks)
    sent_lens = [len(tokens(s)) for s in sents] or [0]
    sub_count = sum(len(SUBORD_RE.findall(s)) for s in sents)
    connector_counts = {cat: len(rx.findall(text)) for cat, rx in CONN_RE.items()}
    mech = MECH_CONN_RE.findall(text)
    openers = []
    for p in paras:
        first = re.match(r"[\"'(]?\s*([A-Za-z][A-Za-z'\u2019]*(?:\s+[A-Za-z][A-Za-z'\u2019]*){0,4})", p)
        if first:
            openers.append(first.group(1))
    opener_first_words = [o.split()[0].lower() for o in openers if o]
    mech_para_openers = sum(1 for o in openers if MECH_CONN_RE.search(o))
    # short sentence runs
    run = []
    short_run_example: list[str] = []
    for s in sents:
        if len(tokens(s)) <= 12:
            run.append(s)
        else:
            if len(run) >= 3 and not short_run_example:
                short_run_example = run[:3]
            run = []
    if len(run) >= 3 and not short_run_example:
        short_run_example = run[:3]
    # run-on heuristic
    run_on = [
        s
        for s in sents
        if len(tokens(s)) > 45 and len(re.findall(r",", s)) >= 3 and len(re.findall(r"\b(?:and|but|so|or)\b", s, re.I)) >= 2
    ]
    content = [t for t in toks if t not in STOPWORDS and len(t) > 1]
    ttr250 = len(set(content[:250])) / max(1, len(content[:250]))
    refs = re.compile(r"\b(?:this|these|those|they|them|their|it|its|such|which|that)\b", re.I)
    chain = 0
    best_chain = 0
    for s in sents:
        if refs.search(s):
            chain += 1
            best_chain = max(best_chain, chain)
        else:
            chain = 0
    # sentence-type mix (heuristic)
    simple = compound = complex_ = 0
    for s in sents:
        has_sub = bool(SUBORD_RE.search(s))
        has_coord = bool(re.search(r",\s*(?:and|but|so|or)\s", s, re.I)) or bool(re.search(r"\b(?:and|but|so|or)\b", s, re.I)) and len(re.findall(r"\b(?:is|are|was|were|has|have|had|can|could|will|would|should|may|might|do|does|did)\b", s, re.I)) >= 2
        if has_sub:
            complex_ += 1
        elif has_coord:
            compound += 1
        else:
            simple += 1
    n_sents = max(1, len(sents))
    # specificity signals
    proper = 0
    for s in sents:
        for m in re.finditer(r"\b([A-Z][a-z]{2,})\b", s):
            w = m.group(1)
            if s[: m.start()].strip() and w not in ("I", "IELTS"):
                proper += 1
    numeric = len(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", text))
    implication = len(IMPLICATION_RE.findall(text))
    example_sents = [s for s in sents if EXAMPLE_RE.search(s)]
    specific_examples = 0
    for s in example_sents:
        if re.search(r"\b\d+(?:[.,]\d+)?%?\b", s) or re.search(r"(?<!^)\b[A-Z][a-z]{2,}\b", s):
            specific_examples += 1
    return {
        "word_count": wc,
        "paragraph_count": len(paras),
        "sentence_count": len(sents),
        "avg_sentence_length": statistics.mean(sent_lens) if sent_lens else 0.0,
        "sentence_len_sd": statistics.pstdev(sent_lens) if len(sent_lens) > 1 else 0.0,
        "long_sentence_ratio": sum(1 for x in sent_lens if x > 25) / max(1, len(sent_lens)),
        "subordinate_count": sub_count,
        "subordinate_density": sub_count * 100 / max(1, wc),
        "connector_total": sum(connector_counts.values()),
        "connector_density": sum(connector_counts.values()) * 100 / max(1, wc),
        "connector_variety": sum(1 for v in connector_counts.values() if v),
        "connector_counts": connector_counts,
        "mechanical_connector_count": len(mech),
        "mechanical_connector_density": len(mech) * 100 / max(1, wc),
        "mech_connector_paragraph_openers": mech_para_openers,
        "paragraph_openers": openers,
        "paragraph_opener_first_words": opener_first_words,
        "short_sentence_run": bool(short_run_example),
        "short_sentence_run_example": short_run_example,
        "run_on": run_on,
        "ttr250": ttr250,
        "content_token_count": len(content),
        "reference_chain_max": best_chain,
        "reference_density": len(refs.findall(text)) * 100 / max(1, wc),
        "simple_ratio": simple / n_sents,
        "compound_ratio": compound / n_sents,
        "complex_ratio": complex_ / n_sents,
        "proper_noun_count": proper,
        "numeric_count": numeric,
        "implication_count": implication,
        "specific_example_count": specific_examples,
        "example_sentence_count": len(example_sents),
        "people_count": len(re.findall(r"\bpeople\b", text, re.I)),
        "template_hits": len(TEMPLATE_RE.findall(text)),
        "mechanism_hits": len(MECHANISM_RE.findall(text)),
        "example_hits": len(EXAMPLE_RE.findall(text)),
        "template_matches": TEMPLATE_RE.findall(text),
        "mechanism_matches": MECHANISM_RE.findall(text),
        "example_matches": EXAMPLE_RE.findall(text),
        "position_marker": bool(POSITION_RE.search(text)),
        "position_in_intro": bool(paras and POSITION_RE.search(paras[0])),
        "position_in_conclusion": bool(paras and POSITION_RE.search(paras[-1])),
    }


def compute_features(rec: dict, vocab_df: dict[str, int] | None = None, n_docs: int = 0) -> dict:
    """All quantitative features used by the blind scorer and the distribution table."""
    text = rec["essay"]
    base = base_text_stats(text)
    toks = tokens(text)
    wc = max(1, len(toks))
    content = [t for t in toks if t not in STOPWORDS and len(t) > 1]
    long_words = sum(1 for t in toks if len(t) >= 7)
    awl_hits = sum(1 for t in content if t in AWL)
    rare = 0
    if vocab_df:
        for t in toks:
            if len(t) >= 4 and vocab_df.get(t, 0) <= 2:
                rare += 1
    q_tokens = [t for t in content_tokens(rec["question"]) if len(t) > 2]
    q_set = set()
    for t in q_tokens:
        q_set.add(t)
        if t.endswith("s") and len(t) > 4:
            q_set.add(t[:-1])
    body = set(toks) | {t[:-1] if t.endswith("s") and len(t) > 4 else t for t in toks}
    coverage = len([t for t in q_set if t in body]) / max(1, len(q_set))
    feats = dict(base)
    feats.update(
        {
            "id": rec["id"],
            "band": rec["band"],
            "task_type": effective_task_type(rec),
            "topic": rec["topic"],
            "source": rec["source"],
            "long_word_ratio": long_words / wc,
            "awl_ratio": awl_hits / max(1, len(content)),
            "rare_token_ratio": rare / wc,
            "question_keyword_coverage": coverage,
        }
    )
    if feats["paragraph_opener_first_words"]:
        c = collections.Counter(feats["paragraph_opener_first_words"])
        feats["paragraph_opener_max_repeat"] = max(c.values())
    else:
        feats["paragraph_opener_max_repeat"] = 0
    return feats


def build_vocab_df(recs: list[dict]) -> dict[str, int]:
    df: dict[str, int] = collections.Counter()
    for rec in recs:
        df.update(set(tokens(rec["essay"])))
    return dict(df)


# ---------------------------------------------------------------- blind scorer


def _checklist_band(points: int, max_points: int) -> float:
    """Map a descriptor checklist score to an IELTS-style band value."""
    table = {
        0: 4.0,
        1: 4.5,
        2: 5.0,
        3: 5.5,
        4: 6.0,
        5: 6.5,
        6: 7.0,
        7: 7.5,
        8: 8.0,
        9: 9.0,
    }
    pts = int(round(points / max_points * 9)) if max_points != 9 else points
    return table.get(max(0, min(9, pts)), 6.0)


def blind_module_scores(feat: dict) -> dict[str, float]:
    """Descriptor-operationalised scores that never see the true band.

    The scorer is deliberately simple and fully documented in the deviation
    report; its purpose is to expose where the official descriptors and the
    measured text features disagree, not to replace examiner judgement.
    """
    wc = feat["word_count"]
    # TR checklist (0-9)
    tr = 0
    if feat["question_keyword_coverage"] >= 0.65:
        tr += 2
    elif feat["question_keyword_coverage"] >= 0.45:
        tr += 1
    if feat["position_marker"]:
        tr += 1
    if feat["position_in_intro"]:
        tr += 1
    if feat["paragraph_count"] >= 4:
        tr += 1
    if feat["mechanism_hits"] >= 3:
        tr += 1
    if feat["example_hits"] >= 2:
        tr += 1
    if wc >= 250:
        tr += 1
    if feat["mechanism_hits"] >= 5 and feat["example_hits"] >= 3:
        tr += 1
    # CC checklist
    cc = 0
    if 3 <= feat["paragraph_count"] <= 6:
        cc += 2
    if feat["connector_variety"] >= 4:
        cc += 1
    if feat["connector_density"] <= 9:
        cc += 1
    if feat["mechanical_connector_density"] < 1.5:
        cc += 1
    if feat["paragraph_opener_max_repeat"] <= 1:
        cc += 1
    if feat["reference_chain_max"] >= 2:
        cc += 1
    if not feat["short_sentence_run"]:
        cc += 1
    if feat["reference_density"] >= 2:
        cc += 1
    # LR checklist
    lr = 0
    if feat["ttr250"] >= 0.62:
        lr += 2
    elif feat["ttr250"] >= 0.52:
        lr += 1
    if feat["long_word_ratio"] >= 0.20:
        lr += 1
    if feat["awl_ratio"] >= 0.06:
        lr += 1
    if feat["rare_token_ratio"] <= 0.02:
        lr += 1
    if feat["people_count"] <= max(4, wc / 45):
        lr += 1
    if not feat["template_hits"]:
        lr += 1
    if feat["question_keyword_coverage"] >= 0.55:
        lr += 1
    if feat["connector_variety"] >= 5:
        lr += 1
    # GRA checklist
    gra = 0
    if 14 <= feat["avg_sentence_length"] <= 24:
        gra += 2
    if feat["subordinate_density"] >= 2.0:
        gra += 1
    if feat["sentence_len_sd"] >= 5:
        gra += 1
    if not feat["run_on"]:
        gra += 1
    if feat["connector_variety"] >= 4:
        gra += 1
    if feat["word_count"] >= 250:
        gra += 1
    if feat["rare_token_ratio"] <= 0.015:
        gra += 1
    if feat["long_sentence_ratio"] <= 0.35:
        gra += 1
    return {
        "TR": _checklist_band(tr, 9),
        "CC": _checklist_band(cc, 9),
        "LR": _checklist_band(lr, 9),
        "GRA": _checklist_band(gra, 9),
    }


def infer_subscores(feat: dict, band: float, blind: dict[str, float]) -> tuple[dict[str, float], str]:
    """Anchored distribution of the true total band across four dimensions.

    The blind module estimates provide the relative strengths/weaknesses;
    the known total band anchors the level; the official rounding rule is
    enforced as a constraint. Marked as inferred in the enriched records.
    """
    mean_blind = statistics.mean(blind.values())
    offsets = {d: clamp(round_half(blind[d] - mean_blind), -1.0, 1.0) for d in blind}
    subs = {d: clamp(round_half(band + offsets[d]), 4.0, 9.0) for d in blind}
    # enforce official rounding: mean of the four rounds to the true band
    for _ in range(12):
        avg = statistics.mean(subs.values())
        if round_half(avg) == band:
            break
        # nudge the most extreme dimension toward the band
        d = max(subs, key=lambda k: abs(subs[k] - band))
        step = 0.5 if subs[d] < band else -0.5
        new = clamp(subs[d] + step, 4.0, 9.0)
        if new == subs[d]:
            break
        subs[d] = new
    avg = statistics.mean(subs.values())
    if round_half(avg) != band:
        # last resort: collapse to the band itself
        subs = {d: band for d in blind}
        return subs, "low"
    conf = "medium"
    if all(abs(blind[d] - band) <= 0.5 for d in blind):
        conf = "high"
    elif any(abs(blind[d] - band) > 1.5 for d in blind):
        conf = "low"
    return subs, conf


# ---------------------------------------------------------------- collocations


GENERIC_TOKENS = set(
    """
    people person society world country countries government governments individual individuals
    thing things way ways time times year years day days life lives problem problems issue issues
    reason reasons cause causes result results effect effects change changes development developments
    number amount level levels part parts place places area areas group groups point points fact facts
    example examples situation situations case cases question questions answer answers idea ideas
    importance role impact benefit benefits drawback drawback advantage advantages disadvantage disadvantages
    good bad important necessary possible impossible able huge big small large great high low
    make makes made making take takes took taking get gets got getting give gives gave giving
    think thinks thought thinking know knows knew known knowing see sees saw seeing come comes came coming
    go goes went going use uses used using need needs needed needing want wants wanted wanting
    help helps helped helping become becomes became becoming
    """.split()
)


def extract_collocations(
    recs: list[dict],
    min_docs: int = 3,
    ns=(2, 3, 4),
    min_docs_map: dict[str, int] | None = None,
) -> dict:
    """Topic-seeded collocation mining over the provided records.

    Candidate grams must contain at least one topic-seed token, so each entry
    is anchored to the topic's context. Returns {"topics": {...}, "generic": {...}}
    with a real example sentence and its source id for every surviving gram.
    """
    min_docs_map = min_docs_map or {}
    by_topic: dict[str, dict[tuple, dict]] = {t: {} for t in TOPICS}
    generic: dict[tuple, dict] = {}
    total_docs = len(recs)
    seed_res = {t: topic_seed_re(t) for t in TOPICS}
    for rec in recs:
        toks = tokens(rec["essay"])
        text = rec["essay"]
        band = rec["band"]
        topic = rec["topic"]
        seed_re = seed_res[topic]
        sents = sentences(text)
        seen: set[tuple] = set()
        for n in ns:
            for g in ngrams(toks, n):
                if g[0] in STOPWORDS or g[-1] in STOPWORDS:
                    continue
                if all(t in STOPWORDS or t in GENERIC_TOKENS for t in g):
                    continue
                if sum(1 for t in g if t in STOPWORDS) > n - 2:
                    continue
                if len(" ".join(g)) < 8:
                    continue
                if not seed_re.search(" ".join(g)):
                    continue
                seen.add(g)
        for g in seen:
            gram = " ".join(g)
            # find example sentence
            sent = None
            for s in sents:
                if re.search(r"(?<![a-z])" + re.escape(gram).replace(r"\ ", r"\s+") + r"(?![a-z])", s, re.I):
                    sent = s
                    break
            entry = {
                "gram": gram,
                "docs": 1,
                "bands": [band],
                "examples": [(rec["id"], band, sent or "")],
            }
            table = by_topic[topic]
            if g in table:
                table[g]["docs"] += 1
                table[g]["bands"].append(band)
                if len(table[g]["examples"]) < 3:
                    table[g]["examples"].append((rec["id"], band, sent or ""))
            else:
                table[g] = entry
        # generic candidates: no topic seed, still content-anchored
        for n in ns:
            for g in ngrams(toks, n):
                if g[0] in STOPWORDS or g[-1] in STOPWORDS:
                    continue
                if all(t in STOPWORDS or t in GENERIC_TOKENS for t in g):
                    continue
                if sum(1 for t in g if t in STOPWORDS) > n - 2:
                    continue
                if len(" ".join(g)) < 8:
                    continue
                if ALL_SEED_RE.search(" ".join(g)):
                    continue
                gram = " ".join(g)
                sent = None
                for s in sents:
                    if re.search(r"(?<![a-z])" + re.escape(gram).replace(r"\ ", r"\s+") + r"(?![a-z])", s, re.I):
                        sent = s
                        break
                if g in generic:
                    generic[g]["docs"] += 1
                    if len(generic[g]["examples"]) < 3:
                        generic[g]["examples"].append((rec["id"], band, sent or ""))
                else:
                    generic[g] = {
                        "gram": gram,
                        "docs": 1,
                        "bands": [band],
                        "examples": [(rec["id"], band, sent or "")],
                    }
    # keep topic grams with enough distinct documents
    kept: dict[str, dict] = {}
    for topic, table in by_topic.items():
        effective_min = min_docs_map.get(topic, min_docs)
        rows = {}
        for g, info in table.items():
            if info["docs"] < effective_min:
                continue
            rows[g] = dict(info)
        kept[topic] = rows
    gen_rows = {
        g: info
        for g, info in generic.items()
        if info["docs"] >= max(5, int(total_docs * 0.08))
    }
    return {"topics": kept, "generic": gen_rows}


def collocation_density(text: str, grams: list[str]) -> float:
    toks = len(tokens(text)) or 1
    hits = 0
    for g in grams:
        pat = r"(?<![a-z])" + re.escape(g).replace(r"\ ", r"\s+") + r"(?![a-z])"
        hits += len(re.findall(pat, text, re.I))
    return hits * 100 / toks


# ---------------------------------------------------------------- misc


def reliability_tier(rec: dict) -> str:
    src = rec["source"]
    if src in ("ieltswritingcorrectionservice.com", "ielts.international"):
        return "A-examiner"
    if src in ("cdieltsprep.com", "allthingsielts.com", "ieltsprepstudio.com", "bandnine.ai"):
        return "B-teacher"
    if src == "ielts-blog.com":
        return "C-blog"
    if src == "writing9.com":
        return "D-auto"
    return "E-other"


def md_escape_cell(s: str) -> str:
    return norm_space(s).replace("|", "\\|")


def sample_rows(rows: list, k: int, seed: int = 20261007) -> list:
    rng = random.Random(seed)
    rows = list(rows)
    rng.shuffle(rows)
    return rows[:k]

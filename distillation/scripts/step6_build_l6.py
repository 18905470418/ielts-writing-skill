"""Build L6 topic-vocab.md from curated entries + verified corpus evidence.

Each curated entry is (collocation, Chinese gloss, source sample id). The
builder verifies the collocation really occurs in the cited source, counts how
many band>=8 essays of the topic use it, and pulls a real example sentence.
Entries that fail verification are listed in reports/l6-review.md.
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distill_lib import (  # noqa: E402
    DATA_DIR,
    REFS_DIR,
    REPORT_DIR,
    TOPIC_CN,
    load_enriched,
    sentences,
    write_text,
)

# (collocation, gloss, source id)
CURATED: dict[str, list[tuple[str, str, str]]] = {
    "education": [
        ("practical skills", "实用技能", "B8-ADV-009"),
        ("higher education", "高等教育", "B8-ADV-009"),
        ("academic subjects", "学科课程", "B8-DIS-002"),
        ("educational institutions", "教育机构", "B8-REP-029"),
        ("communication skills", "沟通能力", "B8-ADV-030"),
        ("university education", "大学教育", "B8-DIS-033"),
        ("formal education", "正规教育", "B8-DIS-001"),
        ("tuition fees", "学费", "B8-ADV-021"),
        ("life skills", "生活技能", "B8-ADV-022"),
        ("academic performance", "学业表现", "B8-ADV-022"),
        ("university degree", "大学学位", "B8-ADV-009"),
        ("education systems", "教育体系", "B8-DIS-001"),
        ("vocational programmes", "职业培训课程", "B8-ADV-009"),
        ("hands-on experience", "实操经验", "B8-ADV-009"),
        ("wide range of subjects", "广泛的科目范围", "B8-DIS-015"),
        ("academic qualifications", "学历资格", "B8-DIS-033"),
        ("school curriculum", "学校课程体系", "B8-OP-078"),
    ],
    "technology": [
        ("mobile phones", "手机", "B8-OP-055"),
        ("modern technology", "现代科技", "B8-ADV-011"),
        ("technological advancements", "技术进步", "B8-ADV-015"),
        ("artificial intelligence", "人工智能", "B8-OP-055"),
        ("digital devices", "数字设备", "B8-OP-055"),
        ("digital tools", "数字工具", "B8-DIS-003"),
        ("digital communication", "数字通信", "B8-OP-063"),
        ("online platforms", "网络平台", "B8-ADV-036"),
        ("screen time", "屏幕使用时间", "B8-OP-057"),
        ("technological developments", "技术发展", "B8-ADV-015"),
        ("technology companies", "科技公司", "B85-ADV-022"),
        ("digital platforms", "数字平台", "B8-DIS-003"),
        ("online stores", "线上商店", "B8-ADV-004"),
        ("information online", "线上信息", "B8-ADV-036"),
        ("use of computers", "电脑的使用", "B8-OP-055"),
        ("new technologies", "新兴技术", "B8-OP-084"),
    ],
    "environment": [
        ("global warming", "全球变暖", "B8-REP-005"),
        ("environmental issues", "环境问题", "B8-OP-060"),
        ("climate change", "气候变化", "B8-OP-027"),
        ("fossil fuels", "化石燃料", "B8-REP-005"),
        ("natural environment", "自然环境", "B8-ADV-003"),
        ("natural resources", "自然资源", "B8-OP-060"),
        ("renewable energy", "可再生能源", "B8-OP-029"),
        ("air quality", "空气质量", "B8-ADV-003"),
        ("environmental degradation", "环境退化", "B8-REP-001"),
        ("renewable energy sources", "可再生能源来源", "B9-DIS-023"),
        ("habitat destruction", "栖息地破坏", "B8-ADV-003"),
        ("environmentally friendly", "环境友好的", "B8-DIS-025"),
        ("environmental protection", "环境保护", "B8-OP-027"),
        ("greenhouse gas emissions", "温室气体排放", "B85-DIS-027"),
        ("carbon emissions", "碳排放", "B8-OP-029"),
        ("conservation efforts", "保护行动", "B8-DIS-018"),
        ("natural habitats", "自然栖息地", "B8-OP-029"),
    ],
    "government": [
        ("public services", "公共服务", "B8-OP-050"),
        ("tax revenue", "税收收入", "B8-OP-050"),
        ("infrastructure spending", "基础设施支出", "B8-OP-005"),
        ("government-funded", "政府资助的", "B8-ADV-008"),
        ("minimum income", "最低收入保障", "B8-OP-026"),
        ("public money", "公共资金", "B85-OP-082"),
        ("public transportation", "公共交通运输", "B8-REP-030"),
        ("means of transport", "交通方式", "B85-OP-011"),
        ("taxpayers", "纳税人", "B8-OP-026"),
        ("public healthcare", "公共医疗", "B8-OP-054"),
        ("regulations", "法规/监管规定", "B8-DIS-005"),
        ("public facilities", "公共设施", "B9-TQ-008"),
        ("government regulations", "政府监管", "B8-DIS-022"),
        ("government policies", "政府政策", "B8-REP-030"),
        ("public transport system", "公共交通系统", "B85-ADV-005"),
    ],
    "social": [
        ("rural areas", "农村地区", "B8-ADV-001"),
        ("urban areas", "城市地区", "B8-OP-053"),
        ("senior citizens", "老年人", "B8-OP-053"),
        ("society as a whole", "整个社会", "B8-ADV-025"),
        ("community service", "社区服务", "B8-OP-064"),
        ("ageing population", "人口老龄化", "B8-REP-009"),
        ("family members", "家庭成员", "B8-OP-030"),
        ("younger generations", "年轻一代", "B8-ADV-006"),
        ("rural communities", "农村社区", "B8-ADV-001"),
        ("elderly citizens", "老年公民", "B8-OP-026"),
        ("elderly people", "老年人", "B8-OP-026"),
        ("city centre", "市中心", "B8-OP-053"),
        ("family and friends", "家人与朋友", "B8-ADV-026"),
        ("living standards", "生活水平", "B85-ADV-028"),
        ("working adults", "在职成年人", "B8-REP-009"),
    ],
    "crime": [
        ("criminal activities", "犯罪活动", "B85-OP-005"),
        ("criminal behaviour", "犯罪行为", "B8-OP-032"),
        ("crime prevention", "犯罪预防", "B8-OP-010"),
        ("criminal record", "犯罪记录", "B8-DIS-038"),
        ("committing crimes", "实施犯罪", "B8-OP-010"),
        ("law enforcement", "执法机关", "B8-OP-010"),
        ("reducing crime", "减少犯罪", "B8-REP-003"),
        ("crime rates", "犯罪率", "B8-OP-010"),
        ("potential offenders", "潜在犯罪者", "B8-DIS-038"),
        ("criminal activity", "犯罪行为", "B8-REP-003"),
        ("former offenders", "前科人员", "B8-REP-013"),
        ("prison system", "监狱体系", "B8-OP-032"),
        ("reoffending rates", "再犯率", "B8-OP-032"),
        ("commit crimes", "犯罪", "B8-DIS-034"),
        ("return to crime", "重新犯罪", "B8-OP-032"),
    ],
    "culture": [
        ("museums and art galleries", "博物馆与美术馆", "B8-OP-028"),
        ("universal language", "通用语言", "B8-OP-040"),
        ("different cultures", "不同文化", "B8-OP-040"),
        ("historical records", "历史记录", "B85-OP-018"),
        ("cultural heritage", "文化遗产", "B85-OP-010"),
        ("language learner", "语言学习者", "B8-OP-024"),
        ("local traditions", "地方传统", "B8-REP-008"),
        ("foreign language", "外语", "B8-TQ-005"),
        ("language skills", "语言能力", "B8-OP-024"),
        ("art galleries", "美术馆", "B8-OP-028"),
        ("cultural identity", "文化认同", "B8-OP-020"),
        ("traditional crafts", "传统手工艺", "B9-TQ-005"),
        ("cultural value", "文化价值", "B8-OP-028"),
        ("museum authorities", "博物馆管理机构", "B8-REP-008"),
        ("cultural boundaries", "文化边界", "B8-OP-040"),
        ("historic buildings", "历史建筑", "B9-OP-071"),
    ],
    "health": [
        ("physical activity", "体育活动", "B8-REP-004"),
        ("public health", "公共健康", "B8-ADV-008"),
        ("healthy lifestyle", "健康生活方式", "B8-DIS-005"),
        ("health problems", "健康问题", "B8-REP-018"),
        ("healthier lifestyles", "更健康的生活方式", "B8-REP-018"),
        ("public health costs", "公共健康成本", "B8-ADV-008"),
        ("childhood obesity", "儿童肥胖", "B8-REP-028"),
        ("regular exercise", "规律锻炼", "B8-REP-012"),
        ("dietary habits", "饮食习惯", "B8-DIS-005"),
        ("heart disease", "心脏病", "B8-DIS-031"),
        ("healthy food", "健康食品", "B8-DIS-022"),
        ("healthy diet", "健康饮食", "B8-DIS-042"),
        ("mental health", "心理健康", "B8-DIS-031"),
        ("sedentary lifestyle", "久坐生活方式", "B8-REP-012"),
        ("nutrition", "营养", "B8-DIS-022"),
        ("obesity-related illnesses", "肥胖相关疾病", "B9-OP-020"),
    ],
    "media": [
        ("social media", "社交媒体", "B8-REP-023"),
        ("social media platforms", "社交媒体平台", "B8-REP-023"),
        ("print media", "纸质媒体", "B8-REP-023"),
        ("streaming platforms", "流媒体平台", "B9-OP-085"),
        ("celebrity endorsement", "名人代言", "B9-DIS-015"),
        ("advertising campaign", "广告宣传活动", "B8-ADV-014"),
        ("completion rates", "完播率", "B9-ADV-001"),
        ("retention curves", "留存曲线", "B9-ADV-001"),
        ("behavioural data", "行为数据", "B9-ADV-033"),
        ("front page", "报纸头版", "B9-OP-060"),
        ("public interest", "公共利益", "B9-DIS-014"),
        ("target young children", "以低龄儿童为目标", "B9-OP-059"),
        ("viewers", "观众", "B8-OP-022"),
        ("readership", "读者群体", "B9-OP-060"),
        ("media coverage", "媒体报道", "B85-TQ-005"),
        ("news reports", "新闻报道", "B85-OP-057"),
    ],
    "globalization-work": [
        ("working hours", "工作时长", "B8-ADV-002"),
        ("work-life balance", "工作与生活平衡", "B8-REP-017"),
        ("job satisfaction", "工作满意度", "B8-DIS-014"),
        ("job opportunities", "就业机会", "B8-ADV-005"),
        ("economic growth", "经济增长", "B8-OP-050"),
        ("remote working", "远程办公", "B8-ADV-002"),
        ("changing jobs", "换工作", "B8-OP-031"),
        ("working life", "职业生涯", "B8-OP-031"),
        ("job market", "就业市场", "B8-ADV-028"),
        ("international companies", "跨国公司", "B85-ADV-032"),
        ("unemployment benefits", "失业救济", "B9-ADV-025"),
        ("economic development", "经济发展", "B8-OP-050"),
        ("local businesses", "本地企业", "B8-OP-050"),
        ("paid employment", "有偿就业", "B8-OP-017"),
        ("career paths", "职业路径", "B8-DIS-045"),
        ("career development", "职业发展", "B8-OP-031"),
    ],
    "generic": [
        ("long term", "长期", "B85-OP-003"),
        ("well-being", "幸福感/福祉", "B8-ADV-031"),
        ("hard work", "努力工作", "B8-OP-039"),
        ("public awareness", "公众意识", "B8-REP-011"),
        ("public transport", "公共交通", "B8-OP-061"),
        ("young people", "年轻人", "B8-ADV-001"),
        ("quality of life", "生活质量", "B9-DIS-024"),
        ("financial burden", "经济负担", "B8-ADV-022"),
    ],
}

FUNCTION_RULES = [
    (re.compile(r"\b(should|must|invest|protect|reduce|increase|improve|promote|regulate|prohibit|guarantee|target|funding)\b", re.I), "措施建议"),
    (re.compile(r"\b(cause|causes|due|result|effect|impact|cost|costs|rates|growth|degradation|emissions|gap|decline)\b", re.I), "原因结果"),
]


def classify(gram: str) -> str:
    for rx, label in FUNCTION_RULES:
        if rx.search(gram):
            return label
    return "观点表达"


def main() -> None:
    recs = [r for r in load_enriched() if not r["excluded_from_distillation"]]
    by_id = {r["id"]: r for r in recs}
    gram_re_cache: dict[str, re.Pattern] = {}

    def gram_re(g: str) -> re.Pattern:
        if g not in gram_re_cache:
            gram_re_cache[g] = re.compile(r"(?<![a-z])" + re.escape(g).replace(r"\ ", r"\s+").replace(r"\-", r"[\s-]+") + r"(?![a-z])", re.I)
        return gram_re_cache[g]

    misses: list[str] = []
    low_freq: list[str] = []
    lines: list[str] = []
    A = lines.append
    A("# L6 主题词库")
    A("")
    A("> **层级**：L6 · 主题高频词伙（解决「用什么词」）。")
    A("> **来源**：训练集 Band 8+ 样本；每条给出原文语境例句与来源样本 id，出现篇数为该主题 8+ 语料中的文档频次。")
    A("> **加载时机**：LR 反馈的「主题高频高级词汇调用」环节（SKILL.md §6.5-2）按主题检索。")
    A("> **状态**：已填充（任务二 v1，2026-10-07）。本库优先收录在 ≥3 篇 8+ 样本中出现的词伙；")
    A("> 标「低频」者为不足 3 篇的补充条目（新题或窄主题语境所限），反馈时须标注不确定性。例句均为原文截断。")
    A("")
    A("> 使用提示：反馈时须把词伙放进用户当前题目的语境重写例句；不要整段照搬。")
    A("")

    order = [
        "education", "technology", "environment", "government", "social", "crime", "culture", "health", "media", "globalization-work",
    ]
    for topic in order + ["generic"]:
        entries = CURATED.get(topic, [])
        title = "通用（跨主题）" if topic == "generic" else TOPIC_CN[topic]
        A(f"## {title}")
        A("")
        A("| 词伙 | 功能 | 释义 | 原文语境例句（节选） | 来源样本 | 出现篇数 |")
        A("|---|---|---|---|---|---:|")
        for gram, gloss, src in entries:
            src_rec = by_id.get(src)
            ok = bool(src_rec and gram_re(gram).search(src_rec["essay"]))
            if not ok:
                # try to find any 8+ essay of the topic that contains it
                pool = [r for r in recs if r["band"] >= 8.0 and (topic == "generic" or r["topic"] == topic) and gram_re(gram).search(r["essay"])]
                if pool:
                    src_rec = sorted(pool, key=lambda r: (-r["band"], r["id"]))[0]
                    misses.append(f"{topic}: {gram!r} 不在 {src}，已改用 {src_rec['id']}（建议核对来源标注）")
                    ok = True
                else:
                    misses.append(f"{topic}: {gram!r} 在 8+ 语料中未找到（来源 {src}）")
            pool = [r for r in recs if r["band"] >= 8.0 and (topic == "generic" or r["topic"] == topic) and gram_re(gram).search(r["essay"])]
            count = len(pool)
            if count < 3:
                low_freq.append(f"{topic}: {gram!r} 仅 {count} 篇")
            example = ""
            ex_id = src
            if src_rec:
                ex_id = src_rec["id"]
                for s in sentences(src_rec["essay"]):
                    if gram_re(gram).search(s):
                        example = s.strip()
                        break
            if len(example) > 190:
                cut = example[:190]
                if " " in cut:
                    cut = cut[: cut.rfind(" ")]
                example = cut.rstrip(" ,;:") + " ..."
            example = example.replace("|", "\\|")
            freq = f"{count}" + ("（低频）" if count < 3 else "")
            band_note = f"`{ex_id}`"
            if src_rec:
                band_note += f"（{src_rec['band']:g}）"
            A(f"| {gram} | {classify(gram)} | {gloss} | {example} | {band_note} | {freq} |")
        A("")

    A("---")
    A("")
    A("## 使用纪律")
    A("")
    A("1. 反馈中的例句必须结合用户当前题目重写；本库例句只作语境参照。")
    A("2. 词伙优先于单词：鼓励整块使用（如 curb carbon emissions），避免把名词拆开硬套。")
    A("3. 出现篇数 <3 的条目为「低频」候选，反馈时标注不确定性；D-auto 来源样本仅作参考。")
    A("4. 抽检记录见 `distillation/reports/l5-l6-audit.md`。")

    write_text(REFS_DIR / "topic-vocab.md", "\n".join(lines) + "\n")
    review = ["# L6 构建校验", ""]
    review += ["## 未通过来源校验 / 已替换来源的条目", ""] + (misses or ["（无）"])
    review += ["", "## 低频条目（<3 篇，已标注）", ""] + (low_freq or ["（无）"])
    write_text(REPORT_DIR / "l6-review.md", "\n".join(review) + "\n")
    print("misses:", len(misses), "low_freq:", len(low_freq))
    for m in misses[:20]:
        print("  !", m)


if __name__ == "__main__":
    main()

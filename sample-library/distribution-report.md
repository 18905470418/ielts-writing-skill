# 样本库分布盘点报告

> 任务一 §2.1/§2.4 交付物。语料: `IELTS_Task2_1490/ielts_task2_collection.md`(1490 篇)。
> 题型/主题由 `build_sample_library.py` 规则分类器自动标注(基于题目文本),
> 未逐篇人工复核; 任务二蒸馏时若发现误标, 直接在 JSONL 中修正并回写台账。

## 1. 总量与切分

| 分数档 | 总数 | 训练集 | 盲测集 |
|---|---:|---:|---:|
| 6.0 | 211 | 169 | 42 |
| 6.5 | 214 | 171 | 43 |
| 7.0 | 210 | 168 | 42 |
| 7.5 | 217 | 174 | 43 |
| 8.0 | 212 | 170 | 42 |
| 8.5 | 216 | 173 | 43 |
| 9.0 | 210 | 168 | 42 |
| **合计** | **1490** | **1193** | **297** |

切分方式: 分数档 × 题型分层随机(种子 20261007), 盲测占比 20%; 盲测集物理隔离于 `blindtest/` 并设只读, 仅供任务三使用。

## 2. 分数档 × 题型 透视(理想值: 每档每题型约 40 篇)

| 分数档 | opinion | discussion | adv-disadv | report | two-part | 小计 |
|---|---:|---:|---:|---:|---:|---:|
| 6.0 | 87 | 45 | 43 | 29 | 7 | 211 |
| 6.5 | 75 | 52 | 55 | 19 | 13 | 214 |
| 7.0 | 92 | 53 | 37 | 17 | 11 | 210 |
| 7.5 | 69 | 45 | 61 | 28 | 14 | 217 |
| 8.0 | 87 | 46 | 36 | 31 | 12 | 212 |
| 8.5 | 103 | 34 | 43 | 25 | 11 | 216 |
| 9.0 | 110 | 32 | 35 | 25 | 8 | 210 |
| **合计** | 623 | 307 | 310 | 174 | 76 | **1490** |

## 3. 分数档 × 主题 透视(要求: 每档至少覆盖 8 个主题)

| 分数档 | education | technology | environment | government | social | crime | culture | health | media | globalization-work | 覆盖主题数 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6.0 | 49 | 20 | 10 | 5 | 45 | 3 | 9 | 20 | 11 | 39 | 10/10 |
| 6.5 | 39 | 21 | 17 | 14 | 43 | 4 | 9 | 24 | 14 | 29 | 10/10 |
| 7.0 | 34 | 27 | 18 | 14 | 46 | 7 | 4 | 13 | 10 | 37 | 10/10 |
| 7.5 | 22 | 26 | 19 | 15 | 49 | 7 | 10 | 16 | 16 | 37 | 10/10 |
| 8.0 | 34 | 18 | 18 | 4 | 40 | 12 | 11 | 26 | 17 | 32 | 10/10 |
| 8.5 | 23 | 34 | 16 | 10 | 61 | 3 | 8 | 18 | 14 | 29 | 10/10 |
| 9.0 | 32 | 23 | 16 | 12 | 47 | 11 | 8 | 17 | 13 | 31 | 10/10 |
| **合计** | 233 | 169 | 114 | 74 | 331 | 47 | 59 | 134 | 95 | 234 | |

## 4. 薄弱格子清单(7档 × 5题型 × 10主题 全网格)

规则: 格子样本数 = 0 记 **空缺**, 1–2 记 **薄弱**; 任务二在对应规则上须标注「样本不足, 此规则置信度低」, 并据此定向补样。

| 分数档 | 题型 | 空缺主题 | 薄弱主题(篇数) |
|---|---|---|---|
| 6.0 | opinion | — | government(2), crime(2) |
| 6.0 | discussion | environment | crime(1) |
| 6.0 | adv-disadv | government, crime | environment(2), culture(1) |
| 6.0 | report | government, crime, media | education(2), technology(1), culture(1) |
| 6.0 | two-part | technology, government, crime, culture, media, globalization-work | education(1), environment(1), health(1) |
| 6.5 | opinion | — | crime(1) |
| 6.5 | discussion | crime | government(1) |
| 6.5 | adv-disadv | — | government(2), crime(1), culture(1) |
| 6.5 | report | government, culture, media | education(2), technology(1), environment(1), crime(2), globalization-work(2) |
| 6.5 | two-part | technology, crime, media, globalization-work | education(2), culture(1), health(1) |
| 7.0 | opinion | — | culture(1), media(2) |
| 7.0 | discussion | culture | crime(2) |
| 7.0 | adv-disadv | crime | environment(1), government(2), culture(2), health(2), media(2) |
| 7.0 | report | education, technology, government, crime | culture(1), media(2), globalization-work(2) |
| 7.0 | two-part | education, culture | technology(2), environment(1), government(1), crime(1), health(1), media(1), globalization-work(1) |
| 7.5 | opinion | — | — |
| 7.5 | discussion | health | crime(1) |
| 7.5 | adv-disadv | — | environment(2), government(2), crime(1), culture(1) |
| 7.5 | report | government | education(2), technology(1), crime(2), culture(1), media(1) |
| 7.5 | two-part | technology, crime, media, globalization-work | education(2), government(2), culture(1), health(1) |
| 8.0 | opinion | — | — |
| 8.0 | discussion | government | culture(1), media(2) |
| 8.0 | adv-disadv | government, crime | environment(1), culture(2) |
| 8.0 | report | technology | education(2), government(1), culture(1), media(1) |
| 8.0 | two-part | education, technology, government | social(2), crime(1), culture(1), health(1), media(1) |
| 8.5 | opinion | — | crime(2) |
| 8.5 | discussion | crime | government(1), culture(1), media(1) |
| 8.5 | adv-disadv | — | education(2), environment(1), government(1), crime(1), culture(1), health(2) |
| 8.5 | report | government, crime, media | technology(1), culture(1) |
| 8.5 | two-part | government, crime | education(1), technology(1), environment(1), culture(1), health(1), media(1), globalization-work(1) |
| 9.0 | opinion | — | — |
| 9.0 | discussion | — | government(1), crime(1), culture(2), health(2) |
| 9.0 | adv-disadv | culture, health | environment(1), government(2), crime(2) |
| 9.0 | report | government, media | technology(2), environment(1), culture(1) |
| 9.0 | two-part | education, technology, health, media, globalization-work | government(1), social(2), crime(1), culture(1) |

全网格共 350 格, 空缺+薄弱合计 158 格 (健康格子占比 54.9%)。

## 5. 数据质量注记

- **分数可靠性**: 沿用源语料 README 警告——8.5 档 199/200 来自 writing9.com 自动评分, 6.5/7.5 半分档亦以自动评分为主; 任务二蒸馏 L1/L2 时应对 8.5 档锚点从严甄选。
- **单项分/考官评语**: 源语料正集缺失; 已从 IWCS(18 条)与 IELTS International(10 条) 官网回填四维小分与考官评语共 28 条(小分与总分官方取整规则 100% 吻合), 并据官网补回缺失题目 6 条; 其余 1462 条 `subscores`/`examiner_comment` 为 null, 待任务二反向标注。复现方式: `python enrich_from_sources.py && python build_sample_library.py`。
- **疑似非 Task 2 泄漏**: 8 篇题目疑似 Task 1 图表/书信题(源语料过滤残留), 已在 JSONL 与台账 `flags` 列标注 `suspected-offtask`; 任务二蒸馏与任务三抽测时应剔除。
- **入库清洗**: 剥除题目中混入的 Task 1 指令样板句 8 处; 修正题目半串重复 1 处、正文半串重复 1 处(采集器拼接瑕疵, 清洗动作确定性可复现)。
- **主题零命中兜底**: 73 篇题目未命中任何主题关键词, 已归入 social; 清单见台账筛选 `topic=social` 且低频主题交叉复核。
- **题型分类边界**: 混合型设问(如 why + agree)统一归入 two-part; 「positive/negative development」归入 adv-disadv; 单句 What/How/Why 直接问句归入 report。
- **每档每题型理想 40 篇**: 实际分布见第 2 节, report 与 two-part 普遍偏低, 补样优先级: two-part > report > adv-disadv。

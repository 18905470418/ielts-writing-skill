# 结构化样本库（任务一交付物）

> IELTS Writing Task 2 评分 Skill 的校准基础：1490 篇标注范文（Band 6 / 6.5 / 7 / 7.5 / 8 / 8.5 / 9），
> 已按统一 Schema 结构化、切分训练/盲测并物理隔离。任务二的蒸馏输入、任务三的校准测试输入均取自本目录。

## 文件布局

```
sample-library/
├── essays.train.jsonl            训练集 1193 篇（供任务二蒸馏 L1–L6）
├── blindtest/
│   ├── essays.blindtest.jsonl    盲测集 297 篇（只读封存, 仅供任务三, 严禁用于规则归纳）
│   └── README.md                 盲测集封存说明
├── ledger.csv                    采样台账（1490 条元数据, 含小分/旗标/来源, 不含正文）
├── schema.md                     单篇记录字段说明（§2.2 Schema 的落地版）
├── distribution-report.md        分布盘点报告（7档×5题型×10主题, 薄弱格子标注）
├── enrichment.json               28 条官网回填数据（小分+考官评语+补题）
├── enrich_from_sources.py        增强步骤（抓取 IWCS / IELTS International 官网结构化小分）
├── build_sample_library.py       入库主脚本（解析→清洗→分类→切分→产出上表全部文件）
└── _cache/                       增强步骤的网页缓存（复现用）
```

## 数量与切分总览

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

切分：分数档 × 题型分层随机（种子 20261007），盲测占比 20%，每档 42–43 篇。

## 使用纪律

1. **盲测集封存**：`blindtest/` 目录文件设只读，任务二的任何蒸馏步骤不得读取；任务三校准时才解封。
2. **题/主题为规则自动标注**：基于题目文本的关键词分类，未逐篇人工复核；任务二发现误标直接在
   JSONL 修正并回写 `ledger.csv`（修正时保持 id 不变）。
3. **`flags:["suspected-offtask"]`** 的 8 条为源语料残留的 Task 1/书信题，蒸馏与抽测时应剔除。
4. **分数可靠性分层**：8.5 档与半分档多来自 writing9.com 自动评分；选锚点（L2）时应优先
   teacher-marked / examiner-labelled 来源，细节见 `distribution-report.md` §5。
5. **28 条已回填四维小分与考官评语**（IWCS 18 条 + IELTS International 10 条），其余
   `subscores`/`examiner_comment` 为 null，由任务二反向标注补齐。

## 复现

```powershell
python sample-library/enrich_from_sources.py     # 可选: 抓取/解析官网增强数据(有缓存)
python sample-library/build_sample_library.py    # 重建全部入库产物
```

两个脚本为纯标准库实现，全程确定性（固定种子），重复运行结果一致。
新增/修正样本时改 `build_sample_library.py` 的规则或上游语料后重跑即可；盲测切分随之重算，
因此**修正样本后必须重新封存盲测集**（本仓库通过只读属性实现封存）。

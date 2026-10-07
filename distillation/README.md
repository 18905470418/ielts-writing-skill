# 任务二 · 文件蒸馏工作区

> 本目录是 IELTS Task 2 评分 Skill 的蒸馏流水线：把 `sample-library/essays.train.jsonl`
> （训练集 1193 篇）压缩为 `ielts-writing-scorer/references/` 的六层知识资产 + 题目库，
> 并交付《偏差记录表》与《定量特征各档分布区间表》给任务三。
>
> **盲测纪律**：全流程只读 `split: train`；`sample-library/blindtest/` 在整个任务二中未被读取。
> 需要校验时可用 `rg -n "blindtest" distillation/` 自查（只应出现纪律说明，不出现读取代码）。

## 目录

```
distillation/
├── scripts/                 # 可复现流水线（纯标准库）
│   ├── distill_lib.py           # 文本/特征/检测/评分/词伙工具
│   ├── task_type_fix.py         # 题型标注修正函数（任务三对盲测集复用）
│   ├── step1_clean_enrich.py    # 结构化清洗 + 小分反向标注
│   ├── step2_blind_deviation.py # 盲评分 + 《偏差记录表》
│   ├── step3_features.py        # 定量特征 + 词伙挖掘 + 分布区间表
│   ├── step4_extract_assets.py  # L3/L4/L5/题目簇/黄金组/锚点候选提取
│   ├── step4b_diff_ngrams.py    # 6–7.5 vs 8+ 词串差频
│   ├── step5_build_anchors.py   # 生成 L2 锚点文件（黄金锚点置顶）
│   ├── step6_build_l6.py        # v1：生成 L6 主题词库（已被 step9/10 取代，保留追溯）
│   ├── step7_build_question_bank.py # 生成题目解析库
│   ├── step8_units.py           # v2：全量论证单元抽取（510 篇 / 1084+ 段 → 主题摘要）
│   ├── step9_candidates.py      # v2：扩容词伙候选（8+ 为主 + 薄主题 7.5 补充）
│   ├── step10_preprocess_curation.py # v2：词伙真实性过滤 / 分级修正 / 跨主题去重
│   ├── step10_build_l5l6.py     # v2：迁移 v1 + 合并策展 → 按主题拆分 L5/L6（含档位政策与例句重取）
│   ├── verify_curation.py       # v2：单主题策展校验（数量/来源/例句/覆盖）
│   ├── check_duplicates.py      # v2：L5 语义重复 + L6 精确重复检查
│   ├── query_units.py           # 论证单元检索（策展助手）
│   ├── audit_l5_l6.py           # 分层抽检包（≥30 条）
│   ├── verify_assets.py         # 全量引用/原文一致性验证
│   └── show_*.py / debug_*.py   # 人工复核辅助工具
├── data/                    # 派生数据（enriched 记录、特征、候选、评分明细）
└── reports/                 # 交付报告（清洗、偏差、特征、抽检、验证）
```

## 交付物索引（对应任务二验收清单）

| 验收项 | 交付物 | 状态 |
|---|---|---|
| 仅用 train、盲测零接触 | 各脚本只加载 `essays.train.jsonl` / `essays.train.enriched.jsonl` | ✅ |
| 《偏差记录表》 | `reports/deviation-record.md` + `data/blind-scores.csv` + `reports/deviation-review.md`（20 篇人工复核） | ✅ |
| L1 TR/CC/LR/GRA × 7 档 + 6 组 Delta + 半分档 + 置信度 | `../ielts-writing-scorer/references/band-rules.md` | ✅ |
| L2 五个题型锚点（每档 2–3 篇 + 逐项评语 + 黄金锚点置顶） | `../ielts-writing-scorer/references/anchors/*.md` | ✅ |
| L3 按模块 + 负迁移标签轴 | `../ielts-writing-scorer/references/error-patterns.md` | ✅ |
| L4 按题型和主题索引 | `../ielts-writing-scorer/references/language-assets.md` | ✅ |
| L5 观点库（编号 + 来源 id） | v2：`references/viewpoint-bank.md`（索引）+ `references/viewpoint-bank/<主题>.md` ×10；`data/curation/<主题>.json` 为策展源 | ✅ v2：248 条（每主题 ≥23；薄主题 ≥25） |
| L6 主题词库（词伙 + 例句 + 来源） | v2：`references/topic-vocab.md`（索引）+ `references/topic-vocab/<主题>.md` ×10 + `generic.md`；`data/l6-candidates.json` 为候选源 | ✅ v2：487 行（每主题 ≥42；薄主题 ≥47；跨主题重复 0） |
| L5/L6 分层抽检（≥30 条） | `reports/l5-l6-audit.md`（抽样包 `reports/l5-l6-audit-pack.md`） | ✅ 分层抽样，逐条复核 |
| v2 覆盖报告 | `reports/coverage-report.md` + `data/coverage.json`（处理覆盖 + 引用覆盖） | ✅ |
| 题目解析库 | `../ielts-writing-scorer/references/question-bank.md`（56 个高频题簇） | ✅ |
| 定量特征各档分布区间表（交付任务三） | `reports/feature-distribution.md` + `data/feature-distribution.csv` | ✅ |
| 引用真实性验证 | `reports/asset-verification.md`（全部 id/原文/搭配回查） | ✅ |

## 重建方式（确定性）

```powershell
python distillation/scripts/step1_clean_enrich.py       # 清洗 + 小分反向标注
python distillation/scripts/step2_blind_deviation.py    # 偏差记录
python distillation/scripts/step3_features.py           # 特征与词伙（约 1–2 分钟）
python distillation/scripts/step4_extract_assets.py     # L3/L4/L5/题目/锚点原料
python distillation/scripts/step4b_diff_ngrams.py       # 差频表
python distillation/scripts/step5_build_anchors.py      # L2 锚点文件
# 注意：step6_build_l6.py 为 v1 遗留脚本，v2 不要重跑（会覆盖 topic-vocab.md 索引）
python distillation/scripts/step7_build_question_bank.py# 题目解析库
python distillation/scripts/step8_units.py              # v2 论证单元抽取（全量 8+）
python distillation/scripts/step9_candidates.py         # v2 词伙候选（8+ 主池 + 7.5 补充）
# 每个主题按 distillation/CURATION_GUIDE.md 产出 data/curation/<topic>.json
python distillation/scripts/step10_preprocess_curation.py  # 词伙过滤 / 分级 / 跨主题去重
python distillation/scripts/verify_curation.py --topic <topic>   # 10 个主题逐个校验（PASS 才继续）
python distillation/scripts/step10_build_l5l6.py        # 合并 v1 + 策展，按主题拆分（档位政策）
python distillation/scripts/audit_l5_l6.py              # 分层抽检包（≥30 条）
python distillation/scripts/verify_assets.py            # 全量引用验证（应输出 issues: 0）
python distillation/scripts/check_duplicates.py         # 重复检查（应输出 0 / 0）
python distillation/scripts/final_acceptance.py         # 验收自检（应输出 FAIL count: 0）
```

## 关键约定

1. **题型修正**：`task_type_fix.effective_task_type()` 修正了任务一分类器的两类实现性误分
   （`best way + agree` 单问句、`why + positive/negative` 混合设问），共 63 条；原始
   `task_type` 不动，`task_type_effective` 写入 enriched 记录。任务三必须对盲测集调用同一函数。
2. **小分反向标注**：22 条官方小分保留；其余 1171 条按「真实总分锚定 + 盲评分四维相对强弱」
   推断并标注 `subscores_source=inferred-v1` 与置信度，不得当作盲测真值。
3. **L5/L6 来源纪律**：只收 8+ 样本（L5 全部来自 9.0/8.5）；L6 中出现篇数 <3 的补充条目
   已标注「低频」；全部搭配/例句可回查来源 id。
4. **计数型信号只作辅助**：《偏差记录表》§6 证明字面覆盖率、连接词密度、复杂句计数在本语料中
   会系统性误判，L1 已按质量型判别操作改写；任务三复检规则见 `feature-distribution.md` §4。
5. **v2 来源与覆盖**：L5/L6 以 8+ 样本为主；薄主题（government / crime / culture / media）
   允许 7.5 样本补充并逐条标注。处理覆盖要求 100%（510 篇 8+ / 1084+ 主体段进入候选），
   引用覆盖要求 L5 ≥40%、L6 ≥50%（按主题分别统计，见 `coverage-report.md`）。
6. **文件结构**：`references/viewpoint-bank.md` 与 `references/topic-vocab.md` 保留为索引
   （兼容旧路径），正文在各自子目录按主题拆分；评分时只读对应主题分文件。

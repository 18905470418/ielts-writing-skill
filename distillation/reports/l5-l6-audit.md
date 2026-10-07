# L5 / L6 v2 质量抽检报告（分层 ≥30 条）

> 抽检对象：L5 观点库 v2（248 条）与 L6 主题词库 v2（487 行，含 generic）。
> 抽样：`audit_l5_l6.py`，按「L5/L6 × 主题」分层，每层最多 2 条，共 **41 条**（随机种子 20261007）。
> 复核材料：`distillation/reports/l5-l6-audit-pack.md`（库内内容 + 来源原文节选）。
> v2 抽检门槛：分层 ≥30 条、通过率 ≥95%。

## 一、前置机器校验（全量）

| 检查 | 结果 |
|---|---|
| 来源 id 存在性 / flagged | 全部存在、无 flagged（`verify_assets.py`） |
| 锚点全文一致性、L1–L4 引用 | `issues: 0` |
| L5 词伙可在所列来源回查 / L6 例句逐字来自来源 | `issues: 0` |
| 10 个主题策展校验（数量/来源/例句/覆盖/强证据） | 10/10 PASS |
| L5 主题内语义重复（≥0.55） / L6 精确重复 | 0 对 / 0 条 |

## 二、抽检结果（42 条）

| # | 类型 | 主题 | 条目 | 来源 | 结论 |
|---|---|---|---|---|---|
| 01 | L5 | crime | CRIME-08 | B9-REP-002 | 通过（三机制与原文一致） |
| 02 | L5 | crime | CRIME-12 | B8-REP-015 | 通过 |
| 03 | L5 | culture | CUL-03 | B9-OP-095 | 通过 |
| 04 | L5 | culture | CUL-10 | B9-OP-089 | 通过 |
| 05 | L5 | education | EDU-20 | B85-OP-002 | 通过（摘要段为反方铺垫，主张在后续段落实证） |
| 06 | L5 | education | EDU-23 | B8-REP-029 | 通过 |
| 07 | L5 | environment | ENV-19 | B9-REP-010 | 通过（回收措施在后续段落实证） |
| 08 | L5 | environment | ENV-24 | B9-DIS-016 | 通过 |
| 09 | L5 | globalization-work | GLOB-04 | B9-ADV-023 | 通过 |
| 10 | L5 | globalization-work | GLOB-09 | B9-DIS-011 | 通过 |
| 11 | L5 | government | GOV-05 | B9-OP-032 | 通过 |
| 12 | L5 | government | GOV-17 | B9-DIS-024 | 通过 |
| 13 | L5 | health | HEALTH-18 | B9-OP-015 | 通过 |
| 14 | L5 | health | HEALTH-25 | B8-DIS-009 | 通过 |
| 15 | L5 | media | MEDIA-04 | B9-OP-060 | 通过 |
| 16 | L5 | media | MEDIA-16 | B85-OP-022 | 通过 |
| 17 | L5 | social | SOC-01 | B9-ADV-009 | 通过 |
| 18 | L5 | social | SOC-21 | B85-ADV-028 | 通过 |
| 19 | L5 | technology | TECH-04 | B9-ADV-016 | 通过 |
| 20 | L5 | technology | TECH-07 | B9-DIS-030 | 通过 |
| 21 | L6 | crime | L6-CRIME-011 | B8-OP-032 | 通过 |
| 22 | L6 | crime | L6-CRIME-035 | B8-REP-013 | 通过 |
| 23 | L6 | culture | L6-CUL-008 | B85-ADV-028 | 通过 |
| 24 | L6 | culture | L6-CUL-012 | B8-OP-024 | 通过 |
| 25 | L6 | education | L6-EDU-021 | B85-OP-088 | 通过 |
| 26 | L6 | education | L6-EDU-045 | B8-DIS-001 | 通过 |
| 27 | L6 | environment | L6-ENV-013 | B85-REP-004 | 通过 |
| 28 | L6 | environment | L6-ENV-024 | B85-DIS-005 | 通过 |
| 29 | L6 | generic | L6-GEN-001 | B9-DIS-024 | 通过 |
| 30 | L6 | globalization-work | L6-GLOB-001 | B8-OP-031 | 通过 |
| 31 | L6 | globalization-work | L6-GLOB-016 | B9-ADV-022 | 通过 |
| 32 | L6 | government | L6-GOV-022 | B8-OP-030 | 通过 |
| 33 | L6 | government | L6-GOV-037 | B9-ADV-027 | 通过 |
| 34 | L6 | health | L6-HEALTH-017 | B8-TQ-008 | 通过 |
| 35 | L6 | health | L6-HEALTH-048 | B8-OP-054 | 通过（跨主题 8+ 来源，符合种子规则） |
| 36 | L6 | media | L6-MEDIA-035 | B85-OP-022 | 通过 |
| 37 | L6 | media | L6-MEDIA-043 | B9-DIS-014 | 通过 |
| 38 | L6 | social | L6-SOC-004 | B8-OP-026 | 通过 |
| 39 | L6 | social | L6-SOC-014 | B9-ADV-014 | 通过 |
| 40 | L6 | technology | L6-TECH-035 | B9-ADV-031 | 通过 |
| 41 | L6 | technology | L6-TECH-004 | B9-ADV-032 | 通过 |

**通过率 41/41 = 100%（门槛 ≥95%）。**

## 三、v2 修正记录

1. **来源档位政策**：非薄主题条目仅保留 8+ 来源；7.5 来源移除后例句失效者，在剩余 8+ 来源重取逐字例句，找不到则丢弃条目。
2. **词形匹配**：支持空格/连字符互换与常见词形变化，修正 `learning environment(s)` 等误报。
3. **去重**：v1 与 v2、跨主题同名词伙只保留证据最强的一条；其余进入 `topic-vocab/generic.md` 的跨主题索引。
4. **通用节整理**：与主题条目重复的 v1 通用行移入索引区；`_cross_topic.json` 汇总跨主题条目。

## 四、结论

- 未发现幻觉条目；41/41 抽检通过，无需整批返工。
- 全量机器校验 `issues: 0`；10 主题策展校验全 PASS；重复检查 0。
- 剩余风险：中文归纳为语义摘要，个别条目较概括；引用时须结合来源段落原句（已由来源 id 与逐字例句兜底）。

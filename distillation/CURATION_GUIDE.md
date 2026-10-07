# L5 / L6 v2 策展指南（每个主题一份 JSON）

> 目标：把该主题的全部 8+（薄主题含 7.5 补充）语料压缩成 **可检索、可溯源** 的观点与词伙条目。
> 产出：`distillation/data/curation/<topic>.json`（每个主题一个文件，互不覆盖）。
> 纪律：只使用 `sample-library/essays.train.jsonl`（经 `distillation/data/essays.train.enriched.jsonl`）；
> 严禁读取 `sample-library/blindtest/`；不得编造来源 id、例句或原文中不存在的观点。

## 输入文件

1. `distillation/reports/units-<topic>.md`（如过大则另有 `units-<topic>-partN.md`）：
   该主题的论证单元聚簇，每簇含代表句链（topic/mechanism/example/linkback）、合并来源 id。
2. `distillation/reports/l6-candidates-<topic>.md`：
   该主题的词伙候选（A/B 级、8+/7.5 篇数、功能、例句来源）。
3. 需要更多原始上下文时：
   `python distillation/scripts/query_units.py --topic <topic> [--band 9] [--max 60]`
4. 需要核对某条真实原文时，读取 `distillation/data/essays.train.enriched.jsonl` 中对应 id 的 `essay` 字段
   （可用 `python distillation/scripts/show_essays.py <id>`）。

## 输出 JSON 结构

```json
{
  "topic": "education",
  "viewpoints": [
    {
      "claim": "中文一句话观点（不许编造；须能由来源段落支持）",
      "tendency": "支持|反对|中立|条件性",
      "chain": "机制 → 例证方向 → 回扣（用 → 分隔，中文归纳，可含英文术语）",
      "task_types": ["opinion", "discussion"],
      "sources": [{"id": "B8-ADV-009", "band": 8.0}, {"id": "B9-OP-068", "band": 9.0}],
      "collocations": ["practical skills", "hands-on experience"]
    }
  ],
  "vocab": [
    {
      "collocation": "practical skills",
      "function": "观点表达|原因结果|措施建议|评价判断",
      "gloss": "实用技能",
      "sources": [{"id": "B8-ADV-009", "band": 8.0}],
      "docs8": 10,
      "docs75": 0,
      "tier": "A|B",
      "supplement_75": false,
      "example": "One major advantage of vocational programmes is that they equip trainees with practical skills that directly reflect the demand of the labour market."
    }
  ]
}
```

说明：不要写条目编号（`EDU-07`、`L6-EDU-018` 等）——构建脚本会按 v1 续号统一分配。

## 数量与质量门槛

| 项目 | 普通主题 | 薄主题（government / crime / culture / media） |
|---|---|---|
| L5 观点条目 | 15–20 条 | 12–20 条 |
| L5 每条来源 | 1–3 个真实 id（第一个放最高分/最可靠来源） | 同左 |
| L5 引用覆盖 | 该主题 8+ 标签样本的 ≥40%（可一条多源） | 同左 |
| L6 词伙条目 | 40–60 条 | 30–60 条 |
| L6 单条来源 | 1–3 个真实 id | 同左 |
| L6 强证据占比 | `docs8+docs75 ≥ 3` 的条目 ≥80% | `docs8 ≥ 2` 或 `docs8+docs75 ≥ 3` 的条目 ≥80%（薄主题放宽为 8+ 两篇） |
| L6 引用覆盖 | 该主题 8+ 标签样本的 ≥50% | 同左 |

**分级规则**（与候选文件一致）：
- A 级：`docs8 ≥ 3`；
- B 级：仅薄主题可用，`docs8 == 2`，或 `docs8 ≥ 1 且 docs75 ≥ 2`，或 `docs75 ≥ 3`；
- `supplement_75 = true` 表示该条主要依赖 7.5 样本（在正文中会被标注「7.5 补充」）。

**例句纪律**：`example` 必须是来源 `essay` 中的逐字片段（可截断到 ≤190 字符并在末尾加 ` ...`，
但截断前的内容必须连续出现）。中文释义/观点是归纳，不得添加样本中没有的数据或例证。

## 完成前自检（必须执行）

```powershell
python distillation/scripts/verify_curation.py --topic <topic>
```

输出 `PASS` 才算完成；失败项（数量、来源、例句、覆盖、强证据占比）逐条修复后重跑。
校验报告会写到 `distillation/reports/curation-verify-<topic>.md`。

## 推荐工作流

1. 通读 `units-<topic>.md` 的全部部分（若分 part 则全部读完），做**语义去重**：
   同一论点只保留展开最完整、来源最可靠的一条，把它合并进 `sources`（最多 3 个）。
2. 从 `l6-candidates-<topic>.md` 挑选：先取 A 级与高篇数词伙，再用 B 级补足数量；
   优先 3–5 元组、动宾/形名搭配，剔除过于泛化或与主题无关的条目。
3. 用 `query_units.py` 或 `show_essays.py` 回读来源，补齐/校正例句与观点链条。
4. 写 JSON → 跑校验 → 修复 → 再跑校验，直到 PASS。

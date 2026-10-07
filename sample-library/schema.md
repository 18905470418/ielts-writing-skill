# 单篇记录 Schema

每条记录为 `essays.train.jsonl` / `blindtest/essays.blindtest.jsonl` 中的一行（JSONL，UTF-8，一行一条）。
以下为字段全表；「必填」列中 `*` 表示任何情况下不得为空。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | * | 编码 `B{分数}-{题型}-{三位序号}`，如 `B7-OP-023`。分数码：B6/B65/B7/B75/B8/B85/B9；题型码：OP/DIS/ADV/REP/TQ。序号按原始篇号在「分数×题型」内递增，稳定不重编。 |
| `band` | number | * | 真实总分（6.0–9.0 半步进）。来源页面标注，未经本管道重新打分。 |
| `subscores` | object/null | | `{TR, CC, LR, GRA}` 四维小分。仅 28 条从官网回填；其余为 `null`（任务二反向标注）。 |
| `task_type` | string | * | `opinion` / `discussion` / `adv-disadv` / `report` / `two-part`。规则自动标注。 |
| `topic` | string | * | 十类主题：`education` `technology` `environment` `government` `social` `crime` `culture` `health` `media` `globalization-work`。规则自动标注，零命中兜底 `social`。 |
| `question` | string | * | 题目原文（已剥除混入的 Task 1 指令样板句、去半串重复）。 |
| `essay` | string | * | 文章原文，逐字保留（含源站拼写/语法错误），段落以空行分隔。 |
| `word_count` | number | * | 按空白切分计数（与源 CSV 的计数口径可能有 ±1 差异）。 |
| `examiner_comment` | string/null | | 考官评语。仅 28 条回填；其余 `null`。 |
| `source` | string | * | 站点域名（如 `writing9.com`）。 |
| `source_url` | string | * | 原页面 URL，溯源用。 |
| `source_no` | number | * | 源语料篇号 1–1490（与 `IELTS_Task2_1490/ielts_task2_collection.md` 的「第NNN篇」一致）。 |
| `split` | string | * | `train` / `blindtest`。盲测集物理隔离于 `blindtest/` 子目录。 |
| `flags` | array | * | 质量旗标；当前可能值：`suspected-offtask`（疑为 Task 1/书信题）。无旗标为 `[]`。 |

## 派生约定（下游任务用）

- **题型码**映射：OP=opinion，DIS=discussion，ADV=adv-disadv，REP=report，TQ=two-part。
- **同题多档**：源站同一题目下常有多个分数档的答卷（如 IWCS 一页 6.5/7.5/9.0 三篇），
  共享同一 `question` 但 `id`、`band`、`essay` 各自独立；蒸馏 L2 锚点时按「题型 × 分数」取用。
- **盲测口径**：任务三只应通过 `blindtest/essays.blindtest.jsonl` 读取盲测数据；解封前先解除
  只读属性，用完恢复。
- **修正流程**：发现误标（题/主题/旗标）→ 直接改对应 JSONL 记录 → 同步修正 `ledger.csv` →
  不改 `id`。若修正使条数/内容变化，重跑 `build_sample_library.py` 并重新封存盲测集。

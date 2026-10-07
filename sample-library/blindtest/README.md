# 盲测集（只读封存）

本目录存放 297 篇盲测范文，按「分数档 × 题型」分层自 1490 篇语料中切出（种子 20261007，每档 42–43 篇）。

## 封存纪律

- 本目录仅限**任务三「测试校准」**使用；任务二（文件蒸馏）的任何环节均不得读取，
  防止规则过拟合到已见过的文章。
- 目录内文件已设只读属性（`essays.blindtest.jsonl`、本 README）。
  任务三使用前可解除只读，使用后请恢复：

  ```powershell
  # 解除只读
  Get-ChildItem -LiteralPath . -File | ForEach-Object { $_.IsReadOnly = $false }
  # 恢复只读
  Get-ChildItem -LiteralPath . -File | ForEach-Object { $_.IsReadOnly = $true }
  ```

- 记录 Schema 与训练集一致，见 `../schema.md`。每档数量：

  | 分数档 | 6.0 | 6.5 | 7.0 | 7.5 | 8.0 | 8.5 | 9.0 |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | 盲测篇数 | 42 | 43 | 42 | 43 | 42 | 43 | 42 |

# 任务二 · 第 1 步结构化清洗报告

> 输入：`sample-library/essays.train.jsonl`（1193 篇，split=train）。
> 本步骤只读训练集；盲测集（`sample-library/blindtest/`）全程未读取。
> 产出：`distillation/data/essays.train.enriched.jsonl`（带反向标注小分与修正后题型）。

## 1. Schema 校验

- 必填字段/number 校验：**通过**（错误 0 条）。
- 警示项：0 条（字数口径 ±2 与超短样本提示；不影响入库）。
- 行数：1193；重复 id：0；重复正文：0；U+FFFD 替换符：0。

## 2. 分数可靠性分层

| 层级 | 来源 | 训练集篇数 | 用途约束 |
|---|---|---:|---|
| A-examiner | 考官/官方标注（含官网小分与考官评语） | 22 | L2 锚点首选、L1 证据优先 |
| B-teacher | 教学机构批改或精选范文（cdieltsprep / allthingsielts / ieltsprepstudio / bandnine） | 141 | L2 锚点首选、L1 证据优先 |
| C-blog | 教师博客范文（ielts-blog） | 156 | 可用于统计与常规锚点，8.5 档须标注来源；L2 黄金锚点不单独采用 |
| D-auto | writing9.com 自动评分 | 867 | 可用于统计与常规锚点，8.5 档须标注来源；L2 黄金锚点不单独采用 |

**处理原则**：训练集内不存在「无任何分数来源」的记录（全部带 source/source_url/band）。
按任务一 README 的口径，writing9.com 自动评分依赖其页面标注，本任务不删除、不重打分，
但在锚点选择与 8.5 档规则归纳时按上表降权，并在产物中显式标注来源层级。

## 3. 题型标注审计与修正

任务一分类器有一条实现性问题：`RE_REPORT` 的 `best way to (solve|reduce|...)` 分支
会把「单一评价式设问」（best way + do you agree）误导向 two-part；且 `RE_ADV` 优先级高于
「why + positive/negative」的混合设问判定，把一部分双问题类误标为 adv-disadv。
按任务一记录的分类边界（混合型设问→two-part、positive/negative development→adv-disadv、
单句 What/How/Why→report）逐题复核后，对训练集做如下修正（id 保持不变）：

| id | 原题型 | 修正为 | 依据（题干摘要） |
|---|---|---|---|
| B6-ADV-007 | adv-disadv | two-part | IELTS 17 Some children spend hours every day on their smartphones. Why is this the case? Do you think this is a positive or a negative development? |
| B6-ADV-008 | adv-disadv | two-part | : In many countries, more and more people want to study at universities. Why is this happening? Do you think this is a positive or negative development? |
| B6-ADV-015 | adv-disadv | two-part | In their advertising, businesses nowadays usually emphasize that their products are new in some way Why is this? Do you think it is a positive or negative development? |
| B6-ADV-018 | adv-disadv | two-part | Leaders of all kinds are often younger now than in the past. What are the reasons for this? Is it a positive or a negative development? |
| B6-ADV-024 | adv-disadv | opinion | Nowadays, there is a trend that reports in the media focus on problems and emergencies rather than positive development. Some people think it is harmful to individuals and to society. To what extent do you agree or disag |
| B6-ADV-026 | adv-disadv | two-part | People today buy more things than they need. Why is this happening, and is it a positive or negative development? |
| B6-ADV-027 | adv-disadv | two-part | Some children spend hours every day on their smartphones. Why is this the case? Do you think this is a positive or a negative development? |
| B6-ADV-035 | adv-disadv | two-part | The popularity of fast food is increasing, especially among younger people. What are the cause for this trend? Is it a positive or negative development? |
| B6-OP-023 | opinion | two-part | In many countries today, crime novels and tv crimes dramas are becoming more and more popular. Why do you think these books and tv shows are popular? What is your opinion of crime fiction tv crime dramas? |
| B6-OP-026 | opinion | two-part | In some countries, owning a home rather than renting one is very importatant for people. Why might this be the case? Do you think this is a positive or negative situation? |
| B6-TQ-002 | two-part | opinion | The best way to reduce the number of traffic accidents is to raise the age limit for younger drivers and to lower the age limit for aged drivers. Do you agree ? |
| B6-TQ-003 | two-part | opinion | The best way to reduce the number of traffic accidents is to raise age limit for the younger drivers and to lower age limit for the aged ones. Do you agree? |
| B6-TQ-007 | two-part | opinion | Some people think that the best way to improve road safety is to get drivers tested each year. To what extent do you agree or disagree? |
| B65-ADV-020 | adv-disadv | two-part | It is now common for people to change careers several times during their working lives. Why is this happening? Do you think it is a positive or a negative development? |
| B65-OP-016 | opinion | two-part | In some countires , owning a home rather than renting one is very important for people Why might be this case? Do you think this is a positive or negative situation? |
| B65-OP-044 | opinion | two-part | Ordinary people try to copy famous people either reading magazines or watching TV. Why do they do this? Do you think it is a good idea to copy famous people? |
| B65-REP-018 | report | two-part | Some people work harder than other. Why is this? Is this a positive or negative habit? |
| B65-TQ-006 | two-part | opinion | Increasing the prices of petrol is the best way to solve growing traffic and pollution problems. to what extent do you agree or disagree? |
| B65-TQ-010 | two-part | opinion | The best way to reduce the number of traffic accidents is to raise the age limit for younger drivers and lower the age limit for elderly ones. Do you agree or disagree? |
| B65-TQ-011 | two-part | opinion | The best way to tackle traffic jams is to invest in public transport. To What extent do you agree or disagree with this statement. |
| B65-TQ-013 | two-part | opinion | The growing number of overweight people is putting a strain on the health care system in an effort to deal with the health issues involved. Some people think that the best way to deal with this problem is to introduce mo |
| B7-ADV-006 | adv-disadv | two-part | In many countries, shopping is no longer just about buying what you need; it has become a popular hobby. Why is this the case? Is this a positive or negative development? |
| B7-ADV-019 | adv-disadv | two-part | Nowadays managers and team leaders in different organizations are much younger compared to the past. What are the reasons for this? Is it a positive or negative development? |
| B7-ADV-023 | adv-disadv | two-part | People spend a lot of money on appearance because they want to look younger. why does this happen? Do you think this is a positive or negative development? |
| B7-ADV-024 | adv-disadv | two-part | Some children spend hours every day on their smartphones. Why is this the case? Do you think this is a positive or a negative development? |
| B7-ADV-036 | adv-disadv | two-part | Nowadays managers and team leaders in different organizations are much younger compared to the past. What are the reasons for this? Is it a positive or negative development? |
| B7-ADV-037 | adv-disadv | two-part | Some children spend hours every day on their smartphones. Why is this the case? Do you think this is a positive or a negative development |
| B7-OP-029 | opinion | two-part | In some countries, owning a home rather than renting one is very important for people. Why might this be the case? Do you think this is a positive or negative situation? |
| B75-ADV-002 | adv-disadv | two-part | More and more people are choosing to work from home rather than in a traditional office. Why is this happening? Do you think this is a positive or negative development? |
| B75-ADV-041 | adv-disadv | two-part | Nowadays, some employers think that formal academic qualifications are more important than life experience or personal qualities when they look for new employees. Why is it the case? Is it a positive or negative developm |
| B75-ADV-046 | adv-disadv | two-part | Practice Question for IELTS Submit your responses and I will evaluate each response. An increasing number of people are choosing to have cosmetic surgery in order to improve their appearance. Why are more people choosing |
| B75-ADV-047 | adv-disadv | two-part | Some countries have introduced laws to limit the working hours that an employer can ask from an employee. Why are these law introduced? Is this a positive or negative trend? |
| B75-ADV-052 | adv-disadv | two-part | The popularity of fast food is increasing, especially among younger people. What are the cause for this trend? Is it a positive or negative development? |
| B75-ADV-053 | adv-disadv | opinion | The tendency of news reports in the media to focus more on problems and emergencies than on positive developments is harmful to individuals and society as a whole. To what extent do you agree or disagree? Give reasons fo |
| B75-TQ-008 | two-part | opinion | Littering in cities is an increasing problem which needs to be dealt with. Some people think that steeper fines is the best way to deal with the problem. To what extent do you agree? |
| B8-ADV-001 | adv-disadv | two-part | Many young people today are leaving rural areas to live in cities. Why is this happening? Is it a positive or negative development? |
| B8-ADV-006 | adv-disadv | two-part | Fewer and fewer people nowadays use hand like pen, pencil and brush. What are the reasons?It is positive or negative development. |
| B8-ADV-011 | adv-disadv | two-part | In some parts of the world it is becoming popular to research the history of one’s own family. Why might people want to do this? Is it a positive or negative development? |
| B8-ADV-013 | adv-disadv | two-part | In their advertising, businesses nowadays usually emphasise that their products are new in some way. Why is this? Do you think it is a positive or negative development? |
| B8-ADV-014 | adv-disadv | two-part | In their advertising, businesses nowadays usually emphasize that their products are new in some ways. Why is this? Do you think it is a positive or negative development? |
| B8-ADV-023 | adv-disadv | two-part | Nowadays celebrities earn more money than politicians. What are the reasons for this? Is it a positive or negative development? |
| B8-ADV-025 | adv-disadv | two-part | Nowadays more and more people want to live by themselves. What are the reasons? Is it a positive or negative trend? |
| B8-ADV-032 | adv-disadv | two-part | Some people tend to buy products or get services instantly, without waiting. Why is it happening? Is this a positive or negative development? |
| B8-OP-009 | opinion | two-part | Art is considered an essential part of all cultures throughout the world. However, these days fewer and fewer people appreciate art and turn their focus to science, technology and business. Why do you think that is? What |
| B8-OP-054 | opinion | two-part | Some countries invest a significant amount of money in promoting the use of bicycles. Why do you think this is the case? Does it have a positive or a negative impact on individuals and the society? |
| B8-OP-060 | opinion | two-part | Some people believe that preserving natural environment is crucial, however, most make no effort to do so. Why do you think this is happening? What are some simple actions that could help the environment? |
| B8-REP-023 | report | two-part | Newspapers have a significant influence on people’s ideas and opinions. Why is this happening? Is it a positive or negative situation? |
| B8-TQ-009 | two-part | opinion | Some people believe that the best way to solve environmental problems is to increase the price of fuel.Do you agree or disagree? |
| B8-TQ-010 | two-part | opinion | The best way to reduce traffic accidents is to raise the age limit for younger drivers and to lower the age limit for elderly ones. Do you agree or disagree? |
| B85-ADV-017 | adv-disadv | two-part | In their advertising, businesses nowadays usually emphasize that their products are new in some way. Why is this? Do you think it is a positive or negative development? |
| B85-ADV-033 | adv-disadv | two-part | Some children spend hours every day on their smartphones. Why is this the case? Do you think this is a positive or a negative development? |
| B85-OP-019 | opinion | two-part | in some countries, owning a home rather than renting one is very important for people. why might this be the case? what do you think this is a positive or negative situation? |
| B85-OP-073 | opinion | two-part | Sometimes, companies choose people based on their personality rather than skill set. Why do you think that is the case? What do you think is more important – personality or skills? |
| B85-REP-008 | report | adv-disadv | In some culture children are often told that they can achieve anything if they try hard enough. What are the advantages and disavdantages of giving children this message? |
| B85-TQ-008 | two-part | opinion | Some people think that the best way to improve road safety is to have drivers tested every year. To what extent do you agree or disagree? |
| B9-ADV-010 | adv-disadv | two-part | Handwriting today is less formal than it was in the past. What are the causes of this change? Is it a positive or negative development? |
| B9-ADV-020 | adv-disadv | two-part | In their advertising, businesses nowadays usually emphasize that their products are new in some ways. Why is this? Do you think it is a positive or negative development? |
| B9-ADV-021 | adv-disadv | two-part | It is now common for people to change careers several times during their working lives. Why is this happening? Do you think it is a positive or a negative development? |
| B9-ADV-031 | adv-disadv | two-part | Some children spend hours every day on their smartphones. Why is this the case? Do you think this is a positive or a negative development? |
| B9-ADV-032 | adv-disadv | two-part | some children spend hours every day on their smartphones. why is this the case? do you think this is a positive or negative development? |
| B9-ADV-035 | adv-disadv | two-part | Some children spend hours every day on their smartphones. Why is this the case? Do you think this is a positive or a negative development? |
| B9-OP-030 | opinion | adv-disadv | Some schools insist that students have laptops in class (advantages / disadvantages) |
| B9-TQ-007 | two-part | opinion | The best way to solve the world’s environmental problems is to increase the cost of fuel. Do you agree or disagree with this view? |

共修正 **63** 条。`task_type_effective` 字段写入 enriched 记录；
原始 `task_type` 保持不变，便于审计。修正函数固化在 `distillation/scripts/task_type_fix.py`，
任务三对盲测集评分时须调用同一函数，保持两边口径一致。

## 4. 剔除清单（不参与任何规则/锚点/观点/词伙蒸馏）

| id | 分数 | flags | 理由 |
|---|---|---|---|
| B6-OP-070 | 6.0 | suspected-offtask | flags: suspected-offtask（疑为 Task 1/非 Task 2） |
| B6-OP-077 | 6.0 | suspected-offtask | flags: suspected-offtask（疑为 Task 1/非 Task 2） |
| B6-OP-078 | 6.0 | suspected-offtask | flags: suspected-offtask（疑为 Task 1/非 Task 2） |
| B6-OP-087 | 6.0 | suspected-offtask | flags: suspected-offtask（疑为 Task 1/非 Task 2） |
| B65-OP-075 | 6.5 | suspected-offtask | flags: suspected-offtask（疑为 Task 1/非 Task 2） |
| B75-OP-069 | 7.5 | suspected-offtask | flags: suspected-offtask（疑为 Task 1/非 Task 2） |
| B8-OP-065 | 8.0 | suspected-offtask | flags: suspected-offtask（疑为 Task 1/非 Task 2） |

## 5. 四维小分反向标注（subscores back-annotation）

- 训练集中 22 条带官网小分与考官评语（A-examiner），原样保留，`subscores_source=official`。
- 其余 1171 条（含 7 条剔除项）执行反向标注：
  1. 用官方 Band Descriptor 操作性化的盲评分器（`blind_module_scores`）计算四维相对强弱；
  2. 以**真实总分**为锚，把相对强弱分布到四个维度（±1.0 内），并强制满足官方取整规则
     （四项平均按 .25→.5、.75→下一档取整后等于真实总分）；
  3. 标注 `subscores_source=inferred-v1` 与置信度（high/medium/low）。
- 推断值仅作为规则归纳与锚点评语的内部依据；不得用于任务三的盲测真值。

| 推断置信度 | 篇数 |
|---|---:|
| high | 44 |
| medium | 437 |
| low | 690 |

## 6. 清洗后分布与薄弱格子（训练集口径）

| 分数档 | opinion | discussion | adv-disadv | report | two-part | 小计 |
|---|---:|---:|---:|---:|---:|---:|
| 6.0 | 68 | 36 | 26 | 23 | 12 | 165 |
| 6.5 | 61 | 42 | 43 | 14 | 10 | 170 |
| 7.0 | 72 | 42 | 24 | 14 | 16 | 168 |
| 7.5 | 56 | 36 | 43 | 22 | 16 | 173 |
| 8.0 | 67 | 37 | 21 | 24 | 20 | 169 |
| 8.5 | 81 | 27 | 33 | 19 | 13 | 173 |
| 9.0 | 88 | 26 | 23 | 20 | 11 | 168 |

训练集内「分数档 × 题型」全部格子 ≥3 篇。

> 说明：distribution-report.md 的薄弱格子按 1490 全集统计；本表按修正后训练集 1186 篇
>（剔除 7 条 suspected-offtask）统计，作为 L1 置信度标注的唯一依据。


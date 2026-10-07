# L3 错误模式库

> **层级**：L3 · 错误模式（6–7.5 分样本统计出的高频失分模式）
> **来源**：从训练集中 Band 6 / 6.5 / 7 / 7.5 样本统计归纳。
> **加载时机**：评分主流程第 2 步「四模块独立诊断」时加载**全文**（诊断时必读）。
> **当前状态**：已填充（v1，2026-10-07）。统计口径：训练集 6–7.5 档 676 篇 / 8+ 档 510 篇；
> 所有例句均取自真实样本并标注 id；各模式的触发信号见条目内的文本特征描述。
> 说明：自动检测用于统计与提示，反馈时仍须人工复核命中句；少量模式在语料中低频出现不等于不重要
> （低发生率 + 高可修复性 = 提分性价比高）。

## 编号与字段约定（本库已按此执行）

1. 每条编号 `L3-{TR|CC|LR|GRA}-{序号}`，如 `L3-LR-04`。
2. 每条包含：**模式名**（如「中式直译搭配」「指代断裂」）→ **触发信号**（可正则/可人工识别的文本特征）→ **典型例句**（原句 + 修正 + 一句解析）→ **频次统计**（在 6–7.5 分样本中出现篇数/占比）→ **修复策略** → **来源样本 id**。
3. 需覆盖 SKILL.md 第七节模块诊断使用的分类口径：
   - CC：跳跃 / 循环论证 / 论点例证脱节 / 衔接词机械化 / 指代断裂
   - LR：搭配错误 / 词性误用 / 中式直译 / 语义不准 / 语域不当 / 重复用词
   - GRA：主谓一致 / 时态 / 单复数 / 冠词 / 词性 / 句子残缺 / run-on / 悬垂结构 / 从句误用 / 标点
4. 每条错误模式须给出「命中该模式在评分时如何影响对应维度分数」的说明，供评分与反馈共用。
5. 该库同时是「个人成长档案」的个人高频错误画像来源（命中即累加计数）。

---

## 索引（按模块）

| 模块 | 条目 | 负迁移标签 |
|---|---|---|
| TR | L3-TR-01 模板化开头 / L3-TR-02 例证停留在常识层 / L3-TR-03 论点—例证脱节 / L3-TR-04 限定词未回应 | 01 |
| CC | L3-CC-01 衔接词机械化 / L3-CC-02 连续短句堆叠 / L3-CC-03 指代断裂 / L3-CC-04 段内逻辑跳跃 / L3-CC-05 循环论证 | 01 |
| LR | L3-LR-01 搭配错误（中式直译） / L3-LR-02 词性误用 / L3-LR-03 语义不准 / L3-LR-04 语域不当 / L3-LR-05 重复用词 / L3-LR-06 介词与固定搭配冗余 | 01、02 |
| GRA | L3-GRA-01 主谓一致 / L3-GRA-02 不可数名词复数化 / L3-GRA-03 one of the + 单数 / L3-GRA-04 although…but / L3-GRA-05 句子残缺 / L3-GRA-06 悬垂结构 / L3-GRA-07 run-on / L3-GRA-08 标点：逗号粘连 / L3-GRA-09 时态选择 / L3-GRA-10 冠词缺失 | 01、02、03、04 |

**负迁移标签说明**：`NEG=是` 表示该模式在中国考生中复发率极高、且纠正成本低（提醒即可见效）。
评分反馈中命中负迁移模式时，附一句「中文思维 vs 英文思维」点醒语。

---

## TR 模块

### L3-TR-01 模板化开头（NEG=是）

- **触发信号**：开头出现可套用任何题目的万能句：in this modern era / with the development of / it is undeniable that / every coin has two sides。
- **典型例句**：`B6-ADV-001`（6.0）「In this modern era, it is undeniable that education plays an important role in human development.」
  → 修正：「University courses that include a placement abroad are popular because they promise employability; whether that promise holds is the question this essay addresses.」
  → 解析：模板句没有提供关于本题的任何信息，只消耗了 15 个词。
- **频次统计**：6–7.5 档 121/676（17.9%），8+ 档 67/510（13.1%）。
- **修复策略**：把万能句换成「争议点 + 双方立场 + 自己回应方向」三件事；第一句必须出现题目关键词。
- **评分影响**：命中 1 处即提示 TR 复检（模板句占比高的文章 TR 上限 6.5）；命中 2 处以上且
  其余段落无具体展开时，TR 封顶 6.0。
- **中文思维 vs 英文思维**：「科技发展/现代社会」式背景铺垫在中文作文里是礼貌，在英语议论文里是噪音。
- **来源样本**：`B6-ADV-001`、`B6-ADV-004`、`B6-ADV-010`。

### L3-TR-02 例证停留在常识层

- **触发信号**：例证只有 for example, many/some people… 式泛化，没有具体主体、场景或数据；例证后无解释。
- **典型例句**：`B6-DIS-029`（6.0）「For instance, many countries introduced modern teaching methods, which have helped students by improving their academic performance and communication skills.」
  → 修正：指定国家与年份 + 结果指标（如「Finland's 2016 curriculum reform…」）+ 一句机制解释。
  → 解析：国家、方法、结果都是抽象名词，无法验证，也无法支撑论点。
- **频次统计**：6–7.5 档 10/676（1.5%），8+ 档 4/510（0.8%）；另有大量「具体但相关度低」的例证未被此正则捕获。
- **修复策略**：例证三件套——主体（谁/哪里）+ 变化（发生什么）+ 关联（这如何证明论点）。
- **评分影响**：单个主体段命中不定档；两个主体段均命中且无机制句时，TR 上限 6.5。
- **来源样本**：`B6-DIS-029`、`B6-REP-004`、`B65-DIS-025`。

### L3-TR-03 论点—例证脱节

- **触发信号**：例证本身真实/具体，但证明的是另一个命题；段末用 therefore/thus 强行回扣。
- **典型例句**：`B6-ADV-001`（6.0）论点「实习/留学浪费时间」，例证却是「印度 UPSC 考生因专注考试而成功」
  → 修正：换成「具体某大学要求学生参加无薪实习，学生因通勤与打杂挤占复习时间导致成绩下滑」这类与论点同向的例证。
  → 解析：例证与论点之间缺少「同一因果方向」的桥。
- **频次统计**：需人工判定；检测辅助信号为「段内 example 标记后 40 词内无机制词且段末以 therefore/thus 收束」。
- **修复策略**：写完例证后自问「这个例子换成反面例子，论点还成立吗」；若不成立，例子选错了。
- **评分影响**：命中 1 段即 TR 复检；命中 ≥2 段或与结论矛盾时，TR 封顶 6.0。
- **来源样本**：`B6-ADV-001`、`B6-REP-004`。

### L3-TR-04 限定词未回应（best / only / most）

- **触发信号**：题目含绝对或范围限定词，文章只讨论「利弊/重要性」，没有专门句子处理该限定。
- **典型例句**：`B65-TQ-013`（6.5，best way + 体育课）——正文论证体育课的价值，但未讨论
  「为什么这是**最好**的方式（与其他方式比较）」。
  → 修正：补一段比较句（相比饮食监管/校内供餐改革，体育课的边际效果更大/更小），直接回应 best。
  → 解析：IELTS 的 TR 看「题目所有部分」，限定词是题目的一部分。
- **频次统计**：best/only/most 题干族在训练集中出现 130+ 篇；误回应形态需人工复核（本条的判定以审题比对为准）。
- **修复策略**：审题时圈出限定词；正文至少 1 句显式比较或限缩（如「this works only when…」）。
- **评分影响**：命中且无回应时 TR 封顶 6.5；有部分回应（提及但未展开）封顶 7.0。
- **来源样本**：`B65-TQ-013`、`B6-TQ-007`、`B75-TQ-008`。

---

## CC 模块

### L3-CC-01 衔接词机械化（NEG=是）

- **触发信号**：段首反复 Firstly / Secondly / Moreover / On the one hand；或机械连接词密度 ≥2/100 词、
  且段落开头 ≥2 处为连接词。
- **典型例句**：`B6-ADV-004`（6.0）「Firstly, young adults are good with technology, and countries can grow rapidly…」
  → 修正：删去 Firstly，用与前段的语义关系开句（"That technological fluency also matters at the national level: …"）。
  → 解析：连接词标注了序号，但没有建立两个论点之间的逻辑关系。
- **频次统计**：6–7.5 档 353/676（52.2%），8+ 档 181/510（35.5%）；显性连接词密度与分数
  负相关（ρ=−0.36，见 L1 §0.2）。
- **修复策略**：能靠指代/替换衔接的，删掉连接词；保留的连接词必须承担真实逻辑（转折、因果、让步）。
- **评分影响**：命中 ≥2 处段首机械词 + 密度 >4.5/100 词时，CC 上限 6.5。
- **中文思维 vs 英文思维**：中文用「首先/其次/最后」组织段落；英文靠信息位置与指代链推进。
- **来源样本**：`B6-ADV-001`、`B6-ADV-004`、`B65-DIS-052`。

### L3-CC-02 连续短句堆叠

- **触发信号**：连续 3 句以上 ≤12 词，句间无明确逻辑推进（不是有意使用的修辞短句）。
- **典型例句**：`B6-ADV-020`（6.0）「This includes how people live. Some people believe that the small family is common. However, others believe that the large family is difficult.」
  → 修正：合并为「While small families have become standard in many cities, others still regard the large extended family as the more resilient arrangement.」
  → 解析：三个句子的信息可压缩成一句对比结构。
- **频次统计**：6–7.5 档 44/676（6.5%），8+ 档 20/510（3.9%）。
- **修复策略**：把关系最近的两句合并为从句/分词结构，或补一句解释句说明前句的意义。
- **评分影响**：命中 2 处以上且伴随连接词机械化时，CC 上限 6.0；单处不影响定档。
- **来源样本**：`B6-ADV-009`、`B6-ADV-020`、`B6-ADV-033`。

### L3-CC-03 指代断裂（this/they/it 无明确先行词）

- **触发信号**：句首 this/they/it 作主语，前一句找不到明确名词先行词；或跨段使用 this 指代上上段内容。
- **典型例句**：`B6-ADV-012`（6.0）「This makes the travel more comfortable.」——this 指代的是上文的
  「driverless cars」还是「shorter travel time」无法确定。
  → 修正：「Driverless technology makes travelling more comfortable, because…」。
  → 解析：指代越具体，衔接越强；this + 抽象动词是最常见的断裂形态。
- **频次统计**：扫描器命中 6–7.5 档 221/676（32.7%）、8+ 档 108/510（21.2%）（扫描包含合法用法，须人工复核）。
- **修复策略**：把 this 换成 this policy / such measures / that shift 等「限定词 + 名词」。
- **评分影响**：命中 2 处以上且无法回溯时，CC 上限 6.5。
- **来源样本**：`B6-ADV-002`、`B6-ADV-012`、`B6-ADV-015`。

### L3-CC-04 段内逻辑跳跃

- **触发信号**：结论句先于论据出现；或两个相邻句使用不同话题，中间没有过渡。
- **典型例句**：`B6-REP-004`（6.0）「For example, many students study science because they are interested in science
  but they work on the business area.」——兴趣、专业与就业之间的推理链缺失。
  → 修正：补一句因果桥（「…so they graduate with scientific training but pursue business roles, which explains the mismatch」）。
  → 解析：读者被迫自行补全论证。
- **频次统计**：人工判定；辅助信号为段内连续两句无共同实词、且第二句以 Therefore/Thus 开头。
- **修复策略**：段内做「还句」自查：每两句之间写一句它们的关系（因果/对比/递进），再删掉多余的话。
- **评分影响**：命中 1 段即触发 CC 复检；命中 2 段以上时 CC 上限 6.5。
- **来源样本**：`B6-REP-004`、`B6-ADV-001`。

### L3-CC-05 循环论证

- **触发信号**：解释句把主题句换成同义词重复，或结论句与主题句结构相同、信息未增加。
- **典型例句**：`B6-OP-017`（6.0）「If the nations wants to be progressive it is very important that the people
  are more educated and progressive.」——用 progressive 解释 progressive。
  → 修正：「…more educated, because education supplies the skills that make economic and social reform possible.」
  → 解析：机制句必须引入新信息（原因、条件、证据）。
- **频次统计**：人工判定；常见伴随信号是主题句与段末句实词重合率 >70%。
- **修复策略**：对每段写一句「为什么这句成立」，若与主题句重复即重写。
- **评分影响**：命中 ≥2 段时 TR 上限 6.5（论证未推进），CC 同步复检。
- **来源样本**：`B6-OP-017`、`B6-OP-010`。

---

## LR 模块

### L3-LR-01 搭配错误（中式直译）（NEG=是）

- **触发信号**：动词与名词/介词按中文语义拼接：learn knowledge（学习知识）、discuss about（讨论关于）、
  the most of people（大多数人）、make crime（犯罪）。
- **典型例句**：`B65-ADV-003`（6.5）「Firstly, let me discuss about the advantages.」
  → 修正：「Let me first discuss the advantages.」
  → 解析：discuss 是及物动词，about 是中文「关于」的直译残留。
  另见 `B65-REP-013`（6.5）「this is not easy for the most of people」→「for most people」；
  `B6-OP-005`（6.0）「This will effect the aquactic creature」→「This will affect the aquatic creatures」。
- **频次统计**：discuss about 6–7.5 档 1/676、8+ 档 1/510（`B85-OP-031` 出现 "discuss about about" 的重复）；
  the most of 中档 7/676、8+ 档 1/510；learn knowledge 在语料中仅 1 例（`B9-OP-069`）。
- **修复策略**：把中文动宾结构还原为英文搭配（acquire knowledge / discuss sth / commit a crime / affect sth）。
- **评分影响**：单项搭配错误不改档；同一段出现 ≥2 处或涉及核心论点关键词时，LR 复检并考虑封顶 6.5。
- **中文思维 vs 英文思维**：中文「学习知识、讨论关于」是动宾+介词结构，英文里对应动词很多是及物动词。
- **来源样本**：`B65-ADV-003`、`B65-REP-013`、`B6-OP-005`、`B85-OP-031`。

### L3-LR-02 词性误用（NEG=是）

- **触发信号**：effect/affect、success/succeed、development/develop、economic/economical 等词性混用；
  或把名词当动词（"will effect"）。
- **典型例句**：`B6-OP-005`（6.0）「This will effect the aquactic creature」（effect 名词误作动词）
  → 修正：「This will affect aquatic creatures」。
  → 解析：拼写错误（aquactic）与词性错误叠加，属于最低成本的提分点。
- **频次统计**：effect 作动词 6–7.5 档 1/676、8+ 档 0；词性混用整体需人工复核（本语料中多为拼写问题伴随出现）。
- **修复策略**：建立个人易混词表（affect/effect、economic/economical、success/succeed），写完用搜索功能逐词检查。
- **评分影响**：密集词性错误（≥3 处）时 GRA/LR 同时复检；单处不影响定档但必须在反馈中列出。
- **来源样本**：`B6-OP-005`。

### L3-LR-03 语义不准

- **触发信号**：词形正确但语义偏离（用词与句意不匹配），读起来「怪」但语法无误。
- **典型例句**：`B6-ADV-001`（6.0）「Thus, hustle will teach them to survive independently.」
  → 修正：「That daily struggle teaches them to manage their lives independently.」
  → 解析：hustle 指「奔忙/打拼」，不能指代前文「做饭、找工作」的具体经历。
  另见 `B6-OP-017`（6.0）「people are more educated and progressive」——progressive 用于人时语义偏狭。
- **频次统计**：人工判定；常见伴随信号是「低频词 + 与上下文名词无共现」。
- **修复策略**：不确定的词换成确定的词；用搭配词典核对名词/动词搭配。
- **评分影响**：单处不改档；影响论点理解或出现在主题句中时，LR 复检并提示改写。
- **来源样本**：`B6-ADV-001`、`B6-OP-017`。

### L3-LR-04 语域不当（口语词入文）

- **触发信号**：kids / stuff / a lot of / bestie / guys 等口语表达出现在学术语域。
- **典型例句**：`B6-DIS-019`（6.0）「…make the most of the driving time to become bestie with their children.」
  → 修正：「…use the commute to build a closer relationship with their children.」
  → 解析：bestie 是社交口语，直接破坏语域一致性。
  另见 `B6-ADV-027`「plenty of kids use their tablets」→「many children use tablets」。
- **频次统计**：a lot of/lots of 6–7.5 档 99/676（14.6%）、8+ 档 51/510（10.0%）。
- **修复策略**：语域替换表（kids→children、a lot of→a considerable number of、stuff→material）。
- **评分影响**：≥2 处口语表达时 LR 复检；≥4 处且未在反馈中修复，LR 封顶 6.5。
- **来源样本**：`B6-DIS-019`、`B6-ADV-027`、`B6-ADV-003`。

### L3-LR-05 重复用词

- **触发信号**：同一实词（尤其 people）在全文出现 ≥6 次且无替换；同一句式反复出现。
- **典型例句**：`B65-OP-044`（6.5）全文出现 people 16 次；`B7-ADV-011`（7.0）出现 11 次。
  → 修正：按语义替换 individuals / citizens / residents / employees / the public，或改用具体群体。
  → 解析：重复不是词汇错误，但会拉低 precision 与得分感知。
- **频次统计**：people 过密（≥6 次或 ≥1/40 词）在 6–7.5 档 46/676（6.8%）、8+ 档 10/510（2.0%）。
  注意：more and more 在 8+ 档反而略多（14 vs 17），**不能**把该短语单独当作低分标记。
- **修复策略**：写作后统计高频实词 Top 5，逐个做替换链。
- **评分影响**：命中且替换空间未被利用时，LR 复检；与其他问题叠加时考虑封顶 6.5。
- **来源样本**：`B65-OP-044`、`B6-OP-071`、`B7-ADV-011`。

### L3-LR-06 介词与固定搭配冗余

- **触发信号**：discuss about / explain about / mention about / emphasise on / contact with（当 contact 为动词时）。
- **典型例句**：`B6-OP-008`（6.0）「…to explain about a balanced budget…」
  → 修正：「…to explain a balanced budget…」。
  → 解析：explain 后直接接宾语；about 属于中文「解释关于」的直译。
- **频次统计**：discuss/explain/mention about 6–7.5 档 2/676（0.3%）、8+ 档 1/510。
- **修复策略**：删除冗余介词；对固定搭配（explain sth to sb / emphasise sth）建立清单。
- **评分影响**：单处不改档；与搭配错误同段出现 ≥2 处时 LR 封顶 6.5。
- **来源样本**：`B6-OP-008`、`B65-ADV-003`、`B85-OP-031`。

---

## GRA 模块

### L3-GRA-01 主谓一致（NEG=是）

- **触发信号**：复数主语 + is/was/has/does；第三人称单数主语 + are/were/have/do；
  相对从句内主语与谓语数不一致。
- **典型例句**：`B6-DIS-003`（6.0）「I do agree individual who have advanced education are more likely…」
  → 修正：「…individuals who have advanced education are more likely…」。
  另见 `B6-ADV-018`「Although there are many positive tips, there are many mistake.」→「many mistakes」；
  `B6-OP-017`「If the nations wants to be progressive」→「If a nation wants…」。
  → 解析：中文没有主谓数的一致要求，写作时靠「邻近一致」直觉检查容易漏。
- **频次统计**：检测器命中 6–7.5 档 36/676（5.3%）、8+ 档 27/510（5.3%）（含邻近一致的少量误报，需人工复核）。
- **修复策略**：每句写完先找主语再对谓语；重点检查 there be、each、one of、相对从句。
- **评分影响**：同一错误类型 ≥3 次或跨段出现时，GRA 不进入高档（≥7.5）。
- **来源样本**：`B6-DIS-003`、`B6-ADV-018`、`B6-OP-017`。

### L3-GRA-02 不可数名词复数化（NEG=是）

- **触发信号**：informations / advices / equipments / knowledges / researches / evidences / homeworks。
- **典型例句**：`B6-OP-005`（6.0）「…due to the lack of knowledge and equipments.」
  → 修正：「…due to a lack of knowledge and equipment.」
  另见 `B6-DIS-041`「reseanable evidences」→「reasonable evidence」；
  `B65-ADV-025`「other informations」→「other information」；`B65-DIS-005`「scientific researches」→「scientific research」。
  → 解析：这些名词在英语中不可数，复数形式是典型负迁移。
- **频次统计**：6–7.5 档 5/676（0.7%）、8+ 档 3/510（0.6%）。
- **修复策略**：建立不可数名词清单；计数时用 a piece of / an item of。
- **评分影响**：≥2 处同类错误时 GRA 复检；≥3 处时该项不得进入 7.0 以上。
- **来源样本**：`B6-OP-005`、`B6-DIS-041`、`B65-ADV-025`、`B65-DIS-005`。

### L3-GRA-03 one of the + 单数（NEG=是）

- **触发信号**：one of the + 单数名词（one of the reason / one of the biggest problem）。
- **典型例句**：`B65-DIS-003`（6.5）「The climate change is one of the biggest problem in the world today…」
  → 修正：「…one of the biggest problems…」。
  另见 `B65-OP-034`「one of the reason」；`B6-ADV-018`「one of the common reason」。
- **频次统计**：6–7.5 档 6/676（0.9%）、8+ 档 0/510——在语料中几乎只出现于中档样本。
- **修复策略**：写 one of the 时强行想到「复数名词 + 单数谓语」。
- **评分影响**：命中即 GRA 复检；≥2 处时 GRA 复检并考虑封顶 6.5。
- **来源样本**：`B65-DIS-003`、`B65-OP-034`、`B6-ADV-018`。

### L3-GRA-04 从句误用：although…but（NEG=是）

- **触发信号**：同一句中 although/though 与 but 连用（中文「虽然……但是……」）。
- **典型例句**：`B7-TQ-003`（7.0）「Thirdly, although sharing wealth with poorer nations is very necessary but this help should only stop at…」
  → 修正：「Although sharing wealth with poorer nations is necessary, such help should stop at…」。
  另见 `B85-TQ-006`（8.5）「even though they have excellent remunerations, but, they are still paying…」。
- **频次统计**：6–7.5 档 1/676、8+ 档 1/510——低频但零容忍（一出现即被考官注意到）。
- **修复策略**：although 与 but 二选一；检查 "not only…but also" 的合法用法避免误改。
- **评分影响**：出现 1 次即 GRA 复检；若句意因此受损，GRA 不高于 6.5。
- **来源样本**：`B7-TQ-003`、`B85-TQ-006`。

### L3-GRA-05 句子残缺

- **触发信号**：Because/Although 引导的从句单独成句；无主句。
- **典型例句**：`B65-DIS-018`（6.5）「Because every species has its own role in the environment.」
  → 修正：「Every species has its own role in the environment, so …」或把 because 从句并入主句。
  另见 `B6-ADV-027`「Because they know that the game will affect their children positively.」；
  `B7-TQ-001`「Because bad news makes us curious.」；
  `B9-ADV-035`（9.0，D-auto 评分样本）「Although I find this statement to be an extremely negative development for various reasons.」
  ——该例说明自动评分来源的高档样本也可能存在结构残缺，锚点选用时须复核。
- **频次统计**：句首 Because/Although 的残缺句检测：6–7.5 档 7/676、8+ 档 1/510。
- **修复策略**：写完从句后检查「谁在做主句动作」；把从句与主句用逗号连接。
- **评分影响**：≥1 处即 GRA 复检；≥2 处或出现在主题句时，GRA 封顶 6.5。
- **来源样本**：`B65-DIS-018`、`B6-ADV-027`、`B7-TQ-001`、`B9-ADV-035`。

### L3-GRA-06 悬垂结构

- **触发信号**：句首分词短语的逻辑主语与主句主语不一致。
- **典型例句**：`B6-REP-020`（6.0）「Having no place to be discarded, part of these wastes are thrown into the sea.」
  → 修正：「Because there is nowhere to dispose of them, some of these wastes are thrown into the sea.」
  → 解析：having 的逻辑主语应是「人/机构」，而不是「wastes」。
- **频次统计**：人工判定为主（自动检测仅提示 Being/Having 开头的长句）；语料中低档样本更常见。
- **修复策略**：分词短语改写为原因/时间从句，或让主句主语成为分词的逻辑主语。
- **评分影响**：命中 1 处即 GRA 复检；≥2 处时 GRA 不高于 6.5。
- **来源样本**：`B6-REP-020`。

### L3-GRA-07 run-on 句

- **触发信号**：单句 >45 词、多个并列谓词只用逗号连接，或缺少空格的句间粘连。
- **典型例句**：`B6-ADV-010`（6.0）「In conclusion,both government-dundee and privately-funded healthcare systems have their own pros and cons.While covering for medicine promotes equality…」
  → 修正：拆为两句，并补空格：「In conclusion, both publicly and privately funded healthcare systems have advantages and disadvantages. While covering medicine promotes equality, …」。
- **频次统计**：6–7.5 档 28/676（4.1%）、8+ 档 32/510（6.3%）——**高档样本同样常见**，
  因此 run-on 只作为本地修正项，不能单独作为降档依据（长度本身可能来自复杂论证）。
- **修复策略**：按意群拆分；分号/从句建立层级；检查句号后空格等排版问题。
- **评分影响**：命中不改档；但命中且句子语义受损（多个主语混乱）时，GRA 复检并可考虑封顶 7.0。
- **来源样本**：`B6-ADV-010`、`B6-DIS-014`、`B6-DIS-029`。

### L3-GRA-08 标点：逗号粘连

- **触发信号**：两个独立句用逗号连接，后接 however/therefore 等连接副词（应为分号或新句）。
- **典型例句**：`B65-DIS-010`（6.5）「Some persons think that this is very good for the workers, however other persons think that it is bad for the team work…」
  → 修正：「…for the workers; however, other people believe it harms teamwork…」。
- **频次统计**：检测器扫描命中 6–7.5 档 17/676、8+ 档 30/510，其中包含大量合法用法（如「Employers, however, must…」），
  **必须人工复核示例**（`B6-DIS-015`、`B6-OP-036` 含真实粘连；`B6-ADV-031` 为合法用法）。
- **修复策略**：阅读时专门检查「, however + 主语+谓语」结构；改为「. However, …」或「; however, …」。
- **评分影响**：命中 1 处即 GRA 复检；≥2 处时 GRA 不高于 6.5。
- **来源样本**：`B65-DIS-010`、`B6-OP-036`、`B6-DIS-015`。

### L3-GRA-09 时态/语态选择

- **触发信号**：In recent years + 一般过去时；状态变化用 be + 过去分词（are disappeared / is improved）；
  同一段时态无故切换。
- **典型例句**：`B65-ADV-020`（6.5）「Many jobs which existed twenty years ago are disappeared now…」
  → 修正：「…have disappeared now」；`B65-DIS-005`「many languages are disappeared」→「are disappearing / have disappeared」。
  另见 `B75-REP-020`（7.5）「In recent years, it was reported that…」——用现在完成时更自然（has been reported）。
- **频次统计**：are/is disappeared 类共 3 篇中档命中（`B65-ADV-020`、`B65-DIS-005`、`B6-ADV-018` 类）；
  In recent years + 过去时需人工判定（部分语境合法）。
- **修复策略**：锁定全文时态锚（一般现在 + 现在完成），完成时/被动语态改写后回读检查。
- **评分影响**：系统性时态错误（≥3 处）时 GRA 不进入 7.0 以上；单处进入逐句教学卡的「原句错误与不当」。
- **来源样本**：`B65-ADV-020`、`B65-DIS-005`、`B75-REP-020`。

### L3-GRA-10 冠词缺失/误用

- **触发信号**：定冠词误加（in the society）、a/an 误用、单数可数名词裸用（Government should…）。
- **典型例句**：`B6-TQ-003`（6.0）「…which deal with the underlying problems in the society…」
  → 修正：「…the underlying problems in society…」。
  另见 `B8-DIS-044`（8.0）「…causes some tension in the society.」——同一问题在 8.0 样本中亦出现，
  说明冠词问题通常不致命，但会被考官系统察觉。
- **频次统计**：in the society 6–7.5 档 1/676、8+ 档 1/510；冠词错误整体需人工复核（自动检测不可靠）。
- **修复策略**：泛指的抽象名词不加 the（society / education / technology）；特指才加。
- **评分影响**：冠词错误 ≥4 处且集中在关键名词时，GRA 封顶 6.5；否则进入逐条反馈。
- **来源样本**：`B6-TQ-003`、`B8-DIS-044`。

---

## 使用接口

1. **评分与诊断时**：L3 全文扫描 → TR/CC 层面的命中进入模块诊断；LR/GRA 层面的具体错误进入逐句教学卡的「原句错误与不当」。命中负迁移标签的模式在卡内附一句点醒语。
2. **教学时**：优先讲解 `NEG=是` 且中高差值大的模式（如衔接词机械化、重复用词、one of the + 单数）。
3. **个人成长档案**：每次批改把命中条目计数写入用户档案，形成个人高频错误画像。
4. **输出脱敏**：模式编号（如 L3-GRA-01）只用于内部检索和档案计数，不写入交付文件。

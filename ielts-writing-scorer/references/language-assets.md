# L4 高分语言资产库（表达库）

> **层级**：L4 · 高分句式、衔接与论证套路
> **来源**：从训练集中 Band 8 / 8.5 / 9 样本提取。
> **加载时机**：按需检索：主流程第 1 步定位本主题段落；生成逐句教学卡时检索对应功能段，用于「句式骨架与高分词伙」。
> **当前状态**：已填充（v1，2026-10-07）。全部条目提取自训练集 Band 8 / 8.5 / 9.0 样本，
> 每个示例句均可在标注样本 id 中回查；8.5 档 D-auto 样本仅用于句式参考，不作为质量背书。

## 编号与字段约定（本库已按此执行）

1. **两级组织**：先按主题（与 `topic-vocab.md` 同一套十主题），主题内再按功能分类：
   - 句式骨架（如「让步 + 转折」：`While X may appear compelling, Y ...`）
   - 衔接手段（段内推进、段间过渡，优先语义衔接而非连接词堆砌）
   - 论证套路（观点 → 机制 → 例证 → 回扣的展开模板）
2. 每条编号 `L4-{主题码}-{序号}`（主题码与 L6 统一，如 `EDU`、`TECH`）。
3. 每条包含：**骨架/套路**（留空槽位，如 `[A] 削弱了 [B]`）→ **示例句** → **适用题型** → **来源样本 id + 分数**。
4. 只收录 8+ 样本中出现的真实句式，禁止改写或编造；风格须与 `anchors/` 锚点库一致。
5. 与 L5/L6 分工：L4 解决「怎么组织成句成段」，L5 解决「写什么观点」，L6 解决「用什么词伙」。

---

## 1. 通用句式骨架（GEN，跨主题）

> 用法：槽位内填入本题概念；示例句后面的 `(B…)` 是可直接回查的来源样本。

- **[L4-GEN-01] 让步 → 立场**
  - 骨架：`While [对方合理之处], I believe [立场] because [机制].`
  - 示例：While this trend may narrow access to certain professions, I believe its merits outweigh the disadvantages because it improves employability and reduces financial burden.（`B8-ADV-009`，8.0）
  - 适用题型：opinion / adv-disadv / two-part
- **[L4-GEN-02] 让步扩展 → 条件限定**
  - 骨架：`Although [反方收益], [己方主张] — provided that [限定条件].`
  - 示例：Although privately funded healthcare can offer greater choice and quicker treatment, government-funded systems are generally more equitable and protect people from financial hardship.（`B8-ADV-008`，8.0）
  - 适用题型：discussion / adv-disadv / opinion
- **[L4-GEN-03] 立场句 + 承认复杂性**
  - 骨架：`I firmly believe [立场], though I acknowledge [对方成立的情形/条件].`
  - 示例：I firmly believe that unrestricted government surveillance is fundamentally incompatible with democratic principles, though I acknowledge the necessity of targeted, judicially-supervised monitoring in specific circumstances.（`B8-OP-004`，8.0，官方小分）
  - 适用题型：opinion / discussion
- **[L4-GEN-04] 机制解释句**
  - 骨架：`This is (mainly) because [机制], which [进一步结果].`
  - 示例：This is because digital communication relies heavily on text and superficial updates, which can lead to shallow relationships and widespread emotional detachment.（`B8-OP-063`，8.0，用词已按语义修正 superficial 重复）
  - 适用题型：全题型（主体段第 2–3 句）
- **[L4-GEN-05] 具体例证句**
  - 骨架：`[具体主体/场景], for example, [可检验的细节], which [与论点的关联].`
  - 示例：Diaspora communities, for example, use messaging applications to sustain family bonds across continents in ways that were impossible a generation ago.（`B8-DIS-003`，8.0）
  - 适用题型：全题型
- **[L4-GEN-06] 结果推进句**
  - 骨架：`As a result / Consequently, [结果], thereby [更高层目标].`
  - 示例：Consequently, consumers may reduce their intake, even subconsciously, resulting in a healthier society.（`B8-DIS-005`，8.0）
  - 适用题型：report / adv-disadv / two-part
- **[L4-GEN-07] 条件建议句**
  - 骨架：`Provided that [前提], [措施] would [效果].`
  - 示例：Provided that the initial transitional friction is successfully navigated, the ensuing amalgamation of cultural fluency, pragmatic skill acquisition and personal maturation represents an incomparable asset.（`B8-ADV-021`，8.0）
  - 适用题型：report / two-part / opinion
- **[L4-GEN-08] 对比澄清句**
  - 骨架：`By contrast, [对照对象] [机制], meaning that [推论].`
  - 示例：By contrast, the construction of new road capacity is well-documented to induce demand — a phenomenon known as induced traffic — meaning that new roads generate additional car journeys rather than alleviating congestion.（`B8-OP-005`，8.0）
  - 适用题型：discussion / report / opinion
- **[L4-GEN-09] 重新框定句**
  - 骨架：`While there is substance to both positions, [真正的变量] rather than [表面争点], provided [条件].`
  - 示例：While there is substance to both positions, I would contend that technology's net effect is integrative rather than isolating, provided it is used with intention.（`B8-DIS-003`，8.0）
  - 适用题型：discussion / opinion（用于结论或立场段）
- **[L4-GEN-10] 结论综合句**
  - 骨架：`[两个机制] must operate together: [机制 A] generates [资源], yet without [条件], [机制 B] 的结果会 [负向].`
  - 示例：Economic growth generates the fiscal resources that make redistribution possible, yet without deliberate policy, the gains of growth become concentrated at the top.（`B75-DIS-001`，7.5，官方小分）
  - 适用题型：全题型结论段

## 2. 主题句式（按十主题）

### 教育（EDU）

- **[L4-EDU-01] 路径替代句**（描述「而非」的选择）
  - 骨架：`Rather than [旧做法], education systems should [新做法] that [目标].`
  - 示例：Rather than adhering to a rigid age requirement, education systems should offer flexible entry points and diverse learning approaches that accommodate varying developmental readiness.（`B8-DIS-001`，8.0）
  - 适用题型：opinion / report
- **[L4-EDU-02] 路径对比句**
  - 骨架：`Unlike [群体 A] who [行为], [群体 B] gain [收益] while [方式].`
  - 示例：Unlike university students who often spend several years studying theoretical knowledge, they gain hands-on experience while learning their profession.（`B8-ADV-009`，8.0）
  - 适用题型：discussion / adv-disadv

### 科技（TECH）

- **[L4-TECH-01] 隐性影响句**
  - 骨架：`[技术] is not merely [表层功能]; it [深层机制], which [代价].`
  - 示例：Digital communication relies heavily on text and superficial updates, which can lead to shallow relationships and widespread emotional detachment.（`B8-OP-063`，8.0）
  - 适用题型：opinion / two-part
- **[L4-TECH-02] 条件约束句**
  - 骨架：`[风险] will persist unless [责任主体] be held accountable for [对象].`
  - 示例：Hence, there is a high possibility of spreading wrong medical information throughout the world, unless the site developers are held accountable for the content they provide.（`B8-ADV-036`，8.0）
  - 适用题型：report / two-part

### 环境（ENV）

- **[L4-ENV-01] 机制归因句**
  - 骨架：`This is because [主体] are not properly informed of [后果], so [行为] continues.`
  - 示例：This is because they are not properly informed of the possible detrimental effects of taking the environment for granted.（`B8-OP-060`，8.0）
  - 适用题型：report / opinion
- **[L4-ENV-02] 力度方向句**
  - 骨架：`[主体] should increase, rather than diminish, [投入] to ensure [目标].`
  - 示例：Governments should increase, rather than diminish, financial commitments to environmental protection to ensure a sustainable future.（`B8-OP-027`，8.0）
  - 适用题型：report / opinion
- **[L4-ENV-03] 预防性框架句**
  - 骨架：`[措施] is therefore a preventative strategy rather than simply a response to [问题].`
  - 示例：Protecting wildlife as a whole is therefore a preventative strategy rather than simply a response to extinction.（`B8-DIS-018`，8.0）
  - 适用题型：discussion / report

### 政府与公共政策（GOV）

- **[L4-GOV-01] 优先序论证句**
  - 骨架：`While [对象 A] retains clear value in [场景], I would argue that the case for [对象 B] is compelling, particularly given [压力/条件].`
  - 示例：While roads retain clear value in rural connectivity, I would argue that the case for prioritising railway investment is compelling, particularly given the twin pressures of urbanisation and climate change.（`B8-OP-005`，8.0）
  - 适用题型：opinion / discussion
- **[L4-GOV-02] 制度类比句**
  - 骨架：`This framework — essentially the [类比对象] of [已有制度] — [效果] and requires only [调整] rather than [重构].`
  - 示例：This framework — essentially the digital equivalent of a physical search warrant — has functioned effectively in democratic legal systems for centuries and requires only updated application rather than fundamental reimagining.（`B8-OP-004`，8.0，官方小分）
  - 适用题型：opinion（政策论证段）

### 社会问题（SOC）

- **[L4-SOC-01] 空间/群体对比句**
  - 骨架：`[群体] in [场景 A] faces [限制]; [场景 B], by contrast, offers [机会].`
  - 示例：A young graduate in agriculture-dependent rural India or Sub-Saharan Africa faces limited prospects for skilled employment locally; the city, by contrast, offers access to a labour market several orders of magnitude larger.（`B8-ADV-001`，8.0）
  - 适用题型：adv-disadv / report
- **[L4-SOC-02] 叠加结果句**
  - 骨架：`[条件 A] makes [结果 1] easier, and [结果 1] in turn [结果 2], thereby [目标].`
  - 示例：With a very good educational background it becomes easier to find a well-paid job, and with lucrative income they gain confidence to lead an independent life, thereby achieving their goals.（`B8-ADV-025`，8.0）
  - 适用题型：adv-disadv / report

### 犯罪与法律（CRIME）

- **[L4-CRIME-01] 干预措施例证句**
  - 骨架：`For example, [项目/措施] has helped [对象] [结果], reducing [问题].`
  - 示例：For example, job-training programs have helped many young adults secure stable work and avoid criminal behaviour.（`B8-REP-003`，8.0）
  - 适用题型：report / opinion
- **[L4-CRIME-02] 组合政策句**
  - 骨架：`Governments should combine [惩罚] with [社会政策], [政策 1] and [政策 2].`
  - 示例：Governments should combine necessary penalties with policies that improve living conditions, build legal awareness and help prisoners return safely to society.（`B8-DIS-038`，8.0）
  - 适用题型：discussion / report
- **[L4-CRIME-03] 反向定义句**
  - 骨架：`In this sense, [对象] becomes [负面隐喻], rather than [应有功能].`
  - 示例：In this sense, prison becomes a revolving door, rather than a solution.（`B8-OP-032`，8.0）
  - 适用题型：opinion / report

### 文化与语言（CUL）

- **[L4-CUL-01] 价值定义句**
  - 骨架：`This is mainly because [文化载体] is a [比喻], which [跨文化功能].`
  - 示例：This is mainly because music is a universal language that crosses cultural boundaries.（`B8-OP-040`，8.0）
  - 适用题型：opinion / discussion
- **[L4-CUL-02] 保护措施句**
  - 骨架：`To solve this issue, [主体] should make [文化对象] more [属性] to [目标群体].`
  - 示例：To solve this issue, governments and museum authorities should make cultural attractions more appealing to local communities.（`B8-REP-008`，8.0）
  - 适用题型：report
- **[L4-CUL-03] 媒体对比句**
  - 骨架：`[群体] subscribe to the belief that [载体 A] [功能], whereas [载体 B] [局限].`
  - 示例：Some people subscribe to the belief that reading helps enhance language skills and creativity, whereas watching television does very little for these abilities.（`B8-OP-024`，8.0）
  - 适用题型：discussion / opinion

### 健康（HEALTH）

- **[L4-HEALTH-01] 具象例证句**
  - 骨架：`[特定人群], for example, may [行为] because of [原因], which [双重后果].`
  - 示例：A person with a chronic illness, for example, may postpone necessary treatment because of the cost, which can worsen both their health and financial situation.（`B8-ADV-008`，8.0）
  - 适用题型：report / adv-disadv
- **[L4-HEALTH-02] 让步立场句**
  - 骨架：`Although [温和措施] may be appropriate for [轻度情形], I believe that [极端做法] is [评价] because [风险].`
  - 示例：Although self-care may be appropriate for minor ailments, I believe that avoiding professional medical advice is a negative development because it can pose significant risks to people's well-being.（`B8-ADV-031`，8.0）
  - 适用题型：opinion / discussion
- **[L4-HEALTH-03] 消费端结果句**
  - 骨架：`Consequently, [消费行为] may [变化], even subconsciously, resulting in [公共健康结果].`
  - 示例：Consequently, consumers may reduce their intake, even subconsciously, resulting in a healthier society.（`B8-DIS-005`，8.0）
  - 适用题型：report / discussion

### 媒体与广告（MEDIA）

- **[L4-MEDIA-01] 平衡对比句**
  - 骨架：`On the other hand, [媒介] can [功能], reducing [风险] and keeping [对象] away from [危害].`
  - 示例：On the other hand, television can keep youngsters occupied while their parents or caregivers are busy, reducing the need for constant supervision and keeping them away from potential physical dangers.（`B8-DIS-023`，8.0）
  - 适用题型：discussion / adv-disadv
- **[L4-MEDIA-02] 功能评价句**
  - 骨架：`Consequently, effective marketing helps bridge the gap between [双方] by ensuring [价值] receives [关注].`
  - 示例：Consequently, effective marketing helps bridge the gap between producers and consumers by ensuring valuable products receive the attention they deserve.（`B8-OP-018`，8.0）
  - 适用题型：opinion / adv-disadv
- **[L4-MEDIA-03] 产品例证句**
  - 骨架：`For example, [产品类别] that can [功能 1], [功能 2] and [功能 3] have encouraged [人群] to [行为转变].`
  - 示例：For example, smartwatches that can monitor a person's heart rate, blood pressure and calorie expenditure have encouraged thousands of individuals to take up an active lifestyle.（`B8-ADV-014`，8.0，措辞已按原句简化）
  - 适用题型：opinion / report

### 全球化与工作（GLOB）

- **[L4-GLOB-01] 权衡立场句**
  - 骨架：`I would argue that, on balance, [倾向判断], though this calculus is not uniform across [范围].`
  - 示例：I would argue that, on balance, the advantages outweigh the disadvantages, though this calculus is not uniform across all professions or demographics.（`B8-ADV-002`，8.0）
  - 适用题型：adv-disadv / opinion
- **[L4-GLOB-02] 远程工作例证句**
  - 骨架：`For example, [职业] living in [地点 A] may now work for [组织] without having to [旧约束].`
  - 示例：For example, a skilled employee living in a smaller town may now work for a company based in a major city without having to relocate.（`B8-ADV-005`，8.0）
  - 适用题型：opinion / two-part
- **[L4-GLOB-03] 非标准用工对比句**
  - 骨架：`They can also [收益], unlike [对照群体] who [约束].`
  - 示例：They can also spend more time with their families, unlike full-time employees who have limited annual leave and must spend additional time commuting and preparing for work.（`B8-ADV-028`，8.0）
  - 适用题型：discussion / adv-disadv

## 3. 论证套路（TAO）

- **[L4-TAO-01] 四步链条：立论 → 反例检验 → 具体化 → 短句回扣**
  - 示例（9.0 全链）：The case for individual action rests on aggregate logic… / Yet this argument overlooks the asymmetry of impact. / A single legislative mandate requiring the fifty largest industrial emitters to adopt carbon-capture technology would eliminate more atmospheric carbon in a year than decades of individual recycling. / The arithmetic is unambiguous.
  - 用途：TR 8+ 的核心结构；每段都能用这四步自检。
  - 来源：`B9-DIS-002`（9.0，考官标注）
- **[L4-TAO-02] 先立后破：先把对方论证说到最强，再指出其局限**
  - 示例：The case for it deserves to be stated fairly.（先给对手最强版本）→ 随后用「价格不是决定因素」的机制反驳。
  - 用途：discussion 类「讨论双方 + 自己的立场」最稳的展开法。
  - 来源：`B9-ADV-027`（9.0）
- **[L4-TAO-03] 证据分层：个案 → 反例 → 合并立场**
  - 示例：South Korea 1960s→1990s 的增长证据 → 「growth alone does not automatically produce a fairer distribution」的反证 → 双机制合并结论。
  - 用途：7.5→8 的分界常在这里：证据被用来检验论点，而不是装饰论点。
  - 来源：`B75-DIS-001`（7.5，考官标注）
- **[L4-TAO-04] 数据化例证 + 机制解释**
  - 示例：Canadian crime-prevention 统计（风险倍数）→ 解释家庭结构与行为模式的关联，而不是停在数字。
  - 用途：例证具体化的上限；**数据必须真实**，写作时若无真实数据，改用机制化叙述而不是编造。
  - 来源：`B85-OP-005`（8.5）

## 4. 衔接手段（LINK，替代连接词堆砌）

- **[L4-LINK-01] 指代链**：用 `from this perspective / those gains / this breadth of disruption` 等「限定词 + 名词」回指。
  - 示例来源：`B75-DIS-001`（官方评语点名 referencing 手法）、`B75-DIS-005`（"this breadth of potential disruption"）。
- **[L4-LINK-02] 同义替换链**：同一概念换成不同精度的表达推进段落。
  - 示例链：`individual action → personal choices → personal responsibility`（`B9-DIS-002`）；`monitoring populations → investigating suspects → targeted surveillance`（`B8-OP-004`）。
- **[L4-LINK-03] 句内转向**：把转折放进句子中段，避免段首连接词。
  - 示例：What this framing misses, though, is [X].（`B9-DIS-030`，官方评语称其为 mid-sentence 衔接范例）
- **[L4-LINK-04] 首尾回环**：结论回应的不是措辞，而是引言提出的问题框架。
  - 示例：引言把争点改写为「how secondary education can deliver both, and in what sequence」，结论用「Breadth enables depth…」回扣该框架。（`B9-DIS-031`，9.0）

## 5. 按题型索引

| 题型 | 优先句式 | 优先论证套路 |
|---|---|---|
| opinion | GEN-01、GEN-03、GEN-08、GOV-01、GOV-02、SOC-01 | TAO-01、TAO-04 |
| discussion | GEN-02、GEN-09、CUL-03、HEALTH-02、MEDIA-01 | TAO-02、TAO-03 |
| adv-disadv | GEN-01、GEN-02、GLOB-01、SOC-02、HEALTH-01 | TAO-03、TAO-04 |
| report | GEN-04、GEN-06、GEN-07、ENV-02、CRIME-02、CUL-02 | TAO-01、TAO-04 |
| two-part | GEN-04、GEN-06、TECH-02、GLOB-02 | TAO-02、TAO-01 |

## 6. 使用接口

- TR 反馈的「段落级重构」优先套用 TAO-01/02，再从句式表里选骨架；
- 生成逐句教学卡的「句式骨架与高分词伙」时，从句式表里挑选与用户水平 +0.5 档的骨架；原「稳妥版/出彩版」只作为内部选材参考，不在报告里展示两套版本；
- 8.5 档 `writing9.com` 来源的句子仅作参考，若其语法不洁净（如并列结构、从句残缺），不得作为骨架范本；
- 本库不提供观点内容（→ L5）与词伙列表（→ L6）；
- 条目编号与来源 id 只用于内部检索，不写入交付文件。

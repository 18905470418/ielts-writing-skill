# 题目解析库（审题要点）

> **层级**：增强项 · 题目解析（服务于「审题前置」）。
> **来源**：从训练集按题目聚类（模糊聚类 Jaccard≥0.75）后整理；每题给出真实样本 id。
> **加载时机**：评分流程最前端的「审题前置」：先按题目关键词/题型检索；未命中时现场生成审题要点并追加回本库。
> **覆盖**：训练集内出现 ≥3 篇的题目簇 56 个。

## 使用说明

1. 每条的「隐含限定」是 TR 的第一证据：未回应限定词时 TR 封顶 6.5（参见 `band-rules.md` L1-TR-6.3 / 65.3 / 75.3）。
2. 「常见审题失误」列出该题真实低档样本的覆盖缺口；反馈时对照用户作文逐项检查。
3. 「双边观点池」给出可展开维度与 L5 观点库入口；内部检索时保留 L5 编号，最终报告只写观点角度，不显示编号。
4. 运行时遇到库中未收录的题目：按同一格式现场生成（标注 `source: runtime-generated` 与日期）并追加。

## QB-001｜Some children spend hours every day on their smartphones. Why is this the case? Do you think this is a positive or a negative ...

- **指纹**：题型 two-part；主题 科技；样本 B6-ADV-027 等 7 篇
- **关键词圈定**：`children`, `spend`, `hours`, `smartphones`, `case`, `think`, `positive`
- **隐含限定**：children（对象限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——设问 1：Some children spend hours every day on their smartphones. Why is this the case；B——设问 2：Do you think this is a positive or a negative development。可展开维度见 L5 条目 TECH-01, TECH-02, TECH-03。
- **常见审题失误**：`B6-ADV-027`（6.0，关键词覆盖 33%）开头：「Nowadays, plenty of kids use their tablets and consoles every day for many hours. This statement means their parents do not care about their children.」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6·`B6-ADV-027`；7·`B7-ADV-024`；7·`B7-ADV-037`；8.5·`B85-ADV-033`；9·`B9-ADV-031`；9·`B9-ADV-032`；9·`B9-ADV-035`

## QB-002｜Some people believe that it is best to accept a bad situation, such as an unsatisfactory job or shortage of money. Others argue ...

- **指纹**：题型 discussion；主题 全球化与工作；样本 B6-DIS-015 等 7 篇
- **关键词圈定**：`people`, `believe`, `best`, `accept`, `situation`, `unsatisfactory`, `shortage`
- **隐含限定**：best（最优断言）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——Some people believe that it is best to accept a bad situation, such as an unsatisfactory job or shortage of money；B——题干后半部分的对立主张。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-DIS-015`；6·`B6-DIS-016`；6.5·`B65-DIS-026`；8.5·`B85-DIS-013`；8.5·`B85-DIS-016`；8.5·`B85-DIS-017`；8.5·`B85-DIS-034`

## QB-003｜In their advertising, businesses nowadays usually emphasize that their products are new in some ways. Why is this? Do you think ...

- **指纹**：题型 two-part；主题 媒体与广告；样本 B6-ADV-015 等 5 篇
- **关键词圈定**：`advertising`, `businesses`, `nowadays`, `emphasize`, `products`, `ways`, `think`
- **隐含限定**：positive/negative（评价方向）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——设问 1：In their advertising, businesses nowadays usually emphasize that their products are new in some ways. Why is this；B——设问 2：Do you think it is a positive or negative development。可展开维度见 L5 条目 MEDIA-01, MEDIA-03, MEDIA-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-ADV-015`；8·`B8-ADV-013`；8·`B8-ADV-014`；8.5·`B85-ADV-017`；9·`B9-ADV-020`

## QB-004｜in some countries, owning a home rather than renting one is very important for people. why might this be the case? what do you ...

- **指纹**：题型 two-part；主题 社会问题；样本 B6-OP-026 等 4 篇
- **关键词圈定**：`countries`, `owning`, `home`, `renting`, `important`, `people`, `case`
- **隐含限定**：in some countries（范围限定）；positive/negative（评价方向）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——设问 1：in some countries, owning a home rather than renting one is very important for people. why might this be the case；B——设问 2：what do you think this is a positive or negative situation。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-OP-026`；6.5·`B65-OP-016`；7·`B7-OP-029`；8.5·`B85-OP-019`

## QB-005｜The best way to provide enough homes in large cities is to build tall apartment blocks. To what extend do you agree or disagree ...

- **指纹**：题型 opinion；主题 社会问题；样本 B6-OP-068 等 4 篇
- **关键词圈定**：`best`, `provide`, `enough`, `homes`, `large`, `cities`, `build`
- **隐含限定**：best（最优断言）；all（全量）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-OP-068`；7·`B7-OP-075`；7.5·`B75-OP-060`；8·`B8-OP-061`

## QB-006｜The most important aim of science should be to improve people's lives. To what extent do you agree or disagree with this statement

- **指纹**：题型 opinion；主题 科技；样本 B6-OP-076 等 4 篇
- **关键词圈定**：`important`, `science`, `improve`, `people's`, `lives`, `extent`, `agree`
- **隐含限定**：most important（最高级）；should（规范性主张）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 TECH-01, TECH-02, TECH-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-OP-076`；7·`B7-OP-077`；7.5·`B75-OP-063`；8.5·`B85-OP-083`

## QB-007｜Many children today are overweight. This is a serious health issue. Give reasons for child obesity today and give solutions to ...

- **指纹**：题型 report；主题 健康；样本 B6-REP-011 等 4 篇
- **关键词圈定**：`children`, `today`, `overweight`, `serious`, `health`, `issue`, `give`
- **隐含限定**：children（对象限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 HEALTH-01, HEALTH-02, HEALTH-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-REP-011`；6·`B6-REP-014`；7.5·`B75-REP-017`；8·`B8-REP-012`

## QB-008｜The best way to reduce the number of traffic accidents is to raise the age limit for younger drivers and lower the age limit for ...

- **指纹**：题型 opinion；主题 社会问题；样本 B6-TQ-002 等 4 篇
- **关键词圈定**：`best`, `reduce`, `number`, `traffic`, `accidents`, `raise`, `limit`
- **隐含限定**：best（最优断言）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-TQ-002`；6·`B6-TQ-003`；6.5·`B65-TQ-010`；8·`B8-TQ-010`

## QB-009｜Surveillance cameras in banks, offices, shops and streets have been very successful in reducing crime in the workplace and ...

- **指纹**：题型 report；主题 全球化与工作；样本 B6-REP-025 等 4 篇
- **关键词圈定**：`surveillance`, `cameras`, `banks`, `offices`, `shops`, `streets`, `successful`
- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：`B6-REP-026`（6.0，关键词覆盖 40%）开头：「Nowadays, the use of surveillance cameras has become increasingly common in many countries. Although these devices can help reduce crime in public places and workplaces ...」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6·`B6-REP-025`；6·`B6-REP-026`；7.5·`B75-REP-025`；7.5·`B75-REP-028`

## QB-010｜Money is important for everyone, including young people, to save money for their future. To what extent do you agree or disagree ...

- **指纹**：题型 opinion；主题 社会问题；样本 B7-OP-034 等 4 篇
- **关键词圈定**：`money`, `important`, `everyone`, `including`, `young`, `people`, `save`
- **隐含限定**：young people（对象限定）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：7·`B7-OP-034`；7·`B7-OP-041`；8.5·`B85-OP-026`；8.5·`B85-OP-096`

## QB-011｜Some people think it is a good thing for senior managers to receive much higher salaries than other workers in a company. To what ...

- **指纹**：题型 opinion；主题 全球化与工作；样本 B7-OP-059 等 4 篇
- **关键词圈定**：`people`, `think`, `good`, `thing`, `senior`, `managers`, `receive`
- **隐含限定**：to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：7·`B7-OP-059`；7·`B7-OP-088`；7·`B7-OP-089`；8·`B8-OP-042`

## QB-012｜All university undergraduate courses should include a period of time spent studying abroad or doing a work placement. Do you ...

- **指纹**：题型 adv-disadv；主题 教育；样本 B6-ADV-001 等 3 篇
- **关键词圈定**：`university`, `undergraduate`, `courses`, `include`, `period`, `time`, `spent`
- **隐含限定**：all（全量）；should（规范性主张）；outweigh（比较结构）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 EDU-01, EDU-02, EDU-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-ADV-001`；6.5·`B65-ADV-006`；7.5·`B75-ADV-005`

## QB-013｜In some countries, the government pays for health care. In others, the individual must pay for their own health care. Discuss the ...

- **指纹**：题型 adv-disadv；主题 健康；样本 B6-ADV-010 等 3 篇
- **关键词圈定**：`countries`, `government`, `pays`, `health`, `care`, `individual`, `discuss`
- **隐含限定**：in some countries（范围限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 HEALTH-01, HEALTH-02, HEALTH-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-ADV-010`；7·`B7-ADV-010`；8·`B8-ADV-008`

## QB-014｜Some people believe that allowing children to make their own choices on everyday matters (such as foood, clothes and ...

- **指纹**：题型 discussion；主题 社会问题；样本 B6-DIS-012 等 3 篇
- **关键词圈定**：`people`, `believe`, `allowing`, `children`, `make`, `choices`, `everyday`
- **隐含限定**：only（排他限定）；children（对象限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——A 方：题干前半部分主张；B——B 方：题干后半部分主张。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：`B6-DIS-012`（6.0，关键词覆盖 41%）开头：「In contrast to previous generations, children today are granted greater freedom in making everyday decisions, such as what they eat and wear. Although some argue that ...」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6·`B6-DIS-012`；8·`B8-DIS-013`；8.5·`B85-DIS-014`

## QB-015｜Some people think that all university students should study whatever they like. Others believe that they should only be allowed ...

- **指纹**：题型 discussion；主题 教育；样本 B6-DIS-028 等 3 篇
- **关键词圈定**：`people`, `think`, `university`, `students`, `study`, `whatever`, `like`
- **隐含限定**：only（排他限定）；all（全量）；should（规范性主张）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——Some people think that all university students should study whatever they like；B——题干后半部分的对立主张。可展开维度见 L5 条目 EDU-01, EDU-02, EDU-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-DIS-028`；7·`B7-DIS-005`；7.5·`B75-DIS-038`

## QB-016｜Promotions to a higher level should be made from within the company rather than appointing a new person from outside. Do you ...

- **指纹**：题型 opinion；主题 全球化与工作；样本 B6-OP-040 等 3 篇
- **关键词圈定**：`promotions`, `higher`, `level`, `made`, `company`, `appointing`, `person`
- **隐含限定**：should（规范性主张）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-OP-040`；6.5·`B65-OP-048`；7·`B7-OP-048`

## QB-017｜A small number of global streaming companies now decide which films and television series are made. Do you think this is a ...

- **指纹**：题型 adv-disadv；主题 媒体与广告；样本 B65-ADV-001 等 3 篇
- **关键词圈定**：`small`, `number`, `global`, `streaming`, `companies`, `decide`, `films`
- **隐含限定**：all（全量）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 MEDIA-01, MEDIA-03, MEDIA-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-001`；7.5·`B75-ADV-001`；9·`B9-ADV-001`

## QB-018｜In many countries around the world, rural people are moving to cities, so the population in the countryside is decreasing. Do you ...

- **指纹**：题型 adv-disadv；主题 社会问题；样本 B65-ADV-002 等 3 篇
- **关键词圈定**：`countries`, `around`, `world`, `rural`, `people`, `moving`, `cities`
- **隐含限定**：in many countries（范围限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-002`；7.5·`B75-ADV-022`；8.5·`B85-ADV-006`

## QB-019｜In many countries, companies are employing fewer permanent staff and are using more short-term contractors and gig workers. Do ...

- **指纹**：题型 adv-disadv；主题 全球化与工作；样本 B65-ADV-010 等 3 篇
- **关键词圈定**：`countries`, `companies`, `employing`, `fewer`, `permanent`, `staff`, `using`
- **隐含限定**：in many countries（范围限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-010`；7.5·`B75-ADV-012`；9·`B9-ADV-008`

## QB-020｜In many countries, services that were once run by the state, such as prisons, railways and rubbish collection, are now operated ...

- **指纹**：题型 adv-disadv；主题 犯罪与法律；样本 B65-ADV-012 等 3 篇
- **关键词圈定**：`countries`, `services`, `state`, `prisons`, `railways`, `rubbish`, `collection`
- **隐含限定**：in many countries（范围限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 CRIME-01, CRIME-02, CRIME-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-012`；7.5·`B75-ADV-015`；9·`B9-ADV-011`

## QB-021｜Many developing countries have built their economies around large-scale international tourism. Do the advantages of this approach ...

- **指纹**：题型 adv-disadv；主题 全球化与工作；样本 B65-ADV-024 等 3 篇
- **关键词圈定**：`developing`, `countries`, `built`, `economies`, `around`, `large`, `scale`
- **隐含限定**：outweigh（比较结构）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-024`；7.5·`B75-ADV-024`；9·`B9-ADV-023`

## QB-022｜Some cities have made all public transport free to use, paying for it through taxation instead of fares. Do you think this is a ...

- **指纹**：题型 adv-disadv；主题 政府与公共政策；样本 B65-ADV-030 等 3 篇
- **关键词圈定**：`cities`, `made`, `public`, `transport`, `free`, `paying`, `through`
- **隐含限定**：all（全量）；positive/negative（评价方向）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 GOV-01, GOV-03, GOV-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-030`；7.5·`B75-ADV-029`；9·`B9-ADV-027`

## QB-023｜Some countries are considering reducing the standard working week from five days to four, with no reduction in pay. Do the ...

- **指纹**：题型 adv-disadv；主题 全球化与工作；样本 B65-ADV-031 等 3 篇
- **关键词圈定**：`countries`, `considering`, `reducing`, `standard`, `working`, `week`, `days`
- **隐含限定**：outweigh（比较结构）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-031`；7.5·`B75-ADV-030`；9·`B9-ADV-028`

## QB-024｜Some governments are moving ministries and other public bodies out of the capital city to smaller towns and regions. Do the ...

- **指纹**：题型 adv-disadv；主题 政府与公共政策；样本 B65-ADV-033 等 3 篇
- **关键词圈定**：`governments`, `moving`, `ministries`, `public`, `bodies`, `capital`, `city`
- **隐含限定**：outweigh（比较结构）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 GOV-01, GOV-03, GOV-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-033`；7.5·`B75-ADV-031`；9·`B9-ADV-029`

## QB-025｜Many people argue that individuals are responsible for addressing environmental problems, while others believe that governments ...

- **指纹**：题型 discussion；主题 环境；样本 B65-DIS-002 等 3 篇
- **关键词圈定**：`people`, `argue`, `individuals`, `responsible`, `addressing`, `environmental`, `problems`
- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。
- **双边观点池**：A——A 方：题干前半部分主张；B——B 方：题干后半部分主张。可展开维度见 L5 条目 ENV-01, ENV-02, ENV-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-DIS-002`；7.5·`B75-DIS-003`；9·`B9-DIS-002`

## QB-026｜Some people believe that the introduction of artificial intelligence and automation will lead to widespread unemployment and ...

- **指纹**：题型 discussion；主题 科技；样本 B65-DIS-004 等 3 篇
- **关键词圈定**：`people`, `believe`, `introduction`, `artificial`, `intelligence`, `automation`, `lead`
- **隐含限定**：always（全称）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——Some people believe that the introduction of artificial intelligence and automation will lead to widespread unemployment and social problems；B——others argue that technology has always created more jobs than it has destroyed. Discuss both views and give your own opinion.。可展开维度见 L5 条目 TECH-01, TECH-02, TECH-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-DIS-004`；7.5·`B75-DIS-005`；9·`B9-DIS-004`

## QB-027｜In some areas, libraries, parks and community centres that were once run by paid council staff are now managed by local ...

- **指纹**：题型 discussion；主题 社会问题；样本 B65-DIS-007 等 3 篇
- **关键词圈定**：`areas`, `libraries`, `parks`, `community`, `centres`, `paid`, `council`
- **隐含限定**：best（最优断言）；should（规范性主张）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——Some people believe this is the best way to keep such services open；B——others argue that local government should pay professionals to run them. Discuss both views and give your own opinion.。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-DIS-007`；7.5·`B75-DIS-010`；9·`B9-DIS-009`

## QB-028｜Many major museums hold objects that were removed from other countries in the past. Some people believe these objects should be ...

- **指纹**：题型 discussion；主题 文化与语言；样本 B65-DIS-013 等 3 篇
- **关键词圈定**：`major`, `museums`, `hold`, `objects`, `removed`, `countries`, `past`
- **隐含限定**：should（规范性主张）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——Some people believe these objects should be returned to their countries of origin；B——others argue they are better preserved and more widely seen where they are. Discuss both views and give your own opinion.。可展开维度见 L5 条目 CUL-01, CUL-02, CUL-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-DIS-013`；7.5·`B75-DIS-016`；9·`B9-DIS-012`

## QB-029｜Some schools teach children of all abilities together in the same class, while others divide students into groups according to ...

- **指纹**：题型 discussion；主题 教育；样本 B65-DIS-019 等 3 篇
- **关键词圈定**：`schools`, `teach`, `children`, `abilities`, `together`, `class`, `divide`
- **隐含限定**：all（全量）；children（对象限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——A 方：题干前半部分主张；B——B 方：题干后半部分主张。可展开维度见 L5 条目 EDU-01, EDU-02, EDU-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-DIS-019`；7.5·`B75-DIS-019`；9·`B9-DIS-018`

## QB-030｜News organisations sometimes publish stories that later turn out to be false. Some people believe that the law should require ...

- **指纹**：题型 opinion；主题 媒体与广告；样本 B65-OP-020 等 3 篇
- **关键词圈定**：`news`, `organisations`, `publish`, `stories`, `later`, `turn`, `false`
- **隐含限定**：should（规范性主张）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 MEDIA-01, MEDIA-03, MEDIA-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-OP-020`；7.5·`B75-OP-019`；9·`B9-OP-060`

## QB-031｜Some governments now fund university places only in subjects that lead directly to employment. To what extent do you agree or ...

- **指纹**：题型 opinion；主题 教育；样本 B65-OP-023 等 3 篇
- **关键词圈定**：`governments`, `fund`, `university`, `places`, `subjects`, `lead`, `directly`
- **隐含限定**：only（排他限定）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 EDU-01, EDU-02, EDU-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-OP-023`；7.5·`B75-OP-024`；9·`B9-OP-068`

## QB-032｜Some people argue that offenders who have committed non-violent crimes should serve their sentences in the community rather than ...

- **指纹**：题型 opinion；主题 犯罪与法律；样本 B65-OP-025 等 3 篇
- **关键词圈定**：`people`, `argue`, `offenders`, `committed`, `violent`, `crimes`, `serve`
- **隐含限定**：should（规范性主张）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 CRIME-01, CRIME-02, CRIME-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-OP-025`；7.5·`B75-OP-025`；9·`B9-OP-070`

## QB-033｜Some people believe that individual efforts to live more sustainably achieve nothing while governments fail to regulate polluting ...

- **指纹**：题型 opinion；主题 环境；样本 B65-OP-029 等 3 篇
- **关键词圈定**：`people`, `believe`, `individual`, `efforts`, `live`, `sustainably`, `achieve`
- **隐含限定**：to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 ENV-01, ENV-02, ENV-04。
- **常见审题失误**：`B65-OP-029`（6.5，关键词覆盖 37%）开头：「Nowadays, the climate change is one of the biggest problem in the world. Some people think that when a person try to live in a green way, it is useless, because the ...」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6.5·`B65-OP-029`；7.5·`B75-OP-028`；9·`B9-OP-075`

## QB-034｜Some people believe that private cars should be banned from the centres of large cities. To what extent do you agree or disagree?

- **指纹**：题型 opinion；主题 社会问题；样本 B65-OP-030 等 3 篇
- **关键词圈定**：`people`, `believe`, `private`, `cars`, `banned`, `centres`, `large`
- **隐含限定**：should（规范性主张）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-OP-030`；7.5·`B75-OP-029`；9·`B9-OP-078`

## QB-035｜Many manufactured food and drink products contain high levels of sugar, which causes many health problems. Sugary products should ...

- **指纹**：题型 opinion；主题 健康；样本 B65-OP-033 等 3 篇
- **关键词圈定**：`manufactured`, `food`, `drink`, `products`, `contain`, `high`, `levels`
- **隐含限定**：should（规范性主张）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 HEALTH-01, HEALTH-02, HEALTH-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-OP-033`；7·`B7-OP-038`；9·`B9-OP-050`

## QB-036｜Some people think that children should not be allowed to own a smartphone until they start secondary school. To what extent do ...

- **指纹**：题型 opinion；主题 科技；样本 B65-OP-035 等 3 篇
- **关键词圈定**：`people`, `think`, `children`, `allowed`, `smartphone`, `start`, `secondary`
- **隐含限定**：children（对象限定）；should（规范性主张）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 TECH-01, TECH-02, TECH-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-OP-035`；7.5·`B75-OP-034`；9·`B9-OP-084`

## QB-037｜Some people argue that primary schools focus too much on formal learning. To what extent do you agree with this opinion? How ...

- **指纹**：题型 opinion；主题 教育；样本 B65-OP-054 等 3 篇
- **关键词圈定**：`people`, `argue`, `primary`, `schools`, `focus`, `formal`, `learning`
- **隐含限定**：children（对象限定）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 EDU-01, EDU-02, EDU-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-OP-054`；7·`B7-OP-050`；8·`B8-OP-035`

## QB-038｜Fraud committed over the internet has increased significantly in recent years. Why has this type of crime become so common? What ...

- **指纹**：题型 report；主题 犯罪与法律；样本 B65-REP-001 等 3 篇
- **关键词圈定**：`fraud`, `committed`, `internet`, `increased`, `significantly`, `recent`, `years`
- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 CRIME-01, CRIME-02, CRIME-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-REP-001`；7.5·`B75-REP-002`；9·`B9-REP-002`

## QB-039｜In many communities, local charities and clubs are finding it increasingly difficult to recruit volunteers. Why is this ...

- **指纹**：题型 report；主题 社会问题；样本 B65-REP-002 等 3 篇
- **关键词圈定**：`communities`, `local`, `charities`, `clubs`, `finding`, `increasingly`, `difficult`
- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-REP-002`；7.5·`B75-REP-003`；9·`B9-REP-003`

## QB-040｜In many countries, a high proportion of young people who are released from prison commit further offences within a short period. ...

- **指纹**：题型 report；主题 犯罪与法律；样本 B65-REP-005 等 3 篇
- **关键词圈定**：`countries`, `high`, `proportion`, `young`, `people`, `released`, `prison`
- **隐含限定**：in many countries（范围限定）；young people（对象限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 CRIME-01, CRIME-02, CRIME-03。
- **常见审题失误**：`B65-REP-005`（6.5，关键词覆盖 39%）开头：「It is a fact that many young criminals are committing the crime again very soon after they are released from the prison. This is a serious problem for the society and in ...」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6.5·`B65-REP-005`；7.5·`B75-REP-004`；9·`B9-REP-004`

## QB-041｜In many large cities, ordinary working people can no longer afford to live near the places where they work. Why has this ...

- **指纹**：题型 report；主题 全球化与工作；样本 B65-REP-009 等 3 篇
- **关键词圈定**：`large`, `cities`, `ordinary`, `working`, `people`, `longer`, `afford`
- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-REP-009`；7.5·`B75-REP-008`；9·`B9-REP-008`

## QB-042｜In many societies, a growing number of older people live alone and have little regular contact with others. What are the causes ...

- **指纹**：题型 report；主题 社会问题；样本 B65-REP-010 等 3 篇
- **关键词圈定**：`societies`, `growing`, `number`, `older`, `people`, `live`, `alone`
- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：`B65-REP-010`（6.5，关键词覆盖 40%）开头：「In the modern society, a lot of old people are living alone and they are feeling very lonely because they do not have the contact with the other people. This is a ...」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6.5·`B65-REP-010`；7.5·`B75-REP-009`；9·`B9-REP-009`

## QB-043｜Many countries invest heavily in training doctors, engineers and other skilled professionals, only for large numbers of them to ...

- **指纹**：题型 report；主题 健康；样本 B65-REP-012 等 3 篇
- **关键词圈定**：`countries`, `invest`, `heavily`, `training`, `doctors`, `engineers`, `skilled`
- **隐含限定**：only（排他限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 HEALTH-01, HEALTH-02, HEALTH-04。
- **常见审题失误**：`B65-REP-012`（6.5，关键词覆盖 44%）开头：「In many developing countries, the government is spending a lot of money for the education of the doctors and engineers, but after the graduation these people are leaving ...」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6.5·`B65-REP-012`；7.5·`B75-REP-012`；9·`B9-REP-015`

## QB-044｜People in many countries now depend heavily on their smartphones. Why has this happened? What effects does this dependence have ...

- **指纹**：题型 report；主题 科技；样本 B65-REP-015 等 3 篇
- **关键词圈定**：`people`, `countries`, `depend`, `heavily`, `smartphones`, `happened`, `effects`
- **隐含限定**：in many countries（范围限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 TECH-01, TECH-02, TECH-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-REP-015`；7.5·`B75-REP-016`；9·`B9-REP-019`

## QB-045｜Large quantities of plastic waste end up in the world's oceans every year. What do you think are the main reasons for this, and ...

- **指纹**：题型 two-part；主题 环境；样本 B65-TQ-003 等 3 篇
- **关键词圈定**：`large`, `quantities`, `plastic`, `waste`, `world's`, `oceans`, `year`
- **隐含限定**：the main（主因/主渠道）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——设问 1：题干第一个问题；B——设问 2：题干第二个问题。可展开维度见 L5 条目 ENV-01, ENV-02, ENV-04。
- **常见审题失误**：`B65-TQ-003`（6.5，关键词覆盖 39%）开头：「It is true that a huge amount of the plastic waste is going to the ocean every year and this is a very serious problem for our planet. In this essay, I am going to ...」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6.5·`B65-TQ-003`；7.5·`B75-TQ-003`；9·`B9-TQ-002`

## QB-046｜Traditional crafts such as weaving, pottery and woodcarving are dying out in many parts of the world. Why is this happening? Do ...

- **指纹**：题型 two-part；主题 文化与语言；样本 B65-TQ-007 等 3 篇
- **关键词圈定**：`traditional`, `crafts`, `weaving`, `pottery`, `woodcarving`, `dying`, `parts`
- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。
- **双边观点池**：A——设问 1：Traditional crafts such as weaving, pottery and woodcarving are dying out in many parts of the world. Why is this happening；B——设问 2：Do you think it is important to keep these skills alive。可展开维度见 L5 条目 CUL-01, CUL-02, CUL-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-TQ-007`；7.5·`B75-TQ-010`；9·`B9-TQ-005`

## QB-047｜Nowadays many people choose to be self-employed, rather than to work for a company or organisation. Why might this be the case? ...

- **指纹**：题型 adv-disadv；主题 全球化与工作；样本 B7-ADV-020 等 3 篇
- **关键词圈定**：`nowadays`, `people`, `choose`, `self`, `employed`, `work`, `company`
- **隐含限定**：无明显绝对词；注意范围词（in some countries / 对象限定）与题干动词的强度。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：7·`B7-ADV-020`；8.5·`B85-ADV-031`；9·`B9-ADV-025`

## QB-048｜Governments should spend money on railways rather than roads. To what extent do you agree or disagree with this statement?

- **指纹**：题型 opinion；主题 政府与公共政策；样本 B7-OP-026 等 3 篇
- **关键词圈定**：`governments`, `spend`, `money`, `railways`, `roads`, `extent`, `agree`
- **隐含限定**：should（规范性主张）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 GOV-01, GOV-03, GOV-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：7·`B7-OP-026`；8·`B8-OP-005`；8.5·`B85-OP-013`

## QB-049｜Some people believe that unpaid community service should be a compulsory part of high school programmers (for example working for ...

- **指纹**：题型 opinion；主题 社会问题；样本 B75-OP-051 等 3 篇
- **关键词圈定**：`people`, `believe`, `unpaid`, `community`, `service`, `compulsory`, `part`
- **隐含限定**：children（对象限定）；should（规范性主张）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 SOC-01, SOC-04, SOC-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：7.5·`B75-OP-051`；8·`B8-OP-064`；8.5·`B85-OP-056`

## QB-050｜People who decide on a career path early in their lives and keep to it are more likely to have a satisfying working life than ...

- **指纹**：题型 opinion；主题 全球化与工作；样本 B8-OP-031 等 3 篇
- **关键词圈定**：`people`, `decide`, `career`, `path`, `early`, `lives`, `keep`
- **隐含限定**：to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：8·`B8-OP-031`；8.5·`B85-OP-049`；9·`B9-OP-063`

## QB-051｜Some people think that parents should teach their children how to be good members of society. Others, however, believe that ...

- **指纹**：题型 discussion；主题 教育；样本 B6-DIS-033 等 3 篇
- **关键词圈定**：`people`, `think`, `parents`, `teach`, `children`, `good`, `members`
- **隐含限定**：best（最优断言）；children（对象限定）；should（规范性主张）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——Some people think that parents should teach their children how to be good members of society；B——题干后半部分的对立主张。可展开维度见 L5 条目 EDU-01, EDU-02, EDU-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6·`B6-DIS-033`；6·`B6-DIS-044`；7·`B7-DIS-047`

## QB-052｜Even though globalization affects the world’s economies in a very positive way, its negative side should not be forgotten. ...

- **指纹**：题型 opinion；主题 全球化与工作；样本 B6-OP-005 等 3 篇
- **关键词圈定**：`globalization`, `affects`, `world’s`, `economies`, `positive`, `negative`, `side`
- **隐含限定**：should（规范性主张）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 GLOB-01, GLOB-03, GLOB-05。
- **常见审题失误**：`B6-OP-083`（6.0，关键词覆盖 38%）开头：「Everything has two sides and the globalization is not the exception. Our first thoughts about this topic include the process of global “McDonaldisation” and, generally ...」——低覆盖预警（未必跑题，须人工复核限定词与设问的回应情况）。
- **样本分布**：6·`B6-OP-005`；6·`B6-OP-083`；8·`B8-OP-015`

## QB-053｜In the future, all cars, buses, and trucks will be driverless. The only people travelling inside these vehicles will be ...

- **指纹**：题型 adv-disadv；主题 科技；样本 B65-ADV-028 等 3 篇
- **关键词圈定**：`future`, `cars`, `buses`, `trucks`, `driverless`, `people`, `travelling`
- **隐含限定**：only（排他限定）；all（全量）；outweigh（比较结构）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——收益方（advantages / positive）；B——成本方（disadvantages / negative）。可展开维度见 L5 条目 TECH-01, TECH-02, TECH-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：6.5·`B65-ADV-028`；8.5·`B85-ADV-014`；8.5·`B85-ADV-015`

## QB-054｜The most important aim of science should be to improve people's lives. To what extent do you agree or disagree with this ...

- **指纹**：题型 opinion；主题 科技；样本 B75-OP-064 等 3 篇
- **关键词圈定**：`important`, `science`, `improve`, `people's`, `lives`, `extent`, `agree`
- **隐含限定**：most important（最高级）；should（规范性主张）；to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 TECH-01, TECH-02, TECH-03。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：7.5·`B75-OP-064`；8.5·`B85-OP-084`；8.5·`B85-OP-085`

## QB-055｜Many young people leave school with negative attitudes towards learning. What are the causes？How to encourage young people to ...

- **指纹**：题型 report；主题 教育；样本 B75-REP-020 等 3 篇
- **关键词圈定**：`young`, `people`, `leave`, `school`, `negative`, `attitudes`, `towards`
- **隐含限定**：young people（对象限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——原因 / 问题机制；B——措施 / 建议。可展开维度见 L5 条目 EDU-01, EDU-02, EDU-04。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：7.5·`B75-REP-020`；9·`B9-REP-018`；9·`B9-REP-024`

## QB-056｜In the future, nobody will buy printed newspapers or books because they will be able to read everything they want online without ...

- **指纹**：题型 opinion；主题 媒体与广告；样本 B85-OP-021 等 3 篇
- **关键词圈定**：`future`, `nobody`, `printed`, `newspapers`, `books`, `able`, `read`
- **隐含限定**：to what extent（程度限定）。逐项检查用户文是否显式回应；`best/only/most` 需要比较或排他性论证。
- **双边观点池**：A——支持题干主张；B——反对或限定题干主张（有条件同意）。可展开维度见 L5 条目 MEDIA-01, MEDIA-03, MEDIA-05。
- **常见审题失误**：（本簇低档样本未检出「低覆盖 + 低分」组合，未列真实偏题案例；以限定词逐项核对为准。）
- **样本分布**：8.5·`B85-OP-021`；8.5·`B85-OP-022`；8.5·`B85-OP-095`


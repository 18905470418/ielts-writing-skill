# L3 错误模式统计摘要（6–7.5 vs 8+）

> 中档样本（6–7.5）：676 篇；高分样本（8+）：510 篇。
> 命中率 = 命中篇数 / 该组篇数。示例优先取中档样本。

| 模式 | 模块 | 中档命中率 | 高分命中率 | 差值 | 负迁移 |
|---|---|---:|---:|---:|---|
| 模板化开头 (`TR-template-opening`) | TR | 17.9% | 13.1% | +4.8% | 是 |
| 例证停留在常识层 (`TR-generic-example`) | TR | 1.5% | 0.8% | +0.7% | 否 |
| 连接词机械化 (`CC-mechanical-connectors`) | CC | 52.2% | 35.5% | +16.7% | 是 |
| 连续短句堆叠 (`CC-short-sentence-run`) | CC | 6.5% | 3.9% | +2.6% | 否 |
| 指代断裂 (`CC-dangling-reference`) | CC | 32.7% | 21.2% | +11.5% | 否 |
| 搭配错误：learn knowledge (`LR-unlearn-knowledge`) | LR | 0.0% | 0.2% | -0.2% | 是 |
| 搭配错误：多余介词 (`LR-verb-prep`) | LR | 0.3% | 0.2% | +0.1% | 是 |
| 词汇贫乏：very + 形容词 (`LR-vague-intensifier`) | LR | 5.8% | 1.2% | +4.6% | 否 |
| 语域不当：a lot of (`LR-a-lot-of`) | LR | 14.6% | 10.0% | +4.6% | 否 |
| 重复用词：more and more (`LR-more-and-more`) | LR | 2.1% | 3.3% | -1.3% | 否 |
| 重复用词：people (`LR-people-overuse`) | LR | 6.8% | 2.0% | +4.8% | 否 |
| 从句误用：although ... but (`GRA-although-but`) | GRA | 0.1% | 0.2% | -0.0% | 是 |
| there be 滥用 (`GRA-there-be`) | GRA | 4.1% | 3.7% | +0.4% | 是 |
| 主谓一致 (`GRA-sva`) | GRA | 5.3% | 5.3% | +0.0% | 是 |
| 不可数名词复数化 (`GRA-countability`) | GRA | 0.7% | 0.6% | +0.2% | 是 |
| one of the + 单数 (`GRA-one-of`) | GRA | 0.9% | 0.0% | +0.9% | 是 |
| run-on 句 (`GRA-run-on`) | GRA | 4.1% | 6.3% | -2.1% | 否 |
| 标点：逗号粘连 (`GRA-comma-splice`) | GRA | 2.5% | 5.9% | -3.4% | 否 |

## 模板化开头 (`TR-template-opening`)

- 触发信号：开头使用可套用任何题目的万能句（in this modern era / with the development of ...）
- 修复策略：把万能句换成对本题具体概念的重述：点出争议点 + 双方立场 + 自己的回应方向。
- 中档命中：121/676（17.9%）；高分命中：67/510（13.1%）
  - `B6-ADV-001`（6.0）: “In this modern era, it is undeniable that education plays an important role in human development.”
  - `B6-ADV-004`（6.0）: “In this modern era, it is undeniable that the developed countries have a large number of youngsters compared to older people.”
  - `B6-ADV-008`（6.0）: “First and foremost, people can work to a high degree, with a high income.”
  - `B6-ADV-010`（6.0）: “In some nations,the government is responsible for covering healthcare costs,whereas in others,individuals must may pay for their own medical treatment.This essay will discuss the benefits and drawbacks of both systems.”
  - `B6-ADV-011`（6.0）: “This essay will discuss both sides of this idea.”
  - `B6-ADV-014`（6.0）: “In a nutshell, the advantages of pursuing education in other countries outweigh the disadvantages.”

## 例证停留在常识层 (`TR-generic-example`)

- 触发信号：例证只有 for example, many people ... 式泛化，没有具体主体、场景或数据
- 修复策略：给例证加上具体主体与情境（谁、在哪里、什么条件下发生了变化），并解释它如何证明论点。
- 中档命中：10/676（1.5%）；高分命中：4/510（0.8%）
  - `B6-DIS-029`（6.0）: “For instance, many countries introduced modern teaching methods, which have helped students by improving their academic performance and communication skills.”
  - `B6-REP-004`（6.0）: “For example, many students study science because they are iinterest in science but they work on the business area .”
  - `B65-DIS-025`（6.5）: “For example, some people have a large wedding party even though they do not have enough savings.”
  - `B65-OP-064`（6.5）: “For instance, many children in Indonesia attend kindergarten at the age of five, where they learn basic letters, numbers, and social skills through structured activities.”
  - `B7-ADV-017`（7.0）: “For instance, many people began looking for remote jobs during and after the COVID-19 pandemic, especially parents and those who have long commutes.”
  - `B7-ADV-019`（7.0）: “For example, many countries around the world consider the population of youths as a power point and provide free scholarships overseas to educate their next generation.”

## 连接词机械化 (`CC-mechanical-connectors`)

- 触发信号：段落开头反复 Firstly / Secondly / Moreover；显性连接词密度过高且集中在段首
- 修复策略：删除可由语义自然衔接的连接词，用指代链与同义替换推进（this policy / such measures / that shift）。
- 中档命中：353/676（52.2%）；高分命中：181/510（35.5%）
  - `B6-ADV-001`（6.0）: “On the one hand”
  - `B6-ADV-002`（6.0）: “On the one hand”
  - `B6-ADV-003`（6.0）: “On the one hand”
  - `B6-ADV-005`（6.0）: “On the one hand”
  - `B6-ADV-006`（6.0）: “On the other hand”
  - `B6-ADV-009`（6.0）: “On the other hand”

## 连续短句堆叠 (`CC-short-sentence-run`)

- 触发信号：连续 3 句以上均为 12 词以内的短句，句间无明确逻辑推进
- 修复策略：把关系最近的短句合并为从句或分词结构，或补一句解释句说明前句的意义。
- 中档命中：44/676（6.5%）；高分命中：20/510（3.9%）
  - `B6-ADV-009`（6.0）: “Some people think it has advantages, while others believe it has disadvantages. In this essay, I believe that the advantages outweigh the disadvantages. There are several advantages of planting fruit and vegetables.”
  - `B6-ADV-018`（6.0）: “In society, life has changed a great deal, especially in the leader. This includes how the leaders are changed. Some positive people believe that the development leader is common.”
  - `B6-ADV-020`（6.0）: “This includes how people live. Some people believe that the small family is common. However, others believe that the large family is difficult.”
  - `B6-ADV-033`（6.0）: “This essay will examine the advantages and the disadvantages of the Internet. There are multiple advantages to the internet. First, it is useful for communication.”
  - `B6-ADV-034`（6.0）: “Society has undergone massive changes, and a big reason is technology. The internet has changed the way people live. It is a tremendous invention which has shaped the world.”
  - `B6-ADV-040`（6.0）: “There are many advantages of transferring money online. First, it saves time. People do not need to go to a bank to send money.”

## 指代断裂 (`CC-dangling-reference`)

- 触发信号：句首 this/they/it 指代前文不明确或跨段跳跃
- 修复策略：把代词换成具体名词（this policy / these conditions），或补一个限定短语明确指向。
- 中档命中：221/676（32.7%）；高分命中：108/510（21.2%）
  - `B6-ADV-002`（6.0）: “This is mainly because organisations still need to complete the same amount of work within a shorter working week.”
  - `B6-ADV-010`（6.0）: “This is because everyone has access to medical treatment, meaning that chronic illnesses and diseases can be diagnosed and treated early.Nevertheless, this system often results in long waiting times, which can be ...”
  - `B6-ADV-011`（6.0）: “This can help children develop a positive attitude towards their future.”
  - `B6-ADV-012`（6.0）: “This makes the travel more comfortable.”
  - `B6-ADV-013`（6.0）: “This is because they spent their age in a specific role in the same institution.”
  - `B6-ADV-015`（6.0）: “This is mainly because companies need to compete with others and attract customers’ attention through short advertisements.”

## 搭配错误：learn knowledge (`LR-unlearn-knowledge`)

- 触发信号：learn knowledge / study knowledge（中文『学习知识』直译）
- 修复策略：acquire / gain / obtain knowledge。
- 中档命中：0/676（0.0%）；高分命中：1/510（0.2%）
  - `B9-OP-069`（9.0）: “Besides learning knowledge, schools provide other basic educational resources to children in my opinion.”

## 搭配错误：多余介词 (`LR-verb-prep`)

- 触发信号：discuss about / emphasize on / mention about / research about 等动词冗余介词
- 修复策略：删去多余介词：discuss sth / emphasise sth / mention sth / research sth。
- 中档命中：2/676（0.3%）；高分命中：1/510（0.2%）
  - `B6-OP-008`（6.0）: “The main idea of teaching a financial subject must be to explain about a balanced budget and that debt could ruins one’s future.”
  - `B65-ADV-003`（6.5）: “Firstly, let me discuss about the advantages.”
  - `B85-OP-031`（8.5）: “In this essay, I will discuss about about this change and its impact on student life.”

## 词汇贫乏：very + 形容词 (`LR-vague-intensifier`)

- 触发信号：very important / very big / very good 等高密度模糊强化
- 修复策略：换成精确形容词（crucial / pivotal / substantial / detrimental），或直接用量化信息替代。
- 中档命中：39/676（5.8%）；高分命中：6/510（1.2%）
  - `B6-ADV-004`（6.0）: “To illustrate, these days, everything is based on technology , and adults are very good with technology because they started using it in their childhood.”
  - `B6-DIS-038`（6.0）: “First, it is very easy and cheap.”
  - `B6-OP-010`（6.0）: “The second reason that a big salary is very important is for family security.”
  - `B6-OP-017`（6.0）: “If the nations wants to be progressive it is very important that the people are more educated and progressive.”
  - `B6-OP-026`（6.0）: “However, although buying a home is very important, I believe that this is a negative situation.”
  - `B6-OP-035`（6.0）: “Despite this, it may be very difficult to garner the support needed to pass such a bill in Congress.”

## 语域不当：a lot of (`LR-a-lot-of`)

- 触发信号：学术语域中反复使用 a lot of / lots of / kids / stuff 等口语表达
- 修复策略：a considerable number of / numerous / children / material 等学术表达。
- 中档命中：99/676（14.6%）；高分命中：51/510（10.0%）
  - `B6-ADV-003`（6.0）: “Firstly, it costs people a lot of money to begin college in foreign countries.”
  - `B6-ADV-007`（6.0）: “Another contributing factor to mention is that smartphones contain a lot of entertainment content.”
  - `B6-ADV-012`（6.0）: “In addition, people can save a lot of time while traveling.”
  - `B6-ADV-026`（6.0）: “For instance, last year, one of my friends bought a lot of food items without realising he had spent his budget for two months, so he needed to take a loan from a bank.”
  - `B6-ADV-027`（6.0）: “Nowadays, plenty of kids use their tablets and consoles every day for many hours.”
  - `B6-ADV-033`（6.0）: “As well, it wastes a lot of time.”

## 重复用词：more and more (`LR-more-and-more`)

- 触发信号：more and more 反复出现，且全文重复使用同一名词
- 修复策略：an increasing number of / a growing proportion of / rising。
- 中档命中：14/676（2.1%）；高分命中：17/510（3.3%）
  - `B6-ADV-008`（6.0）: “To sum up, in many countries, more and more people want to study at universities.”
  - `B6-ADV-019`（6.0）: “Nowadays, globalisation of fashion has become more and more prevalent among youths in the majority of countries.”
  - `B65-ADV-003`（6.5）: “These days, more and more students are going to the foreign countries for completing their university degree instead of studying in their own country.”
  - `B65-ADV-054`（6.5）: “In recent years, there has been an ongoing debate regarding whether more and more people use robots to do tasks at home and in the workplace.”
  - `B65-ADV-055`（6.5）: “Places such as the Sahara desert of the Antarctic are visited more and more.”
  - `B7-ADV-016`（7.0）: “Nowadays, more and more individuals living in large cities are living alone or in small families instead of big families .In this essay, I will be discussing why I strongly believe that it is a positive development.”

## 重复用词：people (`LR-people-overuse`)

- 触发信号：people 在全文出现次数过多，缺少同义替换（individuals / citizens / residents / the public）
- 修复策略：按语境替换为 individuals / citizens / residents / employees / the public。
- 中档命中：46/676（6.8%）；高分命中：10/510（2.0%）

## 从句误用：although ... but (`GRA-although-but`)

- 触发信号：although/though 与 but 在同一句连用（中文『虽然……但是……』负迁移）
- 修复策略：二选一：Although X, Y. / X, but Y。
- 中档命中：1/676（0.1%）；高分命中：1/510（0.2%）
  - `B7-TQ-003`（7.0）: “Thirdly, although sharing wealth with poorer nations is very necessary but this help should only stop at providing such things as food, medicine and education.”
  - `B85-TQ-006`（8.5）: “Besides, even though they have excellent remunerations, but, they are still paying for the equipment that they need for work.”

## there be 滥用 (`GRA-there-be`)

- 触发信号：there is/are 反复使用，且多为无信息量的存在句
- 修复策略：改写成实义主语结构：Many governments face ... / This trend produces ...。
- 中档命中：28/676（4.1%）；高分命中：19/510（3.7%）
  - `B6-ADV-003`（6.0）: “First, students can choose more suitable education methods for themselves because there are more options.”
  - `B6-ADV-008`（6.0）: “There are some downsides to studying at universities.”
  - `B6-ADV-018`（6.0）: “Although there are many positive tips, there are many mistake.”
  - `B6-ADV-020`（6.0）: “On the one hand, in terms of the advantages, according to the primary view, according to the given information, there are many significant benefits.”
  - `B6-ADV-033`（6.0）: “There are multiple advantages to the internet.”
  - `B6-ADV-036`（6.0）: “There is an ongoing debate among people about whether television is good or not.”

## 主谓一致 (`GRA-sva`)

- 触发信号：复数主语 + is/was/has/does、第三人称单数主语 + are/were/have/do
- 修复策略：主谓一致：People are / The government has / They have / It is。
- 中档命中：36/676（5.3%）；高分命中：27/510（5.3%）
  - `B6-ADV-019`（6.0）: “If it were not for this globalisation, more Myanmar traditional costumes would still be seen in public places of our country.”
  - `B6-DIS-024`（6.0）: “Riding a bicycle for transportation to a specific place for other people is a good idea.”
  - `B6-DIS-045`（6.0）: “In recent years, pursuing higher education in foreign countries has become increasingly common.”
  - `B6-OP-008`（6.0）: “In many countries the discussion about the rising financial problems of young people has been getting more emphasis.”
  - `B6-OP-028`（6.0）: “It is often argued that providing university places for a high proportion of young people is unnecessary.”
  - `B6-REP-003`（6.0）: “All in all, the increase in processed milk consumption for children is projected as the primary cause of childhood obesity and preparation from the early stage of pregnancy is needed, so the parents can still provide ...”

## 不可数名词复数化 (`GRA-countability`)

- 触发信号：informations / advices / equipments / knowledges / researches / evidences 等
- 修复策略：information / advice / equipment / knowledge / research / evidence（不可数）。
- 中档命中：5/676（0.7%）；高分命中：3/510（0.6%）
  - `B6-DIS-041`（6.0）: “In conclusion, as we mentioned before, both views displayed a reseanable evidences to their claim, including looking to develop personality and gain mastery.”
  - `B6-OP-005`（6.0）: “They are the poorer countries that are not connected to the people globally and their people are unskilled due to the lack of knowledge and equipments .”
  - `B65-ADV-025`（6.5）: “People should use social media carefully and also check other informations before they choose the destination.”
  - `B65-DIS-005`（6.5）: “In addition, almost all of the scientific researches are published in English, so the scientists from all over the world can read them and share the knowledge.”
  - `B65-REP-001`（6.5）: “In this essay I will discuss the reasons of this increasing and I will give some advices for the people to protect themselves.”
  - `B8-ADV-019`（8.0）: “Firstly, museums will have money to operate which covers their business overhead such as personnel cost, equipments , electricity and water bills.”

## one of the + 单数 (`GRA-one-of`)

- 触发信号：one of the + 单数名词（one of the reason）
- 修复策略：one of the + 复数名词（one of the reasons）。
- 中档命中：6/676（0.9%）；高分命中：0/510（0.0%）
  - `B6-ADV-018`（6.0）: “This is due to many clear reasons. second, The smart educational method is one of the common reason.”
  - `B65-DIS-003`（6.5）: “The climate change is one of the biggest problem in the world today, so all of the countries are trying to reduce the carbon emissions.”
  - `B65-OP-029`（6.5）: “Nowadays, the climate change is one of the biggest problem in the world.”
  - `B65-OP-034`（6.5）: “This is one of the reason of the childhood obesity which is increasing in many countries.”
  - `B65-REP-008`（6.5）: “Firstly, one of the main reason is the fast food.”
  - `B65-REP-013`（6.5）: “One of the main reason is that the doctors do not have enough time.”

## run-on 句 (`GRA-run-on`)

- 触发信号：单句超过 45 词、含多个并列谓词却只用逗号连接
- 修复策略：按意群拆分，或补上从属连词/分号建立层级。
- 中档命中：28/676（4.1%）；高分命中：32/510（6.3%）
  - `B6-ADV-010`（6.0）: “In conclusion,both government-dundee and privately-funded healthcare systems have their own pros and cons.While covering for medicine promotes equality and accessibility,self-funded services provide faster services.From ...”
  - `B6-ADV-035`（6.0）: “In Japan, a lot of students and young workers take out their breakfast or lunch from McDonald's because the company offers various set menus, hamburgers and appetisers with a cup of coffee or tea, ranging from 500 yen ...”
  - `B6-DIS-014`（6.0）: “For example, if a person is stuck in a similar situation as above but their financial situation is much better, they must take action to improve the situation and learn some skills to acquire a better earning job, they ...”
  - `B6-DIS-016`（6.0）: “In conclusion, change should be gradual and well planned rather than an impulsive decision that creates more problems, for instance, someone who develops new skills or improves their circumstances is often better ...”
  - `B6-DIS-029`（6.0）: “Firstly, many people believe that students should spend more time on academic subjects.The primary reason is that academic subjects are more important for higher education and future careers.This can be explained by the ...”
  - `B6-DIS-045`（6.0）: “Currency exchange disparities and high tuition fees frequently force students to take on demanding part-time jobs alongside their studies, which can adversely affect their academic performance. ​In conclusion, although ...”

## 标点：逗号粘连 (`GRA-comma-splice`)

- 触发信号：逗号连接两个独立句且用 however/therefore 作连接词（缺分号或另起句）
- 修复策略：; however, ... / . Therefore, ...。
- 中档命中：17/676（2.5%）；高分命中：30/510（5.9%）
  - `B6-ADV-031`（6.0）: “Employers, however, must remain vigilant about their employees' well-being and should foster an environment where workers feel supported and connected, thus preventing feelings of isolation.”
  - `B6-DIS-015`（6.0）: “Advocates of active change, however, contend that most difficulties, however entrenched, admit at least partial improvement, and that resignation forecloses possibilities that effort might otherwise realise.”
  - `B6-OP-036`（6.0）: “I partly agree with this statement , as people should be aware of their own history and culture , and it helps to preserve history and heritage, however they should not exclude foreign historical works, as it helps to ...”
  - `B6-REP-019`（6.0）: “For example, if a country introduces a new TV channel, especially in terms of technology, people can receive useful knowledge about the drawbacks of using phones at night, thus avoiding the use of such devices.”
  - `B6-REP-029`（6.0）: “This would benefit a reduced number of cars during peak hours and, therefore less sources of gas emissions concentrated at the same time and place.”
  - `B65-ADV-034`（6.5）: “Employers, however, must remain vigilant about their employees' well-being and should foster an environment where workers feel supported and connected, thus preventing feelings of isolation.”


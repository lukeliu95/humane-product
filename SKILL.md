---
name: humane-product
description: "Use when building or changing a product, tool, feature, or app screen that real people operate and the result must not feel AI-made: 做产品、做小工具、做功能、改界面时要去 AI 味、符合人的操作习惯。The caller layer on top of impeccable: locks intent with an 意图卡 and 不做清单 before any UI code, stops the AI from adding filters, fields, menus or terms nobody asked for, hands visual craft and implementation to impeccable, then checks interaction AI smell and runs real-task walkthroughs (任务走查、验收) and writes conclusions back to a ledger. Not for marketing landing pages, slide decks, pure visual tweaks such as colors, fonts or spacing (call impeccable directly), backend-only work, or translation."
---

# humane-product

impeccable 管"做得好不好看"。这个 skill 管另外三件事：**AI 别自作主张**、**交互别像机器**、**做完让人试过**。

它是 impeccable 的调用方：视觉和实现一律交给 impeccable，本 skill 不另立视觉规则（两套视觉规则一起跑会互相打架）。**impeccable 是必需的基础 skill。** `<本skill目录>` 指这个 SKILL.md 所在的文件夹。

## 先分清是哪种活

| 情况 | 走哪条 |
|---|---|
| 新产品、新页面、新流程、新功能 | 全流程，下面 0～6 |
| 改已有功能 | 轻流程：0 → fence 检查 → 一次只改一类 → 5 → 6 |
| 只要评审、检查、诊断 | 只读：只做第 5 步，出报告，不改代码 |
| 只改颜色、字体、间距、动效 | 不走这里，直接用 impeccable 对应命令 |

可单独调用的子命令：`intent`、`fence`、`sample`、`check`（第 5 步全部）、`smell`、`walk`、`ledger`。不带参数时按上表判断。

## 全流程

**0. 读现状。** 先确认装了 impeccable（项目里的 `.claude/skills/impeccable` 或 `.agents/skills/impeccable`，或者全局的 `~/.claude/skills/impeccable`、`~/.agents/skills/impeccable`）。没装就停下，请用户先装（`npx impeccable install`，装完重启工具），用户明确说"先不装"才降级继续，见 impeccable-bridge.md。然后读被做产品的 `docs/product/LEDGER.md`、已有意图卡、`PRODUCT.md`、`DESIGN.md` 和代码，确认要做的东西是不是已经有了。没有 `docs/product/` 就从 `<本skill目录>/templates/` 复制 `LEDGER.md` 和 `task-tests.md` 过去。

**1. intent：写意图卡。** 读 [references/intent-card.md](references/intent-card.md)。新功能没有确认过的意图卡，不写界面代码。能从需求和仓库推断的先写好请人改，问话最多两轮。

**2. fence：定边界。** 读 [references/fence.md](references/fence.md)。上限、不做清单、术语写进 LEDGER。

**3. sample：真实样本。** 只有搜索、筛选、匹配、导入、识别、AI 生成这类结果取决于数据的功能才做。读 [references/sample-check.md](references/sample-check.md)。

> 1～3 做完，把意图卡、边界（和样本结论）**一次**交给负责人确认。这是动手前唯一的停顿。确认后一路做完，中途只在碰到红线时停。

**4. build：交给 impeccable。** 读 [references/impeccable-bridge.md](references/impeccable-bridge.md)，按它调用 impeccable。开工前读 [references/interaction-smell.md](references/interaction-smell.md) 的"改成"一列和 F 组，当作设计约束，不要等做完再查。每加一个东西都过一遍 fence。

**5. check：验收。** 按顺序：
1. 脚本：`python3 <本skill目录>/scripts/smell_scan.py <源码目录> --ledger docs/product/LEDGER.md`；网页再在浏览器里执行 `<本skill目录>/scripts/dom_probe.js`
2. 逐条看交互去 AI 味清单（interaction-smell.md）
3. impeccable 上线前三件：`audit`、`clarify`、`harden`
4. 任务走查：读 [references/task-walk.md](references/task-walk.md)

脚本标 `fail` 的要修；确实没问题的（比如下载用的 CSV 样例），在那一行加 `humane-ignore`，并在报告里说明。标 `check` 的要么修，要么用一句话说明为什么留着。没过就修，修完**全部任务**重走，不只走改过的那个。

**6. ledger：写回台账。** 读 [references/ledger.md](references/ledger.md)。评审结论先提炼成对整个产品成立的规则再写，不写成个案。

## 红线

1. 新功能没有意图卡和验收任务，不写界面代码。
2. 不擅自新增条件、字段、菜单、设置、术语。意图卡没写的先记进 LEDGER"待议"，负责人定了再做。
3. 内部结构不露给用户：不按数据表或后台模块分菜单，界面上不写技术词、模型名、"AI"。
4. 小步改：一次只改一类，改完全部任务重走，没过不叠加下一个改动。
5. 外发、扣费、删除、改权限：界面默认"起草 → 人确认 → 能撤回"，不让 AI 直接执行。

## 过关门槛

草案，待团队确认；项目里以 LEDGER.md 的"上限"为准。

- 脚本和清单：P0、P1 为 0（P1 有正当理由可以留，理由写进 LEDGER）
- 每个验收任务都走得通，主任务步数不超过意图卡上限（默认 5 步）
- 一屏主按钮 1 个；默认显示的筛选条件不超过 3 个
- 没有意图卡以外的新增条件、字段、菜单、术语
- 真人走查做过才写"已验证"；没做就写"未经真实用户验证"

## 日本企业用户

用户是日本企业的人时，读 [references/japan-business.md](references/japan-business.md)。

## 产出放哪

都放在被做产品自己的 `docs/product/`：

| 文件 | 内容 |
|---|---|
| `YYYY-MM-DD-intent-<功能英文名>.md` | 意图卡（模板 `templates/intent-card.md`） |
| `LEDGER.md` | 台账：上限、术语、不做清单、否决记录、待议、产品级规则 |
| `task-tests.md` | 验收任务和每轮结果 |
| `checks/YYYY-MM-DD/` | 每轮检查：smell 报告、页面探针结果、截图（写绝对路径） |

## 交付时怎么报

分三段：做完了什么、过关情况（逐条门槛，给数字）、接下来做什么。另起一节"要你判断的地方"：审美、取舍、对客户怎么说、被 fence 挡下的待议项。没验证的地方明说，不把"写完了"说成"能用了"。

## 不做的事

- 不改 impeccable 本身，不另立视觉规则
- 不替负责人决定加不加功能
- 评审模式只看不改
- 不编造：演示数据要像真的（长短不一、有缺项、真实格式）并标明虚构；客户名、实绩、数字不编，指不回出处的删掉或标"待确认"

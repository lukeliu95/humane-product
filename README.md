# humane-product

> AI 写界面很快，但它会自作主张加功能、说话像机器、做完没人试过就交付。装上这个 skill，让 AI 做出来的产品像人做的、人用着顺。

*A caller skill on top of [impeccable](https://github.com/pbakaus/impeccable) that keeps AI-built products free of scope creep and AI-flavored interaction, and checks them with real user tasks. Instructions are written in Chinese.*

[![Last commit](https://img.shields.io/github/last-commit/lukeliu95/humane-product?style=flat-square)](https://github.com/lukeliu95/humane-product/commits/main)
[![License](https://img.shields.io/github/license/lukeliu95/humane-product?style=flat-square)](LICENSE)

## 第一步：先装 impeccable（必需）

**这个 skill 不能单独用。** 它是 [impeccable](https://github.com/pbakaus/impeccable) 的调用层：视觉、版式、实现全部交给 impeccable，自己只管范围、交互和验收。没装 impeccable 时，它会停下来请你先装。

```bash
# 在任意项目根目录运行，按提示选全局安装，勾上你用的工具（Claude Code、Codex 等）
npx impeccable install
```

装完重启工具，确认装好了：

```bash
ls ~/.claude/skills/impeccable/SKILL.md     # Claude Code
ls ~/.agents/skills/impeccable/SKILL.md     # Codex
```

Claude Code 也可以用插件市场装：`/plugin marketplace add pbakaus/impeccable`，再在 `/plugin` 里安装。其他安装方式见 [impeccable 的说明](https://github.com/pbakaus/impeccable#installation)。

## 第二步：装 humane-product

```bash
# Claude Code
git clone https://github.com/lukeliu95/humane-product ~/.claude/skills/humane-product

# Codex
git clone https://github.com/lukeliu95/humane-product ~/.agents/skills/humane-product
```

装完重启工具。Claude Code 里输入 `/humane-product` 能看到它；Codex 里打开 `/skills`，或者输入 `$humane-product`。

用 skills CLI 的也可以试 `npx skills add lukeliu95/humane-product`（作者没在 skills CLI 上测过，以上面的 git clone 为准）。

验证脚本能跑：

```bash
python3 ~/.claude/skills/humane-product/tests/test_smell_scan.py
```

## 为什么值得用

用 Claude Code、Codex 一个人做产品时，常见三种问题：

1. **AI 自作主张。** 你要一个筛选，它顺手加了六个条件、一个设置页、一个通知中心。
2. **交互像机器。** 只有一个空白聊天框、按钮上写着"AI 自动生成"、结果不能直接改、报错只说"出错了"。
3. **没人试过。** 测试都过了，但第一次用的人找不到入口。

impeccable 解决"好不好看"。这个 skill 补上另外三件事：动手前锁住意图和范围，做的时候避开交互层的 AI 味，做完用真实任务走一遍。

## 你可以直接这样说

- "帮我做一个企业名片管理小工具，界面要好用，不要有 AI 味"
- "这个功能做得太像 AI 生成的了，帮我去 AI 味"
- "加这个功能之前，先写意图卡和不做清单"
- "用真实任务走查一遍，看普通销售能不能用"
- "只检查这个页面的交互问题，先不要改代码"

也可以带子命令：`/humane-product intent`、`fence`、`sample`、`check`、`smell`、`walk`、`ledger`。

## 它会做什么

| 步 | 做什么 | 谁来做 |
|---|---|---|
| 0 | 确认装了 impeccable；读台账、意图卡、PRODUCT.md、DESIGN.md、代码 | humane-product |
| 1 | 写意图卡：给谁用、真实目的、怎样算成功、不做什么（问话最多两轮） | humane-product |
| 2 | 定边界：上限、不做清单、术语表 | humane-product |
| 3 | 真实样本验证（只有搜索、匹配、导入、AI 生成这类数据功能才做） | humane-product |
| — | **你确认一次**，之后一路做完，只在碰到红线时停 | 你 |
| 4 | 设计和实现 | impeccable（init、shape、new-work） |
| 5 | 验收：两个检查脚本、交互去 AI 味清单、impeccable 的 audit / clarify / harden、真实任务走查 | 两者 |
| 6 | 结论写回台账，下一轮先读 | humane-product |

五条红线：

1. 新功能没有意图卡和验收任务，不写界面代码
2. 不擅自新增条件、字段、菜单、设置、术语，想加的先记进"待议"
3. 内部结构不露给用户：不按数据表分菜单，界面上不写技术词、模型名、"AI"
4. 一次只改一类，改完全部任务重走，没过不叠加
5. 外发、扣费、删除、改权限：界面默认"起草 → 人确认 → 能撤回"

## 和 impeccable 怎么分工

| 谁管 | 管什么 |
|---|---|
| impeccable | 视觉、版式、文字层级、动效、视觉层的 AI 味、实现品质 |
| humane-product | 范围（意图卡、不做清单）、交互层的 AI 味、文案里的机器腔、真实任务能不能走通 |

humane-product 不另立视觉规则。两套视觉规则一起跑会互相打架，impeccable 的作者也这样提醒过。

## 前置条件

- [ ] impeccable 已安装：`ls ~/.claude/skills/impeccable/SKILL.md`（Codex：`ls ~/.agents/skills/impeccable/SKILL.md`）
- [ ] Python 3.9 以上：`python3 --version`（扫描脚本不需要装别的包）
- [ ] 一个能让 agent 操作的浏览器（任务走查和页面探针要用）：Claude Code 内置浏览器、Chrome 扩展、Playwright 任选一个
- [ ] 能读中文：skill 的指令是中文写的。做出来的界面用什么语言，由你的产品决定

## 输出示例

被做的产品里会多出一个 `docs/product/`：

```text
docs/product/
├── 2026-10-26-intent-card-list.md   意图卡
├── LEDGER.md                        台账：上限、术语表、不做清单、否决记录、待议、产品级规则
├── task-tests.md                    验收任务和每轮结果（写明谁走的：agent、负责人、真实用户）
└── checks/2026-10-26/               每轮检查的报告和截图
```

扫描脚本的输出（`evals/cases/case1-before.html` 是故意写坏的样例）：

```text
$ python3 scripts/smell_scan.py evals/cases/case1-before.html
humane-product smell scan: 1 files, 13 findings (fail 9, check 4); P0 0 · P1 6 · P2 7 · P3 0
P1  fail   B1   evals/cases/case1-before.html:29  「✨ AIで自動入力」  界面出现 AI 或模型名 → 用产品名和业务动作；模型和数据去向写在给管理员的说明里
P1  check  B3   evals/cases/case1-before.html:45  「undefined」  中文或日文界面里露出英文状态词或程序原始值 → 换成用户的话，例如「確認中」「未提出」
P2  fail   D6   evals/cases/case1-before.html:24  「交通費精算ダッシュボード 🚀」  emoji 当图标或装饰 → 换成单色线条图标，或者删掉
（中间 10 条省略）
blocking (fail at P1 or above): 3
```

交付时，agent 会分三段汇报（做完了什么、过关情况、接下来做什么），并单独列出"要你判断的地方"：审美、取舍、对客户怎么说、被挡下的待议项。

## 两个检查脚本

```bash
# 扫源码：AI 字眼、机器腔、emoji、假数据、编造的数字、术语表里"不要用"的词
python3 ~/.claude/skills/humane-product/scripts/smell_scan.py src/ --ledger docs/product/LEDGER.md
python3 ~/.claude/skills/humane-product/scripts/smell_scan.py src/ --json
```

`scripts/dom_probe.js` 在页面里执行（浏览器工具的 JS 执行、Playwright 的 `page.evaluate`、或开发者工具控制台），返回首屏有几个主按钮、几个默认筛选条件、几段说明文字，以及页面上的文字问题。

结果分两种：`fail` 要修；`check` 要么修，要么写一句话说明为什么留着。某一行确实没问题时，在那一行加注释 `humane-ignore`。

## 配置

不需要环境变量。可以调的地方：

| 在哪 | 调什么 |
|---|---|
| `docs/product/LEDGER.md` 的"上限" | 主按钮数、默认筛选条件数、主任务步数 |
| `docs/product/LEDGER.md` 的"术语表" | "不要用"一列的词会被扫描脚本拦下 |
| 源码某一行加 `humane-ignore` | 让扫描脚本跳过这一行 |
| 页面里先设 `window.__HUMANE_LIMITS` | 页面探针用的上限，例如 `{primaryButtons: 1, defaultFilters: 3, helpParagraphs: 2}` |

## 它会动什么

- 会在你的项目里写文件：源码（通过 impeccable 实现）和 `docs/product/`
- 会在本机运行 Python 脚本，会打开浏览器操作你的本地页面
- 自己不联网、不往外部发送任何东西。impeccable 第一次运行时会下载它的引擎，那是 impeccable 自己的行为
- 真实客户资料不要放进 git：真实样本请放在 `.gitignore` 里的目录

## 适合谁

| 适合 | 不适合 |
|---|---|
| 用 Claude Code 或 Codex 做产品功能、内部工具、管理后台、带 AI 能力的功能 | 营销落地页、演示稿、纯视觉调整（直接用 impeccable） |
| 做给非技术用户用的界面，尤其是日本企业的业务人员 | 纯后端、翻译 |

## 已知限制

- 0.1.x 是试用版。整套流程还没有在多个真实项目里从头跑过
- 门槛数字（一屏主按钮 1 个、默认筛选条件不超过 3 个、主任务不超过 5 步）是草案，请按你们的产品改
- 交互清单里要人判断的条目没有自动测试；页面探针只在样例页上测过
- 日本企业用户的细节（`references/japan-business.md`）只在用户是日本企业时才用

## 文件结构

```text
SKILL.md                 主文件：流程、红线、门槛
references/              按需读
  impeccable-bridge.md   什么时候调 impeccable 的哪个命令、怎么少打扰用户
  intent-card.md         意图卡怎么问、怎么写
  fence.md               边界怎么守
  sample-check.md        真实样本验证
  interaction-smell.md   交互去 AI 味清单（A～G）
  task-walk.md           任务走查
  ledger.md              台账怎么记
  japan-business.md      日本企业用户的细节
templates/               复制到你的项目 docs/product/
scripts/                 smell_scan.py、dom_probe.js
evals/                   触发测试用例、3 组改前改后样例
tests/                   扫描脚本的单元测试
reports/                 同类 skill 调研、交付说明、触发测试结果
```

## 开发和验证

```bash
python3 tests/test_smell_scan.py
```

包结构和触发测试用 [luke-meta-skill](https://github.com/lukeliu95/luke-meta-skill) 的脚本（需要能 import yaml 的 python3）：

```bash
python3 <luke-meta-skill>/scripts/validate_skill.py .
python3 <luke-meta-skill>/scripts/trigger_eval.py . --cases evals/trigger_cases.json
```

页面探针：用任意静态服务器打开 `evals/cases/` 下的页面，在页面里执行 `scripts/dom_probe.js`，对照 `evals/cases/expected.json`。

## Troubleshooting

| 现象 | 原因 | 处理 |
|---|---|---|
| 一开始就停下，说没装 impeccable | impeccable 是必需的基础 skill | 运行 `npx impeccable install`，装完重启工具 |
| Codex 里看不到 humane-product | 装错目录，或者没重启 | 放在 `~/.agents/skills/` 或 `~/.codex/skills/` 下，重启 Codex，在 `/skills` 里看 |
| 扫描结果太多 | 扫了整个仓库 | 只扫前端源码目录（如 `frontend/src`）；隐藏目录、`node_modules`、`docs`、测试目录默认跳过 |
| 管理员页面里的模型名被标出来 | 规则默认不许界面出现模型名 | 路径带 `admin` 的文件只标 `check`；确实要写就保留，或加 `humane-ignore` |
| 发给模型的提示词被当成界面文字 | 脚本分不清字符串给谁看 | 放进 `agentPrompt`、`systemPrompt` 这类名字的字段，脚本会跳过；多行拼接的后几行加 `humane-ignore` |
| 下载用的 CSV 样例被标成假数据 | 示例和演示数据长得一样 | 加 `humane-ignore` |
| 探针说主按钮太多，其实是选中的标签页 | 探针按"实心、显眼的背景"判断 | 选中状态加 `aria-selected` 或 `aria-current`；拿不准的看返回结果里的 `items` 自己判断 |
| Claude Code 内置浏览器里探针跑不了 | 本地文件页面不能执行脚本 | 先起本地服务（项目的开发服务器，或 `python3 -m http.server`），用 localhost 地址打开 |

## 致谢

- [impeccable](https://github.com/pbakaus/impeccable)（Paul Bakaus，Apache-2.0）：本 skill 的基础，视觉和实现全部依赖它；流程对照它的[开始、迭代、打磨、维护四个阶段](https://impeccable.cn/designing/)
- 借鉴了做法（没有复制内容）：[adversarial-ux-test](https://github.com/NousResearch/hermes-agent/tree/main/optional-skills/dogfood/adversarial-ux-test)（最难伺候的用户、务实过滤）、[dsh-client-ui-ux](https://github.com/deepseek-ai/deepseek-harness/tree/master/.agents/skills/dsh-client-ui-ux)（先复用再新增）、[n8n content-design](https://github.com/n8n-io/n8n/tree/master/.agents/skills/content-design)（术语表）、[taste-skill](https://github.com/Leonxlnx/taste-skill)（源码加浏览器两道检查）、[hallmark](https://github.com/nexu-io/open-design/tree/main/plugins/community/hallmark)（项目记忆）。取舍见 `reports/prior-art-research.md`
- 依据：Nielsen 的 [10 条可用性原则](https://www.nngroup.com/articles/ten-usability-heuristics/)；Amershi 等，[Guidelines for Human-AI Interaction](https://doi.org/10.1145/3290605.3300233)，CHI 2019
- 用 [luke-meta-skill](https://github.com/lukeliu95/luke-meta-skill) 的方法制作和检查

## License

[MIT](LICENSE) © 2026 Luke Liu

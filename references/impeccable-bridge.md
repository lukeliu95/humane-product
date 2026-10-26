# 怎么调用 impeccable

## 分工

| 谁管 | 管什么 | 以什么为准 |
|---|---|---|
| impeccable | 视觉、版式、文字层级、动效、视觉 AI 味、实现品质 | PRODUCT.md、DESIGN.md、它自己的规则 |
| 本 skill | 范围、交互、文案里的机器腔、真实任务能不能走通 | 意图卡、LEDGER.md |

冲突时：视觉听 impeccable；范围和交互听意图卡和台账；两边都没写的，问负责人。不要在 impeccable 之外再加视觉规则。

## 怎么调用

- Claude Code：用 Skill 工具调用 `impeccable`，参数写"子命令 目标"，例如 `shape 申請一覧`、`audit src/pages/list.tsx`。
- Codex：用 `$impeccable`，或读 impeccable 的 SKILL.md，按它的 Setup 和对应 reference 执行。
- 没装 impeccable：先停下，告诉用户这是必需的基础 skill，给出安装命令 `npx impeccable install`（装完重启工具）。用户明确说"先不装、继续"时才降级：视觉按 PRODUCT.md、DESIGN.md 和团队已有产品的样子做，交付时标"视觉未经 impeccable 检查"。

impeccable 每个会话会先跑一次 `impeccable context`，这是它自己的规矩，照它来。

## 对照 impeccable 的四个阶段

impeccable 官方把设计工作分成开始、迭代、打磨、维护四段（impeccable.style / impeccable.cn 的 designing 页）。本 skill 在每段前后加的东西：

| 阶段 | impeccable 命令 | 本 skill 加什么 |
|---|---|---|
| 开始 | `init` → `shape` → 实现（new-work） | 之前：intent、fence、sample。之后：check |
| 迭代 | `live`、`layout`、`typeset`、`colorize`、`animate`、`bolder`、`quieter`、`critique` | 每次改动前过 fence；一次只改一类；改完 walk 全部重走 |
| 打磨（上线前） | `audit`、`clarify`、`harden` | 之前：smell。`clarify` 时把 LEDGER 术语表和机器腔清单（interaction-smell.md 的 D 组）一起交给它。之后：walk |
| 维护 | `extract`、`document` | ledger。DESIGN.md 由 impeccable 写，LEDGER.md 由本 skill 写，不混在一起 |

用户说的话怎么对到命令：

| 用户说 | 调用 |
|---|---|
| "有点不对劲，说不清哪里" | impeccable `live` |
| "排版 / 布局 / 颜色 / 动效不好" | `typeset` / `layout` / `colorize` / `animate` |
| "太花了" / "太平淡了" | `quieter` / `bolder` |
| "这个到底行不行" | 本 skill `check`；要完整的设计评分再加 impeccable `critique` |
| "文案别扭" | impeccable `clarify`，带上术语表和 D 组 |
| "要上线了" | 本 skill `check`（含 audit、clarify、harden） |
| "加一个 xx 功能" | 先 fence，再决定要不要调 impeccable |

`critique` 比较重（它要求两个独立的评审），在第一个完整版本和上线前各跑一次就够；日常每轮用本 skill 的 `check`。

## 少打扰用户：问话合并

impeccable 的 `init` 要问"用户是谁、产品做什么、有什么约束"，`shape` 和 new-work 要问"任务、信息、状态、频率、约束、成功标准"。这些意图卡都答过了。

调用时把意图卡全文交给它，并写明："以下内容已由负责人确认，不要重问，只补问你独有的问题。"

init 独有的问题放进意图卡确认的那一轮一起问，不要单独再打扰一次：
- 技术栈（项目里还没有代码时）：纯 HTML/CSS、指定框架，还是交给你选
- 构建方式（comp-first 还是 code-first）：只有能生成图片、并且要做落地页这类展示页面时才问；产品界面 impeccable 规定直接写代码，不用问

## 意图卡怎么对到 PRODUCT.md

没有 PRODUCT.md 时，用意图卡预填 init 要写的字段，请负责人在同一轮确认：

| PRODUCT.md 字段 | 从意图卡哪里来 |
|---|---|
| Users | 1. 谁、在什么场景用 |
| Product Purpose | 2. 真实目的 + 3. 怎样算成功 |
| Operating Context | 1 里"他现在怎么做" |
| Capabilities and Constraints | 5. 明确不做 + LEDGER 术语表 |
| Evidence on Hand | 4. 真实样本；没有的写明"没有，不能编" |
| Product Principles | 红线里和这个产品相关的两三条 |

## 产品界面的模式

产品界面多数是 impeccable 的 Operate 模式：用户来办事，熟悉的控件比新奇的表现更重要。它规定这类界面直接写代码、不出效果图，视觉"世界"只借字体、配色、密度和一个记忆点，不改导航和控件。这和"符合人的操作习惯"是一致的，不要让视觉盖过任务。

## 团队默认风格（示例，换成你们自己的）

没有 DESIGN.md 时，把团队默认风格当作需求里写死的约束交给 impeccable（它会优先遵守需求里写死的审美）。有 DESIGN.md 或团队已有同类产品时，以它们为准。下面是作者团队用的一套，供参考：

- 和公司已有产品保持一致
- 黑灰为主，品牌色只做点缀，默认亮色
- 少用线框、阴影、渐变；选中项不用侧边高亮竖线
- 图标用单色线条图标，不用 emoji
- 不要蓝紫色的"AI 风"
- 一屏放下主要内容和操作，少放说明文字

## 检查工具不重复

- impeccable 的检测器 `<impeccable目录>/scripts/impeccable detect --json <文件>`：只查视觉层的毛病，网页项目在 check 时跑一次
- 本 skill 的 `smell_scan.py`、`dom_probe.js`：只查文案、交互和数量上限

两者结果合在一份报告里，按 P0～P3 排。

# 同类 skill 调研（2026-10-26）

## 怎么查的

- SkillsMP：用 luke-meta-skill 的 `search_skillsmp.py`，4 个查询，按仓库星数排序，各取前 10 条
  - "ai slop ui design"、"ux heuristics usability review"、"human centered product design"、"anti ai generic interface"
  - 注意：星数是整个仓库的星数，不代表这个 skill 的质量
- skills.sh：**没查**。它要执行 `npx skills find`（会下载并运行 npm 包），这次没有执行。记为缺失证据
- GitHub：用 `gh api` 只读拉取候选的 SKILL.md 原文

## 读过原文的候选

| 候选 | 来源 | 为什么入选 | 学到的做法 | 用在哪 |
|---|---|---|---|---|
| adversarial-ux-test | NousResearch/hermes-agent（仓库星数 254,141，SkillsMP 2026-10 数据） | 唯一一个专门"扮成最难伺候的用户去走真实任务"的 | 最难伺候的真实用户画像；走真实任务而不是功能巡览；数步数；务实过滤（一般用户也会遇到才修，"想要新功能"不直接做） | task-walk.md 的刁难任务、计步、务实过滤 |
| dsh-client-ui-ux | deepseek-ai/deepseek-harness（250,596） | 一线产品团队的产品界面规则 | 先复用再新增；反馈按生命周期选位置；失败时数据留在原处；报错要短、要说人话 | fence.md 的"先复用再新增"；interaction-smell.md 的 E5 |
| content-design | n8n-io/n8n（207,388） | 第一方的产品文案规范，可信度高 | 术语表；一个意思只用一个词；确认框写成"删除项目？"而不是"你确定要……吗" | LEDGER 术语表、C4 规则、E3 的写法 |
| taste-skill（design-taste-frontend） | Leonxlnx/taste-skill（97,410） | 反 AI 味设计里最热门的之一 | 源码扫描（lint）加真实浏览器测量（inspect）两道关；"有 WARN 就当错，除非一句话说得清" | smell_scan.py + dom_probe.js；fail / check 两级 |
| hallmark | nexu-io/open-design（101,372） | 反 AI 味设计 skill，有项目记忆 | 每次开工前读项目记录，避免重复；检查清单只在交付前加载 | LEDGER 每轮先读；清单按需加载 |

## 取舍

- **保留**：任务走查加务实过滤；先复用再新增；术语表一词一义；两道机器检查（源码、页面）
- **改编**：
  - adversarial-ux-test 的"用角色口吻吐槽"改成平实记录（要直说，不要表演）
  - 它的"自动开工单"改成写进 LEDGER 的"待议"（不往外部系统写东西）
  - taste-skill 的视觉测量不要，只量交互数量（主按钮、筛选条件、说明段落）
- **不要**：
  - taste-skill、hallmark 的视觉方向库、主题轮换、视觉禁令：视觉归 impeccable。impeccable 官网也明确说，两个设计 skill 同时跑会让规则互相打架、彼此抵消
  - ui-ux-pro-max 这类大而全的设计数据库：和 impeccable 重叠，而且会占大量上下文
- **原创**：
  - 交互层的 AI 味清单（A～G），尤其是带 AI 能力的功能：只有聊天框、让用户写提示词、结果不能直接改、看不出依据、外发不经人确认
  - 意图卡和 impeccable 的 init / shape 对接，问话合并成一轮，减少打扰
  - 日本企业用户的细节（フリガナ排序、全角半角不敏感搜索、前株後株、CSV 不乱码、稟議要用的导出）
  - 台账反哺：一条规则在两个以上产品成立，就提议加进本 skill

## 缺失证据

- skills.sh 的安装量没有查
- 没有和这些候选做公平的效果对比，不能说本 skill "更好"

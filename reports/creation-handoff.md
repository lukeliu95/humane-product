# 交付说明：humane-product 0.1.1

## 1. 结果

- 名字和版本：humane-product 0.1.1（试用中）
- 做什么：让 AI 做出来的产品像人做的、人用着顺。动手前锁住意图和范围，视觉交给 impeccable，做完用交互清单和真实任务验收
- 前提：impeccable 是必需的基础 skill
- 仓库：https://github.com/lukeliu95/humane-product（MIT）

## 2. 参考过的 skill

见 `reports/prior-art-research.md`。读过原文的 5 个：adversarial-ux-test、dsh-client-ui-ux、n8n content-design、taste-skill、hallmark。

## 3. 保留、改编、不要、原创

- 保留：任务走查加务实过滤；先复用再新增；术语表一词一义；源码和页面两道机器检查
- 改编：角色吐槽改成平实记录；自动开工单改成写进 LEDGER"待议"；视觉测量改成只量交互数量
- 不要：别家的视觉规则和视觉方向库（视觉归 impeccable，两套一起跑会打架）
- 原创：交互层 AI 味清单 A～G；意图卡和 impeccable init / shape 的问话合并；日本企业用户细节；台账反哺 skill

## 4. 优势和证据

| 标签 | 内容 | 证据 |
|---|---|---|
| validated advantage | 源码扫描在 3 组样例上：坏例子里预先埋的问题全部抓到，好例子 0 条 | `tests/test_smell_scan.py` 20 个测试，Python 3.9.6 和 3.12.14 都通过 |
| validated advantage | 页面探针在真实浏览器里：坏例子抓到 4 个主按钮（上限 1）、6 个默认筛选条件（上限 3）、页面上的 undefined；好例子全部通过；深色页面和 oklch 颜色判断正确 | 2026-10-26 在 Claude Code 内置浏览器里逐页执行，结果对照 `evals/cases/expected.json` |
| validated advantage | 在真实项目上误报可控：一个内部项目的前端源码（91 个文件）里，找到 47 处界面直接写着"AI"；剩下的误报主要是发给模型的多行提示词和下载用的 CSV 样例。第一版曾把整个仓库里的 worktree 副本也扫进去（5308 个文件），已改成跳过隐藏目录 | 只读扫描，没有改任何文件 |
| validated advantage | 触发描述通过 18 个用例（7 个该触发、6 个不该触发、5 个相近但不该触发） | `reports/trigger-eval.json`。这是按关键词的快速测试，不是让模型真实触发 |
| validated advantage | Codex 能发现这个 skill | 链到 `~/.codex/skills/` 后，用 `codex debug prompt-input` 渲染出的技能列表里有 humane-product（不调用模型） |
| design advantage | 和 impeccable 分工清楚：视觉不另立规则，问话合并成一轮 | `references/impeccable-bridge.md` |
| hypothesis | 用了这个 skill 做出来的产品 AI 味更少、更好用 | 还没有真实项目从头跑过 |

## 5. 验证和缺口

没验证（missing evidence）：
- 整个流程（意图卡 → impeccable → 检查 → 台账）还没有在真实项目里从头跑过
- 交互清单里要人或模型判断的部分（标 M 的）没有自动测试
- 页面探针只在样例页上测过，没在真实应用页面上测
- 和其他 skill 没做公平的效果对比
- 门槛数字是草案
- skills.sh 的安装量没查；`npx skills add` 安装方式没测过

刻意不做的：不改 impeccable；不往外部系统写东西。公开前删掉了来自内部资料的结论和内部项目名。

## 6. 包结构检查

2026-10-26，luke-meta-skill `validate_skill.py`（系统 Python 3.9.6，带 PyYAML）：`ok: true`，失败 0，警告 0。`reports/skill-ir.json` 和 `reports/trigger-eval.json` 每次改版后重新生成。

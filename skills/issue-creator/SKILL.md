---
name: issue-creator
description: 从认可样本归纳本仓库 issue 画像，挖掘 main 分支可证明的真实缺陷，产出高认可度、易被维护者打正向标签的 issue
source:
  type: original
  repo: skills-repo/open-source-contributor
  path: skills/issue-creator/SKILL.md
  version: 1.0.0
  updated: 2026-10-12
metadata:
  category: 发现+报告
  platform: GitHub
  difficulty: 进阶
---

# Issue 创造者（缺陷发现 → 认可工程）

> 不是"报单礼仪"，而是**端到端的"找缺陷 → 报出被认可的 issue"**能力。认可度不是文风问题，是工程问题——可验证性 × 影响面 × 维护者修复成本。

本子技能补上 open-source-contributor 能力链里缺失的"报单"一环：体系原本能**选单**（issue-finder 发现别人的 issue）、**做单**（github-contribution 修复提 PR），但**自己主动找缺陷、报出好 issue** 的能力为零——而 issue-finder 评分里合并率最高的正是带 `source-repro`（高质量复现）的 issue，缺的就是生产这种 issue 的源头。

## 何时使用

- 想主动为一个项目做贡献，但**不想只挑别人报剩的 issue**，要从代码里自己挖缺陷
- 报过 issue 却被维护者冷淡处理 / 打 `needs-repro` / 直接关闭，想知道"什么样的 issue 会被认可"
- 修复实战中发现了新缺陷，想规范地报出来再认领修复
- 需要先摸清"这个仓库认可什么样的 issue"，再决定报不报、怎么报

## 能力索引（先读画像，再挖缺陷，最后报单）

| 阶段 | 读取 | 关键词（grep 线索） |
|------|------|---------------------|
| ① 认可画像：从目标仓库被认可的 issue 语料归纳"高认可度画像" checklist | [references/recognized-issue-gold-cases.md](references/recognized-issue-gold-cases.md) | 认可画像 正向标签 gold case 语料采集 source-repro 归纳 |
| ② 缺陷挖掘：在最新 main 上按 ROI 找**可证明**的真实缺陷 | [references/defect-hunting-playbook.md](references/defect-hunting-playbook.md) | 缺陷挖掘 找bug churn 错误处理 并发 复现 根因 file:line |
| ③ 报单方法论：七阶段把缺陷写成高认可度 issue | [references/issue-report-playbook.md](references/issue-report-playbook.md) | 报issue 复现 source-repro 五段式 needs-repro 跟踪 闭环 |
| issue 正文骨架与自检 | [../../assets/ISSUE_TEMPLATE.md](../../assets/ISSUE_TEMPLATE.md) + `scripts/check_contribution.py issue` | issue 模板 五段式 自检 Evidence Environment |

> 三个 reference 是**按仓库运行的方法论**，不硬编码任何单仓库结论；文档内的演练样例均标注为示例。

## 与其他子技能衔接

- **上游（缺陷来源）**：自主缺陷挖掘（本技能 ②）；或修复实战中的新发现（github-contribution 过程中撞到的相邻缺陷）。
- **下游（修复闭环）**：issue 获认可后转 [github-contribution](../github-contribution/SKILL.md) 认领修复；报前用 [issue-finder](../issue-finder/SKILL.md) 的 [scripts/scan_issue_claims.py](../../scripts/scan_issue_claims.py) 确认非重复、未被认领。
- **校准基准**：issue 侧的对标物是 [references/merged-pr-gold-cases.md](../../references/merged-pr-gold-cases.md)（PR 侧）——本技能 ① 补齐 issue 侧的对应校准。
- **沟通礼仪**：@ 维护者、AI 辅助披露等对齐 [community-etiquette](../community-etiquette/SKILL.md)。

## 核心原则

1. **可证明先行**：仅代码论证的缺陷必须先构建复现；无法复现时降级为 question/discussion，绝不报成 bug issue（防止消耗维护者信任）。
2. **认可度即工程质量**：对照本仓库认可画像自检，不满足要么补强要么放弃/降级。
3. **最小复现优先**：独立脚本 / 最小 config，其次真实入口；环境矩阵含 commit pin。能复现但无根因也报——复现完整度优先于根因完整度。
4. **诚实边界**：策略提高命中率，不保证发现全部缺陷；未复现的候选不进 bug issue。

---
name: pr-landing-monitor
description: PR 提交后的动态监控与迭代修复：CI 收敛盯守、失败双 checkout 归因分流、评审反馈补强、merge-ready 推进，把 PR 从"提交了"推进到"被合并"
source:
  type: derived
  repo: skills-repo/open-source-contributor
  path: skills/pr-landing-monitor/SKILL.md
  version: 1.0.0
  updated: 2026-10-17
  url: https://skills.sh/spencerpauly/awesome-cursor-skills/babysitting-pr
metadata:
  category: 监控+迭代
  platform: GitHub
  difficulty: 进阶
---

# PR 落地监控（提交后动态监控 → 判断 → 优化修复）

> PR 提交不是终点。`github-contribution` 把 PR 交出去之后，**让 PR 落地**的能力在这里：
> 持续盯 CI 与评审 → 每个失败先归因再动手 → 该修的最小面修掉 → 该解释的发证据评论 →
> 一轮一轮把 "Before merge" 清单清零，直到 `ready for maintainer look` → merged。

## 何时使用

- PR 已提交，CI 在跑/挂了，不知道哪些失败是自己的、哪些是 upstream 的
- 评审机器人（ClawSweeper/Greptile）逐轮拉高 proof 要求，需要系统性应对而不是被动挨审
- 想把"等维护者看"变成"主动推进到 ready for maintainer look"
- 需要定时无人值守监控（自动化 cron/automation），有变化才处理、无变化不打扰

## 能力索引（先监控、再归因、最后迭代）

| 阶段 | 读取 | 关键词（grep 线索） |
|------|------|---------------------|
| ① 监控循环：盯什么、基线怎么记、节奏怎么定、何时静默 | [references/monitoring-playbook.md](references/monitoring-playbook.md) | 监控 CI check-runs 评审轮转 基线 静默 收敛 |
| ② 归因与修复：失败分流（ours vs upstream）、修复循环、评论规范、认知陷阱 | [references/fix-attribution-playbook.md](references/fix-attribution-playbook.md) | 归因 双checkout 对照 修复循环 认知陷阱 归因评论 |
| 只读状态轮询脚本（CI/labels/mergeable 一次拉齐） | [scripts/poll_pr_state.py](scripts/poll_pr_state.py) | 轮询 状态 check-runs |

## 与其他子技能/引用衔接

- **上游**：[github-contribution](../github-contribution/SKILL.md) 提交 PR 后即进入本技能的监控循环。
- **评审细节**：反馈分类与回复话术用 [pr-review](../pr-review/SKILL.md) 与根级 [review-response-playbook](../../references/review-response-playbook.md)；proof 构建复用 github-contribution 的 Live-Proof 方法论。
- **下游闭环**：PR merged 后按 [issue-creator](../issue-creator/SKILL.md) 阶段 7 的资产升级思路，把复现资产沉淀为回归测试。

## 核心原则

1. **先归因再动手**：每个 CI 失败必须走"日志 → 本地复现 → 双 checkout 对照"三步；**基线同样失败 = upstream 回归，发归因评论，绝不代修**。
2. **最小面迭代**：一次迭代只解决一类问题；本地（相关测试 + 类型 + lint/格式）全绿才 push；每次迭代发一条说明评论。
3. **诚实边界**：无法本地验证的（缺 key/缺 OS）在 PR 里如实注明，不虚报"已测试"；归因结论必须附证据，不凭标签/名称猜。
4. **无变化不打扰**：无人值守监控时，无变化仅输出"无变化"；写操作（push/评论）只在授权分支上进行。

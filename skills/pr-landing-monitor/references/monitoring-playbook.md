# Monitoring Playbook —— PR 提交后的监控循环

> 回答三个问题：**盯什么**、**怎么记基线**、**什么节奏**。目标是把"被动等"变成"有状态的推进"。

## 盯什么（六项状态，一次拉齐）

用 `scripts/poll_pr_state.py <owner/repo> <PR号>` 一次拉取，或按项手动：

| 状态 | 来源 | 变化意味着 |
|------|------|-----------|
| check-runs 结论分布与失败清单 | `commits/<sha>/check-runs` | CI 红/绿；新失败进归因流程 |
| mergeable / mergeable_state | PR API | 冲突出现/ci-gate 红导致的 blocked |
| labels | PR API | 评审机器人状态机推进（如 `waiting on author` → `ready for maintainer look`） |
| pinned 评审追踪器 | issue comments 的 `updated_at` | 评审刷新：rating 变化、Before-merge/Findings 清单增减 |
| 新增 issue comments / reviews | comments+reviews API（按时间过滤） | 维护者/机器人反馈（优先级最高） |
| state / merged_at | PR API | merged/closed → 监控终态 |

## 基线方法（有状态的对比，不是每次从头看）

1. **每次运行产出一个快照记录**（检查分布、失败名单、labels、评审结论、最后评论时间戳），供下次运行 diff。
2. **已知基线清单**：已归因、已解释、已决定不处理的项写入"勿重复处理"清单（例：某失败已归因为 upstream 回归且评论已发）。后续运行只对比差异。
3. **无变化 = 静默**：无人值守场景下，两 PR 均无差异时只输出"无变化"，不生成冗长报告。

## 节奏（两段式）

- **收敛期**（刚推送/刚触发评审）：高频轮询直到 `pending=0`——90 秒一次，`in_progress+queued+pending+waiting` 归零即停。
- **等待期**（等维护者/等评审轮转）：低频定时（1–3 小时一次），每次只做基线 diff。

## 终态与退出

- `merged_at` 非空 / `state=closed`：报告终态，**停止对该 PR 的一切迭代**（只留归档观察）。
- `mergeable_state=clean` 且无 Before-merge 待办、无新失败：报告"可合并"，转入低频观察——**不催维护者，不 bump**（合并节奏归维护者）。

## 无人值守固化（automation/cron）

把监控循环固化成定时任务时，prompt/脚本必须**自包含**（未来运行看不到今天的对话）：

- 监控对象（PR 号、head 分支、基线 commit）写死；
- 已知基线清单原文写入；
- 授权边界写死：哪些分支可 push、哪些评论可发、哪些"绝不"（不 push main、不 force、不动他人评论）；
- 分层动作：无变化→静默；upstream 失败→归因评论；our 失败/评审反馈→修复循环。

## 关联子技能（层次边界，L2→L3）

- **上游**：[github-contribution](../../github-contribution/SKILL.md) 提交 PR 后即进入本监控循环。
- **评审细节**：反馈分类与回复话术用 [pr-review](../../pr-review/SKILL.md) 与根级 [review-response-playbook](../../../references/review-response-playbook.md)；proof 构建复用 github-contribution 的 Live-Proof 方法论。
- **下游闭环**：PR merged 后按 [issue-creator](../../issue-creator/SKILL.md) 阶段 7 的资产升级思路，把复现资产沉淀为回归测试。
- 本文件只负责"盯什么/记基线/定节奏"，失败后的归因与修复动作见同级 [fix-attribution-playbook.md](fix-attribution-playbook.md)。

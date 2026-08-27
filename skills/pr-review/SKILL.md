---
name: pr-review
description: PR Review 响应策略，应对自动化评审（ClawSweeper/Greptile）和人工审查
source:
  type: derived
  repo: skills-repo/open-source-contributor
  path: skills/pr-review/SKILL.md
  version: 2.0.1
  updated: 2026-07-26
  url: https://clawhub.ai/skills/pr-review
metadata:
  category: 评审
  platform: GitHub
  difficulty: 进阶
---

# PR 评审应对

> 高效响应 PR Review：自动化评审机器人通过指南、人工审查反馈处理、review conversation 管理。

## 能力

- **自动化评审应对**：ClawSweeper、Greptile、Aisle Security 等评审机器人
- **反馈分类**：阻断性问题 → 建议 → 可选优化，按优先级处理
- **响应策略**：每个反馈独立 commit、不强制推送、24h 内响应
- **Review 状态管理**：跟踪 conversation resolved/unresolved 状态
- **重新审查请求**：何时 re-request review、何时等待

## 使用方式

在 Claude Code 中使用 `/pr-review` 调用。

```
/pr-review 分析这个 PR 收到的审查反馈
/pr-review 帮我起草对 Greptile 建议的回复
```

## 工作流

1. 收到审查反馈后，分类排序（阻断/建议/可选）
2. 对每个反馈：理解 → 修改 → 独立 commit → 回复
3. 自动化评审（ClawSweeper）：检查 proof 是否充分、是否覆盖边界值
4. 安全扫描（Aisle Security）：区分真实问题和误报
5. 所有 conversation resolved 后 re-request review

## 常见评审场景

| 场景 | 策略 |
|------|------|
| 机器人要求更多 proof | 补 BEFORE vs AFTER 终端输出 |
| 安全扫描报告 | 引用 SECURITY.md 说明范围，但仍做防御性修复 |
| 代码风格建议 | 遵循项目规范，不争论风格偏好 |
| 架构质疑 | 解释设计权衡，提供替代方案 |
| 要求拆分为小 PR | 接受，关闭大 PR 拆分为 2-3 个小 PR |

## 适用场景

- 首次收到自动化评审机器人反馈（不确定如何应对）
- PR 被标记 "needs more proof"
- 多个审查者同时提出反馈，需要协调
- 审查反馈要求重大修改

## 限制

- 不了解所有评审机器人的规则（不同项目不同配置）
- 不替代与维护者的直接沟通
- 不处理需要项目内部知识的反馈

## 相关参考（Playbook）

- 评审应对 SOP → [`references/review-response-playbook.md`](../../references/review-response-playbook.md)：把本技能的"反馈分类"升级为带 SLA 的处置流水线。
- 提交与 PR 规范 → [`references/commit-pr-conventions.md`](../../references/commit-pr-conventions.md)："每条反馈独立 commit"的量化门禁。
- 已合并 PR Gold Cases → [`references/merged-pr-gold-cases.md`](../../references/merged-pr-gold-cases.md)：从真实案例反推 review 关注点。
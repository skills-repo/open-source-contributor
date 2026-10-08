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

## rebase 与被要求 rebase 时的强制推送

> 本地补充（2026-09-16，源于 openclaw/openclaw #120824 实战）。

机器人（ClawSweeper 等）常要求 "must be rebased"。此时**"不强制推送"原则不适用**——rebase 必然改写历史，只有 force-push 才能更新 PR 分支。

- 只在**自己的 fork 分支**上 force-push；先 `git fetch origin <branch>` 刷新 lease，再 `git push --force-with-lease`。
- 若 `--force-with-lease` 被拒，说明远端已被他方改动 → **停下来查清，绝不要改用 `--force`**。
- 保持 rebase 结果为**单一提交**（用 `git commit --amend` 吸收修正），便于评审。

### ⚠️ 冲突解决是缺陷注入的主要环节

rebase 的价值在于"保留**已发布契约**"，而非"保留 PR 原文"。两类高发缺陷：

| 缺陷 | 症状 | 预防 |
|---|---|---|
| 丢失已发布的契约 | 把上游刻意删除的行为又加回来（如某次发布移除的查询参数） | 读上游测试里的**契约断言**（如 `expect(param).toBeNull()`），以它为准 |
| 丢失标识符 / helper 定义 | 运行时报 `ReferenceError: xxx is not defined`，静态读 diff 却"很正常" | 冲突若涉及 import / helper 区段，解决后必须实际运行测试 |

**硬规则：force-push 之前，必须在 rebase 后的 head 上跑过评审机器人指定的 focus 测试。** 冲突解决无法靠读 diff 自证正确——只有运行能暴露被丢掉的定义。跳过这一步，几乎必然换来一条红的 CI。

### 环境闸门会伪装成测试失败

失败信息未必指向代码。先排除环境因素，再改代码：

- 引擎版本 / SQLite / 运行时安全校验类报错 → 换到符合 `engines` 的运行时，不要改代码。
- 脚本退出码非 0，但 `Test Files` / `Tests` 汇总行全绿 → 多为沙箱或清理钩子干扰，**以汇总行为准**。
- 报错指向与本次改动无关的包（如其他频道的原生依赖）→ 多为安装期网络问题，可忽略。

## 适用场景

- 首次收到自动化评审机器人反馈（不确定如何应对）
- PR 被标记 "needs more proof"
- 多个审查者同时提出反馈，需要协调
- 审查反馈要求重大修改
- 机器人要求 rebase 分支（需 force-push，见上文专节）

## 限制

- 不了解所有评审机器人的规则（不同项目不同配置）
- 不替代与维护者的直接沟通
- 不处理需要项目内部知识的反馈

## 相关参考（Playbook）

- 评审应对 SOP → [`references/review-response-playbook.md`](../../references/review-response-playbook.md)：把本技能的"反馈分类"升级为带 SLA 的处置流水线。
- 提交与 PR 规范 → [`references/commit-pr-conventions.md`](../../references/commit-pr-conventions.md)："每条反馈独立 commit"的量化门禁。
- 已合并 PR Gold Cases → [`references/merged-pr-gold-cases.md`](../../references/merged-pr-gold-cases.md)：从真实案例反推 review 关注点。
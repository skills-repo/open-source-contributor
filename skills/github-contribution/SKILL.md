---
name: github-contribution
description: Fork→Sync→Branch→Fix→PR 全流程自动化，含变更计划和 live-proof 最佳实践
source:
  type: derived
  repo: skills-repo/open-source-contributor
  path: skills/github-contribution/SKILL.md
  version: 1.7.4
  updated: 2026-07-26
  url: https://clawhub.ai/skills/github-contribution
metadata:
  category: 贡献
  platform: GitHub
  difficulty: 进阶
---

# GitHub 贡献工作流

> 自动化 GitHub Fork 贡献流程：同步上游、创建分支、变更计划、PR 提交、Live-Proof 评审应对。

## 能力

- **Fork 保护**：main 分支保护、自动同步上游、干净状态强制
- **变更计划**：5-Point 分析法 — 现象/预期/根因/修改点/风险面
- **PR 模板**：完整 PR 描述、安全清单、人工验证声明
- **Live-Proof**：BEFORE vs AFTER 终端输出，应对自动化评审机器人
- **高质量 PR**：10 项成功特征、合并成功率公式、CI 预检清单

## 使用方式

在 Claude Code 中使用 `/github-contribution` 调用。

```
/github-contribution 为 openclaw/openclaw 修复 issue #5968
/github-contribution 检查 fork 状态并同步上游
```

## 工作流

1. **Issue 确认**：验证 issue 仍开放、无人认领、有正向标签
2. **Fork 同步**：`git fetch upstream && git reset --hard upstream/main`
3. **变更计划**：5-Point 分析 → 写计划 → 确认再写代码
4. **开发修复**：在功能分支上开发，小而专注的 commit
5. **Live-Proof**：BEFORE vs AFTER 终端命令输出，覆盖边界值
6. **PR 提交**：完整模板、关联 issue、安全清单
7. **评审应对**：24h 内响应、每次反馈独立 commit、不强制推送

## Fork 同步命令

```bash
git checkout main
git fetch upstream
git reset --hard upstream/main
git clean -fdx
git push origin main --force
```

## 变更计划模板

```markdown
1. Observed behavior: <当前现象>
2. Expected behavior: <期望行为>
3. Suspected root cause: <根因定位（具体文件/行号）>
4. Safest seam to modify: <最小修改点>
5. Risk surface: <影响范围>
```

## 适用场景

- 首次向开源项目贡献代码
- 需要应对自动化评审机器人（ClawSweeper/Greptile）
- 希望提高 PR 合并成功率
- 多仓库贡献管理

## 限制

- 不涉及 GitLab/Bitbucket 等非 GitHub 平台
- Token 权限问题需自行处理（workflow scope）
- 不替代项目 CONTRIBUTING.md 的特定规则
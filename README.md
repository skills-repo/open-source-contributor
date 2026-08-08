# 开源贡献者技能库

> AI Agent Skills for Open Source Contributors —— 覆盖 Issue 发现、Fork 工作流、PR 提交、评审应对、社区礼仪

## 定位

为开源贡献者（尤其是初次贡献者）提供一套可安装的 AI Agent 技能，让 Claude Code 成为你的开源贡献搭档。从发现第一个 Issue 到 PR 被合并，全程有技能护航。

## 核心理念

> 开源贡献不是代码写得好就行 — 流程、沟通、证据，缺一不可。

- **流程正确优先** — 先 Fork 同步再写代码，不在 main 分支上直接开发
- **证据驱动** — PR 附带 BEFORE vs AFTER 对比，不用截图用终端输出
- **尊重维护者** — 小 PR、清晰描述、快速响应审查反馈

## 架构说明（superpower）

本仓库采用 skills-repo 组织的 **superpower 架构**：

- `SKILL.md` — 唯一入口，只做能力路由（本文件）
- `references/` — 深层 playbook：首次贡献决策、提交规范自检、评审应对 SOP
- `skills/` — 4 个细粒度子技能，可单独安装
- `scripts/` — `check_contribution.py` 提交规范自检（纯标准库、可复现）
- `assets/` — PR 模板与提交规范配置

渐进式加载：Agent 先读路由表，按需读取 `references/` 或 `skills/`，重复任务交给脚本。

## 技能清单

| 环节 | 技能 | 描述 | 来源 |
|------|------|------|------|
| 🔍 发现 | `issue-finder` | 智能 Issue 发现：正向标签检测、优先级评分、多仓库搜索 | [衍生](https://clawhub.ai/skills/issue-finder) |
| 🔄 贡献 | `github-contribution` | Fork→Sync→Branch→Fix→PR 全流程自动化与最佳实践 | [衍生](https://clawhub.ai/skills/github-contribution) |
| 👀 评审 | `pr-review` | PR Review 响应策略、自动化评审（ClawSweeper/Greptile）应对 | [衍生](https://clawhub.ai/skills/pr-review) |
| 🤝 社区 | `community-etiquette` | 开源社区沟通规范、贡献指南遵循、维护者关系 | [衍生](https://skills.sh/daymade/claude-code-skills/github-contributor) |

## 安装

```bash
# 整库安装（推荐）—— 拿到路由层 + references + scripts + assets
npx skills add skills-repo/open-source-contributor

# 单技能安装 —— 只要某一个细粒度能力
npx skills add skills-repo/open-source-contributor@github-contribution -g -y
npx skills add skills-repo/open-source-contributor@issue-finder -g -y
npx skills add skills-repo/open-source-contributor@pr-review -g -y
npx skills add skills-repo/open-source-contributor@community-etiquette -g -y
```

## 推荐工作流

```
Issue 发现 → Fork 同步 → 变更计划 → 开发修复 → PR 提交 → 评审应对 → 合并清理
issue-      github-      change      github-    github-   pr-        github-
finder      contribution  plan        contribution contribution review     contribution
```

## 许可

MIT

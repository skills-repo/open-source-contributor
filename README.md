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
- `references/` — 深层 playbook：首次贡献决策、提交规范自检、评审应对 SOP、feature 价值判据与验证阶梯
- `skills/` — 9 个细粒度子技能，可单独安装
- `scripts/` — `check_contribution.py` 提交规范自检 + Issue 五段式检查；`mine_discussions.py` 讨论区挖掘与 feature 打分（纯标准库 + `gh`，可复现）
- `assets/` — PR 模板、Issue 模板与提交规范配置

渐进式加载：Agent 先读路由表，按需读取 `references/` 或 `skills/`，重复任务交给脚本。

## 技能清单

| 环节 | 技能 | 描述 | 来源 |
|------|------|------|------|
| 🧭 侦察 | `discussion-scout` | 挖掘项目讨论区，提炼还没变成 issue 的 feature 线索，按社区热度与维护者态度判定开发价值（候选强度 C1–C3） | 原创 |
| 📐 合规 | `repo-skill-scout` | 侦察宿主仓库自带的 Agent 规则层与技能包（`AGENTS.md` / `.agents/skills` / `.claude/skills`），重建"场景→先读哪条规则"的路由表，并按权限二分决定哪些能执行、哪些只读契约 | [衍生](https://raw.githubusercontent.com/samber/developer-relations-skills/main/skills/oss-contributor-onboarding/SKILL.md) |
| 📣 提案 | `feature-proposer` | 把判过价值的 feature 落成讨论帖 / feature request issue，再用高级正向标签 + 维护者认可回评验证（V4 才放行写码） | [衍生](https://github.com/paulrberg/agent-skills/blob/main/skills/yeet/SKILL.md) |
| 🔍 发现 | `issue-finder` | 智能 Issue 发现：正向标签检测、优先级评分、多仓库搜索 | [衍生](https://clawhub.ai/skills/issue-finder) |
| 🐛 报单 | `issue-creator` | 端到端报单：认可画像 → 缺陷挖掘 → 产出高认可度 Issue（source-repro 五段式） | 原创 |
| 🔄 贡献 | `github-contribution` | Fork→Sync→Branch→Fix→PR 全流程自动化与最佳实践 | [衍生](https://clawhub.ai/skills/github-contribution) |
| 👀 评审 | `pr-review` | PR Review 响应策略、自动化评审（ClawSweeper/Greptile）应对 | [衍生](https://clawhub.ai/skills/pr-review) |
| 🤝 社区 | `community-etiquette` | 开源社区沟通规范、贡献指南遵循、维护者关系 | [衍生](https://skills.sh/daymade/claude-code-skills/github-contributor) |
| 🚀 落地 | `pr-landing-monitor` | PR 提交后动态监控与迭代修复：CI 收敛盯守、失败双 checkout 归因分流、评审补强、merge-ready 推进 | [衍生](https://skills.sh/spencerpauly/awesome-cursor-skills/babysitting-pr) |

## 安装

```bash
# 整库安装（推荐）—— 拿到路由层 + references + scripts + assets
npx skills add skills-repo/open-source-contributor -g -y

# 单技能安装 —— 只要某一个细粒度能力
npx skills add skills-repo/open-source-contributor@github-contribution -g -y
npx skills add skills-repo/open-source-contributor@issue-finder -g -y
npx skills add skills-repo/open-source-contributor@issue-creator -g -y
npx skills add skills-repo/open-source-contributor@pr-review -g -y
npx skills add skills-repo/open-source-contributor@community-etiquette -g -y
npx skills add skills-repo/open-source-contributor@pr-landing-monitor -g -y
npx skills add skills-repo/open-source-contributor@discussion-scout -g -y
npx skills add skills-repo/open-source-contributor@feature-proposer -g -y
npx skills add skills-repo/open-source-contributor@repo-skill-scout -g -y
```

## 推荐工作流

# A. 缺陷/已有 issue 路径
```
规则层侦察 → Issue 发现 → Fork 同步 → 变更计划 → 开发修复 → PR 提交 → 评审应对 → 合并清理
repo-skill-  issue-       github-      change      github-    github-   pr-        github-
scout        finder       contribution  plan        contribution contribution review     contribution
```

> 第一步不是找 issue，而是读懂仓库自己的 Agent 规则层（`AGENTS.md` 深链、`.agents/skills` 等）：
> 评审判决的验收标准几乎都住在那里，且多数仓库**没有中心索引**，需要现场重建。

## 许可

MIT

```
讨论区挖掘 → 价值判定 → 发提案(讨论帖/feature issue) → 回评验证 → 才写代码
discussion-  feature-     feature-            标签+维护者    github-
 scout        value        proposer            V4 才放行      contribution
              playbook
```

> 硬门禁：**只有拿到 V4（本仓 feature 类正向标签 + OWNER/MEMBER/COLLABORATOR 明确认可回复）**
> 才允许进入编码。社区点赞多（V2/V3）只养帖，不动代码——feature 的价值由维护者愿不愿合决定。

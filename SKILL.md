---
name: open-source-contributor
description: >-
  把 AI 变成开源贡献搭档：从选题立项、Fork 同步、语义化提交到 PR 评审应对的全流程护航。
  覆盖首次贡献决策、commit/PR/CONTRIBUTING 规范自检、自动化评审机器人应对。
  触发词："开源贡献"、"提 PR"、"first contribution"、"commit 规范"、"评审反馈"、"CONTRIBUTING"。
agent_created: true
metadata:
  version: 1.0.0
  category: 开源贡献
  difficulty: 进阶
  architecture: superpower
---

# 开源贡献者

> 让 AI 成为你的开源贡献搭档——从"该贡献哪个项目"到"PR 被合并"，全程有方法、有规范、有证据。

本技能采用 **superpower 架构**：`SKILL.md` 只做路由，深层 playbook 放 `references/` 按需加载，
细粒度能力放 `skills/` 子技能，确定性自检交给 `scripts/`，可复用模板放 `assets/`。

## 何时使用

- 想给某个开源项目提第一个 PR，不知道从哪入手
- 写好了改动，但不确定 commit message / PR 描述是否规范
- PR 收到维护者或自动化机器人（ClawSweeper/Greptile）的反馈，需要应对
- 要检查仓库 CONTRIBUTING.md 是否完整、是否符合社区门槛
- 维护者要求补 proof、拆小 PR、或质疑架构设计

## 能力索引（超级技能路由）

| 任务 | 读取 / 调用 | 关键词（grep 线索） |
|------|------------|---------------------|
| 选目标项目 / Issue / 切入方式（跨子技能的元决策） | `references/first-contribution-playbook.md` | 首次贡献 选题 立题 项目选择 适合贡献 预检 |
| commit / PR / CONTRIBUTING 规范自检与量化规则 | `references/commit-pr-conventions.md` | 提交规范 commit PR 模板 CONTRIBUTING 约定 语义化 |
| 应对评审反馈、自动化机器人、回复话术 | `references/review-response-playbook.md` | 评审 review 反馈 机器人 维护者 反驳 拆分 |
| 用近期已合并 PR 校准 scope、proof、兼容和评审判断 | `references/merged-pr-gold-cases.md` | merged PR gold case OpenClaw owner proof exact-head |
| 发现高价值 Issue、正向标签与优先级评分 | `skills/issue-finder/SKILL.md` | issue 发现 标签 优先级 good first queueable |
| Fork 预检→分支→修复→PR 全流程与 Proof | `skills/github-contribution/SKILL.md` | Fork 预检 分支 PR owner exact-head proof |
| 社区沟通规范、CONTRIBUTING 解读、AI 披露 | `skills/community-etiquette/SKILL.md` | 社区礼仪 CONTRIBUTING PR描述 AI披露 维护者 |
| PR Review 响应策略与反馈分类 | `skills/pr-review/SKILL.md` | PR review 响应 自动化 分类 conversation |

## 内置脚本（确定性、可重复执行）

放在 `scripts/`，提交前自检规范，挡掉大部分打回重写：

- `scripts/check_contribution.py commit --file <msg>` — 检查 commit 格式/关联 issue/行长
- `scripts/check_contribution.py contributing --file CONTRIBUTING.md` — 检查必含章节
- `scripts/check_contribution.py pr --file <pr_body>` — 检查 PR 描述覆盖模板章节
- `scripts/check_contribution.py selfcheck` — 校验内置资产（配置+模板）0 ERROR

运行示例：

```bash
git log -1 --pretty=%B > /tmp/msg.txt
python3 scripts/check_contribution.py commit --file /tmp/msg.txt
```

## 模板资源

`assets/` 提供可直接套用的规范与模板：

- `assets/PULL_REQUEST_TEMPLATE.md` — PR 描述模板（脚本 `pr` 模式以其 `##` 章节为必检项）
- `assets/commit_conventions.json` — 提交规范配置（脚本 `commit`/`contributing` 的规则来源，可团队自定义）

## 核心原则（始终遵循）

1. **先读目标规则**：把根级/scoped 指南、安全政策、CODEOWNERS 和当前 PR 模板当硬性合约。
2. **单一问题、早沟通**：用共享不变量定 scope；产品/兼容/安全大改先讨论，不在共享 base 开发。
3. **证据驱动**：按风险提供测试、终端、日志、截图/录屏或真实行为 proof；声称"已测试"前真跑过。
4. **渐进式加载**：先读路由表与对应 `references/`，再动手，不凭记忆猜命令。
5. **明确边界**：优先用目标仓库模板；内置脚本/模板只作已配置的 fallback，不改代码或替维护者决策。
6. **尊重维护者**：用证据响应评审；仅在已核对的自己 topic branch 必要时用 `--force-with-lease`。

## 与其他技能协作

- 改完代码需要版本管理策略 → `skills-repo/devops-engineer`
- 涉及 CI 流水线配置 → `skills-repo/devops-engineer`
- 贡献的是前端组件 → 配合 `skills-repo/figma-master` 的组件库流程

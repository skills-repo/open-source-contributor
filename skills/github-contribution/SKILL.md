---
name: github-contribution
description: GitHub Fork→分支→修复→PR 全流程；用于状态核验、根因计划、证据与评审应对
source:
  type: derived
  repo: skills-repo/open-source-contributor
  path: skills/github-contribution/SKILL.md
  version: 1.9.0
  updated: "2026-11-21"
  url: https://clawhub.ai/skills/github-contribution
metadata:
  category: 贡献
  platform: GitHub
  difficulty: 进阶
---

# GitHub 贡献工作流

> 先确认规则、身份与工作树，再沿根因 owner 完成修复、证据、PR 和评审闭环。

## 规则优先级

1. 先读目标仓库根级和 scoped `AGENTS.md` / `CLAUDE.md`、`CONTRIBUTING.md`、
   `SECURITY.md`、`CODEOWNERS`、Issue/PR 模板。
2. 以目标仓库当前规则、默认分支、工具链和模板为准；本技能只提供 fallback。
3. 实时核对 issue、关联 PR、当前默认分支、依赖契约、CI 和 review；不要用历史快照替代。
4. 先判断源码是否可信。不要在未审查的 fork 本地运行安装钩子、脚本、测试或 CI wrapper；
   按目标仓库要求使用隔离、无 secrets 的 CI/远程环境。
5. 把本地验证、commit、push、PR、CI、review、merge 分开报告；前一项完成不代表后一项完成。

## 工作流

1. **状态预检**：确认 GitHub 身份、仓库、remote 角色、默认 base、当前分支和 dirty tree 归属。
2. **立题核验**：确认问题仍存在；检查 issue、重复/关联 PR、历史修复、当前和已发布行为。
3. **证据地图**：定位失败行、入口、architectural owner、caller/callee、共享不变量、sibling surface、
   现有测试和依赖契约。缺项先调研，不急着改代码。
4. **修复计划**：写清 Problem、Expected、Root cause/owner、Canonical fix、Risk/siblings、Proof plan、
   Non-goals。范围由被违反的不变量决定，不由固定文件数或“最小 diff”决定。
5. **安全建分支**：从已核对的 `upstream/<base>` 新建 topic branch；只修改和暂存授权路径。
6. **尽早公开进度**：用户要求或已授权提前占位时，按下方草稿流程在上游允许的最早时点创建有实质进展的 Draft PR，
   关联真实 issue 并标明未完成工作；不要等到全部长耗时验证结束才让其他贡献者看到进度。
7. **实现修复**：在事实产生处或生命周期 owner 修复；优先复用 canonical flow，删除同一不变量下的
   重复 retry、fallback、policy 或 dead path。
8. **按风险验证**：证明原失败、修复后的 owner boundary、sibling paths 和用户可见行为；依赖行为先核
   官方文档/源码/类型。从目标规则/package scripts 核实 exact command 和 wrapper，未核实时保留占位符，不猜命令。
   记录 exact head SHA，并明确 unit、mock、真实 Gateway/provider/channel、生产证据边界。
9. **完成 PR**：优先使用目标仓库当前模板；持续更新 PR body，写 Problem、Why、User impact、Evidence、
   Risk/compatibility、LOC、Not tested。只有真实关系或仓库规则要求时才用 `fixes #N`。
10. **处理评审**：先读最新 bot/maintainer finding 和行动项；修复或用证据解释。按仓库历史策略组织 commit，
   不强制“一条反馈一个 commit”。行为或证据 head 改变后，再按项目规则请求 re-review。

## 提前草稿 PR 与防止重复开发

适用前提：用户明确要求或已持续授权提前公开进度；目标仓库允许该时点的 Draft PR。用户没有授权时，
不得仅凭技能自行公开 PR。提交前复查 issue 正文、指派、评论、时间线、按编号和主题搜索的开放/已合并 PR、
当前默认分支，以及作者 PR 限额；搜索结果不能证明没有未公开工作。已有认领、竞争实现、`no-new-fix-pr`、
维护者要求先讨论、产品/安全决定或权限审查门槛时，尊重这些边界，不用草稿绕过。

先核实问题或需求、实现范围与可行验证，按上游要求完成真实入口复现及提交前检查；在独立分支提交**实际工作**，
例如符合仓库要求的最小实现和相应验证。不要用空提交、无关文件、虚构 proof 或纯“占坑”绕过 PR 规则。
上游只允许先开草稿再完成某项构建时，先核实该例外条件并明确记录缺口；上游要求检查在任何 PR 前完成时，
必须先完成。明确该时点不能满足规则时，先继续可做的本地工作，不发送占位 PR。

创建草稿时，标题和 PR body 标明 WIP，关联准确 issue，简述问题、拟采用的范围、已有实际进展、已执行检查、
尚未完成的测试/构建/live proof 和下一步。草稿本身是公开的进度信号，不自动代表 issue 已分配，也不能保证
独占或阻止他人同时开发；不要顺带发送未授权的 issue/Discord 消息或手动添加维护者标签。遵守上游模板与
作者开放 PR 数量上限；不要批量占位或为长期搁置的问题创建草稿。

发布后持续实施；在每次重大变更和转正式前重新核对 issue、维护者意见与并行 PR。遇到冲突或上游另有实现时，
停止重复开发并报告，保留自己的工作；依用户授权和项目流程决定交接或后续处理。按上游门槛完成相关测试、
构建、真实行为证据与必要截图、独立审查，并核对精确 head 后才转正式 PR；草稿未运行 CI 时不可声称 CI 通过。

经验：例如处理 [#202657](https://github.com/openclaw/openclaw/issues/202657) 时，独立实现和浏览器验证进行期间，
另一位贡献者的 [#202678](https://github.com/openclaw/openclaw/pull/202678) 已先提交。同类高活跃项目应在符合其
贡献规则且有实质进展后尽早发草稿、持续查重，减少重复劳动；这不是对未来独占权的保证。

## 安全预检命令

```bash
git status --short --branch
git branch --show-current
git remote
git config --get-regexp '^remote\..*\.url$' |
  sed -E -e 's|(https?://)[^/@]+@|\1<redacted>@|' -e 's|[?#].*$|<redacted>|'
gh repo view <owner/repo> --json defaultBranchRef --jq '.defaultBranchRef.name'
rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g 'CONTRIBUTING*' -g 'SECURITY.md'
```

不要在输出中暴露 remote userinfo、token、cookie 或 secrets；发现 URL 嵌入凭据时，只报告风险并单独请求轮换/脱敏授权。

核对结果后再创建分支：

```bash
git fetch upstream --prune
git switch -c fix/<topic> upstream/<base>
```

若当前 worktree 含他人或未归属改动，保留现场并改用独立 worktree，或先请求用户决定。不要把
`reset --hard`、`clean -fdx`、stash、rebase 或 force push 当同步默认值。确需改写自己的 topic branch 时，
先核对目标和恢复点，只对自己的 fork 使用 `--force-with-lease`；不要改写 upstream 或共享 base。

## Proof 记录模板

```markdown
- Claim: <要证明的行为>
- Exact head: <SHA>
- Surface: <实际运行的生产路径或测试路径>
- Scenario: <输入、执行顺序、边界值>
- BEFORE / control: <原失败或等价负控>
- AFTER: <修复后的可观察结果>
- Siblings: <共享不变量的其他路径>
- Environment: <版本、平台、依赖/provider/channel>
- Limits / not tested: <mock、loopback、真实环境、生产之间的边界>
```

证据形式按风险选择：终端输出、测试/CI、日志、截图、录屏、artifact、真实服务或 live channel 都可以。
视觉改动使用 before/after 媒体；外部 API 行为优先给脱敏 live proof；mock/loopback 不得称为真实租户或生产证明。

## OpenClaw Gold Cases

为 OpenClaw 贡献、应对 ClawSweeper，或设计 owner-boundary / lifecycle / compatibility / proof 时，读取
`../../references/merged-pr-gold-cases.md`。其中包含 2026-08-11 最近 100 个合并 PR 的冻结快照、统计、
可迁移案例和禁止照搬项。使用前重新查询当前规则、PR、CI、标签和 review；不要手工添加 bot/maintainer
控制的 proof、rating、status 或 merge 标签。

## Closeout

完成前逐项报告：

- 工作树边界与变更文件
- 原失败、owner 修复、sibling 和用户可见 proof
- production / tests / docs-generated LOC
- commit SHA 与 push remote/branch
- PR URL、exact-head CI、review/action items
- merge 状态与仍未验证的 proof gap

不要用“测试通过”代替“已 push”，不要用“PR 已开”代替“CI/review 已通过”，不要用 bot 高评分代替维护者合并决定。

## 限制

- 不替代目标仓库的贡献、安全、许可和发布规则。
- 不替用户执行 CLA、DCO、法律声明或生产授权判断。
- 不把单个项目或单次 100-PR 快照的统计相关性写成通用合并公式。

## 相关参考（Playbook）

- 提交与 PR 规范 → [`references/commit-pr-conventions.md`](../../references/commit-pr-conventions.md)：量化规范 + 自检清单，提交前跑 [scripts/check_contribution.py](../../scripts/check_contribution.py)。
- 首次贡献决策 → [`references/first-contribution-playbook.md`](../../references/first-contribution-playbook.md)：选题 → 立项 → 切入的元决策。
- 已合并 PR Gold Cases → [`references/merged-pr-gold-cases.md`](../../references/merged-pr-gold-cases.md)：真实案例校准（正文中已引用）。
- 评审应对 → [`references/review-response-playbook.md`](../../references/review-response-playbook.md)：收到反馈后的带 SLA 处置流水线。

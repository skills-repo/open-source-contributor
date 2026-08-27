# 首次贡献决策手册（First Contribution Playbook）

> 子技能 `issue-finder` / `github-contribution` 告诉你"怎么找 Issue"和"怎么提 PR"，但没回答一个更前置、也更常被卡住的问题：**我到底该从哪个项目、哪个 Issue、用哪种方式切入第一次贡献？** 这篇 playbook 把"选题 → 立项 → 切入"这条横跨多个子技能的元决策显性化，提供可勾选的决策树与选型矩阵。

## 1. 决策树：先判断"适不适合现在贡献"

```
Q1: 这个项目你今天能否跑起来？（依赖、环境、测试命令都通）
 ├─ 否 → 暂不做代码贡献，改做文档/Issue 复现/翻译类低门槛任务
 └─ 是 → Q2

Q2: 维护者对"外部贡献"的态度如何？
 ├─ CONTRIBUTING.md 缺失且无 good first issue → 风险高，先开 Issue 探口风再动手
 ├─ 有 good first issue / help wanted → 低风险，直接进入 Q3
 └─ 明确写"暂不接收外部 PR" → 放弃，换项目

Q3: 你手上的时间窗口？
 ├─ < 2 小时 → 只做单文件 typo / 文档 / 测试补全
 ├─ 半天 ~ 1 天 → 一个独立 bug fix（单文件或单模块）
 └─ > 1 天 → 可接 feature，但必须先开 Issue 讨论方案
```

**关键原则**：第一次贡献的目标不是"显得厉害"，而是"干净合入、留下好印象"。选小不选大。

## 2. 选型矩阵：4 类首贡献任务的成本/收益

| 任务类型 | 合并难度 | 维护者好感 | 适合场景 | 落入的子技能 |
|----------|----------|------------|----------|--------------|
| 文档/README 修正 | ★ | ★★ | 想熟悉仓库结构、零代码风险 | community-etiquette |
| typo / 死链修复 | ★ | ★★ | 十分钟就能合入的破冰 | github-contribution |
| 单测补全 (test gap) | ★★ | ★★★ | 展示你读得懂代码、且不破坏主流程 | github-contribution |
| bug fix（有 issue 锚定） | ★★★ | ★★★★ | 已有 `queueable-fix`/`source-repro` 标签 | issue-finder → github-contribution |

> 经验值：文档类贡献合并率最高、风险最低，是建立"可信任贡献者"画像的最佳起点；但权重低，别停留太久。bug fix 一旦合入，信任积累最快。

## 3. 立题四问（动手前必须回答）

在写任何代码前，用下面四问做自我审查。任一答不上来，先退回调研：

1. **复现路径**：我能在本地稳定复现这个现象吗？（没有复现 = 没有 fix 资格）
2. **最小修改面**：改动是否收敛在单一文件/单一模块？能否不碰公共 API？
3. **测试证据**：我有没有可以运行的测试来证明"之前失败 / 之后通过"？
4. **回退成本**：如果维护者拒绝，这份改动要多久能干净撤回？

四问全过 → 进入 `github-contribution` 的 5-Point 变更计划；任一不过 → 在 Issue 里先抛"复现 + 怀疑根因"，等维护者确认再写代码。

## 4. 可执行的预检命令

```bash
# 1) 快速判断项目活跃度与贡献友好度
gh api repos/<owner>/<repo> --jq '{open_issues: .open_issues_count, pushed: .pushed_at, archived: .archived}'

# 2) 扫描"可贡献"正向标签（具体到本项目标签体系可能不同，先列出来）
gh api repos/<owner>/<repo>/labels --paginate | jq -r '.[].name' | grep -iE 'good.first|help.wanted|queueable|source-repro|fix-shape|easy'

# 3) 确认 issue 仍开放且无人认领（无关联开放 PR）
gh issue view <num> --json state,assignees,title
gh pr list --repo <owner>/<repo> --search "<keyword>" --state open

# 4) 本地能否跑通测试（合入前的硬门槛）
# 注意：不同项目命令不同，先读 CONTRIBUTING / package.json scripts / Makefile
```

## 5. 典型坑与规避

| 坑 | 表现 | 规避 |
|----|------|------|
| 闷头写大 PR | 改了 20 个文件，维护者直接关掉 | 先开 Issue 讨论，再拆成 ≤3 文件的 PR |
| 没读 CONTRIBUTING | PR 被要求补 DCO 签名 / 改 base 分支 | 把 CONTRIBUTING 当合约逐条过（见 `commit-pr-conventions.md`） |
| 在 main 上直接开发 | 无法干净 rebase 上游，冲突爆炸 | 永远从 `upstream/main` 切功能分支（见 `github-contribution`） |
| 抢已被认领的 issue | 与别人重复劳动，双方 PR 被拒 | 看 `assignees` 与开放 PR 列表（命令见上） |
| 用裸 `--force` 推 | 冲掉 review 线程，激怒维护者 | 仅用 `--force-with-lease`，且只在自己 fork 的 main |
| 假"已测试" | 声称跑过测试实际没跑 | 贴 BEFORE vs AFTER 终端输出（见 `github-contribution` Live-Proof） |

## 6. Fork 工作流命令详解

```bash
# 添加上游并同步（保持 fork 与上游一致）
git remote add upstream https://github.com/<owner>/<repo>.git
git fetch upstream
git checkout main
git merge upstream/main          # 或 rebase，保持线性
git push origin main

# 功能分支（永远不在 main 开发）
git checkout -b fix/issue-5968 upstream/main
# ... 开发、提交（语义化）...
git push -u origin fix/issue-5968
```

> 推自己 fork 可用 `--force-with-lease`（安全）；**绝不**对 upstream 用裸 `--force`。

## 7. CONTRIBUTING 解读清单

读 CONTRIBUTING.md 时提取并打勾：
- [ ] 分支策略（base 分支是 main 还是 dev？）
- [ ] 提交规范（是否要求 Conventional Commits / DCO 签名）
- [ ] 测试命令（怎么跑、覆盖要求）
- [ ] PR 模板（必填哪些 section）
- [ ] 许可与 CLA（贡献即授权？）

读不懂任一条 → 先在 Issue 问，别猜。

## 8. 实战：首次给 openclaw 提一个文档 PR

```
1) 选目标：openclaw/openclaw，有 good first issue 标签 → 低风险
2) 立题四问：
   - 复现？文档修复无需复现，但能本地构建文档 ✅
   - 最小面？只改 1 个 .md ✅
   - 测试？文档站构建通过 ✅
   - 回退？删 1 文件即可 ✅
3) 切分支：git checkout -b docs/fix-readme upstream/main
4) 改 README 的接口示例错误
5) 本地构建文档通过
6) 提 PR：fix(docs): 修正 README 快速开始示例 (fixes #5968)
7) 套 PR 模板，附构建输出（非截图）
```
全流程未碰 main、改动 1 文件、带 issue 关联、proof 充分 → 高合并率。

## 9. 选题反模式（扩展）

| 反模式 | 后果 | 修正 |
|--------|------|------|
| 闷头写大 PR | 被关 | 先 Issue 讨论 |
| 没读 CONTRIBUTING | 被打回 | 当合约读 |
| 在 main 开发 | 难 rebase | 功能分支 |
| 抢已认领 issue | 重复劳动 | 查 assignees |
| 裸 force 推 | 冲线程 | --force-with-lease |
| 假"已测试" | 失信 | 真跑 |
| 选僵尸项目 | 石沉大海 | 查最后 push |
| 首贡献做架构 |  overload | 从文档/typo 起 |
| 忽略标签体系 | 低合并率 | 找正向标签 |
| 一次改多库 | 难审 | 单库单 PR |

## 10. 首次贡献检查清单

- [ ] 已确认项目能本地跑通（Q1 = 是）
- [ ] 已读 CONTRIBUTING.md，提取合并前置条件
- [ ] 已确认目标 Issue 开放、无人认领、有正向标签
- [ ] 立题四问全部通过（复现/最小面/测试/回退）
- [ ] 已切出独立功能分支，不在 main 开发
- [ ] 改动收敛在 ≤3 文件
- [ ] 已准备 BEFORE vs AFTER 证据（终端输出，非截图）
- [ ] 已选定将要落到哪个子技能的流程（issue-finder / github-contribution / pr-review）

## 11. 何时该放弃这个项目

出现以下任一信号，果断换项目比硬刚更划算：
- 最后一次 push 超过 12 个月（僵尸项目，PR 大概率石沉大海）
- `archived: true`
- 维护者在历史 Issue 里明确拒绝外部 PR
- 你连续两次在 Issue 提问都被无视

> 开源贡献是**长期博弈**，不是一锤子买卖。第一次合入的目标只是"在维护者心里挂上号"，选对战场比写对代码更重要。

## 相关子技能与层次边界

- 找 Issue → [`skills/issue-finder`](../skills/issue-finder/SKILL.md)：本手册解决"选哪个项目/Issue 切入"的元决策，具体的标签扫描与优先级评分交给 issue-finder。
- 执行工作流 → [`skills/github-contribution`](../skills/github-contribution/SKILL.md)：立题四问通过后进入 github-contribution 的 5-Point 变更计划。
- 软规则 → [`skills/community-etiquette`](../skills/community-etiquette/SKILL.md)：文档/typo 类首贡献与维护者互动礼仪。
- 关联手册：提交规范见 [`commit-pr-conventions.md`](commit-pr-conventions.md)，评审应对见 [`review-response-playbook.md`](review-response-playbook.md)。
- 层次边界：本篇是**前置选题决策**（子技能执行之前），不重复 issue-finder 的扫描命令，也不重复 github-contribution 的修复流程。

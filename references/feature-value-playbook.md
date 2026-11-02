# Feature 价值判定与验证 Playbook

> `discussion-scout` 判价值、`feature-proposer` 做验证，本篇把这条**跨子技能链路**的判据与
> 命令显性化。既有 `first-contribution-playbook.md` 的「立题四问」面向**缺陷**（复现/最小面/
> 测试/回退），不适用于 feature——缺陷有客观对错，feature 只有"维护者要不要、社区等不等得起"。
> 本篇补的是后者。
>
> **判据来源**：讨论区挖掘范式无可借鉴实现（30+ 关键词检索为空）；价值判据借自
> `phuryn/pm-skills@analyze-feature-requests`（2.8K）、`posit-dev/skills@maintainer-decline`、
> `lignertys/reddit-research-skills@reddit-research`（11.4K，非结构化社区帖→诉求提炼）；
> 标签机制借自 `mattpocock/skills@triage`（1.02M）、`samber@oss-issue-triage`（12.6K）。

## 1. 决策树：这条线索要不要投入

```
D1: 仓库开启了 Discussions 吗？（hasDiscussionsEnabled）
 ├─ 是 → 走 Discussions 通道（--mode discussions）
 └─ 否 → **不要放弃**：改走 feature 标签 issue 通道（--mode issues）
          先 gh api repos/<o>/<r>/labels 列本仓真实 feature 类标签，再检索开放 issue
          评论串同样能读维护者立场（issues/<n>/comments 的 author_association）
 → D2

D2: 这个诉求已成文吗？（issue 搜索 + Ideas 分类去重）
 ├─ 已有 open issue 且带正向标签 → 不是空白，改做"认领已有"，走 issue-finder
 ├─ 已有 closed issue（state_reason=not planned / duplicate）→ 高概率被拒，除非你有新证据
 └─ 未见成文 → D3

D3: 维护者表态过吗？（读讨论帖评论的 author_association）
 ├─ OWNER/MEMBER/COLLABORATOR 正面 → 候选 C3，进入验证（预期拿到 V3+）
 ├─ 维护者负面/暂缓（"not a priority"/"out of scope"/"we plan to…"）→ 放弃
 └─ 无人回应 → D4

D4: 社区热度够吗？（upvoteCount 扣自建票，评论数，非作者参与人数）
 ├─ upvote ≥10 或 评论 ≥5 → 候选 C2/C3，值得养帖：发讨论帖测温度，不提 PR
 └─ 都低 → 观察或放弃（你的判断缺外部支撑，别硬做）

D5: 官方 roadmap 是否明确反对？
 ├─ 读 ROADMAP.md / README 的 Non-goals / 历史拒绝同类 feature 的 issue
 ├─ 明确"不做这类功能" → 放弃（做了必被拒）
 └─ 未表态 → 可以验证，走 feature-proposer
```

**核心原则**：feature 的"有开发价值"不由你觉得酷决定，由**维护者愿不愿意合**决定。
所以验证的目标产物是**一个标签和一条认可回复**，不是点赞数。

## 2. 立题五问（feature 版，动手写码前必答）

对应缺陷版「立题四问」，此处五问全部答"是"才允许进入 `github-contribution`：

1. **痛点真实吗**：有具体场景说明"现在做不到 X，代价是 Y"，而不是"有了 X 会更酷"？
2. **没它会同归于尽吗**：现有 workaround 的代价是否已被写进提案（维护者第一问就是"你怎么绕过"）？
3. **维护者背书了吗**：拿到 V4（正向标签 + 维护者明确认可回复）？
4. **我切得出最小片吗**：能不能只实现第一个可交付子集，其余留作后续 PR？
5. **被拒后我认吗**：若维护者说 no，这份投入能接受沉没吗？（架构级改动通常答"不认"→ 别提）

## 3. 验证阶梯与取数（V1–V4）

| 档 | 信号组合 | 取数命令 |
|---|---|---|
| V4 | 本仓 feature 正向标签（`enhancement`/`roadmap`/`accepting-pr`/`design-approved`）+ 维护者认可回复 | `gh api repos/<o>/<r>/issues/<n> --jq '.labels'` + `.../issues/<n>/comments --jq '.[].author_association'` |
| V3 | 正向标签 + `upvoteCount ≥ 10` 或 ≥5 名非作者参与者 | GraphQL `upvoteCount` / `comments{totalCount}` |
| V2 | 有热度、维护者 >7 天未回应 | 同上 |
| V1 | `closed`+`state_reason=not planned\|duplicate`、`wontfix`/`rejected`/`needs-more-info`、明确反对、或 14 天零回应 | `gh api repos/<o>/<r>/issues/<n> --jq '{state,state_reason: .closed_reason}'` |

> **标签名先列本仓体系再用**，不要照抄裸标签。本仓实例：`openclaw/openclaw` 的 bot 标签带
> `clawsweeper:` 前缀，裸 `queueable-fix` 检索恒返 0（见 `issue-finder` 同一坑）。
> ```bash
> gh api repos/<owner>/<repo>/labels --paginate | jq -r '.[].name' | grep -iE 'enhance|roadmap|accept|help.want|good.first|design|priority'
> ```

## 4. API 事实表（2026-11-02 实测，写命令前先对齐）

| # | 事实 | 后果 |
|---|---|---|
| 1 | `gh` 无 `discussions` 子命令 | 一切走 `gh api` |
| 2 | REST `GET /repos/{o}/{r}/discussions` 可用，字段含 `category/comments/labels/reactions/author_association/answer_chosen_at/state` | 读侧够打分 |
| 3 | REST `?category=` 与 `?sort=top` **静默忽略**（HTTP 200 但未过滤/未排序） | **必须客户端过滤排序**，否则自信地错 |
| 4 | `/repos/{o}/{r}/discussion_categories` → **404** | 分类只能 GraphQL `discussionCategories` |
| 5 | **Search API 搜不到 discussions**（`is:discussion` → `total_count 0`；`SearchType` 无 `DISCUSSION`） | **只能逐仓枚举**，无跨仓扫描 |
| 6 | GraphQL Discussion 字段是 `upvoteCount`（非 `upCount`），**无 `state`**（用 `closed`+`stateReason`），有 `isAnswered/poll/answerChosenAt/reactionGroups` | 字段名写错直接报错 |
| 7 | `ReactionGroup` **无 `count`**，计数在 `reactors{totalCount}` | 表情热度取错字段 |
| 8 | `repository.viewerCanCreateIssues` 存在；**`viewerCanCreateDiscussions` 不存在** | 提 issue 可预检，发帖不可（只能试） |
| 9 | 写路径：`createDiscussion(input:{repositoryId,categoryId,title,body})`（**不接受 `discussionCategoryId`**）、`addDiscussionComment(input:{discussionId,body})`、`deleteDiscussion(input:{id})`；REST 评论 POST → **404** | 写只能 GraphQL，且入参必须 `input` 包裹 |
| 10 | 新帖创建者自带 1 票（`upvoteCount` 初始 = 1），`authorAssociation=MEMBER` | 打分须扣自建票，否则自证热度 |
| 11 | `hasDiscussionsEnabled` 是硬性 pre-flight；开启需 `PATCH -f has_discussions=true`（需管理权限） | 第三方仓多半没开，别假设可用 |
| 12 | **过半主流项目未开 Discussions**（实测 vscode / cargo / kubernetes / openclaw = false，next.js / deno = true） | 必须双通道，无 Discussions 时挖 feature 标签 issue 评论串 |
| 13 | **`author_association` 低估维护者**：vscode 核心团队 `joaomoreno`/`jrieken` 仅报 `CONTRIBUTOR` | V4 判据要交叉 CODEOWNERS 与近期提交者，不能只看该字段 |
| 14 | **`gh api search/issues -f q=...` 返回 404**，同一查询 URL 编码进路径才通 | 脚本里 search 一律走 `search/issues?q=<urlencode>` |
| 15 | **标签名各仓不同且会漂移**：vscode 现行 `feature-request`（旧名 `Feature Request` 返 **0**）；cargo 用 `C-feature-request`；k8s 用 `kind/feature`，正文在独立仓 `kubernetes/enhancements`（KEP） | 先列本仓标签再检索，跨仓照抄标签名必错 |

## 5. 重复检测（发帖前必做）

同一诉求常在 Ideas 分类和旧 issue 里各出现一次，重复开帖是信任损耗。

```bash
# 1) 讨论区内查重（Search 不可用 → 拉列表客户端匹配）
python3 scripts/mine_discussions.py --repo <o>/<r> --limit 100 --json | grep -i "<关键词>"
# 2) issue 侧查重（Search 对 issue 可用）
gh search issues --repo <o>/<r> "<关键词>" --limit 10 --json number,state,title,labels
# 3) 已实现查重（最容易被忽略）——搜代码而不是搜讨论
gh search code --repo <o>/<r> "<能力关键词>" --limit 5
```

命中即**并入旧线程**（评论补充），不要新开。

## 6. 常见坑

| 坑 | 规避 |
|---|---|
| 把方案当问题写，第一句就是"建议加个 --foo 参数" | 先写"做不到什么 + 代价"，方案后置 |
| 一开口要整个能力 | 主动切最小片，声明"我先做 A" |
| 把社区点赞当维护者认可 | C2 不许开工，只许养帖 |
| 认定"项目没开 Discussions = 没有讨论区" | 过半主流项目没开（vscode/cargo/k8s/openclaw），需求在 feature 标签 issue 的评论串里 |
| 只用 `author_association` 判定维护者 | 核心团队可能只报 CONTRIBUTOR（vscode 实测），须交叉 CODEOWNERS + 提交史 |
| 用 `gh api search/issues -f q=...` | 实测 404；必须把查询 URL 编码进路径 |
| 自己发帖自己 +1 当成热度 | 扣 1 票（`--self-upvote`） |
| 向第三方仓发测试帖 | 只在自有仓测，测后 `deleteDiscussion` 清理 |
| 发了就忘 | 7 天 / 14 天两个复查点，用 `pr-landing-monitor` 的盯守思路挂个定时 |
| 维护者说"we plan to do this" 就开写 | 那是暂缓不是背书，继续等 V4 |

## 7. 标签映射层（发出前先建表，别照抄 canonical 名）

抄 `mattpocock/skills@triage`（1.02M 安装）的做法：**维护 canonical → 本仓实际标签映射表**。
同一语义各仓叫法不同（本组织实例：`openclaw/openclaw` 用 `clawsweeper:fix-shape-clear`，裸标签检索恒返 0）。

| canonical | 本仓可能叫法 |
|---|---|
| `type/feature` | `enhancement` / `feature request` / `Kind: Feature` |
| `accepting-prs` | `accepting pr` / `help wanted` / `contributions welcome` / `good first issue` |
| `roadmapped` | `roadmap` / `priority:*` / `design-approved` / `tracked` |
| `needs-input` | `needs more info` / `waiting-on-author` / `needs-review` |
| `declined` | `wontfix` / `rejected` / `out of scope` / `no plan` |

建表：`gh api repos/<o>/<r>/labels --paginate --jq '.[].name'`。

**两条铁律**（`samber@oss-issue-triage`，12.6K 安装）：① 置信度不足就打 `needs-review` 或不打，**不猜**；
② **自动化永远不得打最高优先级**——本技能的验证评级只是建议，终局标签由维护者决定。

## 8. 检查清单（发提案前）

- [ ] `hasDiscussionsEnabled` 已确认，或已确定走 issue 路径
- [ ] 三处查重都做过（讨论区 / issue / **代码**）
- [ ] 维护者历史表态已读（含被拒的同类 issue）
- [ ] 官方 ROADMAP / Non-goals 未明确反对
- [ ] 提案含"痛点 → workaround → 最小切片 → 愿提 PR"四段
- [ ] 已声明 AI 辅助（`community-etiquette`）
- [ ] 已设 7 天 / 14 天复查点
- [ ] 清楚知道只有 V4 才放行写代码

## 相关

- 判价值 → [`skills/discussion-scout`](../skills/discussion-scout/SKILL.md)
- 发提案与回评 → [`skills/feature-proposer`](../skills/feature-proposer/SKILL.md)
- 存量 issue 评分 → [`skills/issue-finder`](../skills/issue-finder/SKILL.md)
- 缺陷报单 → [`skills/issue-creator`](../skills/issue-creator/SKILL.md)
- 拿到 V4 后执行 → [`skills/github-contribution`](../skills/github-contribution/SKILL.md)
- 层次边界：本篇只讲"要不要做 / 怎么验证"，不重复 discussion-scout 的扫描命令，也不重复 feature-proposer 的入参形态。

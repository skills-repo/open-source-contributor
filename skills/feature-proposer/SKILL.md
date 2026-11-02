---
name: feature-proposer
description: 把判过价值的 feature 落成讨论帖与 feature request issue，再用正向标签回评验证
source:
  type: derived
  repo: paulrberg/agent-skills
  path: skills/yeet/SKILL.md
  version: unversioned
  updated: 2026-11-02
  url: https://github.com/paulrberg/agent-skills/blob/main/skills/yeet/SKILL.md
  also:
    - mattpocock/skills@triage（1.02M 安装，标签状态机 + canonical 映射层）
    - samber/developer-relations-skills@oss-issue-triage（12.6K，两条铁律）
    - github/awesome-copilot@create-github-issue-feature-from-specification（8.9K）
metadata:
  category: 报告+验证
  platform: GitHub
  difficulty: 进阶
---

# Feature 提案与验证闭环（讨论帖 → issue → 标签回评）

> 改编来源：`paulrberg/agent-skills@yeet`（2.6K 安装，含 `create-discussion` / `comment-discussion` /
> `create-issue` 子工作流）与 `github/awesome-copilot@create-github-issue-feature-from-specification`
> （8.9K 安装，走目标仓库自带 `feature_request.yml` 模板）。
> 借用的三套机制：① `mattpocock/skills@triage`（1.02M 安装）的**标签状态机 + canonical 名→本仓实际标签
> 映射层**，正好解 `clawsweeper:` 前缀那类踩坑；② `samber@oss-issue-triage`（12.6K）两条铁律——
> **低置信度不猜标签**、**自动化永远不得打最高优先级**；③ `apache/magpie` 做法——严重度猜测
> **只写进正文、从不作为标签输出**，与本技能"评级须由维护者标签确认"同构。

> 改编之处：原三者是**下行**（已有 spec/plan → 生成 issue）或**维护者侧打标签**，本技能是**上行验证**——
> 把 `discussion-scout` 判出的候选发出去，再用维护者的标签与回应**反证**判断是否成立。

## 能力

- **两条落地路径**：养讨论帖（低承诺、测温度）/ 提 feature request issue（可打标签、可锚定 PR）
- **优先用目标仓自己的模板**：先探测 `feature_request.yml` issue-forms，再 fallback 内置骨架
- **写路径命令均为实测**：`createDiscussion` / `addDiscussionComment` / `deleteDiscussion` 入参形态已验证
- **回评门禁**：只有拿到高级正向标签 + 维护者认可（V4）才放行进入编码

## ⚠️ 写路径实测（2026-11-02，在自有仓库跑通并已清理）

| 操作 | 可用形态 | 踩过的坑 |
|---|---|---|
| 建讨论帖 | GraphQL `createDiscussion(input:{repositoryId, categoryId, title, body})` | **不接受 `discussionCategoryId`**（网上大量示例写错）；需要节点 ID：repository 用 `R_kg…`、category 用 `DIC_kw…` |
| 评论讨论帖 | GraphQL `addDiscussionComment(input:{discussionId, body})` | **REST `POST /discussions/<n>/comments` → 404**，写只能走 GraphQL |
| 提 issue | `gh issue create --repo <o>/<r> --title … --body-file …` | 先查 `repository.viewerCanCreateIssues` 可预检权限；**`viewerCanCreateDiscussions` 字段不存在**，发帖权限无法预检，只能试 |
| 删除（自测清理） | GraphQL `deleteDiscussion(input:{id})` | 需要 `input` 包裹，裸 `id` 参数被拒 |

```bash
# 取节点 ID（一次拿全）
gh api graphql -f query='query($o:String!,$r:String!){repository(owner:$o,name:$r){id discussionCategories(first:10){nodes{id slug}}}}' \
  -f o=<owner> -f r=<repo>

# 发讨论帖
gh api graphql -f query='mutation($rid:ID!,$cid:ID!,$t:String!,$b:String!){createDiscussion(input:{repositoryId:$rid,categoryId:$cid,title:$t,body:$b}){discussion{number url upvoteCount authorAssociation}}}' \
  -f rid=$RID -f cid=$CID -f t='<标题>' -f b='$(cat proposal.md)'

# 探测目标仓是否有 feature_request 模板（有则必须优先用）
gh api repos/<owner>/<repo>/issues/templates 2>/dev/null | head -40
ls .github/ISSUE_TEMPLATE/ 2>/dev/null
gh api graphql -f query='query($o:String!,$r:String!){repository(owner:$o,name:$r){issueTemplates{name template body}}} ' -f o=<owner> -f r=<repo>
```

## 提案文书要求

用 `assets/DISCUSSION_PROPOSAL_TEMPLATE.md`（讨论帖）或 `assets/FEATURE_ISSUE_TEMPLATE.md`（issue）。
两者的硬要求相同，缺一项就不要发：

1. **问题而非方案开头**：先讲"现在做不到什么、代价是什么"，方案放后面
2. **引用原讨论线索**：链接 `discussion-scout` 挖到的帖子，表明不是凭空提
3. **给出最小切片**：明确"我先只做 A 部分"，避免一次要整个能力
4. **主动表态愿意提 PR**：这是验证的真意——维护者若认可，会给 `accepting-pr`/`help wanted` 类标签
5. **AI 披露**：按 [`community-etiquette`](../community-etiquette/SKILL.md) 声明由 AI 辅助起草

## 回评阶梯（对应需求：issues 评级为高级正向标签）

发出后**不是结束，而是开始**。按档判定：

| 档 | 信号 | 取数 | 放行 |
|---|---|---|---|
| **V4 立项确认** | 本仓 feature 类正向标签（`enhancement`/`roadmap`/`accepting-pr`/`design-approved`）**且** 认可回复来自**真实维护者** | `labels` + 评论者身份（见下） | ✅ 唯一可进 `github-contribution` 写代码 |

> **别只信 `author_association`**：实测 vscode 核心团队账号仅报 `CONTRIBUTOR`，用它过滤会漏判真维护者。
> 交叉比对 CODEOWNERS 与近期提交者：
> ```bash
> gh api repos/<o>/<r>/contents/CODEOWNERS --jq .content | base64 -d | grep -oE '@[A-Za-z0-9._-]+'
> gh api "repos/<o>/<r>/commits?per_page=100" --jq '.[].author.login' | sort -u
> ```
> `scripts/mine_discussions.py` 已内置该比对（`codeowners_logins`）。
| V3 强需求 | 正向标签 + `upvoteCount ≥ 10`（扣自建票）或 ≥5 名非作者参与者 | GraphQL `upvoteCount` | 只做 spike，不提 PR |
| V2 待观察 | 有热度无维护者回应，>7 天 | 同上 | 继续养帖，不动代码 |
| V1 否决 | `closed` + `stateReason=duplicate|not planned`、`wontfix`/`rejected`/`needs-more-info`、明确反对、或 14 天零回应 | `state`/`closed`/`labels` | 撤 proposal，回 `discussion-scout` 换候选 |

```bash
# 发出后定期复查（标签名先列本仓体系再用，别照抄裸标签）
gh api repos/<owner>/<repo>/issues/<n> --jq '{state,state_reason: .closed_reason,labels:[.labels[].name],comments:.comments,reactions}'
gh api "repos/<owner>/<repo>/issues/<n>/comments?per_page=30" --jq '.[]|"\(.user.login)|\(.author_association)|\(.created_at)"'
```

> 提醒：`state` 字段**看不出是否已合并**，但 issue 的 `state_reason`（`completed`/`not_planned`/`duplicate`）
> 是关键否决信号；判定认领与重复仍走 [`issue-finder`](../issue-finder/SKILL.md) 的 timeline 五分类，不要用 `linked:pr`。

## 边界

- 不判断值不值得做 → 那是 [`discussion-scout`](../discussion-scout/SKILL.md)
- 不报缺陷 → 那是 [`issue-creator`](../issue-creator/SKILL.md)
- 不写实现代码、不提 PR → 那是 [`github-contribution`](../github-contribution/SKILL.md)
- **不在未获 V4 前开写**；不向第三方仓库投递测试内容（自测请用自有仓库，测后 `deleteDiscussion` 清理）

---
name: discussion-scout
description: 挖掘项目讨论区提炼未成文的 feature 线索，按社区热度与维护者态度判定其开发价值
source:
  type: original
  repo: skills-repo/open-source-contributor
  path: skills/discussion-scout/SKILL.md
  version: 1.0.0
  updated: 2026-11-02
metadata:
  category: 发现
  platform: GitHub
  difficulty: 进阶
---

# 讨论区侦察（Discussions → feature 价值判定）

> **来源边界**：讨论区/RFC/forum 挖掘这一能力，经 30+ 关键词检索（discussions / idea mining /
> feature discovery / pain point / rfc analysis / community signals）**在 skills.sh 与 clawhub 均无现成实现**，
> 故标 `original`；但价值判据**借鉴** PM 侧成熟技能：`phuryn/pm-skills@analyze-feature-requests`
> （2.8K，Opportunity Score）、`posit-dev/skills@maintainer-decline`（拒绝原型反读为合并概率）。

> `issue-finder` 找的是**别人已经报出来的** issue；本技能找的是**还没变成 issue 的需求**，
> 并回答一个更贵的问题：这个 feature **现在**值不值得你投入几天去开发。

## 能力

- **讨论区挖掘**：按分类（Ideas / Feature request / General / RFC）拉取开放讨论帖，提取潜在 feature 线索
- **价值判定**：社区热度（upvote / 评论 / eyes）+ 维护者是否下场 + 新鲜度 + 重复度，输出候选强度 C1–C3
- **重复拦截**：同一诉求是否已成文为 issue（常已在 Ideas 分类或旧 issue 里出现过）
- **验证路径决策**：该发讨论帖养需求，还是直接提 feature issue 试探

## 边界（不越界）

- 存量 issue 的标签评分 → 交 [`issue-finder`](../issue-finder/SKILL.md)，本技能不重复它的池子扫描
- 缺陷（bug）挖掘与报单 → 交 [`issue-creator`](../issue-creator/SKILL.md)
- 发帖/提单动作 → 交 [`feature-proposer`](../feature-proposer/SKILL.md)
- 判定为"值得做"之后写代码 → 交 [`github-contribution`](../github-contribution/SKILL.md)

## ⚠️ 四条会静默失效的 API 事实（2026-11-02 实测）

不知道这四条，挖出来的结果是**自信的错**：

1. **`gh` 没有 `discussions` 子命令**，且 **REST 写讨论帖返回 404** → 读走 REST/GraphQL，写只能走 GraphQL。
2. **REST `?category=<id>` 被静默忽略**——过滤 Ideas 却返回 General/Q&A，而且 HTTP 200。必须客户端过滤。
3. **REST `?sort=top` 同样静默忽略**，返回与无参数完全一致。"最热讨论"取不到，只能自己按信号排序。
4. **Search API 搜不到 discussions**（`is:discussion` → `total_count 0`；GraphQL `SearchType` 无 `DISCUSSION`）→ **无法跨仓扫描，只能逐仓枚举**。
5. **多数主流项目根本没开 Discussions**（实测 `openclaw/openclaw`、`microsoft/vscode`、`rust-lang/cargo`、
   `kubernetes/kubernetes` 均 `has_discussions=false`；`vercel/next.js`、`denoland/deno` 为 true）。
   只支持 Discussions 的技能会在过半真实目标上失效 → **必须有 feature 标签 issue 通道兜底**。
6. **`author_association` 会低估维护者身份**：vscode 核心团队 `joaomoreno`/`jrieken` 只报 `CONTRIBUTOR`。
   单靠 `OWNER|MEMBER|COLLABORATOR` 过滤会**漏掉真维护者**，须与 CODEOWNERS / 近期提交者交叉比对。

补充：`/repos/{o}/{r}/discussion_categories` **不存在（404）**，分类清单只能走 GraphQL `discussionCategories`；
GraphQL 字段是 **`upvoteCount`**（不是 `upCount`）、Discussion **无 `state`**（用 `closed`+`stateReason`）；
表情计数在 `reactionGroups{reactors{totalCount}}`，`ReactionGroup` **没有 `count` 字段**。

## 工作流

```
1. pre-flight：确认仓库开了讨论区
   gh api graphql -f query='query($o:String!,$r:String!){repository(owner:$o,name:$r){hasDiscussionsEnabled}}' -f o=<owner> -f r=<repo>
   false → 本技能不适用，退回 issue-finder 走 issue 池

2. 选通道并看分类（`--mode auto`：有 Discussions 用它，否则自动走 feature 标签 issue）
   python3 scripts/mine_discussions.py --repo <owner>/<repo> --list-categories
   python3 scripts/mine_discussions.py --repo <owner>/<repo> --mode issues   # 强制 issue 标签通道

3. 挖掘 + 打分
   python3 scripts/mine_discussions.py --repo <owner>/<repo> --category ideas --top 8 --dup-check

4. 读维护者信号（判定 V 级的关键，脚本已内置）
   GET /repos/{o}/{r}/discussions/<n>/comments  → 每条的 author_association

5. 用下方判据独立复核，不要只信分数
```

## feature 价值判据（候选强度 C0–C3，独立判断、不外包给热度）

| 级别 | 判定 | 行动 |
|---|---|---|
| **C3 值得做** | 维护者（OWNER/MEMBER/COLLABORATOR）已下场且态度非否定，且 `upvoteCount ≥ 5`、无重复 issue | 进 `feature-proposer` 提验证 issue |
| **C2 有需求无背书** | 社区热度够（upvote ≥ 10 或评论 ≥ 5）但维护者未回应 | 先**养讨论帖**（`feature-proposer` 路径 A），不提 PR |
| **C1 边缘** | 热度低、或帖子 >365 天陈旧、或与已合并实现部分重叠 | 观察，不投入 |
| **C0 否决** |

> **两个轴别混**：本篇 **C0–C3 = 候选强度**（这条线索有多热，脚本输出同此）；
> `feature-proposer` 的 **V1–V4 = 验证阶梯**（我发出去的提案被背书到什么程度）。
> **C3 ≠ 可以开工**，放行写代码只认 V4。 被 `closed`/`stateReason=duplicate|resolved`、被标 `wontfix`/`rejected`/`needs-more-info`、或维护者明确反对 | 放弃并换候选 |

**借用判据一 · Opportunity Score**（源 `phuryn/pm-skills@analyze-feature-requests`，2.8K 安装）：
`机会分 = 重要度 × (1 − 现有满意度)`。重要度看场景普遍性与阻塞代价，满意度看 workaround 是否已够用——
workaround 越能凑合分越低。用它区分"很多人喊"与"真值得做"。

**借用判据二 · 维护者拒绝原型**（源 `posit-dev/skills@maintainer-decline`）：把常见拒绝话术反读成合并概率——
`out of scope` / `not a priority` / `we plan to…` / `use a plugin` / `duplicate of` / `needs more info` /
`won't fix` / `breaking for users`。命中即降级；**别把 "we plan to" 当背书**。

标签名**各仓不同且会漂移**，先列本仓标签再用（实测：vscode 现行 `feature-request`，旧名 `Feature Request`
检索返回 **0**；cargo 用 `C-feature-request`/`C-enhancement`；kubernetes 用 `kind/feature`，
且需求正文在独立仓 `kubernetes/enhancements`（KEP）里，讨论线索要去那里读）。

打分是**筛候选**，不是**下结论**。下结论前必须自己回答 playbook 里的**立题五问（feature 版）**——
尤其「这事没有官方能力会死吗」和「维护者的 roadmap 有没有明确反对方向」。

## 反模式

| 反模式 | 后果 |
|---|---|
| 照抄别仓分类 slug / 标签名 | 检索返回 0，误判"没人提过" |
| 相信 REST `category`/`sort` 参数 | 拿到未过滤数据还以为筛过了 |
| 把 upvote 当维护者认可 | 社区需求 ≠ 官方意愿，V2 直接开工最容易被拒 |
| 不做重复检测就发帖 | 同一诉求第 N 次出现，招致维护者反感 |
| 创建者自带 1 票未扣减 | 自己发帖自己 +1 会被算成需求热度 |
| 试图用 Search API 跨仓扫讨论 | 恒返 0，白跑 |

## 参考

- 判据展开与命令详解 → [`references/feature-value-playbook.md`](../../references/feature-value-playbook.md)
- 讨论区/issue 写入模板 → `assets/DISCUSSION_PROPOSAL_TEMPLATE.md`、`assets/FEATURE_ISSUE_TEMPLATE.md`

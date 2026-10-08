---
name: issue-finder
description: 智能发现高价值 GitHub Issue，正向标签检测和优先级评分找到最佳贡献机会
source:
  type: derived
  repo: skills-repo/open-source-contributor
  path: skills/issue-finder/SKILL.md
  version: 1.6.0
  updated: 2026-07-26
  url: https://clawhub.ai/skills/issue-finder
metadata:
  category: 发现
  platform: GitHub
  difficulty: 入门
---

# Issue 发现器

> 在成千上万的 Issue 中找到最值得投入的贡献机会。不是随便找一个 bug 修，而是找到维护者认可的、有清晰修复路径的 Issue。

## 能力

- **正向标签检测**：识别 queueable-fix、source-repro、fix-shape-clear 等维护者认可标签
- **优先级评分**：按标签组合计算贡献价值（Diamond → Gold → Silver）
- **多仓库搜索**：跨组织搜索高价值 Issue
- **重复检测**：检查是否已有 PR 在处理
- **可行性评估**：修复范围、技术栈匹配、时间估算

## 使用方式

在 Claude Code 中使用 `/issue-finder` 调用。

```
/issue-finder 在 openclaw/openclaw 中找值得修的 issue
/issue-finder 跨多个仓库搜索 good first issue
```

## 正向标签优先级

| 优先级 | 标签组合 | 合并率 |
|--------|---------|--------|
| 🦞 Diamond | queueable-fix + source-repro + impact:* | 90%+ |
| 💎 Gold | fix-shape-clear + impact:* | 80%+ |
| 🔥 Platinum | source-repro + severity:critical | 75%+ |
| 🥈 Silver | good first issue + help wanted | 60%+ |
| ✅ Standard | 单个正向标签 | 50%+ |
| ⚪ Low | 无正向标签 | <30% |

## 工作流

1. 指定目标仓库（单个或多个）
2. AI 扫描仓库标签体系，识别正向标签
3. 搜索带有正向标签的开放 Issue
4. 按优先级排序，检查是否有已有 PR
5. 输出 TOP 5 推荐，含标签组合和预估难度

## 搜索命令

> ⚠️ 标签名**因仓库而异，不要照抄裸标签**。先列标签体系再检索。实例：`openclaw/openclaw` 的 bot 标签带 `clawsweeper:` 前缀（`clawsweeper:queueable-fix` / `clawsweeper:source-repro` / `clawsweeper:fix-shape-clear`），用裸 `queueable-fix` 检索会**返回 0**。

```bash
# 1) 发现标签体系（grep 目标仓库的实际前缀）
gh api repos/owner/repo/labels --paginate | jq -r '.[].name' | grep -iE 'queueable|fix-shape|source-repro|needs-live-repro|impact|good.first|help.wanted'

# 2) 搜索高价值 Issue（用实际前缀）
gh issue list --repo openclaw/openclaw --label "clawsweeper:queueable-fix" --state open --json number,title,labels,assignees,comments

# 3) 认领判定（关键，别跳）—— 见下方"认领判定的三个陷阱"，不要用 linked:pr 或裸 state 字段
#    脚本位于本 skill 根的 scripts/（相对本文件为 ../../scripts/）
python3 ../../scripts/scan_issue_claims.py <owner/repo> <issue-number>...
```

## 认领判定的三个陷阱（2026-09 实测踩全过）

判定"这个 issue 还有没有人做"时，有三个**会直接导致白干**的陷阱。三者叠加时的实测漏判率可达 **46%**（37 个候选中 17 个实际已被认领）。

### 陷阱 1：`-linked:pr` 搜索限定符会漏判

GitHub search 的 `linked:pr` **只索引正文里写了 `Fixes #N` / `Closes #N` 关键字而建立的自动链接**。人工在正文里写 "for #12345"、"Related: #12345" 的 PR 不会被索引。

```
# ❌ 不可靠：会把已被认领的 issue 判为"可做"
label:clawsweeper:queueable-fix -linked:pr
```

### 陷阱 2：已合并 PR 的 `state` 字段也是 `"closed"`

REST/GraphQL 返回的 PR 对象里，**merged 不会体现在 `state` 上**，`state` 只有 `open` / `closed` 两个值。必须读 `pull_request.merged_at`（非 null 即已合并）。

```python
# ❌ 错误：把已合并 PR 误判为"关闭未合并 -> 可重做"
if src["state"] == "closed": bucket = "被拒，可重做"

# ✅ 正确
if pr.get("merged_at"):        bucket = "MERGED"    # 疑似已修复
elif src["state"] == "open":   bucket = "CLAIMED"   # 已被认领
else:                          bucket = "ATTEMPTED" # 曾尝试被拒/放弃
```

### 陷阱 3：`MERGED` ≠ 已修复，必须做代码复核

issue 常常在修复合并后**不被关闭**（尤其在自动化仓库里）。所以 `MERGED` 只能作为"疑似已修复"信号，**必须回到当前 HEAD 检查缺陷是否仍存在**，才能下结论。

反例（实测）：`#140757`（P0 data-loss）有 merged PR，但复核 `src/skills/workshop/service.ts:145-158` 后发现修复已完整落地 → 确实不可做。
正例（实测）：`#122622` 无任何 PR，但复核 `extensions/whatsapp/src/session.ts:466` 确认缺陷仍在 → 可做。

### 正确的四分类

| 分类 | 判定依据 | 行动 |
|---|---|---|
| `CLEAN` | 从未有 PR | **首选**，竞争最低 |
| `ATTEMPTED` | 仅有 closed 未合并 PR | 查前次为何被拒，再决定 |
| `MERGED` | 存在 merged_at 非空的 PR | **必须代码复核**缺陷是否仍存在 |
| `CLAIMED` | 存在 open PR | 放弃 |

判定数据源用 **timeline 的 `cross-referenced` 事件**（含全部 PR 引用），不要用 `linked:pr`：

```
GET /repos/{owner}/{repo}/issues/{n}/timeline?per_page=100
  -> 过滤 event == "cross-referenced"
  -> source.issue.pull_request.merged_at  +  source.issue.state
```

可直接调用本 skill 根目录的 `scripts/scan_issue_claims.py`（相对本文件为 `../../scripts/`）批量执行该判定。

## ⚠️ 认知陷阱：queueable-fix 池会饱和

`queueable-fix` 是维护者"欢迎提 PR"的信号，因此**会吸引 bot 化贡献者抢单**。

`openclaw/openclaw` 两次实测（2026-09-16 / 2026-09-22），池子既大又在膨胀，且**绝大部分已被认领**：

| 日期 | 开放 queueable-fix | 未被认领 | 认领率 |
|---|---|---|---|
| 2026-09-16 | 223 | 抽样 6/6 均已被认领 | ~100% |
| 2026-09-22 | 278 | **37**（且其中 17 个实为误判） | 86.7% |

**关键教训**：未认领比例极低，且**新单也在小时级内被抢**——09-20～09-22 期间新开的 30 个单里，绝大多数在 24 小时内出现 open PR。更关键的是：那 37 个"搜出来像没人做"的单里，**再用 timeline 核实后发现有 17 个（46%）其实已被认领**（见上方"认领判定的三个陷阱"）。

应对：

1. **先精确判定，再投入**：用 `scripts/scan_issue_claims.py` 做四分类，只对 `CLEAN` / `ATTEMPTED` 投入。不要相信 `linked:pr` 和裸 `state` 字段。
2. **抢速度**：只盯最新 queueable-fix 单，小时级内提交，否则必被抢。
3. **换池**：转向竞争小、杠杆高的需求类标签，例如 `clawsweeper:needs-live-repro`（提供可靠 live 复现 + 根因分析即可建立信任，不必先写代码）与 `needs-info`。
4. **避开负向标签**：`no-new-fix-pr`（明确不要新修复 PR）、`linked-pr-open`（已有 PR）。注意：**缺负向标签 ≠ 可做**，负向标签本身也滞后。
5. **优选"无需外部环境即可本地复现"的 issue**：像 WhatsApp/Telegram/Slack 账号、Windows/Termux/iOS/macOS 设备、真实 MCP 服务这类依赖，会显著降低可验证性。优先挑根因已给出源码级定位、且能在本机跑测试验证的单。
6. `linked-pr-open` 标签**滞后不可靠**；认领判定一律以 timeline 的 `cross-referenced` 事件 + `merged_at` 为准。

## 适用场景

- 刚开始参与某个开源项目，不知道从哪入手
- 想提高 PR 合并率，找维护者认可的需求
- 定期扫描多个仓库寻找贡献机会
- 评估项目活跃度和贡献友好度

## 限制

- 依赖项目使用规范的标签体系
- 小项目可能没有正向标签，需要人工判断
- 不保证 Issue 未被其他人认领

## 相关参考（Playbook）

- 首次贡献决策 → [`references/first-contribution-playbook.md`](../../references/first-contribution-playbook.md)：标签扫描命中后，用本手册的"立题四问"判断要不要接。
# Issue Report Playbook —— 把缺陷写成高认可度 issue

> 承接上游两个 playbook 的产物：① [recognized-issue-gold-cases](recognized-issue-gold-cases.md) 的"本仓库认可画像 checklist" + ② [defect-hunting-playbook](defect-hunting-playbook.md) 的"已验证候选缺陷登记表"。本 playbook 负责把候选变成**维护者愿意打正向标签**的 issue。

## 七阶段总览

| 阶段 | 动作 | 产出 / 门禁 |
|------|------|------------|
| 1 该不该报 | 查重 + 分类 + scope | 非重复、非已知限制、scope 匹配 |
| 2 认可度自检 | 对照画像 checklist | 全满足，或补强/降级 |
| 3 复现构建 | 最小复现 + 环境矩阵 + transcript | BEFORE 稳定复现 |
| 4 撰写 | 五段式 / 目标仓库模板 | `check_contribution.py issue` 0 ERROR |
| 5 频道礼仪 | 选频道 + 克制 @ + AI 披露 | 符合 CONTRIBUTING |
| 6 创建后跟踪 | 响应机器人/维护者 | 不被 needs-repro 打回 |
| 7 闭环 | 认领修复 + 资产升级 | 复现资产 → PR test case |

## 阶段 1：该不该报（pre-flight）

**查重**（三步，缺一不可）：

```bash
# a) 关键词搜 issue + PR（标题与全文）
gh issue list --repo owner/repo --search "关键词 in:title,body" --state all --limit 20
gh pr list --repo owner/repo --search "关键词 in:title,body" --state all --limit 20
# b) CHANGELOG / release notes 是否已修
gh api repos/owner/repo/releases -q '.[].body' | grep -i "关键词"
# c) 认领判定（复用本 skill 根 scripts/，相对本文件 ../../scripts/）
python3 ../../scripts/scan_issue_claims.py owner/repo <相关issue号>
```

**分类**（决定报什么）：

- **bug**：当前 main 上可复现的错误行为。
- **回归**：曾正常、某版本后坏——**必须给出行为正常的 commit/tag 与开始出错的版本**，否则按普通 bug 报。
- **已知限制**：先读 docs 与代码里的 fails-closed/限制注释；已记录的走 discussion 讨论"是否该改"，不报 bug。
- **scope**：目标仓库 `CONTRIBUTING`/README 声明 out-of-scope 的**不报**（尊重维护者边界）。

## 阶段 2：认可度自检（对齐画像）

把阶段 1 确认要报的缺陷，逐条对照阶段 ① 产出的"本仓库认可画像 checklist"：

- **全满足** → 进入阶段 3。
- **有缺失** → 要么**补强**（如缺 file:line 就去补定位），要么**放弃/降级**（降级为 discussion/question）。不要带着已知缺陷硬报。

## 阶段 3：复现构建（source-repro 标准）

**优先级**：最小独立脚本 / 最小 config fixture **>** 真实 shipped 入口命令 **>** 测试桩（测试桩证明力最弱，慎用）。

**环境矩阵**（每条复现都要记全，缺一项就可能被 `needs-info`）：

- commit pin：`git rev-parse HEAD` 的 SHA，不只写版本号。
- OS + 版本；runtime 版本（node/python…）；安装方式（release / git checkout / built in place）。
- 相关配置/profile/feature flag。

**terminal transcript 规范**（反向使用 [github-contribution](../../github-contribution/SKILL.md) 的 Live-Proof 规范）：

- **单变量 BEFORE/AFTER**：一次只变一个条件，贴出缺陷触发（BEFORE）与消除（AFTER，若有规避/修复）的终端输出，非截图。
- **多次探针稳定**：同一复现跑 ≥2 次，排除偶发；偶发缺陷要说明触发频率与条件。
- **能复现但无根因也报**：复现完整度优先于根因完整度；Evidence 里如实标注"根因待定位"。

## 阶段 4：issue 文本五段式

**标题**：一行可判定的现象陈述（`[Bug]: <组件> <条件> <后果>`），禁感叹号与"救命"式措辞。

**正文五段**（目标仓库自带模板优先，本模板仅 fallback）：

| 段 | 内容 | 质量标准 |
|----|------|----------|
| Summary | 一句话现象 + 背景 | 维护者 3 秒读懂 |
| Environment | commit SHA / OS / runtime / 安装方式 / 配置 | 含 SHA，可复现环境 |
| Steps to Reproduce | 编号步骤 + 命令 | **期望 vs 实际**并列 |
| Evidence | `file:line` 机制链 + terminal transcript | 非空、无未验证措辞 |
| Suspected Cause & Fix Direction | 根因推测 + 最小修复方向 | 标注"推测"，不强求完整 |

骨架见 [assets/ISSUE_TEMPLATE.md](../../../assets/ISSUE_TEMPLATE.md)，写完后自检：

```bash
python3 ../../scripts/check_contribution.py issue --file /tmp/issue_body.md
```

## 阶段 5：频道与礼仪

- **先读**目标仓库 `CONTRIBUTING` 与 issue 模板的选项（bug / feature / question 分开选）。
- **频道**：明确是 bug 走 GitHub issue；设计问题/"该不该做"走 discussion；有的项目 bug 走 dev channel/Discord——以 CONTRIBUTING 为准。
- **@ 维护者克制**：不 @ 除非 issue 里说明的流程要求；让标签/机器人流程自然分流。
- **AI 辅助披露**：用了 AI 辅助分析/复现，按 [community-etiquette](../../community-etiquette/SKILL.md) 的措辞如实说明，不隐瞒也不过度 apologise。

## 阶段 6：创建后跟踪

- **机器人打分**：认识 `issue-rating`/`ClawSweeper` 等自动评分——它是维护者认可标准的显式编码；低分先看差在哪再回应，别急着争。
- **`needs-info` / `needs-repro`**：按索要项**精准补**（更多日志 / 更小的复现 / 环境细节），补完回一条说明补了什么。
- **`wontfix` / `dup` 关闭**：接受判断；`wontfix` 若与文档冲突，礼貌引证据讨论一次即可，不缠斗。`dup` 去原 issue 补充信息。
- **打了正向标签后是否自己认领**：用 `scan_issue_claims.py` 确认仍是 CLEAN，再按 [issue-finder](../../issue-finder/SKILL.md) 评分决定是否认领；注意 queueable 池饱和、小时级被抢（见 issue-finder"认知陷阱"）。
- **bump 频率**：无进展不超过 1–2 周一次，措辞是"补充新信息"而非"求看看"。

## 阶段 7：闭环

- issue 被认可（正向标签/维护者确认）后，转 [github-contribution](../../github-contribution/SKILL.md) 走 Fork→Branch→Fix→PR 全流程认领修复。
- **资产升级**：修复 PR 关联 issue 时，把 issue 的复现资产（最小脚本 / config fixture / transcript）**升级为 PR 的 test case**——既证明修复，又留下回归防护。PR 描述回引 issue（`fixes #N`）。

## 边界提醒

- 策略提高认可率，**不保证**每个 issue 都被接受；维护者有最终判断权。
- 未复现的候选不进 bug issue（回看 [defect-hunting-playbook](defect-hunting-playbook.md) 的"可证明性门槛"）。
- 不替维护者决策 severity/scope；夸大一次，信任折损长期。

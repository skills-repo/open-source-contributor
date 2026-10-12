# 认可 Issue Gold Cases —— 从语料归纳"本仓库认可画像"

> 对标 `merged-pr-gold-cases.md`（PR 侧）的 issue 侧对应物：用目标仓库**被官方认可**的 issue 语料，归纳出"高认可度 issue"的共同特征画像，作为后续产出与措辞的校准基准。

> **时效分层（2026-10-12 建立）**：本页**方法论**（采集口径、画像维度、置信度规则、checklist 模板）是持久内核；文末 **worked example 的数据是 2026-10-12 快照**，只作演示与历史基准，绝对数字会老化——每次报 issue 前必须按"语料采集"对**同仓库当前**重新跑一遍，不要直接引用快照结论。

## 目录

- [为什么要"认可画像"](#为什么要认可画像)
- [第 1 步：语料采集](#第-1-步语料采集)
- [第 2 步：画像维度（逐维度统计）](#第-2-步画像维度逐维度统计)
- [第 3 步：产出认可画像 checklist](#第-3-步产出认可画像-checklist)
- [置信度规则](#置信度规则)
- [Worked Example：openclaw/openclaw（2026-10-12 快照，示例）](#worked-exampleopenclawopenclaw2026-10-12-快照示例)

## 为什么要"认可画像"

维护者给 issue 打正向标签（`queueable-fix` / `source-repro` / `fix-shape-clear` 等）不是随机的——它是一套**隐式的接受标准**。把这套标准从语料里反推成一页 checklist，报 issue 前逐条自检，就把"会不会被认可"从玄学变成可核对的工程问题。

**认可样本的三个来源**（按可靠性排序）：

1. 带**正向标签**的 issue（最可靠：维护者/机器人主动打了"欢迎修"信号）。
2. 被维护者**明确处理**的 issue（回复 `confirmed` / `good catch` / 主动 assign / 关联进 milestone）。
3. 负向样本同样有用：`wontfix` / `needs-repro` / `no-new-fix-pr` —— 看它们**缺什么**，反向校准。

## 第 1 步：语料采集

> ⚠️ **标签名因仓库而异，且常带前缀**。先发现标签体系，再检索。`openclaw/openclaw` 的正向标签带 `clawsweeper:` 前缀，用裸 `queueable-fix` 检索会**返回 0**。

```bash
# 1) 发现标签体系（grep 目标仓库的实际前缀与正向标签）
gh api repos/owner/repo/labels --paginate -q '.[].name' \
  | grep -iE 'queueable|fix-shape|source-repro|needs-live-repro|impact|good.first|help.wanted|needs-info|confirmed|wontfix|no-new-fix'

# 2) 采集带某正向标签的 issue 语料（含正文，供段落结构分析）
gh issue list --repo owner/repo --label "clawsweeper:queueable-fix" --state all --limit 60 \
  --json number,title,body,labels,author,createdAt,comments,assignees \
  > /tmp/recognized_corpus.json

# 3) 无标签体系的小项目：降级为"维护者回复过 confirmed/good catch 或主动 assign 的 issue"
gh issue list --repo owner/repo --state all --limit 100 --search "in:comments confirmed" --json number,title,labels,author
```

**样本边界**：优先采集"开放 + 近期关闭"两类——开放样本代表**当前**标准，近期关闭样本（带正向标签且已合并/关闭）代表**已被验证**的认可。每条样本记录：`number / title / labels / author / createdAt / comments / assignees`。

## 第 2 步：画像维度（逐维度统计）

对每个维度统计样本分布，找出**被认可样本的共同点**（不是单个案例的巧合）。建议样本 ≥ 20 条再看分布，< 10 条只做定性。

| 维度 | 统计什么 | 为什么预测认可 |
|------|----------|----------------|
| **标题结构** | 现象陈述（`[Bug]: X 在 Y 条件下发生 Z`）vs 疑问式 vs 裸崩溃栈 | 一行可判定的现象陈述让维护者 3 秒定位，省去来回澄清 |
| **正文必备段** | 环境 / 复现步骤 / 期望 vs 实际 / 根因定位 的**出现占比** | 缺任一段都会触发 `needs-info`/`needs-repro` 打回 |
| **复现形态** | 独立脚本 / 最小 config / 真实入口步骤 / 仅文字描述（统计 `source-repro` 样本的复现方式） | `source-repro` 标签的 issue 合并率最高——可复现是认可的硬通货 |
| **根因深度** | 仅现象 vs `file:line` 机制链 vs 附修复方向 | 带 `file:line` 机制链显著降低维护者定位成本，更易 `fix-shape-clear` |
| **报告者身份** | 首次贡献者 vs 常驻 vs 维护者自己；是否影响接受度 | 识别"是否只认维护者报的单"（若是，外部贡献策略要变） |
| **维护者首次响应** | 间隔时长 + 首个响应内容（致谢/追问/直接打标签） | 区分"被认可"与"被礼貌搁置"；响应内容是标准的直接信号 |
| **机器人评分** | 是否有 `issue-rating` / `ClawSweeper` 等自动打分标签及其档位 | 自动评分是维护者认可标准的**显式编码**，直接对齐即可 |

## 第 3 步：产出认可画像 checklist

把统计结论压缩成**一页 ≤10 条硬规则**，报 issue 前逐条自检。规则要**可判定**（能满足/不能满足），不要写成"写得清楚点"这种不可核对的废话。

模板：

```markdown
## <仓库> 认可画像 checklist（样本 N 条，采集于 <日期>）
1. 标题 = `[Bug]: <组件> <在什么条件下> <发生什么可判定现象>`（一行，无感叹号/无"救命"）
2. 正文必含：Summary / Steps to reproduce / Expected vs Actual / Environment（含版本+commit SHA）/ Evidence
3. 复现 = 最小独立脚本或真实入口命令，非测试桩；附 terminal transcript
4. 根因 = 至少给出 file:line 机制链（不强求完整修复）
5. 版本必须 pin 到 commit SHA（`git rev-parse HEAD`），不只写版本号
6. 影响面一句话（哪些用户/什么场景），对齐 impact:* 标签
7. 不提"应该可以复现"类未验证措辞；不确定就标"待验证"并说明验证计划
8. …（按该仓库语料继续补至 ≤10 条）
```

## 置信度规则

- 样本 **≥ 20** 且维度分布有明显共识（如 ≥70% 认可样本都带某特征）→ 高置信，checklist 作硬门禁。
- 样本 **10–19** → 中置信，checklist 作强建议，标注样本量。
- 样本 **< 10** → **低置信**：明确声明"画像置信度低"，**回退到通用标准**（下方最小集），不要用 3 个样本强行归纳。

**通用最小集（任何仓库的低置信 fallback）**：可复现 + 期望vs实际 + 版本/SHA + 一行可判定标题 + 影响面。这套即便无标签体系也不会被维护者反感。

## Worked Example：openclaw/openclaw（2026-10-12 快照，示例）

> ⚠️ **以下为演示方法的演练样例，非持久结论**。数字采集于 2026-10-12，报 issue 前请按上方命令重跑。

### 观察到的标签体系

正向：`clawsweeper:queueable-fix` / `clawsweeper:source-repro` / `clawsweeper:fix-shape-clear` / `clawsweeper:needs-live-repro`；影响面：`impact:*`（`crash-loop`/`data-loss`/`security`/`message-loss`/`session-state`/`ux-friction`…）；负向：`clawsweeper:no-new-fix-pr` / `wontfix` / `clawsweeper:needs-info`。另有**机器人评分标签** `issue-rating: 🦞 diamond lobster` 等档位。

### 抽样 5 条 `clawsweeper:queueable-fix` 开放 issue（2026-10-12）

| # | 标题 | 标签组合 | 作者 |
|---|------|---------|------|
| 169972 | `[Bug]: Managed Codex web_search loses typed timeout and budget at WebSearchProviderError.toResult` | source-repro + fix-shape-clear + queueable-fix + impact:ux-friction + 💎diamond | @letsc4 |
| 169959 | `[Docs Bug]: Stable HTTPS URL Guide troubleshooting` | 同上 + docs | @LeoPiero |
| 169950 | `[Bug]: openclaw status keeps prescribing openclaw update for a weeks-old failed git update…` | source-repro + fix-shape-clear + queueable-fix + impact:ux-friction + 💎diamond | @amittell |
| 169944 | `[Bug]: browser open ignores timeoutMs: tab navigation hard-coded to 30 s…` | 同上 + impact:other + 💎diamond | @aleps001 |
| 169929 | `[Bug]: SVG document sent on Telegram fails the whole turn on every model` | 同上 + impact:message-loss + 💎diamond | @SanderHelgesen |

### 维度观察（以 #169950 正文为样本）

- **标题**：全部 `[Bug]:`/`[Docs Bug]:` 开头 + 一行具体现象（点名组件 + 触发条件 + 可判定后果）。
- **正文段落**（该仓库自带模板）：`Bug type` / `Summary` / `Steps to reproduce` / `Expected behavior` / `Actual behavior` / `OpenClaw version` / `Operating system` / `Install method` / `Model/Provider/routing` / `Logs` / `Impact and severity`。
- **复现形态**：真实入口命令（`git checkout v2026.10.1 && pnpm install && pnpm build && openclaw doctor --fix`），非测试桩。
- **版本/SHA**：`2026.10.1 (Git checkout at v2026.10.1…)`，且 pin 到 `main` 的 `33a3fb23db7`。
- **根因深度**：`Logs` 段给出 `file:line` 机制链（`status-update-restart.ts` Line 71/72/101/28 + `update-run-record.ts:143`）。
- **报告者身份**：抽样作者均为非维护者（@letsc4/@LeoPiero/@amittell/@aleps001/@SanderHelgesen）→ **外部贡献者的单会被认可**，值得投入。
- **机器人评分**：5/5 带 `issue-rating: 🦞 diamond lobster` —— 自动评分即维护者认可标准的显式编码。

### 产出的 openclaw 认可画像 checklist（草稿，快照 2026-10-12）

1. 标题 = `[Bug]: <组件> <条件> <可判定现象>`，一行，禁感叹号。
2. 用仓库自带 issue 模板的字段（Bug type / Summary / Steps / Expected / Actual / version / OS / install / logs / impact）。
3. 复现用真实入口命令 + terminal transcript，不用测试桩。
4. 版本 pin 到 commit SHA（`git rev-parse HEAD`），不只写版本号。
5. `Logs` 段给 `file:line` 机制链（不强求完整修复方向）。
6. 明确 impact 与 severity，对齐 `impact:*` 标签取值。
7. 提交前预估能否拿 `clawsweeper:source-repro`——拿不到就先补复现再报。
8. 不用 `clawsweeper:needs-live-repro` 依赖（外部账号/设备会降可验证性），除非无法本地复现。

> 该 checklist 由 5 条抽样得出，**样本 < 20 属中低置信**，仅作演示；实战请按命令采集 ≥20 条后再固化。

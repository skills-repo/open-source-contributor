# 已合并 PR Gold Cases

> 用真实合并案例校准贡献计划、证据和评审判断。先读本页的样本边界，再复用案例。

## 目录

- [OpenClaw 最近 100 个合并 PR 快照](#openclaw-最近-100-个合并-pr-快照)
- [从样本提取的注意事项](#从样本提取的注意事项)
- [Gold Cases](#gold-cases)
- [复用模板](#复用模板)

## OpenClaw 最近 100 个合并 PR 快照

冻结时间：`2026-08-11T02:16:34Z`。

- 最新：[openclaw/openclaw#121074](https://github.com/openclaw/openclaw/pull/121074)，
  `mergedAt=2026-08-11T02:06:55Z`。
- 第 100：[openclaw/openclaw#121561](https://github.com/openclaw/openclaw/pull/121561)，
  `mergedAt=2026-08-10T14:17:41Z`。
- 第 101：`#115198`，与第 100 相差 38 秒；边界无同秒并列。

### 数据口径

不要把 `gh pr list --state merged --limit 100` 当作“最近合并 100 条”：它的候选集合不保证按
`mergedAt` 完备排序，长期开启后刚合并的 PR 会被漏掉。按以下门禁刷新：

1. 冻结 UTC cutoff。
2. 用 GitHub 官方 API 拉完覆盖该 cutoff 的完整合并日期窗口。
3. 按 PR number 去重，再按 `(mergedAt, number)` 降序。
4. 记录候选总数、抓取数、唯一数、末页 `hasNextPage=false` 和第 100/101 边界。
5. 若改用按 `updatedAt` 分页的候选集，至少证明最老候选 `updatedAt` 早于第 100 条 `mergedAt`；
   因 `mergedAt <= updatedAt`，未抓取项才不可能挤入前 100。

### 量化事实

| 维度 | 结果 | 正确解读 |
|---|---:|---|
| 标题类型 | fix 52；refactor 15；test 11；feat 9 | 修复占主导，但不是“只做 bug 才能合并” |
| 作者 | 16 人；`steipete` 74 条 | 快照受集中维护批次显著影响 |
| `maintainer` 标签 | 90/100 | 不要把总体规模和速度当作外部贡献基准 |
| 规模 | 中位 6.5 文件、212 行 churn；32 条 >500 行 | 用共享不变量定范围，不设固定文件上限 |
| commit | 中位 2；49 条单 commit、51 条多 commit | 按仓库策略和可审查性组织，不设统一数量 |
| 测试/文档 | 91 条改测试；31 条改 docs；仅 5 条两者都未改 | 默认准备 changed-surface 测试，文档按契约影响判断 |
| PR body | Problem 94；Why 93；User Impact 94；Evidence 94 | 问题、理由、影响、证据是稳定高价值结构 |
| LOC | 47 条主动拆 production LOC | 将 production 与 tests/docs/generated 分开解释 |
| exact head | 39 条正文明确提到 | earlier-head proof 不得冒充当前 head |
| merge risk | 49 条至少一个风险标签 | compatibility/session/security 等需单列 owner 与证明 |
| proof 标签 | 11 条任意 `proof:*`；9 条 sufficient | 无 proof 标签不等于无验证；维护者 PR 可能豁免标签门禁 |
| 状态标签 | 已合并后仍有 19 waiting、1 needs proof | 标签会滞后；实时查询且不要由贡献者手工补 bot 标签 |

外部贡献校准：排除 `maintainer` 标签、维护者和自动化作者后，狭义样本只有 6 条；6 条全部修改测试，
创建至合并中位数约 181.5 小时。全量样本约 3.1 小时的中位合并时长不适合作为外部贡献 SLA。

## 从样本提取的注意事项

1. 先证明 premise：问题在当前默认分支仍存在；若涉及兼容，继续查 release tag 和真实外部调用者。
2. 将 Root cause 与 architectural owner 一起写。优先在事实产生处修复，删除消费者层重复 policy、retry 或 fallback。
3. 用 base-red/head-green 或等价负控证明原失败；只贴 head 通过不能证明测试会抓住回归。
4. 标注每份 proof 的 exact SHA。rebase、行为改动或关键证据变化后，重新跑相应 proof。
5. 区分 unit、mock Gateway、real Gateway、live provider/channel 和 production；单列未验证项。
6. 直接检查依赖官方文档、源码、类型和具体版本；同时检查共享不变量的 sibling provider/channel/runtime。
7. 拆分 production、tests、docs/generated LOC；生产增长说明 capability、owner boundary、security 或 public contract 理由。
8. issue 关联、commit 数、文件数和 re-review 节奏以目标仓库规则为准；不要从样本虚构硬阈值。
9. ClawSweeper 的 proof/rating/status 与历史 check failures 可能滞后；核对 exact-head required checks 和最新 durable comment。
10. 长期 PR 可在 current main 上重建为单一问题，删除堆叠旧改动，同时保留原作者 provenance 和已知 proof gap。

## Gold Cases

### 1. #114183：删除重复生命周期策略

[PR #114183](https://github.com/openclaw/openclaw/pull/114183) 修复普通空搜索触发全量 memory reindex。

- **不变量/owner**：索引 bootstrap 和 dirty sync 属于 `MemoryIndexManager`，工具层不应再次 force-sync + retry。
- **修复形状**：生产 `+0/-19`，删除重复生命周期策略；两文件保留 focused regression。
- **证据阶梯**：base-red/head-green、42 个 focused tests、脱敏真实 SQLite 500-file corpus、forced-reindex control、exact-head CI。
- **不要照搬**：真实 SQLite corpus 证明该路径性能，不等于所有 embedding provider/live tenant 都已验证。

### 2. #115106：依赖契约与 sibling owners

[PR #115106](https://github.com/openclaw/openclaw/pull/115106) 修复正数 short read 导致 adopted turn 延迟发现。

- **不变量/owner**：Node `FileHandle.read` 的 length 是上限，只有 `bytesRead === 0` 才是 EOF；ACPX 与 Anthropic 两个文件扫描 owner 都欠同一契约。
- **修复形状**：同时覆盖两个 sibling provider；说明为何不把两个私有 bundled consumers 扩成 Plugin SDK 公共契约。
- **证据阶梯**：真实 `FileHandle` 限制到 17 bytes 的 base-red/head-green、16/16 focused tests、依赖文档、shipped regression range、exact-head CI。
- **不要照搬**：相似代码不必一律抽公共 API；先判断 owner 和公共契约成本。

### 3. #121074：外部 API 的 live wire proof

[PR #121074](https://github.com/openclaw/openclaw/pull/121074) 让已验证的 Ollama Cloud 模型原生发送 `think: "max"`。

- **不变量/owner**：provider policy 和 native request adapter 都要保留已验证模型契约；未验证模型继续兼容回落。
- **修复形状**：检查 Ollama 上游源码/文档和具体契约；覆盖 catalog-light、local、GPT-OSS 等相邻模型边界。
- **证据阶梯**：295 focused tests、exact-head build/checks、真实 Cloud 响应和脱敏 outbound wire trace；review 在补 wire proof 后由 changes requested 变为 approved。
- **不要照搬**：mock transport 无法证明 `max` 未被降成 `high`；公开 proof 也不得暴露 token、prompt、配置或运行身份。

### 4. #121129：资源生命周期和非阻塞 cleanup

[PR #121129](https://github.com/openclaw/openclaw/pull/121129) 修复失败 plugin icon 响应残留连接。

- **不变量/owner**：共享 browser response owner 在 fallback/拒绝前启动取消；cleanup 失败不能替换既有 null-result，也不能阻塞认证 fallback。
- **修复形状**：生产 +12 行，测试 +140 行；第二个 commit 专门消除 await cancellation 的阻塞风险。
- **证据阶梯**：真实 streaming socket 关闭、stalled-cancellation control、5 个 focused tests、exact-head 65-job CI。
- **不要照搬**：测试多于生产代码不是目标；关键是覆盖 cleanup 与主结果的耦合边界。

### 5. #77017：长期 PR 在 current main 上重建

[PR #77017](https://github.com/openclaw/openclaw/pull/77017) 从 2026-05-04 持续到 2026-08-10，最终聚焦生成图片操作。

- **不变量/owner**：managed image 的 preview/action 共用 ticketed artifact owner；删除旧 transcript rewrite、credential retry、Codex callback 和 stacked PR 改动。
- **修复形状**：current-main 重建为一个问题，保留原作者 attribution，并记录 maintainer 的 ticket-scope 安全决定。
- **证据阶梯**：mock Gateway 浏览器交互与 real Gateway + SQLite + HTTP media route 分开描述；另有 Telegram userbot E2E。
- **不要照搬**：stale/failed 历史 check 不代表 final head；只核 exact-head required checks 和最终 disposition。mock Gateway 也不是生产证明。

### 6. #121628：视觉与平台差异 proof

[PR #121628](https://github.com/openclaw/openclaw/pull/121628) 修复 macOS Chromium 下 Shift+F10 不触发菜单。

- **不变量/owner**：一个 keyboard/pointer adapter 覆盖 sidebar、catalog、Sessions table，保留 pointer 坐标、焦点与防双开。
- **修复形状**：修共享输入不变量，而不是加 macOS 分支、合成 mouse event 或放宽测试。
- **证据阶梯**：before/after 截图、screencast、exact macOS Playwright、pointer regression、300 sibling UI tests、exact-head CI。
- **不要照搬**：mock Gateway 只覆盖 UI；PR 明示未用 Safari 物理键盘验证，不应把已知 gap 隐去。

### 7. #121757：只为已发布契约保留兼容

[PR #121757](https://github.com/openclaw/openclaw/pull/121757) 恢复误删的 `gateway.restart.preflight` RPC。

- **不变量/owner**：它自稳定版 `v2026.5.4` 已发布，并有 Mission Control、ClawDeckX、AgentOS 真实调用；不是“也许有人用”的猜测。
- **修复形状**：恢复 exact method/descriptor/handler/response/order/Android enum，标 deprecated；canonical `gateway.restart.request` 不倒退。
- **证据阶梯**：tag/history、真实调用者、198 focused tests、real Gateway/WebSocket、Android 生成 byte-identical、exact-head CI。
- **不要照搬**：测试或潜在调用者不能把内部 API 变成兼容契约；必须先证明 shipped public surface。

### 8. #121674：受控 sink 的证明边界

[PR #121674](https://github.com/openclaw/openclaw/pull/121674) 修复 ClawSweeper dispatch 缺少 authoritative default branch。

- **不变量/owner**：OpenClaw sender 与 ClawSweeper receiver 共享 branch/fingerprint/dedupe contract，必须直接检查跨仓 receiver。
- **修复形状**：production workflow block 在隔离容器执行；sink 捕获唯一 dispatch call，并证明没有 repository lookup。
- **证据阶梯**：按 Claim、Surface、Scenario、Environment、Observed、Result、Limits 写 proof；标 exact head 和 companion fallback PR。
- **不要照搬**：controlled sink 没有真实 GitHub dispatch、队列或生产 mutation；该 proof 不能代替 exact-head required checks 全绿。

## 复用模板

新增 Gold Case 时固定记录：

```markdown
### <PR 与一句话模式>

- Problem / user impact:
- Violated invariant:
- Architectural owner and siblings:
- Canonical fix and removed paths:
- Evidence ladder and exact head:
- Known proof gap / not tested:
- Production vs tests/docs/generated LOC:
- Review moves and maintainer decisions:
- Reusable lesson:
- Do not generalize:
```

Gold Case 是决策校准，不是复制粘贴模板。先重查目标仓库当前规则、依赖、默认分支、CI、review 和 release 状态。

## 相关子技能与层次边界

- 执行工作流 → [`skills/github-contribution`](../skills/github-contribution/SKILL.md)：本快照用于校准 github-contribution 的"证据阶梯 / owner boundary / proof"判断；gold case 是决策校准，不是复制模板。
- 评审校准 → [`skills/pr-review`](../skills/pr-review/SKILL.md)：从已合并案例反推 review 关注点。
- 关联手册：提交规范见 [`commit-pr-conventions.md`](commit-pr-conventions.md)，评审应对见 [`review-response-playbook.md`](review-response-playbook.md)。
- 层次边界：本篇是**真实案例校准层**，禁止把 100-PR 快照的统计相关性写成通用合并公式（见 github-contribution 限制节）。

# Fix Attribution Playbook —— CI 失败归因分流与迭代修复循环

> CI 红了不等于你的 PR 坏了。**每个失败先归因，再决定修、解释还是忽略。**

## 归因五步（每步有证据，跳步会误伤）

```bash
# ① 拉失败 job 日志，提取首个失败测试（错误行被沙箱噪声淹没时用精确模式）
curl -sL -H "Authorization: token $TOKEN" "<job_logs_url>" \
  | grep -E "FAIL |AssertionError|error TS|##\[error\]" | grep -v "error\.stderr" | head
# ② 本地复现该测试（同一命令、同一 runner 配置）
npx vitest run <failing-test-file>
# ③ 双 checkout 对照：PR head vs 干净基线（先 fetch upstream）
git fetch upstream main
git checkout -q <merge-base-or-base-sha> && npx vitest run <failing-test-file>
git checkout -q <pr-branch>
```

④ **分流判定**：

| 对照结果 | 定性 | 动作 |
|---|---|---|
| 基线同样失败 | **upstream 回归**（与我们无关） | 发归因评论：失败测试 + 两端复现结果 + 嫌疑 upstream 提交（`git log` 找近期 touching 提交）。**绝不代修** |
| 仅 PR 分支失败 | **ours** | 进修复循环 |
| 仅基线失败 | PR 反而修好了/未触及 | 在评论中说明（体现 diff 无害） |
| 两端都过、仅 CI 挂 | 环境 flaky | 标注观察；下一轮 CI 复现再归因 |

⑤ **归因评论规范**：失败测试名 + 断言差异 + 双 checkout 结果 + 嫌疑提交 SHA 与标题 + "本 PR diff 与失败域无文件交集"（如属实）。ci-gate 聚合红时说明"仅因聚合该 upstream 失败"。

## 修复循环（ours 侧）

1. **最小面**：一次迭代只解决一类问题；优先修"我们自己引入的"，不顺手重构。
2. **本地门禁全绿才 push**：相关测试 + 类型（注意覆盖面，见陷阱②）+ oxlint/oxfmt。
3. **commit 语义化**（`fix(scope): symptom`），push 仅限已授权分支，**永不 force**。
4. **每次迭代发一条说明评论**：改了什么、为什么、验证结果——让评审无需 diff 就能跟上轮次。
5. 评审要求补 proof：复用 github-contribution 的 Live-Proof 规范（单变量 BEFORE/AFTER、多次探针、真实入口优先）。

## 认知陷阱（实战提炼，每条都真实踩过）

1. **CI merge 树竞态**：upstream 分钟级推进时，PR CI 的 merge 树可能检出中间态（如 revert 落了、caller 迁移没落）→ 大面积与 diff 无关的红。处置：等 upstream 稳定后 merge main 刷新 CI，并在评论中还原时间线。
2. **本地验证盲区**：
   - `tsgo -p tsconfig.core.json` **不覆盖测试文件**——测试类型要跑 CI 同款 `test/tsconfig/*.test.*.json`；
   - **re-export 转发会构成运行时值循环**——有 import-cycle 架构守卫的 repo（如 openclaw）直接红，本地 tsgo/vitest 不报，只有 CI guards 抓；
   - **切分支后 node_modules 陈旧制造假类型错误**（workspace 外部依赖版本漂移）——先 `pnpm install --frozen-lockfile` 再跑类型。
3. **评审批次误归因**：评审引用的 "repair" 可能来自 merge 后状态而非你的 diff（实例：`tools.ts line-budget` 实为 upstream 提交把文件推过 max-lines）——**拉日志/本地复现核实再动手**，别按评审措辞直接改。
4. **CI 红先双 checkout 再归因**：一次对照实验即可闭环，比反复拉日志快。
5. **merged ≠ closed ≠ fixed**：定性历史 issue 状态时读 `pull_request.merged_at`，别只看 state。

## 边界

- 策略提高推进效率，不保证被合并；合并决策归维护者。
- upstream 侧失败绝不代修——那是另一个 issue/PR 的事，抢修会踩他人工作。
- 无 push 授权的分支只发评论不动代码；授权以用户明确指示为准。

## 关联子技能（层次边界，L2→L3）

- **监控节奏与基线方法**见同级 [monitoring-playbook.md](monitoring-playbook.md)——本文件只负责"失败归因与迭代修复"，不重复盯守逻辑。
- **proof 构建**复用 [github-contribution](../../github-contribution/SKILL.md) 的 Live-Proof 规范（单变量 BEFORE/AFTER、多次探针、真实入口优先）。
- **反馈分类与回复话术**用 [pr-review](../../pr-review/SKILL.md)；评审轮转状态机的语义以维护者/机器人为准。

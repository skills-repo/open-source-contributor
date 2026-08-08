# 评审应对手册（Review Response Playbook）

> 子技能 `pr-review` 列了"反馈分类"和"常见场景"，但没给出**收到一坨混杂反馈时，按什么顺序、用哪种动作、在多长时间窗内处理**的可执行 SOP。本篇把 review 应对从"心态建议"升级为"带 SLA 的处置流水线"，并给出一组可直接复用的回复话术模板。

## 1. 反馈分类与处置 SLA

收到 review 后，先按来源和严重度二维分类，再决定动作与时限：

| 类别 | 来源 | 严重度 | 动作 | SLA |
|------|------|--------|------|-----|
| 阻塞 (blocker) | 人 / 机器人 | 编译/测试/安全失败 | 必须修，独立 commit | 24h 内 |
| 建议 (suggestion) | 人 | 中 | 修或礼貌解释不选 | 48h 内 |
| 可选 (nit) | 人 | 低 | 顺手改，不争论 | 合并前 |
| 误报 (false-positive) | 机器人 | 低 | 用证据反驳，不默默忽略 | 24h 内 |
| 风格 (style) | 人 | 低 | 照做，绝不争论 | 立即 |

**铁律**：阻塞和误报必须在 24h 内响应；超过 72h 不响应，维护者有权关 PR。

## 2. 处置决策树

```
收到反馈
 ├─ 是编译/测试/CI 红 → blocker → 本地复现 → 修 → 独立 commit → 贴 proof
 ├─ 是安全扫描告警 → 先判真伪
 │    ├─ 真实风险 → 修 + 引用 SECURITY.md 说明范围
 │    └─ 误报 → 贴证据反驳（依赖/数据流证明不可达），不删告警行
 ├─ 是"needs more proof" → 补 BEFORE vs AFTER 终端输出（非截图）
 ├─ 是架构质疑 → 写"权衡说明"：为什么这么设计 + 替代方案对比
 ├─ 是"拆小 PR" → 接受，关大 PR，拆 2-3 个小 PR
 └─ 是风格/命名 → 照做，回 "Done, thanks"
```

## 3. 每个反馈独立 commit（不要混改）

把"回应 N 条反馈"变成"N 个语义化 commit"，维护者能逐条 re-review：

```
fix: 处理 reviewer 关于空指针的阻塞意见   # 对应 blocker
docs: 补充函数复杂度说明回应架构质疑        # 对应 suggestion
style: 按规范重命名变量回应风格意见          # 对应 nit
```

> 反模式：把所有修改 squash 成一个 `address comments` commit。维护者被迫整体重读，且 `git blame` 失去意义。

## 4. 回复话术模板（可直接套用）

**承认并修复（blocker）**
```
Thanks for catching this. Fixed in <commit-hash>: 根因是 <一句话>，已加回归测试。
BEFORE: <复现命令> → 报错
AFTER:  <复现命令> → 通过
```

**礼貌反驳（误报 / 架构质疑）**
```
Good point. 我考虑过 <替代方案>，但 <理由：性能/兼容性/可读性> 下当前方案更优。
如果你更倾向 <替代>，我可以改，请定夺。
```

**接受拆分（大 PR）**
```
同意拆小。已关闭本 PR，拆分为：
- #A 仅做 <X>
- #B 仅做 <Y>
请先看 #A。
```

**风格类（nit）**
```
Done, thanks for the polish.
```

## 5. 自动化评审机器人专项

| 机器人 | 关注点 | 应对 |
|--------|--------|------|
| ClawSweeper | proof 充分性、边界值覆盖 | 补 BEFORE/AFTER + 边界用例输出 |
| Greptile | 跨文件影响、逻辑一致性 | 解释改动波及范围，证明无回归 |
| Aisle Security | 安全风险 | 真实风险就修；误报用数据流证明不可达 |

**机器人误报的正确姿势**：用证据反驳 + 保留告警上下文，而不是默默改掉或 `@skip`。沉默处理会让下次同样的误报再触发。

## 6. Re-request 时机

- 所有 conversation 标记 resolved 后再 re-request review
- 若 48h 无新反馈，可温和 ping：`Gentle ping — all threads resolved, ready for another pass.`
- 不要 24h 内反复 re-request，会被当成骚扰

## 7. 典型坑与规避

| 坑 | 表现 | 规避 |
|----|------|------|
| 用裸 `--force` 推回 fork | 冲掉 review 线程 | 仅 `--force-with-lease`，且只推自己 fork |
| 把反驳当争论 | 维护者觉得不配合 | 用证据说话，不谈风格偏好 |
| 忽略机器人 proof 要求 | PR 卡在 needs more proof | 永远附终端输出 |
| 一次性大 squash 回应 | 维护者重读全部 | 每反馈独立 commit |
| 超时不响应 | PR 被关 | 设 24/48/72h SLA 提醒 |
| 删除安全告警行蒙混 | 埋下隐患 | 误报也用证据反驳 |

## 8. 机器人规则与跨时区

| 机器人 | 判定逻辑要点 | 应对关键 |
|--------|--------------|----------|
| ClawSweeper | 查 proof 覆盖与边界值 | 补 BEFORE/AFTER + 边界用例 |
| Greptile | 跨文件影响分析 | 说明波及范围，证明无回归 |
| Aisle Security | 依赖/数据流扫描 | 真实风险修；误报用数据流证不可达 |

**跨时区协作**：维护者在欧洲、你在亚洲 → 用 Issue 异步沟通，不在深夜 push 大改；所有决策落在 Issue/PR 评论里，不靠私聊。

## 9. Re-request 与升级

- 全 resolved 后再 re-request；48h 无响应可温和 ping 一次。
- 若维护者长期不响应且 PR 重要：在 Issue 提"是否需要帮忙推进"，不反复 at。
- 被拒不等于失败：优雅关闭，总结可复用的经验，换合适项目再战。

## 10. 实战：被要求拆小 PR 的完整应对

场景：你提了 600 行大 PR，维护者评论 "please split into smaller PRs"。

SOP：
1. 在 PR 评论确认方案：`Agreed. Splitting into #A refactor / #B feature / #C tests.`
2. 关闭大 PR，开 3 个小 PR；`#B` 的 base 指向 `#A` 合并后的分支。
3. 每个小 PR 套模板六章节，独立 BEFORE/AFTER、独立编译通过。
4. 请维护者先审 `#A`。

话术模板：
```markdown
Agreed. Splitting into:
- #A refactor tokenizer (no behavior change)
- #B add feature X (depends on #A)
- #C tests for X
Please review #A first.
```
注意：拆分后每个小 PR 必须能独立编译、独立回滚，不出现"A 不合并 B 就坏"的耦合。

## 11. 反馈处置反模式（扩展）

| 反模式 | 后果 | 修正 |
|--------|------|------|
| 裸 force 推回 fork | 冲线程 | --force-with-lease |
| 反驳当争论 | 不配合 | 证据说话 |
| 忽略 proof 要求 | 卡 needs more | 补终端输出 |
| 大 squash 回应 | 重读 | 每反馈独立 commit |
| 超时不响应 | PR 被关 | 24/48h SLA |
| 删安全告警 | 埋隐患 | 误报也反驳 |
| 风格争辩 | 惹烦 | 照做 |
| 反复 re-request | 骚扰 | resolved 后再请 |
| 私聊决策 | 无记录 | 落 Issue/PR |
| 被拒就弃 | 浪费 | 总结再战 |

## 12. 维护者关系长期经营

合并不是终点，而是关系的起点：
- **合并后致谢**：简短感谢 review 时间，维护者记佳。
- **后续 PR 引用前例**：`as discussed in #A` 减少重复解释。
- **成为常客**：持续小贡献比一次性大 PR 更易建立信任。
- **帮他人 review**：当你熟悉项目后，回看新手 PR，反哺社区。
- **不纠缠**：被拒优雅关闭，不争论、不刷屏。

> 开源是**长期博弈**：第一次合入只在维护者心里挂上号，后续信任靠持续、靠谱的小动作积累。

## 13. 评审应对检查清单

- [ ] 已按"阻塞/建议/可选/误报/风格"分类全部反馈
- [ ] 已设 SLA：blocker/误报 24h，建议 48h
- [ ] 每条反馈对应一个独立、语义化 commit
- [ ] 已补 BEFORE vs AFTER 终端输出（应对 needs more proof）
- [ ] 安全告警：真实风险已修，误报已用证据反驳
- [ ] 所有 conversation 标记 resolved
- [ ] 已 re-request review，未超时骚扰
- [ ] 风格意见已照做，未争论

## 14. 跨仓库协作与礼仪

当你在多个仓库都有贡献时，维护者可能是同一批人，口碑会跨仓库传播：

- **身份一致**：不同仓库用同一 GitHub 身份、同一沟通风格，维护者更容易记住靠谱的你，第一次合入积累的信任会延续到下一个仓库。
- **不跨仓甩锅**：A 仓的问题不在 B 仓评论区喊，各自 Issue 内解决；跨仓依赖在对应仓开跟踪 Issue 并互相链接。
- **复用前例**：在 A 仓达成的约定，B 仓直接引用 `as agreed in <org>/<repo>#A`，减少重复解释，也展示你尊重社区既有决策。
- **退出得体**：离开某仓前把进行中的 PR 交接给继任者或优雅关闭，不留半成品让维护者收拾；被拒也不刷屏。
- **公开致谢**：合并后简短感谢 review 时间，维护者记得你的靠谱，后续 PR 评审更快、更信任。

> 开源是**长期博弈**：单次合入只在维护者心里挂上号，跨仓库一致的好口碑靠持续、靠谱的小动作积累，远胜一次性大 PR。

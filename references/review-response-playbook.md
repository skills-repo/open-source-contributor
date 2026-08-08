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

## 8. 评审应对检查清单

- [ ] 已按"阻塞/建议/可选/误报/风格"分类全部反馈
- [ ] 已设 SLA：blocker/误报 24h，建议 48h
- [ ] 每条反馈对应一个独立、语义化 commit
- [ ] 已补 BEFORE vs AFTER 终端输出（应对 needs more proof）
- [ ] 安全告警：真实风险已修，误报已用证据反驳
- [ ] 所有 conversation 标记 resolved
- [ ] 已 re-request review，未超时骚扰
- [ ] 风格意见已照做，未争论

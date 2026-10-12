# Defect Hunting Playbook —— main 分支可证明缺陷挖掘

> 贡献者视角的**可复现挖掘策略**，目标是找到"能写出 source-repro 级 issue"的真实缺陷。

## 诚实边界（先读，避免误解）

- 这不是"教会审计一切代码"——是**提高命中率的启发式**，不保证发现全部缺陷，更不是安全审计替代品。
- 每条候选**必须可证明**：仅有代码论证（"看着像错"）的缺陷，**先构建复现**；复现不了就降级为 question/discussion，**绝不报成 bug issue**（报错方向会消耗维护者信任，比不报更糟）。
- 只挖**当前 main/HEAD 仍存在**的缺陷；涉及行为的先确认在最新 commit 上复现，别拿旧版本的问题报新单。

## 热点选择启发式（按 ROI 排序，每条附可执行命令）

> 通用原则：**找"高频变动 × 状态复杂 × 契约模糊"的三角区**。按下面顺序扫，命中一个就深入，不要平均用力。

### 1. 近期 churn 区（回归高发）

高频改动的模块集成点最易出回归——新代码与旧假设的摩擦处。

```bash
# 近 3 个月改动最频繁的文件（回归热点）
git log --since="3 months ago" --pretty=format: --name-only \
  | sort | uniq -c | sort -rn | head -30

# 交叉：这些文件里被反复修改的函数/区块（看 diff 密度）
git log --since="3 months ago" -p -- <热点文件> | grep -E '^@@' | sort | uniq -c | sort -rn | head
```

### 2. 错误处理边界（吞错 / 判空缺失 / fallback 掩盖状态）

`?.` 链、`catch` 吞错、`return undefined/null` 的调用方未判空、`?? fallback` 掩盖上游失败——这类缺陷普遍、可本地复现、修复面小。

```bash
# 空 catch / 只 log 不 rethrow 的吞错点
grep -rn "catch" --include="*.ts" src/ | grep -vE 'throw|reject|return|console\.(error|warn)|logger\.(error|warn)' | head -40

# ?? / || fallback 可能掩盖上游状态（人工过滤）
grep -rnE '\?\?|\|\|' --include="*.ts" src/ | grep -iE 'null|undefined|default|fallback' | head -30

# 返回可空的 API，查调用方是否判空（以某函数为例）
grep -rn "someMaybeNullFn(" --include="*.ts" src/ | head
```

### 3. 生命周期 / 并发边界（registry / generation / lease / dispose）

资源的创建-借用-释放顺序、generation 快照与借用不同步、AsyncLocalStorage/上下文传递断裂——**缺陷深、影响大、竞争少**，是高价值洼地。

```bash
# 生命周期原语出现处
grep -rnE 'class .*(Registry|Loader|Lease|Generation|Scope)\b|dispose\(|release\(|acquire\(|\.snapshot' --include="*.ts" src/ | head -40

# generation/scope 借用与 narrowing（重点核对借用的快照是否包含应有 owner）
grep -rnE 'withPluginRuntimeGenerationScope|GenerationScope|basePluginIds|lease\.snapshot|narrow' --include="*.ts" src/ | head -30

# 异步上下文传递
grep -rnE 'AsyncLocalStorage|als\.|getStore\(\)|runWithContext' --include="*.ts" src/ | head -20
```

### 4. 契约不一致点（文档/类型声称 vs 实际实现）

注释或类型说"fails-closed"，实现却 fails-open；文档说"总是 X"，代码却有条件跳过。**读注释比读代码更快定位缺陷**。

```bash
# fails-closed / always / must / never 等强契约声明旁，核对该函数体是否真的如此
grep -rnE 'fails[- ]closed|fails[- ]open|always |never |must |guarantee' --include="*.ts" src/ | head -30

# 公开 API 的 JSDoc 声称 vs 实现分支
grep -rnB2 -A8 '@returns\|@throws' --include="*.ts" src/ | head -40
```

### 5. 跨模块集成点（A 产出的状态被 B 按不同假设消费）

最常见的隐藏缺陷：生产者改了什么，消费者仍按旧假设读。找"同一份状态/配置有两个消费方"的地方。

```bash
# 同一 config/状态键被多处读写（潜在假设分歧）
grep -rnE 'config\.[a-zA-Z.]+|state\.[a-zA-Z.]+' --include="*.ts" src/ \
  | grep -oE '(config|state)\.[a-zA-Z.]+' | sort | uniq -c | sort -rn | head -20

# 上游产出 → 下游消费的类型边界（找 any / as 断言绕过处）
grep -rnE ' as [A-Z]\w+|\bas any\b' --include="*.ts" src/ | head -30
```

## 候选缺陷登记表（每条候选必填）

**只有前两格完整才进入报 issue 流程**（第三格是验证状态，未验证的候选不得对外报）。

| 字段 | 说明 |
|------|------|
| 代码路径 | `file:line` 机制链——从触发点到缺陷处的完整调用/数据路径 |
| 触发条件假设 | 什么输入/状态下缺陷显现（具体、可构造） |
| 验证状态 | `已复现` / `仅代码论证` / `待验证` |
| 影响面 | 用户可见故障 / 边缘场景 / 理论问题 |
| 修复成本估计 | 小而清晰 / 大而模糊（维护者视角） |

### 样例行（已验证案例：openclaw #167365）

| 字段 | 内容 |
|------|------|
| 缺陷 | `tools.effective` 漏掉所有非 memory 插件工具（如 `workboard_*`），并打印误导性 "unknown entries" 警告 |
| 代码路径（机制链） | `acquireEffectiveToolInventoryRuntimeModelContext` → `acquireReadOnlyPreparedModelRuntime({loadRuntimePlugins:true})` → `prepareWorkspacePluginRegistries` 因 `loadRuntimePlugins` 强制 `basePluginIds:[]`，generation 只剩 provider/memory/harness owner → 随后在 `withPluginRuntimeGenerationScope(lease.snapshot)` 内运行 inventory，借用的 snapshot 已缺 tool-only owner → `resolvePluginToolLoadState` 从 narrowing 后的 snapshot 算 `onlyPluginIds`，tool-only 插件永不被选中 |
| 触发条件假设 | `tools.profile` allowlist 含 tool-only 插件（如 `workboard_*`）且插件 enabled 时，调用 `tools.effective` 看不到这些工具 |
| 验证状态 | **已复现**（sandbox 会话实测 + gateway 日志佐证；`tools.catalog` 列全 35 个而 `tools.effective` 漏掉） |
| 影响面 | 用户可见故障（策略允许的工具实际不生效） |
| 修复成本 | 小而清晰（generation narrowing 时不应丢 tool-only owner / 借用前补全 basePluginIds） |
| 归类启发式 | 第 3 条（generation/lease 生命周期边界：narrowing × borrowing 顺序） |

> 该案例最终带 `clawsweeper:source-repro` + `fix-shape-clear` + `queueable-fix` + `issue-rating:🦞diamond` —— 正是"深生命周期缺陷 + 可复现 + 修复方向清晰"得到认可的实证。

## 可证明性门槛（硬规则）

1. **仅代码论证 → 必须先构建复现**：写最小独立脚本 / 最小 config / 真实入口命令，跑出 BEFORE（缺陷现象）。
2. **复现不了 → 降级**：转 question/discussion 频道描述疑点，请维护者确认，**不报 bug issue**。
3. **能复现但无根因 → 仍可报**：复现完整度优先于根因完整度（`source-repro` 门槛低于 `fix-shape-clear`）。但要在 Evidence 里如实标注"根因待定位"。

## 优先级排序（维护者视角的"queueable 度"）

两个轴相乘，**优先报"影响面大 × 修复成本小"**的：

| | 修复成本小（清晰） | 修复成本大（模糊） |
|---|---|---|
| **影响面大**（用户可见故障/数据/安全） | 🦞 最高优先，附最小修复方向 | 💎 次优先，报但管理预期 |
| **影响面小**（边缘/理论） | 🥈 可报，作 good-first 候选 | ⚪ 攒成讨论，不单独报 |

**同体量优先报能附带最小修复方向的**（`fix-shape-clear` 比 `source-repro` 更接近合并）。拿不准影响面时，保守按"边缘场景"报，让维护者升级，不要夸大 severity（夸大一次，信任折损长期）。

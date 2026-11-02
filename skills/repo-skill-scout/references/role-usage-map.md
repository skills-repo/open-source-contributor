# 宿主技能包的角色×用法映射（使用说明本体）

> 配套 [../SKILL.md](../SKILL.md) 的侦察工作流使用：侦察解决"这个仓库有哪些规则、谁权威"，
> 本页解决"**我手上的活该用其中哪一个、用到什么程度**"。
> 页面里所有具体技能名都来自 2026-11-02 对一个 54 技能包的实测，仅作案例锚点；
> 换仓库时先用侦察工作流重建同名槽位，再套本表。

## 槽位（slot）：先映射，再照抄

不同仓库技能名不同，但职责槽位高度稳定。侦察完先填这张表，**填不出槽位 = 该仓库没有对应能力**：

| 槽位 | 该槽位回答的问题 | 案例（OpenClaw） |
|---|---|---|
| 证明选择 | 这个改动要配哪种证据才算够 | `openclaw-testing`（#proof-policy） |
| 诊断 | 复现不出来时先看什么、按什么顺序 | `openclaw-debugging` |
| 性能 | 慢/重怎么归因，优化次序是什么 | `openclaw-performance`（delete → batch → cache） |
| 自审 | 提交前怎么把补丁缩到最小完整 | `pr-simplify` |
| 测试红线 | 哪些测试写法会被直接判负 | `test-audit` |
| 评审侧 | 维护者/机器人按什么尺子判 | `openclaw-pr-maintainer`、`clawsweeper`、`autoreview` |
| 查重 | 是否已有人做、是否重复 | `gitcrawl`、`tag-duplicate-prs-issues` |
| 影响面 | 动公共契约前要知道谁在用 | `plugin-sdk-impact` |
| 视觉证据 | UI 改动的截图/录屏规范 | `proof-video`、`control-ui-e2e` |
| 框架专项 | 该仓库指定栈的写法规约 | `solid` |
| 发布 | 版本/签名/公告/核验 | `release-openclaw-*`、`verify-release` |
| live 运维 | 常驻实例与更新 | `openclaw-live-updater`、`openclaw-update` |
| 权限/容量 | CI 资源与 runner 预算 | `openclaw-ci-limits` |
| 安全 | 漏洞披露与密钥告警 | `security-triage`、`openclaw-ghsa-maintainer`、`openclaw-secret-scanning-maintainer` |

## 角色×槽位：四类活各自走哪几个

**A. 本地写代码**（全可执行，都在你自己工作区）
1. 动手前 → 证明选择槽（决定要配哪种证据，别等评审告诉你）
2. 卡住 → 诊断槽；碰性能 → 性能槽
3. 改了测试 → 测试红线槽
4. 开 PR 前 → 自审槽（多数仓库把它写成硬性一步，案例里是 `AGENTS.md:55`）
5. 碰该仓库指定框架/UI → 框架专项槽（"read … first" 类措辞＝前置条件，不是建议）

**B. 提 PR**
1. 查重槽：先确认没人正在做、issue 没被认领（**这是省掉整条白干链路的唯一一步**）
2. 评审侧槽：**只读**。读它的 authority/landing/media 判定条款，用它来塑造改动形状；
   不要因为"它也是技能"就去执行落地下单类动作
3. 机器人语义 → 属于评审侧槽的子文档（评分维度、标签从哪来、什么算 mock-only 证据）
4. 需要证据材料 → 视觉证据槽；需要附对话记录 → 该仓库若有 transcript 脱敏技能则用它

**C. 提 issue**
1. 查重簇 → 查重槽（避免撞车）
2. 正文完整度 → 本仓库自带 issue 模板 + 我们的 `issue-creator`；宿主侧无对应技能属正常
3. 安全类**不走**公开 issue：安全槽的 `SECURITY.md`/GHSA 私有通道优先，公开报等于替攻击者写文档

**D. 提 feature / 改公共契约**（最容易白干）
1. 影响面槽：先量化有多少消费者在用，再谈废弃或改动
2. 读该仓库的产品 doctrine（VISION/ROADMAP 类文件）确认它是否接受外部 feature PR；
   案例仓库三条 doctrine：core 精简、**反复需求才定义接口**、记忆子系统要收敛
3. 决策前沿标签（`needs-product-decision` 一类）：**先开 issue 排队，不要先写代码**
4. 交付形态：优先该仓库期望的扩展点（插件/SDK），而不是往核心加新工具

## 使用深度：三档，别一律"通读"

| 档位 | 判据 | 动作 |
|---|---|---|
| **锚点级**（最常见） | 路由文件深链到 `SKILL.md#某小节` | 只读该小节＋它再路由的 `references/*`；锚点就是验收条款 |
| **全文级** | 路由措辞是 `read … in full` | 整份读完，含其 references |
| **仅索引级** | 与当前任务无关，或属只读契约但你想了解判据 | 只读 description，记下边界词 |

误判代价不对称：该读锚点却没读＝PR 被按未知规则打回；无关技能通读＝浪费上下文。

## 只读契约清单（外来贡献者的硬禁区）

判据：**执行它会改变别人能看到/依赖的状态**。命中即"读条款，不执行"：

- 发布与签名（release 族、verify、公告发布）
- live 实例（常驻更新、部署、Team/server 更新、重启别人的进程）
- 批量 GitHub 写（bulk close/reopen/triage、自动合并、机器人 maintainer 命令）
- 需要他人凭证的 e2e（租用 bot/OAuth 凭据的通道类）
- 他人私有归档（内部 IM/笔记/表格类）
- 安全披露与密钥处置（advisory、secret scanning）

## 复用规则：一个仓库调研一次

角色×槽位映射与锚点清单是**仓库资产**，不是每次会话重算。落盘位置二选一：
项目记忆（推荐，跨会话可取）或该仓库的本地笔记文件；第二次进入同一仓库先取盘，
只增量核对新增/改名的技能。

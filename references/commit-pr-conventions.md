# 提交与 PR 规范手册（Commit & PR Conventions）

> 子技能 `github-contribution` 给了 PR 模板，`community-etiquette` 讲了 PR 描述怎么写，但两者都没把**"一条 commit / 一个 PR 到底什么叫规范"量化成可机械检查的清单**。本篇把规范拆成"格式规则 + 关联规则 + 完整性规则"三层，并直接对应 `scripts/check_contribution.py` 的检查项——写完提交前跑一遍脚本，能挡掉 80% 的"被打回重写"。

## 1. 为什么需要机器检查

人工 review 提交规范有两大问题：(1) 维护者不耐烦逐条指摘格式；(2) 你自己也记不全所有规则。把规则固化成脚本，提交前自检 → 合并率与口碑双升。`scripts/check_contribution.py` 覆盖三种对象：

- `commit` —— 单条 commit message 的格式与关联
- `contributing` —— 仓库 CONTRIBUTING.md 的必含章节
- `pr` —— PR 描述对模板章节的覆盖度

## 2. Commit Message 规范（Conventional Commits 落地）

采用 [Conventional Commits](https://www.conventionalcommits.org) 的实用子集，格式：

```
<type>(<scope>): <subject>

<body 可选，解释 why>
```

**type 白名单**（与脚本 `commit_conventions.json` 中 `allowed_types` 对齐）：

| type | 含义 | 例子 |
|------|------|------|
| feat | 新功能 | `feat(parser): 支持嵌套注释` |
| fix | 修 bug | `fix(lexer): 修复 EOF 处越界` |
| docs | 文档 | `docs: 更新 README 安装段` |
| style | 格式（不改逻辑） | `style: 统一 import 顺序` |
| refactor | 重构 | `refactor(core): 抽取 token 流水线` |
| perf | 性能 | `perf: 缓存 AST 解析结果` |
| test | 测试 | `test: 补全 lexer 边界用例` |
| build | 构建 | `build: 升级 pyproject 依赖` |
| ci | CI | `ci: 增加 macos Runner` |
| chore | 杂务 | `chore: 清理无用注释` |
| revert | 回退 | `revert: 回退 feat(parser)` |

**硬性约束（脚本会查）**：
1. subject 首行必须匹配 `^(type)(\(scope\))?!?: .+`，type 在白名单内
2. subject 长度 ≤ 72 字符（Git 传统硬上限，超了在 GitHub 上被截断）
3. 必须关联 issue：正文或 subject 出现 `#123` / `fixes #123` / `close #123` / `resolve #123`
4. body 单行 ≤ 100 字符（避免横向滚动）
5. 推荐用祈使句、小写开头、无句号结尾（`add` 而非 `added`/`adds`）

### 决策矩阵：什么时候 squash，什么时候保留多 commit

| 场景 | 做法 | 理由 |
|------|------|------|
| PR 只解决一件事 | 合入前 squash 成 1 条语义化 commit | 历史干净，便于 `git bisect` |
| PR 含"重构 + 功能"两阶段 | 保留 2 条（refactor 先、feat 后） | 审查者能分步看 |
| 审查中反复修改 | 用 `--amend` 叠加，不要新增 "fix typo" commit | 避免 "oops" commit 污染历史 |
| 维护者要求线性历史 | 按项目要求 rebase + squash | 见 CONTRIBUTING |

## 3. PR 描述规范

PR 描述 = 模板章节的覆盖度检查。模板 `assets/PULL_REQUEST_TEMPLATE.md` 的 `##` 标题即脚本的必检章节。最低覆盖：

- **描述 (Description)**：一句话说清"改了什么 + 为什么"
- **关联 Issue (Related Issue)**：至少一条 `fixes #N`
- **变更类型 (Type of change)**：勾选 bug / feature / docs / refactor
- **检查清单 (Checklist)**：自测项打勾
- **测试方法 (Test plan)**：怎么验证（命令）
- **证据 (Evidence)**：BEFORE vs AFTER 终端输出（自动化评审机器人最看重）

**关联动词优先级**：`fixes` > `close` > `resolve` > 纯 `#引用`。用 `fixes #123` 能在合并时**自动关闭** Issue，且让 GitHub 把 PR 与 Issue 双向链接。

## 4. CONTRIBUTING.md 完整性规范

仓库若自带 CONTRIBUTING，脚本会检查是否含以下必含章节（大小写不敏感子串匹配，见 `commit_conventions.json` 的 `required_contributing_sections`）：

| 必含章节 | 缺失后果 |
|----------|----------|
| Code of Conduct 引用 | 社区准入门槛，缺了不专业 |
| 环境搭建 / Getting Started / Setup | 贡献者跑不起来 = 白写 |
| 如何提交 / Submitting / 提交流程 | 流程不清，PR 格式乱 |
| 代码风格 / Coding Style | 风格争论拖慢合并 |
| 测试 / Running Tests | 无法验证改动正确性 |

> 若仓库没有 CONTRIBUTING，本检查不适用（脚本 `contributing` 模式会提示 "file not found" 而非报错）。不要为了过检而造一份低质 CONTRIBUTING。

## 5. 典型坑与规避

| 坑 | 表现 | 规避 |
|----|------|------|
| subject 用中文或带句号 | `fix: 修复了 bug。` 被脚本判格式错 | 英文 type + 空格 + 小写祈使，无句号 |
| 超长 subject | `fix: 修复了当用户在登录后点击设置再返回首页时……` | 截断到 ≤72，细节放 body |
| 只写 `update` / `fix bug` | 无信息量，维护者看不懂 | 用 type + scope + 具体对象 |
| 不关联 issue | 合并后 Issue 仍 open，割裂 | 永远带 `fixes #N` |
| PR 描述只有标题 | 机器人判 needs more info | 套模板六章节 |
| body 行过长 | 移动端难读 | 每行 ≤100 字符 |

## 6. Squash 与 CI 实战

```bash
# 合并前把功能分支压成 1 条语义化 commit
git rebase -i upstream/main        # 把 fixup 行改成 s（squash）
git commit --amend                 # 补 issue 关联
git push -u origin fix/issue-5968 --force-with-lease
```

CI 失败排查顺序：lint → type check → unit → build → e2e。先看失败阶段日志，本地复现再改，不要盲改 ci 配置。

## 7. PR 描述反例对比

| 反例 | 正例 |
|------|------|
| "fix bug" | "fix(parser): 处理 EOF 越界，修复 #5968" |
| 只有标题无章节 | 套模板六章节 + BEFORE/AFTER |
| "please review" | "fixes #5968，已补回归测试，CI 全绿" |
| 贴截图当 proof | 贴终端 BEFORE/AFTER 输出 |

## 8. 实战：一条规范 commit 的完整产出

```bash
# 1) 写变更计划（5-Point 摘要）
# Observed: 解析器在文件末尾 EOF 处越界
# Expected: 静默退出或报清晰错误
# Root cause: 循环未检查 index < len
# Seam: lexer.next() 末尾返回 EOF token
# Risk: 仅影响边界解析，单测覆盖

# 2) 提交（语义化 + 关联 issue）
git commit -m "fix(parser): 处理 EOF 越界避免索引异常 (fixes #5968)"

# 3) 自检
git log -1 --pretty=%B > /tmp/msg.txt
python3 scripts/check_contribution.py commit --file /tmp/msg.txt   # 期望 0 ERROR

# 4) PR 描述套模板六章节，跑 pr 模式自检
python3 scripts/check_contribution.py pr --file /tmp/pr_body.md     # 期望 0 ERROR
```

反例对照见上文"PR 描述反例对比"。

## 9. 提交反模式（扩展）

| 反模式 | 后果 | 修正 |
|--------|------|------|
| subject 用中文/句号 | 格式错 | 英文 type+祈使无句号 |
| 超长 subject | 截断 | ≤72 字符 |
| 只写 update/fix bug | 无信息 | type+scope+对象 |
| 不关联 issue | Issue 孤立 | fixes #N |
| body 行过长 | 难读 | ≤100 字符 |
| oops 提交 | 历史脏 | amend |
| 无测试声明 | 不可信 | 写测了什么 |
| DCO 缺失 | 被拒 | 补签名 |
| 改 base 分支 | 跑偏 | 按 CONTRIBUTING |
| 裸 force 推 | 冲线程 | --force-with-lease |

## 10. 提交前自检清单

- [ ] 已跑 `python3 scripts/check_contribution.py commit --file <msg>` 且 0 ERROR
- [ ] subject 符合 Conventional Commits 且 ≤72 字符
- [ ] 已关联 issue（`fixes #N`）
- [ ] 已跑 `python3 scripts/check_contribution.py pr --file <pr_body>` 且 0 ERROR
- [ ] PR 描述覆盖模板全部 `##` 章节
- [ ] 若改了贡献流程相关文件，已跑 `contributing` 模式检查 CONTRIBUTING
- [ ] 无 "oops"/"fix typo" 类噪声 commit（必要则 amend）

## 11. 命令速查

```bash
# 把暂存的提交消息落盘到文件后检查
git log -1 --pretty=%B > /tmp/msg.txt
python3 scripts/check_contribution.py commit --file /tmp/msg.txt

# 检查 PR 描述（从剪贴板或文件）
python3 scripts/check_contribution.py pr --file /tmp/pr_body.md

# 检查仓库 CONTRIBUTING 完整性
python3 scripts/check_contribution.py contributing --file CONTRIBUTING.md

# 自检：脚本校验内置资产（配置+模板）应为 0 ERROR
python3 scripts/check_contribution.py selfcheck
```

## 相关子技能与层次边界

- 执行工作流 → [`skills/github-contribution`](../skills/github-contribution/SKILL.md)：本手册是提交/PR 的**量化规范与自检清单**，真正的 Fork→分支→修复→PR 动作在 github-contribution 执行；提交前用 §11 命令跑 `check_contribution.py` 作为门禁。
- PR 描述评审 → [`skills/pr-review`](../skills/pr-review/SKILL.md)：PR 描述六章节覆盖度由 pr-review 的评审视角校准。
- PR 描述礼仪 → [`skills/community-etiquette`](../skills/community-etiquette/SKILL.md)：措辞与 AI 披露等软规则。
- 关联手册：选题决策见 [`first-contribution-playbook.md`](first-contribution-playbook.md)，评审应对见 [`review-response-playbook.md`](review-response-playbook.md)，真实案例校准见 [`merged-pr-gold-cases.md`](merged-pr-gold-cases.md)。
- 配套资产：`scripts/check_contribution.py`（自检脚本）、`assets/commit_conventions.json`（白名单配置）、`assets/PULL_REQUEST_TEMPLATE.md`（PR 模板章节）。

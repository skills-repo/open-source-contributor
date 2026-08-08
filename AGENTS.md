# AGENTS.md

## 仓库性质

这是一个 **AI Agent 技能库**，不是软件项目。所有内容为 Markdown 格式的技能定义文件。采用 skills-repo 组织的 **superpower 架构**。

## 目录约定（superpower）

```
open-source-contributor/
├── SKILL.md              # L1 路由层：唯一入口，只做索引，不写方法论
├── references/           # L2 深层 playbook：决策树/规范/评审 SOP（按需加载）
│   ├── first-contribution-playbook.md
│   ├── commit-pr-conventions.md
│   └── review-response-playbook.md
├── skills/               # L3 细粒度子技能：可单独 npx skills add
│   ├── issue-finder/SKILL.md
│   ├── github-contribution/SKILL.md
│   ├── pr-review/SKILL.md
│   └── community-etiquette/SKILL.md
├── scripts/              # L4 确定性脚本：check_contribution.py（提交规范自检）
├── assets/               # L5 模板资源：PULL_REQUEST_TEMPLATE.md / commit_conventions.json
├── AGENTS.md             # 本文件
├── README.md             # 面向人类的项目文档
├── LICENSE               # MIT
└── .gitignore
```

## 加载顺序（渐进式加载）

1. 先读 `SKILL.md` 路由表，判断任务属于哪一类。
2. **方法论决策**（选题/规范/评审）→ 读 `references/` 对应 playbook。
3. **落地具体动作**（找 Issue / 提 PR / 社区沟通 / 应对 review）→ 调 `skills/<name>/SKILL.md`。
4. **确定性自检**（commit/PR/CONTRIBUTING 规范）→ 跑 `scripts/check_contribution.py`。
5. 套用 `assets/` 模板，不重复造轮子。

## 工作约定

- 所有技能内容使用中文编写
- 面向开源新手和有经验的贡献者
- GitHub 优先，兼容 GitLab 等平台
- 每个技能聚焦一个环节，可独立使用

## 技能添加流程

1. 在 `skills/` 下创建以技能名命名的目录，写 `SKILL.md`（含完整 `source` 字段）
2. 若新增跨子技能的决策方法论，写进 `references/` 而非堆进子技能
3. 确保 `metadata` 字段完整
4. 更新 `README.md` 中的技能清单表与安装命令

## 不做什么

- 不创建面向特定项目的技能（如 "OpenClaw 贡献指南"）
- 不涉及 GitHub 以外的平台专属功能
- 不教怎么写代码（那是其他技能库的事）
- 不改动 `skills/<name>/` 目录名（下游 `skills-lock.json` 已锁定路径）

# AGENTS.md

## 仓库性质

这是一个 **AI Agent 技能库**，不是软件项目。所有内容为 Markdown 格式的技能定义文件。

## 目录约定

```
open-source-contributor/
├── README.md              # 项目介绍和使用指南
├── AGENTS.md              # AI 助手使用指引（本文件）
└── skills/                # 技能目录
    ├── <skill-name>/      # 单个技能目录
    │   └── SKILL.md       # 技能定义文件
    └── ...
```

## 工作约定

- 所有技能内容使用中文编写
- 面向开源新手和有经验的贡献者
- GitHub 优先，兼容 GitLab 等平台
- 每个技能聚焦一个环节，可独立使用

## 技能添加流程

1. 在 `skills/` 下创建以技能名命名的目录
2. 编写 `SKILL.md`
3. 确保 `metadata` 字段完整
4. 更新 `README.md` 中的技能清单表

## 不做什么

- 不创建面向特定项目的技能（如 "OpenClaw 贡献指南"）
- 不涉及 GitHub 以外的平台专属功能
- 不教怎么写代码（那是其他技能库的事）
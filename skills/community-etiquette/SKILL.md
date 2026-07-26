---
name: community-etiquette
description: 开源社区沟通规范：CONTRIBUTING 解读、PR 描述、AI 披露、维护者互动、审查应对
source:
  type: derived
  repo: skills-repo/open-source-contributor
  path: skills/community-etiquette/SKILL.md
  version: 1.0.0
  updated: 2026-07-26
  url: https://skills.sh/daymade/claude-code-skills/github-contributor
metadata:
  category: 社区
  platform: GitHub
  difficulty: 入门
---

# 社区礼仪

> 开源贡献的软技能全流程：从阅读 CONTRIBUTING.md 到 PR 被合并后的维护者关系维护。

## 能力

- **CONTRIBUTING.md 解读**：将贡献指南视为硬性合约，逐条提取合并前置条件
- **PR 描述写作**：中英双语结构化模板，让维护者 30 秒内决定是否合入
- **AI 辅助披露**：当项目有 AI 贡献条款时，主动、具体地声明 AI 使用方式
- **维护者互动**：回应 bot 审查评论、处理 review 反馈、接受拒绝
- **反模式识别**：10 种导致 PR 被关闭的常见失败模式及避免方法

## 使用方式

```
/community-etiquette 解读这个项目的 CONTRIBUTING.md
/community-etiquette 帮我写这个 PR 的描述
/community-etiquette 如何回应维护者的这条 review 评论
```

## 黄金法则

1. **先读 CONTRIBUTING.md** — 80% 的沟通问题源于没读贡献指南
2. **小 PR，早沟通** — 大改动先开 Issue 讨论，不要闷头写一周
3. **感谢审查时间** — 维护者用业余时间审查，心存感激
4. **不争论风格** — 如果维护者要求改，改就是
5. **接受拒绝** — PR 被拒不是对你的否定，优雅关闭，继续学习
6. **AI 声明要具体** — 不是泛泛说"用了 AI"，而是说清楚在哪一步用了什么工具
7. **证据驱动** — 写"已测试"之前，确保你确实运行了项目指定的测试命令
8. **用 --force-with-lease** — 永远不用裸 --force，防止销毁 review 线程

## 适用场景

- 首次在开源项目下发表评论
- PR 被要求修改，不确定如何回应
- 项目有 AI 辅助贡献条款，需要写声明
- PR 被拒，想保持良好关系

## 限制

- 不了解特定项目的内部文化和潜规则
- 不处理严重行为准则违规（应报告给项目管理者）
- 沟通风格建议需要结合具体项目上下文
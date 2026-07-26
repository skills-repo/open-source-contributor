---
name: community-etiquette
description: 开源社区沟通规范，Issue 讨论、PR 描述、维护者互动、贡献指南
source:
  type: original
  repo: skills-repo/open-source-contributor
  path: skills/community-etiquette/SKILL.md
  version: 1.0.0
  updated: 2026-07-26
metadata:
  category: 社区
  platform: GitHub
  difficulty: 入门
---

# 社区礼仪

> 开源社区沟通的软技能：如何提问、如何写 PR 描述、如何与维护者有效互动。

## 能力

- **Issue 沟通**：如何表达兴趣、询问澄清、请求分配
- **PR 描述优化**：标题格式、描述结构、关联 Issue 方式
- **维护者互动**：感谢审查、接受反馈、推动进展
- **CONTRIBUTING.md 解读**：自动提取项目的贡献规则
- **文化适应**：不同项目的沟通风格（正式/轻松/直接）

## 使用方式

在 Claude Code 中使用 `/community-etiquette` 调用。

```
/community-etiquette 帮我起草在 issue #123 下的评论
/community-etiquette 审查这个 PR 描述是否符合项目规范
```

## 沟通模板

### Issue 兴趣表达

```markdown
Hi, I'd like to work on this issue. Based on my understanding, the fix involves:
- <具体技术点 1>
- <具体技术点 2>

I've read the CONTRIBUTING guide and will follow the project's PR process.
Could you assign this to me? Thanks!
```

### PR 审查感谢

```markdown
Thanks for the review! I've addressed all feedback:
- <改动 1>: <说明>
- <改动 2>: <说明>

All review conversations should now be resolved. Please re-review when convenient.
```

### PR 关闭感谢（PR 未被合并）

```markdown
Thanks for the review and feedback. I understand this approach isn't the right fit.
I've closed this PR and will continue learning the codebase. Appreciate your time!
```

## 黄金法则

1. **先读 CONTRIBUTING.md** — 80% 的沟通问题源于没读贡献指南
2. **小 PR，早沟通** — 大改动先开 Issue 讨论，不要闷头写一周
3. **感谢审查时间** — 维护者用业余时间审查，心存感激
4. **不争论风格** — 如果维护者要求改，改就是
5. **接受拒绝** — PR 被拒不是对你的否定，优雅关闭，继续学习

## 适用场景

- 首次在开源项目下发表评论
- PR 被要求修改，不确定如何回应
- 需要解释复杂的技术决策
- PR 被拒，想保持良好关系

## 限制

- 不了解特定项目的内部文化和潜规则
- 不处理严重行为准则违规（应报告给项目管理者）
- 沟通风格建议需要结合具体项目上下文
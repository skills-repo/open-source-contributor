---
name: issue-finder
description: 智能发现高价值 GitHub Issue，通过正向标签检测和优先级评分找到最佳贡献机会
source:
  type: derived
  repo: skills-repo/open-source-contributor
  path: skills/issue-finder/SKILL.md
  version: 1.6.0
  updated: 2026-07-26
  url: https://clawhub.ai/skills/issue-finder
metadata:
  category: 发现
  platform: GitHub
  difficulty: 入门
---

# Issue 发现器

> 在成千上万的 Issue 中找到最值得投入的贡献机会。不是随便找一个 bug 修，而是找到维护者认可的、有清晰修复路径的 Issue。

## 能力

- **正向标签检测**：识别 queueable-fix、source-repro、fix-shape-clear 等维护者认可标签
- **优先级评分**：按标签组合计算贡献价值（Diamond → Gold → Silver）
- **多仓库搜索**：跨组织搜索高价值 Issue
- **重复检测**：检查是否已有 PR 在处理
- **可行性评估**：修复范围、技术栈匹配、时间估算

## 使用方式

在 Claude Code 中使用 `/issue-finder` 调用。

```
/issue-finder 在 openclaw/openclaw 中找值得修的 issue
/issue-finder 跨多个仓库搜索 good first issue
```

## 正向标签优先级

| 优先级 | 标签组合 | 合并率 |
|--------|---------|--------|
| 🦞 Diamond | queueable-fix + source-repro + impact:* | 90%+ |
| 💎 Gold | fix-shape-clear + impact:* | 80%+ |
| 🔥 Platinum | source-repro + severity:critical | 75%+ |
| 🥈 Silver | good first issue + help wanted | 60%+ |
| ✅ Standard | 单个正向标签 | 50%+ |
| ⚪ Low | 无正向标签 | <30% |

## 工作流

1. 指定目标仓库（单个或多个）
2. AI 扫描仓库标签体系，识别正向标签
3. 搜索带有正向标签的开放 Issue
4. 按优先级排序，检查是否有已有 PR
5. 输出 TOP 5 推荐，含标签组合和预估难度

## 搜索命令

```bash
# 发现标签体系
gh api repos/owner/repo/labels --paginate | jq '.[].name' | grep -E '(queueable|fix-shape|source-repro|impact|good-first)'

# 搜索高价值 Issue
gh issue list --repo owner/repo --label "queueable-fix,source-repro" --state open --json number,title,labels
```

## 适用场景

- 刚开始参与某个开源项目，不知道从哪入手
- 想提高 PR 合并率，找维护者认可的需求
- 定期扫描多个仓库寻找贡献机会
- 评估项目活跃度和贡献友好度

## 限制

- 依赖项目使用规范的标签体系
- 小项目可能没有正向标签，需要人工判断
- 不保证 Issue 未被其他人认领
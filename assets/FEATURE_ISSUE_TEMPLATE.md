---
name: <功能名，kebab-case>
about: 提 feature request issue 用于验证需求是否被维护者接受（拿正向标签即验证通过）
title: "[Feature Request] "
labels: enhancement
---

<!--
优先级顺序：
  1) 目标仓库自带模板 —— 先探测 .github/ISSUE_TEMPLATE/feature_request.yml（issue-forms），有就必须用它的字段
  2) 本骨架 —— 仅在目标仓无模板时作为 fallback
探测命令：
  gh api repos/<owner>/<repo>/issues/templates
  gh api graphql -f query='query($o:String!,$r:String!){repository(owner:$o,name:$r){issueTemplates{name template body}}}' -f o=<owner> -f r=<repo>
-->

## 问题与动机

**我现在做不到什么？**
<具体场景 + 阻塞点，不要写方案>

**绕过它的代价是什么？**
<当前 workaround 与其成本（时间/正确性/维护负担）>

## 建议方案

**最小切片（本次只要求这一片）**
<收敛在单一模块，尽量不碰公共 API 与默认行为>

**后续可扩展（本次不要求）**
<二期方向，明确声明不阻塞>

## 相关线索与查重

| 检查项 | 结论 |
|---|---|
| 讨论区同类诉求 | <discussion URL / 无> |
| 已有 open issue | <#N / 无> |
| 已关闭同类 issue（含 `state_reason`） | <#N + not planned / 无> |
| 代码侧是否已部分实现 | <`gh search code` 结论> |

## 影响面

- 破坏性变更：无 / <说明>
- 配置迁移：无 / <说明>
- 性能影响：无 / <说明>

## 我能投入

- [ ] 我愿意提 PR 实现上面的最小切片
- [ ] 需要先对齐设计，问题是：<1-3 条具体疑问>

## 交付边界（便于维护者快速表态）

<用一句话给维护者一个"可以只同意这一部分"的选项，降低表态成本>

---
<sub>本 issue 由 AI 辅助检索与起草，内容准确性由提交人负责。</sub>

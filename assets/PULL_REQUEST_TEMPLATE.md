<!--
开源贡献 PR 模板（open-source-contributor 资产）。
脚本 scripts/check_contribution.py 的 `pr` 模式会读取本文件的 `##` 标题作为必检章节，
因此：本模板的章节结构即 PR 描述的最低覆盖要求。修改标题前请同步检查脚本逻辑。
-->

## 描述 (Description)

一句话说明改了什么、为什么改。如果是修复，简述复现路径与根因。

## 关联 Issue (Related Issue)

- fixes #000  <!-- 替换为真实 issue 编号，如 #123；#000 仅为占位以便脚本自检 -->

（用 `fixes` 可在合并时自动关闭 Issue；纯引用用 `#<n>`）

## 变更类型 (Type of change)

- [ ] Bug fix（修复缺陷）
- [ ] New feature（新功能）
- [ ] Documentation（文档）
- [ ] Refactor（重构，无行为变化）

## 检查清单 (Checklist)

- [ ] 我已切出独立功能分支（不在 main 直接开发）
- [ ] 改动收敛在最小修改面
- [ ] 已运行项目测试命令且通过
- [ ] commit message 符合 Conventional Commits

## 测试方法 (Test plan)

描述如何验证本 PR（命令 + 预期结果）：

```
<复现/测试命令>
```

## 证据 (Evidence)

贴 BEFORE vs AFTER 的**终端输出**（非截图），应对自动化评审机器人：

```
BEFORE: <命令> → <失败输出>
AFTER:  <命令> → <通过输出>
```

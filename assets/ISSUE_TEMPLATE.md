<!--
开源贡献 Issue 模板（open-source-contributor 资产，issue-creator 子技能的 fallback 骨架）。
目标仓库自带 issue 模板优先；仅在目标仓库无模板时套用本骨架。
脚本 scripts/check_contribution.py 的 `issue` 模式以本文件的 `##` 章节为必检项，
并附语义规则（Environment 含版本/commit SHA、Steps 含期望/实际、Evidence 非空且无"应该可以复现"类未验证措辞）。
修改章节前请同步检查脚本逻辑。

标题（正文外的单独一行，须为可判定的现象陈述）：
  [Bug]: <组件> <在什么条件下> <发生什么可判定现象>
-->

## 概述 (Summary)

<一两句话说明现象与影响：什么组件、在什么条件下、出现什么可判定的错误行为。避免感叹号与情绪化措辞。>

## 环境 (Environment)

- commit: `<git rev-parse HEAD 的 40 位 SHA，如 a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0>`
- 版本: `<产品版本号，如 2026.10.1>`
- OS: `<操作系统与版本，如 macOS 26.5.1>`
- runtime: `<运行时与版本，如 node v20.11.0>`
- 安装方式: `<release / git checkout / built in place>`
- 相关配置 / profile: `<触发缺陷所需的配置、feature flag、profile>`

## 复现步骤 (Steps to Reproduce)

1. `<准备步骤 / 前置条件>`
2. `<执行命令或操作，优先真实 shipped 入口，非测试桩>`
3. `<观察到缺陷的步骤>`

期望（Expected）: `<按文档 / 类型契约应该发生什么>`
实际（Actual）:

```
<缺陷现象的 terminal 输出，贴文本非截图>
```

## 证据 (Evidence)

根因机制链（file:line，能定位则给，不能则留空并说明）:

- `<path/to/file.ts:LINE> — <该行如何导致缺陷>`

Terminal transcript（BEFORE/AFTER，单变量，多次探针稳定）:

```
BEFORE: <命令> → <缺陷输出>
AFTER:  <命令或规避> → <符合预期的输出>（若有）
```

> 能复现但未定位到根因时，保留上方 transcript 并如实写"根因待定位"，不留无根据的猜测。

## 疑似根因与修复方向 (Suspected Cause & Fix Direction)

- 疑似根因（标注为推测，非确证）: `<基于 Evidence 机制链的推测>`
- 最小修复方向: `<维护者视角"小而清晰"的修复建议；无把握则省略，仅提供复现即可>`

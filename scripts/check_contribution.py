#!/usr/bin/env python3
"""check_contribution.py — 开源贡献提交规范检查器（纯标准库，零依赖）

检查四类对象，提交前自检可挡掉大部分"被打回重写"：
  commit       单条 commit message 的格式 / 关联 issue / 行长
  contributing  仓库 CONTRIBUTING.md 的必含章节完整性
  pr           PR 描述对模板(assets/PULL_REQUEST_TEMPLATE.md)章节的覆盖度
  issue        Issue 正文五段式完整度（模板 assets/ISSUE_TEMPLATE.md 驱动 + 语义规则）
  selfcheck    校验内置资产（配置 + 模板）应为 0 ERROR —— 资产与脚本互相验证

规则来源：assets/commit_conventions.json（配置驱动，便于团队自定义）。
PR 必检章节来源：assets/PULL_REQUEST_TEMPLATE.md 的 `##` 标题（模板驱动脚本）。

特性：纯标准库、带 --help、确定性可复现、不联网、只读不修改被检文件。
配置中以 `_` 开头的键为注释/元信息，加载时跳过。

用法:
  python3 check_contribution.py commit --file /tmp/msg.txt
  python3 check_contribution.py commit --message "fix(parser): handle EOF"
  python3 check_contribution.py contributing --file CONTRIBUTING.md
  python3 check_contribution.py pr --file /tmp/pr_body.md
  python3 check_contribution.py issue --file /tmp/issue_body.md
  python3 check_contribution.py selfcheck
  python3 check_contribution.py --help
"""
import argparse
import json
import os
import re
import sys

# 脚本所在目录，用于定位默认资产
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_CONFIG = os.path.join(_HERE, "..", "assets", "commit_conventions.json")
_DEFAULT_TEMPLATE = os.path.join(_HERE, "..", "assets", "PULL_REQUEST_TEMPLATE.md")
_DEFAULT_ISSUE_TEMPLATE = os.path.join(_HERE, "..", "assets", "ISSUE_TEMPLATE.md")


def _load_config(path):
    """读取 JSON 规则配置，跳过 `_` 开头的注释键。返回 (config_dict, errors)。"""
    errors = []
    if not os.path.isfile(path):
        return {}, [f"配置不存在: {path}"]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"配置解析失败: {exc}"]
    if not isinstance(raw, dict):
        return {}, ["配置根必须是 JSON 对象"]
    cfg = {k: v for k, v in raw.items() if not k.startswith("_")}
    # 结构校验
    if not isinstance(cfg.get("allowed_types"), list) or not cfg["allowed_types"]:
        errors.append("allowed_types 必须是非空数组")
    if not isinstance(cfg.get("max_subject_len"), int):
        errors.append("max_subject_len 必须是整数")
    if not isinstance(cfg.get("max_body_line_len"), int):
        errors.append("max_body_line_len 必须是整数")
    if "required_contributing_sections" in cfg and not isinstance(
        cfg["required_contributing_sections"], list
    ):
        errors.append("required_contributing_sections 必须是数组")
    return cfg, errors


def _check_commit(message, cfg):
    errors = []
    text = message.strip()
    if not text:
        return ["commit message 为空"]
    lines = text.splitlines()
    subject = lines[0].strip()
    body = lines[1:]
    allowed = cfg.get("allowed_types", [])
    types = "|".join(re.escape(t) for t in allowed)
    conv = re.compile(rf"^({types})(\([\w.\-/]+\))?!?:\s+.+")
    if not conv.match(subject):
        errors.append(
            f"subject 不符合 Conventional Commits 格式: '{subject}' "
            f"(期望 <type>(<scope>): <subject>，type∈{allowed})"
        )
    max_subj = cfg.get("max_subject_len", 72)
    if len(subject) > max_subj:
        errors.append(f"subject 超长 {len(subject)} > {max_subj} 字符")
    if cfg.get("require_issue_link", True):
        pat = cfg.get("issue_link_regex", r"(#\d+|\b(?:fix|close|resolve|fixes)\s+#\d+)")
        if not re.search(pat, text, re.IGNORECASE):
            errors.append("未关联 issue（建议 'fixes #N' 以合并时自动关闭）")
    max_body = cfg.get("max_body_line_len", 100)
    for i, ln in enumerate(body, start=2):
        if ln.strip() == "":
            continue
        if len(ln) > max_body:
            errors.append(f"第 {i} 行超长 {len(ln)} > {max_body} 字符: {ln[:40]}…")
    return errors


def _check_contributing(text, cfg):
    errors = []
    low = text.lower()
    groups = cfg.get("required_contributing_sections", [])
    for group in groups:
        aliases = group if isinstance(group, list) else [group]
        if not any(a.lower() in low for a in aliases):
            label = " / ".join(aliases)
            errors.append(f"CONTRIBUTING 缺少章节（匹配任一即可）: {label}")
    return errors


def _template_sections(template_path):
    with open(template_path, "r", encoding="utf-8") as fh:
        tpl = fh.read()
    heads = re.findall(r"^##\s+(.+?)\s*$", tpl, re.MULTILINE)
    return [h.strip() for h in heads if h.strip()]


def _check_pr(body_text, template_path, cfg):
    errors = []
    heads = _template_sections(template_path)
    if not heads:
        errors.append(f"模板无 `##` 章节: {template_path}")
        return errors
    low = body_text.lower()
    for h in heads:
        if h.lower() not in low:
            errors.append(f"PR 描述缺少模板章节: {h}")
    if cfg.get("require_issue_link", True):
        pat = cfg.get("issue_link_regex", r"(#\d+|\b(?:fix|close|resolve|fixes)\s+#\d+)")
        if not re.search(pat, body_text, re.IGNORECASE):
            errors.append("PR 未关联 issue（建议 'fixes #N'）")
    return errors


# Issue 语义规则常量（与 assets/ISSUE_TEMPLATE.md 互为验证，改动须同步）
_UNVERIFIED_ISSUE_PHRASES = [
    "应该可以复现", "应该能复现", "应该可复现", "大概率能", "肯定能复现", "一定能复现",
    "should be reproducible", "should reproduce",
]
_ISSUE_PLACEHOLDERS = ["TODO", "待补充", "FIXME"]
_VERSION_OR_SHA_RE = re.compile(r"(\b[0-9a-f]{7,40}\b|\d+\.\d+(?:\.\d+)?)", re.IGNORECASE)
_EXPECTED_ACTUAL_RE = re.compile(r"(期望|实际|expected|actual)", re.IGNORECASE)


def _split_sections(text):
    """按 `##` 标题切分 markdown，返回 [(heading, content), ...]（不含首个标题前的引导内容）。"""
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    sections = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((m.group(1).strip(), text[start:end]))
    return sections


def _issue_required_sections(template_path):
    """Issue 模板 `##` 标题即必检段落（模板驱动，与 pr 模式同构）。"""
    return _template_sections(template_path)


def _issue_section_content(sections, *keywords):
    """按关键字（任一命中 heading 即可）取段落内容；段落不存在返回 None。"""
    for kw in keywords:
        for heading, content in sections:
            if kw.lower() in heading.lower():
                return content
    return None


def _check_issue(text, template_path, cfg):
    """Issue 正文检查：五段齐全 + Environment 可定位 + Steps 期望/实际 + Evidence 非空且已验证 + 无占位符。"""
    errors = []
    heads = _issue_required_sections(template_path)
    if not heads:
        errors.append(f"Issue 模板无 `##` 章节: {template_path}")
        return errors
    low = text.lower()
    for h in heads:
        if h.lower() not in low:
            errors.append(f"Issue 缺少段落: {h}")
    sections = _split_sections(text)

    # Environment：须含版本号或 commit SHA（复现可定位的前提）
    env = _issue_section_content(sections, "Environment", "环境")
    if env is not None and not _VERSION_OR_SHA_RE.search(env):
        errors.append("环境 (Environment) 未含版本号或 commit SHA（复现不可定位）")

    # Steps：须含期望/实际对照
    steps = _issue_section_content(sections, "Steps to Reproduce", "复现步骤")
    if steps is not None and not _EXPECTED_ACTUAL_RE.search(steps):
        errors.append("复现步骤 (Steps to Reproduce) 缺少 期望/实际（Expected/Actual）对照")

    # Evidence：非空，且不得含"应该可以复现"类未验证措辞
    evidence = _issue_section_content(sections, "Evidence", "证据")
    if evidence is not None:
        if not evidence.strip():
            errors.append("证据 (Evidence) 段落为空（须贴 transcript / 日志 / file:line 机制链）")
        else:
            for phrase in _UNVERIFIED_ISSUE_PHRASES:
                if phrase.lower() in evidence.lower():
                    errors.append(f"证据 (Evidence) 含未验证措辞「{phrase}」——只写确已发生的复现")
                    break

    # 全文不得残留占位符
    for ph in _ISSUE_PLACEHOLDERS:
        if ph.lower() in low:
            errors.append(f"Issue 残留占位符: {ph}")
    return errors


def _read_file_or_die(path):
    if not os.path.isfile(path):
        sys.stderr.write(f"[ERROR] 文件不存在: {path}\n")
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="开源贡献提交规范检查器（commit / contributing / pr / issue / selfcheck）"
    )
    ap.add_argument("--config", default=_DEFAULT_CONFIG, help="规则配置 JSON 路径")
    ap.add_argument("--template", default=_DEFAULT_TEMPLATE, help="PR 模板 MD 路径")
    ap.add_argument("--issue-template", default=_DEFAULT_ISSUE_TEMPLATE,
                    help="Issue 模板 MD 路径")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_commit = sub.add_parser("commit", help="检查 commit message")
    g = p_commit.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="commit message 文件路径")
    g.add_argument("--message", help="commit message 字符串")

    p_contrib = sub.add_parser("contributing", help="检查 CONTRIBUTING.md 完整性")
    p_contrib.add_argument("--file", required=True, help="CONTRIBUTING.md 路径")

    p_pr = sub.add_parser("pr", help="检查 PR 描述对模板的覆盖度")
    p_pr.add_argument("--file", required=True, help="PR 描述文件路径")

    p_issue = sub.add_parser("issue", help="检查 Issue 正文的五段式完整度")
    p_issue.add_argument("--file", required=True, help="Issue 正文文件路径")

    sub.add_parser("selfcheck", help="校验内置资产（配置+模板）应为 0 ERROR")

    args = ap.parse_args(argv)

    if args.cmd == "selfcheck":
        cfg, cerr = _load_config(args.config)
        print(f"[selfcheck] 配置 {os.path.relpath(args.config)} : "
              f"{'OK' if not cerr else str(cerr)}")
        heads = _template_sections(args.template) if os.path.isfile(args.template) else []
        tpl_err = [] if heads else [f"模板无章节: {args.template}"]
        print(f"[selfcheck] 模板 {os.path.relpath(args.template)} : "
              f"{len(heads)} 个章节 {'OK' if not tpl_err else tpl_err}")
        # 模板自身应满足自身章节（模板驱动脚本，且回检 0 错误）
        tpl_text = _read_file_or_die(args.template)
        pr_err = _check_pr(tpl_text, args.template, cfg)
        print(f"[selfcheck] 用模板回检自身 PR 章节 : "
              f"{'0 ERROR' if not pr_err else pr_err}")
        # Issue 模板回检（五段式语义规则与模板互为验证）
        itpl_err = []
        issue_err = []
        if os.path.isfile(args.issue_template):
            iheads = _template_sections(args.issue_template)
            itpl_err = [] if iheads else [f"Issue 模板无章节: {args.issue_template}"]
            print(f"[selfcheck] Issue 模板 {os.path.relpath(args.issue_template)} : "
                  f"{len(iheads)} 个章节 {'OK' if not itpl_err else itpl_err}")
            issue_err = _check_issue(_read_file_or_die(args.issue_template),
                                     args.issue_template, cfg)
            print(f"[selfcheck] Issue 模板回检五段式规则 : "
                  f"{'0 ERROR' if not issue_err else issue_err}")
        else:
            itpl_err = [f"Issue 模板不存在: {args.issue_template}"]
            print(f"[selfcheck] Issue 模板 {os.path.relpath(args.issue_template)} : {itpl_err}")
        total = len(cerr) + len(tpl_err) + len(pr_err) + len(itpl_err) + len(issue_err)
        if total == 0:
            print("[selfcheck] PASS — 资产与脚本互相验证通过（0 ERROR）")
            return 0
        print(f"[selfcheck] FAIL — 共 {total} 项错误")
        return 1

    cfg, cerr = _load_config(args.config)
    if cerr:
        for e in cerr:
            sys.stderr.write(f"[ERROR] {e}\n")
        return 2

    if args.cmd == "commit":
        msg = _read_file_or_die(args.file) if args.file else args.message
        errs = _check_commit(msg, cfg)
        if errs:
            for e in errs:
                print(f"ERROR: {e}")
            print(f"\ncommit 检查未通过：{len(errs)} 项")
            return 1
        print("commit 检查通过：0 ERROR")
        return 0

    if args.cmd == "contributing":
        text = _read_file_or_die(args.file)
        errs = _check_contributing(text, cfg)
        if errs:
            for e in errs:
                print(f"ERROR: {e}")
            print(f"\nCONTRIBUTING 检查未通过：{len(errs)} 项")
            return 1
        print("CONTRIBUTING 检查通过：0 ERROR")
        return 0

    if args.cmd == "pr":
        text = _read_file_or_die(args.file)
        errs = _check_pr(text, args.template, cfg)
        if errs:
            for e in errs:
                print(f"ERROR: {e}")
            print(f"\nPR 检查未通过：{len(errs)} 项")
            return 1
        print("PR 检查通过：0 ERROR")
        return 0

    if args.cmd == "issue":
        text = _read_file_or_die(args.file)
        errs = _check_issue(text, args.issue_template, cfg)
        if errs:
            for e in errs:
                print(f"ERROR: {e}")
            print(f"\nIssue 检查未通过：{len(errs)} 项")
            return 1
        print("Issue 检查通过：0 ERROR")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())

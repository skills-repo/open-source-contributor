#!/usr/bin/env python3
"""poll_pr_state.py — PR 提交后监控循环的只读状态拉取（pr-landing-monitor 子技能）。

用法:
    export GITHUB_TOKEN=ghp_xxx   # 或 --token 传入
    python3 poll_pr_state.py <owner/repo> <PR号> [--comments N]

一次拉齐 monitoring-playbook 定义的六项状态，输出可 diff 的文本快照:
state/merged、mergeable_state、labels、check-runs 结论分布与失败清单、
最近评论与 reviews（时间倒序摘要）。只读，不写任何内容。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request


def api(path: str, token: str) -> dict | list:
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="只读拉取 PR 监控状态快照")
    parser.add_argument("repo", help="owner/repo")
    parser.add_argument("number", type=int, help="PR 号")
    parser.add_argument("--comments", type=int, default=5, help="最近评论条数（默认 5）")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""))
    args = parser.parse_args()
    if not args.token:
        print("缺少 token：设 GITHUB_TOKEN 或传 --token", file=sys.stderr)
        return 2
    repo, n = args.repo, args.number

    pr = api(f"/repos/{repo}/pulls/{n}", args.token)
    head_sha = pr.get("head", {}).get("sha", "")
    print(f"PR #{n} {pr.get('state')} merged_at={pr.get('merged_at')}")
    print(f"head={head_sha[:12]} base={pr.get('base', {}).get('ref')}")
    print(
        f"mergeable={pr.get('mergeable')} mergeable_state={pr.get('mergeable_state')}"
    )
    labels = [label["name"] for label in pr.get("labels", [])]
    print(f"labels: {', '.join(labels) if labels else '(none)'}")

    runs = api(f"/repos/{repo}/commits/{head_sha}/check-runs?per_page=100", args.token).get(
        "check_runs", []
    )
    counts: dict[str, int] = {}
    failures: list[str] = []
    for run in runs:
        conclusion = run.get("conclusion") or run.get("status") or "?"
        counts[conclusion] = counts.get(conclusion, 0) + 1
        if conclusion == "failure":
            failures.append(run["name"])
    pending = sum(counts.get(key, 0) for key in ("in_progress", "queued", "pending", "waiting"))
    print(f"checks: {len(runs)} runs {counts} pending={pending}")
    for name in failures:
        print(f"  FAIL: {name}")

    for kind, path in (("comment", f"/repos/{repo}/issues/{n}/comments?per_page={args.comments}&sort=created&direction=desc"), ("review", f"/repos/{repo}/pulls/{n}/reviews?per_page={args.comments}")):
        items = api(path, args.token)
        if isinstance(items, dict):
            items = items.get("comments", [])
        for item in reversed(items[-args.comments :]):
            body = (item.get("body") or "").replace("\n", " ")[:120]
            print(f"{kind}: {item.get('created_at') or item.get('submitted_at')} "
                  f"{item.get('user', {}).get('login')}: {body}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

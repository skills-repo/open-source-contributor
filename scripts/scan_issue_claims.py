#!/usr/bin/env python3
"""判定 GitHub issue 的真实可做性（是否已被 PR 认领/修复）。

用法:
    # A) 直接给 issue 号
    python3 scan_issue_claims.py openclaw/openclaw 122622 155627 138929

    # B) 扫某标签下的 open issue
    python3 scan_issue_claims.py openclaw/openclaw --label clawsweeper:queueable-fix --limit 60

Token 来源（按顺序）: $GITHUB_TOKEN / $GH_TOKEN / 当前目录仓库 git remote 内嵌凭据。
Token 不会被打印。

为什么要这个脚本（三个易踩的坑）:
  1. search 的 `-linked:pr` 只索引 Fixes/Closes 关键字建立的链接，会漏判人工引用的 PR。
  2. 已合并 PR 的 `state` 字段同样是 "closed"，必须用 pull_request.merged_at 判定。
  3. MERGED 只代表"疑似已修复"——issue 常在修复合并后不被关闭，须回到 HEAD 复核代码。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://api.github.com"


def get_token() -> str:
    for env in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(env):
            return os.environ[env].strip()
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:  # noqa: BLE001
        sys.exit("no token: set GITHUB_TOKEN or run inside a repo with a credentialed origin")
    m = re.match(r"https://([^@]+)@", url)
    if not m:
        sys.exit("no token: origin has no embedded credentials")
    cred = m.group(1)
    return cred.split(":", 1)[1] if ":" in cred else cred


class Client:
    def __init__(self, token: str) -> None:
        self.token = token

    def get(self, path: str):
        req = urllib.request.Request(
            f"{API}{path}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=45) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code in (403, 429) and attempt < 2:
                    continue
                return {"__error__": f"HTTP {e.code}"}
            except Exception as e:  # noqa: BLE001
                if attempt == 2:
                    return {"__error__": str(e)}
        return {"__error__": "unreachable"}


def classify(client: Client, repo: str, num: int):
    """返回 (num, bucket, prs)。bucket ∈ CLEAN/ATTEMPTED/MERGED/CLAIMED/ERROR。"""
    tl = client.get(f"/repos/{repo}/issues/{num}/timeline?per_page=100")
    if isinstance(tl, dict) and "__error__" in tl:
        return num, "ERROR", [tl["__error__"]]

    open_prs, merged_prs, closed_prs = [], [], []
    for e in tl:
        if e.get("event") != "cross-referenced":
            continue
        src = (e.get("source") or {}).get("issue") or {}
        pr = src.get("pull_request") or {}
        if not pr:
            continue
        rec = f"PR#{src.get('number')} — {(src.get('title') or '')[:60]}"
        if pr.get("merged_at"):          # 陷阱 2: merged 后 state 仍是 closed
            merged_prs.append(f"{rec}  [merged {pr['merged_at'][:10]}]")
        elif src.get("state") == "open":
            open_prs.append(rec)
        else:
            closed_prs.append(rec)

    if open_prs:
        return num, "CLAIMED", open_prs
    if merged_prs:
        return num, "MERGED", merged_prs
    if closed_prs:
        return num, "ATTEMPTED", closed_prs
    return num, "CLEAN", []


LABELS = {
    "CLEAN": "从未有 PR —— 竞争最低，首选（仍须复核代码确认缺陷存在）",
    "ATTEMPTED": "仅有未合并 PR —— 查前次为何被拒/搁置，再决定",
    "MERGED": "存在已合并 PR —— 疑似已修复，必须回 HEAD 复核",
    "CLAIMED": "存在 open PR —— 已被认领，放弃",
    "ERROR": "查询失败",
}
ORDER = ["CLEAN", "ATTEMPTED", "MERGED", "CLAIMED", "ERROR"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", help="owner/repo")
    ap.add_argument("numbers", nargs="*", type=int, help="issue 号")
    ap.add_argument("--label", help="改为扫描该标签下的 open issue")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--fields", action="store_true", help="附带标题等元信息")
    args = ap.parse_args()

    client = Client(get_token())

    numbers = list(args.numbers)
    meta: dict[int, dict] = {}
    if args.label:
        q = f"repo:{args.repo}+is:issue+is:open+label:{args.label}"
        data = client.get(f"/search/issues?q={q}&sort=created&order=desc&per_page={args.limit}")
        if "__error__" in data:
            sys.exit(f"label search failed: {data['__error__']}")
        for it in data.get("items", []):
            numbers.append(it["number"])
            meta[it["number"]] = {
                "title": it["title"],
                "labels": [l["name"] for l in it.get("labels", [])],
                "created": it["created_at"],
            }
        print(f"label `{args.label}`: {data.get('total_count')} open, 取最新 {len(numbers)}\n")

    if not numbers:
        sys.exit("no issues to scan")

    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(lambda n: classify(client, args.repo, n), numbers))

    buckets: dict[str, list] = {}
    for r in results:
        buckets.setdefault(r[1], []).append(r)

    print("=" * 72)
    for k in ORDER:
        if k in buckets:
            print(f"  {k:10s} {len(buckets[k]):3d}   {LABELS[k]}")
    print("=" * 72)

    for k in ORDER:
        if k not in buckets:
            continue
        print(f"\n### {k} — {LABELS[k]}")
        for num, _, prs in sorted(buckets[k]):
            m = meta.get(num)
            if m:
                prio = [x for x in m["labels"] if x in ("P0", "P1", "P2", "P3")]
                print(f"  #{num}  {prio} {m['title'][:76]}")
            else:
                print(f"  #{num}")
            for p in prs:
                print(f"        {p}")


if __name__ == "__main__":
    main()

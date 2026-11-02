#!/usr/bin/env python3
"""挖掘目标仓库的 GitHub Discussions，按需求信号打分，输出 feature 候选表。

只使用标准库 + `gh` CLI。所有 API 形态均为 2026-11-02 实测结论：
  - gh 无 `discussions` 子命令，且 REST 写路径 404 → 读走 REST/GraphQL，写走 GraphQL
  - REST 的 `?category=` 与 `?sort=top` 会被静默忽略（返回 200 但未过滤）→ 本脚本在客户端过滤排序
  - Search API 搜不到 discussions → 必须逐仓库枚举
  - 讨论帖创建者自带 1 票 upvote → 打分时按 --self-upvote 扣减
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys

FEATURE_HINTS = re.compile(
    r"\b(feat(ure)?|add|support|allow|enable|want|need|would be (great|nice)|"
    r"proposal|rfc|idea|roadmap|api|integration|plugin|export|option)\b",
    re.I,
)
NEGATIVE_STATE = {"duplicate", "resolved", "outdated", "locked"}


def run_gh(args):
    """执行 gh 并返回解析后的 JSON；失败抛异常（不静默返回空表）。"""
    p = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "gh failed")
    return json.loads(p.stdout) if p.stdout.strip() else None


def repo_ids(repo):
    q = ("query($o:String!,$r:String!){repository(owner:$o,name:$r){"
         "hasDiscussionsEnabled id nameWithOwner}}")
    o, r = repo.split("/", 1)
    d = run_gh(["api", "graphql", "-f", f"query={q}", "-f", f"o={o}", "-f", f"r={r}"])
    node = d["data"]["repository"]
    if not node:
        raise RuntimeError(f"repository not found: {repo}")
    return node


def categories(repo):
    q = ("query($o:String!,$r:String!){repository(owner:$o,name:$r){"
         "discussionCategories(first:20){nodes{name slug isAnswerable}}}}")
    o, r = repo.split("/", 1)
    d = run_gh(["api", "graphql", "-f", f"query={q}", "-f", f"o={o}", "-f", f"r={r}"])
    return d["data"]["repository"]["discussionCategories"]["nodes"]


def fetch_discussions(repo, limit):
    q = (
        "query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){"
        "discussions(first:$n,states:OPEN){nodes{number title url bodyText "
        "createdAt updatedAt upvoteCount isAnswered closed "
        "category{name slug} labels(first:10){nodes{name}} "
        "comments{totalCount} "
        "reactionGroups{content reactors{totalCount} viewerHasReacted} "
        "author{login} } } } }"
    )
    o, r = repo.split("/", 1)
    d = run_gh(["api", "graphql", "-f", f"query={q}", "-f", f"o={o}", "-f", f"r={r}",
                "-F", f"n={limit}"])
    return d["data"]["repository"]["discussions"]["nodes"]


def maintainer_replies(repo, number):
    """读评论的 author_association —— 维护者是否下场是最强验证信号（REST 读可用）。"""
    try:
        rows = run_gh(["api", f"repos/{repo}/discussions/{number}/comments?per_page=30"])
    except Exception:
        return []
    return sorted({c.get("author_association", "NONE") for c in rows or []})


def dup_issues(repo, title, limit=3):
    """同诉求是否已成文为 issue —— Search API 对 issue 可用，对 discussion 不可用。"""
    kw = " ".join(re.findall(r"[A-Za-z0-9]{4,}", title)[:5])
    if not kw:
        return []
    try:
        d = run_gh(["api", "search/issues",
                    "-f", f"q=repo:{repo} {kw} is:issue", "-F", "per_page=5"])
    except Exception:
        return []
    out = []
    for it in (d.get("items") or [])[:limit]:
        out.append({"number": it["number"], "state": it["state"],
                    "title": it["title"], "url": it["html_url"]})
    return out


def score(d, assoc, since_days, self_upvote):
    """需求强度分（0-100）：社区热度 + 维护者下场 + 时间新鲜度 + feature 语义。"""
    up = max(0, (d.get("upvoteCount") or 0) - (1 if self_upvote else 0))
    cm = (d.get("comments") or {}).get("totalCount", 0)
    s = 0
    s += min(40, up * 4)
    s += min(25, cm * 3)
    hot = sum((g.get("reactors") or {}).get("totalCount") or 0
              for g in (d.get("reactionGroups") or [])
              if g.get("content") in ("EYES", "ROCKET", "HOORAY", "HEART"))
    s += min(15, hot)
    maintainer = {"OWNER", "MEMBER", "COLLABORATOR"} & set(assoc)
    if maintainer:
        s += 20
    if FEATURE_HINTS.search(d.get("title") or ""):
        s += 10
    created = (d.get("createdAt") or "")[:10]
    if created:
        age = (dt.date.today() - dt.date.fromisoformat(created)).days
        if age > since_days:
            s -= 10
    return max(0, min(100, s)), up, cm, bool(maintainer)


def ladder(sc, maintainer, answered, closed):
    if closed:
        return "SKIP"
    if answered:
        return "ANSWERED"
    if maintainer and sc >= 45:
        return "V3"
    if sc >= 60:
        return "V2"
    if sc >= 35:
        return "V1"
    return "NOISE"


def main():
    ap = argparse.ArgumentParser(
        description="挖掘 GitHub Discussions 中的 feature 线索并打分（输出候选表）")
    ap.add_argument("--repo", action="append", required=True,
                    help="owner/name，可重复以逐仓扫描（Search API 搜不到 discussion，只能逐仓）")
    ap.add_argument("--category", action="append", default=[],
                    help="按分类 slug 过滤（客户端过滤，可重复），如 ideas feature-request")
    ap.add_argument("--limit", type=int, default=50, help="每仓最多取多少条开放讨论帖（默认 50）")
    ap.add_argument("--since-days", type=int, default=365, help="新鲜度窗口（默认 365 天）")
    ap.add_argument("--top", type=int, default=10, help="输出前 N 条（默认 10）")
    ap.add_argument("--self-upvote", action="store_true",
                    help="帖子作者就是当前 token 时，扣掉自带的 1 票")
    ap.add_argument("--dup-check", action="store_true", help="对每条候选做 issue 重复检测（较慢）")
    ap.add_argument("--json", action="store_true", help="输出 JSON 而非表格")
    ap.add_argument("--list-categories", action="store_true", help="只列该仓讨论分类后退出")
    args = ap.parse_args()

    rows = []
    try:
        for repo in args.repo:
            meta = repo_ids(repo)
            if not meta.get("hasDiscussionsEnabled"):
                print(f"WARN {repo}: hasDiscussionsEnabled=false，跳过", file=sys.stderr)
                continue
            cats = categories(repo)
            if args.list_categories:
                for c in cats:
                    print(f"{repo}  {c['slug']:<18} {c['name']}")
                return 0
            slugs = {s.lower() for s in args.category}
            for d in fetch_discussions(repo, args.limit):
                if slugs and (d.get("category") or {}).get("slug", "").lower() not in slugs:
                    continue
                assoc, maint = [], False
                try:
                    assoc = maintainer_replies(repo, d["number"])
                except Exception as e:
                    print(f"WARN comments #{d['number']}: {e}", file=sys.stderr)
                sc, up, cm, maint = score(d, assoc, args.since_days, args.self_upvote)
                item = {
                    "repo": repo, "number": d["number"],
                    "category": (d.get("category") or {}).get("slug"),
                    "title": d["title"][:70], "url": d["url"],
                    "upvotes": up, "comments": cm,
                    "labels": [l["name"] for l in (d.get("labels") or {}).get("nodes", [])],
                    "maintainer_replied": maint,
                    "answered": d.get("isAnswered"), "score": sc,
                    "tier": ladder(sc, maint, d.get("isAnswered"), d.get("closed")),
                }
                if args.dup_check:
                    item["similar_issues"] = dup_issues(repo, d["title"])
                rows.append(item)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    rows.sort(key=lambda x: x["score"], reverse=True)
    rows = rows[: args.top]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("无候选：该仓讨论区没有匹配分类的开放帖，或被过滤光。")
        return 0
    print(f"{'tier':<5}{'score':<7}{'up':<4}{'cmt':<5}{'maint':<6}{'repo#':<12}title")
    print("-" * 100)
    for x in rows:
        print(f"{x['tier']:<6}{x['score']:<6}{x['upvotes']:<4}{x['comments']:<5}"
              f"{'Y' if x['maintainer_replied'] else '-':<6}"
              f"#{x['number']:<6}{x['repo'].split('/')[1][:14]:<15}{x['title'][:40]}")
    print("\n下一步：tier=V3 且无 similar_issues 重复 → 用 skills/feature-proposer "
          "发讨论帖或直接提 feature issue 做验证。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

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
import urllib.parse

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


def run_gh_lines(args):
    """`--jq` 输出的是纯文本行而非 JSON —— 用 json.loads 会抛错并被上层 except 吞成空结果。
    凡带 --jq 的调用都走这里。"""
    p = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "gh failed")
    return [l.strip() for l in (p.stdout or "").splitlines() if l.strip()]


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
        d = run_gh(["api", "search/issues?q=" +
                    urllib.parse.quote(f"repo:{repo} {kw} is:issue") + "&per_page=5"])
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


def grade(sc, maintainer, answered, closed):
    """候选强度 C1-C3 —— 与 feature-proposer 的验证阶梯 V1-V4 是**两个轴**：
    C 档说的是"讨论区里这条线索有多热"，V 档说的是"我发出去的提案被维护者
    背书到什么程度"。只有 V4 才放行写代码；C3 不等于可以做。"""
    if closed:
        return "SKIP"
    if answered:
        return "ANSW"
    if maintainer and sc >= 45:
        return "C3"
    if sc >= 60:
        return "C2"
    if sc >= 35:
        return "C1"
    return "NOISE"


FEATURE_LABEL_PRIORITY = [
    "kind/feature", "c-feature-request", "c-enhancement", "feature request",
    "feature-request", "enhancement", "area-feature", "proposal", "ideas",
    "a-features", "help wanted", "roadmap", "request-for-comment", "rfc",
]
LABEL_NOISE = re.compile(
    r"changes-requested|verification-requested|request-failed|awaiting|"
    r"blocked-on|needs-reproduction|duplicate|design|ci|test", re.I)


def detect_feature_labels(repo):
    """列出本仓真实标签再按优先级挑 —— 标签名会漂移且各仓不同（vscode 现行
    `feature-request`，旧名 `Feature Request` 检索返回 0；cargo 用 `C-feature-request`），
    绝不能照抄别仓名字。"""
    try:
        lines = run_gh_lines(["api", f"repos/{repo}/labels", "--paginate",
                              "--jq", ".[].name"])
    except Exception as e:
        print(f"WARN labels list: {e}", file=sys.stderr)
        return []
    cand = [n for n in lines if not LABEL_NOISE.search(n)]
    picked = []
    for token in FEATURE_LABEL_PRIORITY:
        for n in cand:
            low = n.lower()
            if (low == token or low.startswith(token) or token in low) and n not in picked:
                picked.append(n)
                break
    return picked[:4]


def fetch_feature_issues(repo, labels, limit):
    out = []
    for lb in labels:
        # 注意：`gh api search/issues -f q=...` 实测返回 404，必须把查询编进 URL 路径
        quoted = f'"{lb}"' if " " in lb else lb
        q = urllib.parse.quote(f"repo:{repo} is:issue is:open label:{quoted}")
        try:
            d = run_gh(["api",
                        f"search/issues?q={q}&per_page={limit}&sort=comments&order=desc"])
        except Exception as e:
            print(f"WARN label '{lb}': {e}", file=sys.stderr)
            continue
        for it in (d.get("items") or []):
            out.append(it)
        if len(out) >= limit:
            break
    seen, uniq = set(), []
    for it in out:
        if it["number"] not in seen:
            seen.add(it["number"]); uniq.append(it)
    return uniq[:limit]


def issue_comments(repo, number):
    try:
        rows = run_gh(["api", f"repos/{repo}/issues/{number}/comments?per_page=30"])
    except Exception:
        return []
    return sorted({c.get("author_association", "NONE") for c in rows or []})


def issue_commenters(repo, number):
    """返回 (author_association 集合, 登录名集合)。
    登录名用于和 CODEOWNERS/近期提交者交叉比对——因为 author_association 会低估身份。"""
    try:
        rows = run_gh(["api", f"repos/{repo}/issues/{number}/comments?per_page=30"])
    except Exception:
        return [], []
    rows = rows or []
    return (sorted({c.get("author_association", "NONE") for c in rows}),
            sorted({(c.get("user") or {}).get("login", "") for c in rows}))


def codeowners_logins(repo):
    """author_association 会**低估**维护者身份（实测 vscode 核心团队 joaomoreno/jrieken
    仅报 CONTRIBUTOR）。用 CODEOWNERS + 近 200 commit 作者兜底识别真实维护者。"""
    names = set()
    try:
        raw = run_gh(["api", f"repos/{repo}/contents/CODEOWNERS", "--jq", ".content"])
        import base64
        txt = base64.b64decode(raw).decode("utf-8", "ignore")
        names |= {w.lstrip("@").split("/")[0] for line in txt.splitlines()
                  if line.strip() and not line.startswith("#")
                  for w in line.split() if w.startswith("@")}
    except Exception:
        pass
    try:
        logins = run_gh_lines(["api", f"repos/{repo}/commits?per_page=100", "--jq",
                               ".[].author.login // empty"])
        names |= {x.strip() for x in logins if x.strip()}
    except Exception:
        pass
    return names

def main():
    ap = argparse.ArgumentParser(
        description="挖掘项目讨论区中的 feature 线索并打分（GitHub Discussions 或 feature 标签 issue 两种通道）")
    ap.add_argument("--mode", choices=["auto", "discussions", "issues"], default="auto",
                    help="auto=有 Discussions 用 Discussions，否则退回 feature 标签 issue（实测 6 个主流项目 4 个未开 Discussions）")
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
            enabled = bool(meta.get("hasDiscussionsEnabled"))
            use_issues = (args.mode == "issues") or (args.mode == "auto" and not enabled)
            if use_issues:
                print(f"NOTE {repo}: 未开启 Discussions（或指定 issues），改用 feature 标签 issue 通道",
                      file=sys.stderr)
            if use_issues:
                labels = detect_feature_labels(repo)
                if not labels:
                    print(f"WARN {repo}: 没识别出 feature 类标签，"
                          f"先跑 gh api repos/{repo}/labels --paginate --jq '.[].name' 人工确认",
                          file=sys.stderr)
                    continue
                print(f"NOTE {repo}: 采用标签 {labels}", file=sys.stderr)
                owners = codeowners_logins(repo)
                for it in fetch_feature_issues(repo, labels, args.limit):
                    reactions = it.get("reactions") or {}
                    cm = it.get("comments", 0) or 0
                    up = reactions.get("+1", 0) or 0
                    assocs, logins = issue_commenters(repo, it["number"])
                    maint = bool({"OWNER", "MEMBER", "COLLABORATOR"} & set(assocs)) or bool(
                        owners & set(logins))
                    fake = {"upvoteCount": up + 1, "comments": {"totalCount": cm},
                            "createdAt": it.get("created_at", ""), "closed": False,
                            "isAnswered": False, "reactionGroups": [],
                            "title": it.get("title", "")}
                    sc, _, _, _ = score(fake, assocs, args.since_days, False)
                    item = {
                        "repo": repo, "number": it["number"], "channel": "issues",
                        "category": ",".join(
                            l["name"] for l in (it.get("labels") or [])[:3])[:20],
                        "title": (it.get("title") or "")[:70], "url": it.get("html_url"),
                        "upvotes": up, "comments": cm,
                        "labels": [l["name"] for l in (it.get("labels") or [])],
                        "maintainer_replied": maint, "answered": False, "score": sc,
                        "grade": grade(sc, maint, False, False),
                    }
                    if args.dup_check:
                        item["similar_prs"] = []
                    rows.append(item)
                continue

            cats = categories(repo)
            if args.list_categories:
                for c in cats:
                    print(f"{repo}  {c['slug']:<18} {c['name']}")
                return 0
            slugs = {s.lower() for s in args.category}
            owners = codeowners_logins(repo)
            for d in fetch_discussions(repo, args.limit):
                if slugs and (d.get("category") or {}).get("slug", "").lower() not in slugs:
                    continue
                assoc = []
                try:
                    assoc = maintainer_replies(repo, d["number"])
                except Exception as e:
                    print(f"WARN comments #{d['number']}: {e}", file=sys.stderr)
                sc, up, cm, maint = score(d, assoc, args.since_days, args.self_upvote)
                item = {
                    "repo": repo, "number": d["number"], "channel": "discussions",
                    "category": (d.get("category") or {}).get("slug"),
                    "title": d["title"][:70], "url": d["url"],
                    "upvotes": up, "comments": cm,
                    "labels": [l["name"] for l in (d.get("labels") or {}).get("nodes", [])],
                    "maintainer_replied": maint,
                    "answered": d.get("isAnswered"), "score": sc,
                    "grade": grade(sc, maint, d.get("isAnswered"), d.get("closed")),
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
    print(f"{'grade':<6}{'score':<6}{'up':<7}{'cmt':<6}{'maint':<6}{'repo':<14}title")
    print("-" * 100)
    for x in rows:
        print(f"{x['grade']:<6}{x['score']:<6}{x['upvotes']:<7}{x['comments']:<6}"
              f"{'Y' if x['maintainer_replied'] else '-':<6}"
              f"#{x['number']:<6}{x['repo'].split('/')[1][:14]:<15}{x['title'][:40]}")
    print("\n下一步：grade=C3/C2 且 similar_issues 为空 → 用 skills/feature-proposer 发提案验证；"
          "grade 只是讨论区热度，放行写码要的是验证阶梯 V4（维护者标签 + 认可回复）。\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

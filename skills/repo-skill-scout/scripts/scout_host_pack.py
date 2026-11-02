#!/usr/bin/env python3.12
"""Scout a host repository's own Agent instruction layer and skill pack.

Read-only. Deterministic, stdlib-only. Reproduces the manual reconnaissance of
`.agents/skills` / `.claude/skills` style packs in one pass:

    python3 scripts/scout_host_pack.py <repo-path>

Exit 0 always (it reports; it does not gate).
"""

from __future__ import annotations

import argparse
import collections
import os
import re
import sys

PACK_DIRS = (".agents/skills", ".claude/skills", ".cursor/skills", ".github/skills")
ENTRY_FILES = ("AGENTS.md", "CLAUDE.md", ".cursorrules", "copilot-instructions.md")
SKIP_DIRS = {".git", "node_modules", "dist", "build", "out", "coverage", ".next", "target", ".workbuddy"}
LINK_RE = re.compile(r"\.agents/skills/|\.claude/skills/|\.cursor/skills/|\.github/skills/")
REL_LINK_RE = re.compile(r"\.\./([a-z0-9][a-z0-9._-]*)/(SKILL\.md|references/[^\s)#]+\w\.md)")
FRONT_DESC_RE = re.compile(r"^description:\s*(?:>-|>)?\s*(.*)$", re.M)
BOUNDARY_WORDS = ("not for", "do not use", "don't use", "defer to", "to its owner", "unless")
# Word-boundary patterns only. Substring matching on short tokens is wrong
# ("lease" hides inside "release", "live" inside "delivery") and pushes the most
# contributor-relevant skills into the forbidden bucket.
MUTATES_SHARED = (
    r"\bpublish\w*", r"\bpublication\b", r"\bsigning\b", r"\bnotariz\w*", r"\bpromot\w*",
    r"\bannounc\w*", r"\bauto-?merge\b", r"\bmerg\w*", r"\bland\b|\blanding\b", r"\bhotfix\w*",
    r"\bdeploy\w*", r"\brestart\w*", r"\bclose\b|\breopen\b", r"\bclos\w*out\b",
    r"\badvisor\w*", r"\bghsa\b", r"\bsecret[- ]scanning\b", r"\bbulk\b",
    r"\bsweep\b", r"\breindex\b", r"\bmigrat\w*", r"\bworkflows?\b", r"\brunner\b",
    r"\bcapacity\b", r"\bscorecard\b", r"\btriage\b", r"\bchangelog\b",
    r"\brelease ci\b", r"\bsecret\b", r"\bpreflight\w*",
)
GATED_ACCESS = (
    r"\bcredential\w*", r"\bleas(?:e|ed|ing)\b", r"\boauth\b", r"\bconvex\b", r"\btoken\b",
    r"\barchive\b", r"\bprivate\b", r"\bmaintainer\b", r"\bdesktop app\b", r"\btest server\b",
    r"\blaunchagent\b", r"\bdocker\b", r"\bparallels\b", r"\bremote\b", r"\bgateway\b",
    r"\btranscript\b", r"\boperator\b", r"\bserver\b", r"\badvisory\b",
)
NEGATION = ("not for", "never", "without", "do not use", "don't use", "no ")


def frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


def front_description(text: str) -> str:
    fm = frontmatter(text)
    m = re.search(r"^description:\s*>-\s*\n((?:[ \t]+.*\n?)+)", fm, re.M)
    if m:
        return " ".join(line.strip() for line in m.group(1).splitlines())
    m = FRONT_DESC_RE.search(fm)
    if not m:
        return ""
    value = m.group(1).strip()
    if value in (">-", ">", "|", "|-"):
        start = m.end()
        block = []
        for line in fm[start:].splitlines():
            if not line.strip():
                break
            if not line.startswith((" ", "\t")):
                break
            block.append(line.strip())
        return " ".join(block)
    return value.strip("\"'")


def walk_md(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def rel(root: str, path: str) -> str:
    return os.path.relpath(path, root)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--skills", action="store_true", help="list every skill with boundaries")
    ap.add_argument("--anchors", action="store_true", help="list router deep links with anchors")
    args = ap.parse_args()

    root = os.path.abspath(args.repo)
    if not os.path.isdir(root):
        print(f"not a directory: {root}", file=sys.stderr)
        return 0

    print(f"# host pack scout — {root}\n")

    # 1) instruction layer
    entry_hits = [p for p in walk_md(root) if os.path.basename(p) in ENTRY_FILES]
    root_entries = [p for p in entry_hits if rel(root, p) == os.path.basename(p)]
    scoped = sorted(rel(root, p) for p in entry_hits if p not in root_entries)
    print(f"## 1. instruction layer")
    print(f"- root entries: {', '.join(rel(root, p) for p in sorted(root_entries)) or '(none)'}")
    print(f"- scoped instruction files: {len(scoped)}")
    for path in scoped[:8]:
        print(f"    {path}")
    if len(scoped) > 8:
        print(f"    … {len(scoped) - 8} more")

    # 2) skill packs (dedupe by realpath: alias dirs are often symlinks to one pack)
    packs, aliases = [], {}
    for d in PACK_DIRS:
        path = os.path.join(root, d)
        if not os.path.isdir(path):
            continue
        real = os.path.realpath(path)
        if any(real == os.path.realpath(p) for _, p in packs):
            aliases.setdefault(real, []).append(d)
            continue
        packs.append((d, path))
    print("\n## 2. skill packs")
    if not packs:
        print("- none found (host has no agent skill pack; use CONTRIBUTING route)")
    all_skills: dict[str, tuple[str, str]] = {}
    for name, pack in packs:
        dirs = sorted(
            e for e in os.listdir(pack) if os.path.isfile(os.path.join(pack, e, "SKILL.md"))
        )
        has_readme = os.path.isfile(os.path.join(pack, "README.md"))
        alias = ", ".join(aliases.get(os.path.realpath(pack), []))
        suffix = f"  (alias dirs pointing here: {alias})" if alias else ""
        print(f"- {name}: {len(dirs)} skills, central README={'yes' if has_readme else 'NO'}{suffix}")
        for skill in dirs:
            text = open(os.path.join(pack, skill, "SKILL.md"), encoding="utf-8").read()
            all_skills[skill] = (front_description(text), pack)

    # 3) router deep links
    router_links: collections.Counter[str] = collections.Counter()
    anchors: list[tuple[str, int, str]] = []
    for path in walk_md(root):
        r = rel(root, path)
        if any(r.startswith(os.path.relpath(p, root) + os.sep) for _, p in packs):
            continue
        for lineno, line in enumerate(
            open(path, encoding="utf-8", errors="replace").read().splitlines(), 1
        ):
            if not LINK_RE.search(line):
                continue
            router_links[r] += 1
            for m in re.finditer(r"skills/([a-z0-9][a-z0-9._-]*)/SKILL\.md(?:#[a-z0-9._-]+)?", line):
                anchors.append((r, lineno, m.group(1)))
    print("\n## 3. router deep links into the pack (authority sources)")
    for path, count in router_links.most_common(8):
        print(f"- {path}: {count}")
    print(f"- total hits outside the pack itself: {sum(router_links.values())}")
    anchored = collections.Counter(name for _, _, name in anchors)
    if args.anchors:
        print("- anchored skills (top):")
        for name, count in anchored.most_common(12):
            print(f"    {name}: {count}")

    # 4) cross-skill handshake links
    inbound: collections.Counter[str] = collections.Counter()
    files_with_links = 0
    for _, pack in packs:
        for path in walk_md(pack):
            text = open(path, encoding="utf-8").read()
            found = REL_LINK_RE.findall(text)
            if found:
                files_with_links += 1
                for target, _kind in found:
                    if target in all_skills:
                        inbound[target] += 1
    print("\n## 4. cross-skill links (acknowledged collaboration edges)")
    print(f"- files carrying a relative skill link: {files_with_links}")
    for name, count in inbound.most_common(6):
        print(f"    hub → {name}: {count} inbound")

    # 5) contributor permission split — a hint, not a verdict: matched text is printed
    # so the caller confirms against the skill body before trusting a bucket.
    print("\n## 5. contributor permission split (keyword hint — verify the matched phrase)")

    def hits(patterns, text):
        found = []
        for pat in patterns:
            for m in re.finditer(pat, text, re.I):
                start = max(0, m.start() - 24)
                # Only a negation BEFORE the keyword flips its meaning
                # ("not for archive search"); one after it does not.
                if any(neg in text[max(0, m.start() - 30) : m.start()].lower() for neg in NEGATION):
                    continue
                found.append(text[start : m.end() + 18].strip())
                break
        return found

    gated, shared, open_now, flagged = [], [], [], []
    for name, (desc, _pack) in sorted(all_skills.items()):
        boundary = [w for w in BOUNDARY_WORDS if w in desc.lower()]
        if boundary:
            flagged.append((name, boundary))
        shared_hit, gated_hit = hits(MUTATES_SHARED, desc), hits(GATED_ACCESS, desc)
        if shared_hit:
            shared.append((name, shared_hit[:2]))
        elif gated_hit:
            gated.append((name, gated_hit[:2]))
        else:
            open_now.append(name)
    print(f"- A. mutates shared state → read its terms, never execute ({len(shared)}):")
    for name, words in shared:
        print(f"    {name}  ← { ' | '.join(words) }")
    print(f"- B. needs others' credentials or private archives ({len(gated)}):")
    for name, words in gated:
        print(f"    {name}  ← { ' | '.join(words) }")
    print(f"- C. no gate detected — usable in your own workspace ({len(open_now)}):")
    print(f"    {', '.join(sorted(open_now)) if args.skills else '(pass --skills to list)'}")
    print(f"- skills stating an explicit boundary in description: {len(flagged)}/{len(all_skills)}")
    for name, words in flagged[:10]:
        print(f"    {name}  ← {', '.join(words)}")

    print("\n## next")
    print("- fill the slot table in references/role-usage-map.md from section 5, then")
    print("- open only the router anchors that cover your task (section 3) before editing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

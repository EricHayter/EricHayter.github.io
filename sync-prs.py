#!/usr/bin/env python3
"""
sync-prs.py  —  Update the open-source PR log in index.html.

1. Reads prs.json for known PRs + blurbs + repo config.
2. Fetches current PRs from GitHub via `gh` CLI.
3. For any new PR, calls `claude -p` to generate a one-line blurb.
4. Writes updated prs.json.
5. Regenerates the PR-LOG-START ... PR-LOG-END block in index.html.

Usage:
    python3 sync-prs.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT        = Path(__file__).parent
CONFIG_FILE = ROOT / "prs.json"
INDEX_FILE  = ROOT / "projects.html"

SUMMARIZE_PROMPT = (
    "Summarize this GitHub PR in one concise sentence for a developer portfolio. "
    "Be specific about what changed technically. "
    "No markdown, no trailing period, no subject pronoun at the start (e.g. start with a verb)."
)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()


def fetch_repo_prs(repo, author):
    raw = run([
        "gh", "pr", "list",
        "--repo", repo,
        "--author", author,
        "--state", "all",
        "--limit", "100",
        "--json", "number,title,url,mergedAt,createdAt,state",
    ])
    return json.loads(raw)


def summarize(repo, number):
    try:
        content = run([
            "gh", "pr", "view", str(number),
            "--repo", repo,
            "--json", "title,body",
            "--jq", '(.title) + "\n\n" + (.body // "")',
        ])
        return run(["claude", "-p", f"{SUMMARIZE_PROMPT}\n\n{content}"])
    except Exception as e:
        print(f"  warning: could not summarize #{number}: {e}", file=sys.stderr)
        return ""


def sort_key(pr):
    return pr.get("mergedAt") or pr.get("createdAt") or "0000"


def render_entry(pr, logo_src, logo_alt):
    blurb = pr.get("blurb", "")
    return (
        f'        <div class="pr-entry">\n'
        f'          <img class="co-icon" src="{logo_src}" alt="{logo_alt}" style="align-self:center;" />\n'
        f'          <a class="pr-num" href="{pr["url"]}" target="_blank">#{pr["number"]}</a>\n'
        f'          <span class="pr-blurb">{blurb}</span>\n'
        f'        </div>'
    )


def render_block(config, prs_data):
    repos   = config["repos"]
    all_prs = sorted(prs_data.values(), key=sort_key, reverse=True)
    entries = [
        render_entry(pr, repos[pr["repo"]]["logo"], repos[pr["repo"]]["alt"])
        for pr in all_prs
    ]
    inner = "\n".join(entries)
    return (
        f'      <!-- PR-LOG-START -->\n'
        f'      <div class="pr-log">\n'
        f'{inner}\n'
        f'      </div>\n'
        f'      <!-- PR-LOG-END -->'
    )


def update_html(new_block):
    html    = INDEX_FILE.read_text()
    pattern = r'      <!-- PR-LOG-START -->.*?<!-- PR-LOG-END -->'
    updated = re.sub(pattern, new_block, html, flags=re.DOTALL)
    if updated == html:
        sys.exit("error: PR-LOG-START / PR-LOG-END markers not found in index.html")
    INDEX_FILE.write_text(updated)


def main():
    config   = json.loads(CONFIG_FILE.read_text())
    author   = config["author"]
    repos    = config["repos"]
    prs_data = config.get("prs", {})

    for repo in repos:
        print(f"fetching {repo} ...")
        for pr in fetch_repo_prs(repo, author):
            key = f"{repo}#{pr['number']}"
            if key not in prs_data:
                print(f"  new: #{pr['number']} — {pr['title']}")
                blurb = summarize(repo, pr["number"])
                print(f"  blurb: {blurb}")
                prs_data[key] = {
                    "number":    pr["number"],
                    "repo":      repo,
                    "url":       pr["url"],
                    "mergedAt":  pr.get("mergedAt"),
                    "createdAt": pr.get("createdAt"),
                    "state":     pr.get("state"),
                    "blurb":     blurb,
                }
            else:
                prs_data[key]["mergedAt"] = pr.get("mergedAt")
                prs_data[key]["state"]    = pr.get("state")

    CONFIG_FILE.write_text(json.dumps({**config, "prs": prs_data}, indent=2) + "\n")
    print("saved prs.json")

    update_html(render_block(config, prs_data))
    print("updated index.html")


if __name__ == "__main__":
    main()

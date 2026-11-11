#!/usr/bin/env python3
"""repo-health-report: audit a GitHub user's public repos via the GitHub REST API."""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"


def get(path, token=None):
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "repo-health-report",
        },
    )
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def audit(user, token=None, stale_days=30):
    repos = get(f"/users/{user}/repos?per_page=100&type=owner", token)
    now = datetime.now(timezone.utc)
    rows = []
    for repo in repos:
        if repo["fork"]:
            continue
        name = repo["name"]
        problems = []
        if not repo.get("description"):
            problems.append("no description")
        if not repo.get("license"):
            problems.append("no license")
        if not repo.get("topics"):
            problems.append("no topics")
        try:
            get(f"/repos/{user}/{name}/readme", token)
        except urllib.error.HTTPError:
            problems.append("no README")
        prs = get(f"/repos/{user}/{name}/pulls?state=open&per_page=100", token)
        stale = [
            p
            for p in prs
            if (now - datetime.fromisoformat(p["updated_at"].replace("Z", "+00:00"))).days >= stale_days
        ]
        if stale:
            problems.append(f"{len(stale)} stale PR(s)")
        rows.append((name, repo["stargazers_count"], problems))
    return rows


def render(user, rows):
    lines = [
        f"# Repo health report for {user}",
        "",
        "| Repo | Stars | Issues found |",
        "|---|---|---|",
    ]
    for name, stars, problems in sorted(rows):
        lines.append(f"| {name} | {stars} | {', '.join(problems) or 'healthy'} |")
    return "\n".join(lines) + "\n"


def main():
    user = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GITHUB_ACTOR")
    if not user:
        sys.exit("usage: repo_health_report.py <github-user>")
    token = os.environ.get("GITHUB_TOKEN")
    report = render(user, audit(user, token))
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(report)


if __name__ == "__main__":
    main()

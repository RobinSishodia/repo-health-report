# repo-health-report

A tiny, dependency-free tool that uses the GitHub REST API to audit a user's public repositories and report common hygiene problems.

## What it checks

For every non-fork repo owned by the user:

- Missing description
- Missing license
- Missing topics
- Missing README
- Open pull requests that have not been updated in 30+ days

## Usage

```bash
python repo_health_report.py <github-username>
```

Set `GITHUB_TOKEN` to raise the API rate limit (optional for public repos).

## As a GitHub Action

The included workflow (`.github/workflows/report.yml`) runs every Monday and on demand. The report appears in the run's job summary. Fork this repo and run **Actions > Repo health report > Run workflow**.

## Requirements

Python 3.8+. No third-party packages.

## Contact

Questions or issues: robin.sishodia@gmail.com, or open an issue in this repo.

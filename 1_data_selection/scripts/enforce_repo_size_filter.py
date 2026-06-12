#!/usr/bin/env python3
"""
Filter repositories by size from GitHub (MB) before cloning to reduce time.

"""
import argparse
import json
import os
import sys
import time
from urllib import request, error

GITHUB_API = "https://api.github.com/repos/"


def fetch_repo_size(repo: str, token: str | None) -> float | None:
    url = GITHUB_API + repo

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-size-filter"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(url, headers=headers)

    try:
        with request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
            size_kb = data.get("size")
            if isinstance(size_kb, int):
                return size_kb / 1024  # convert to MB
    except error.HTTPError as e:
        if e.code != 404:
            print(f"[warn] API error for {repo}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[warn] request failed for {repo}: {e}", file=sys.stderr)

    return None


def normalize_repo(repo: str) -> str:
    return repo.strip().removesuffix(".git")


def main():
    parser = argparse.ArgumentParser(
        description="Filter repositories by GitHub size (MB)"
    )
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file (defaults to stdout)"
    )
    parser.add_argument(
        "--max-size-mb",
        type=float,
        required=True,
        help="Maximum repository size in MB"
    )
    parser.add_argument(
        "--token-env",
        default="GITHUB_TOKEN",
        help="Environment variable containing GitHub token"
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.2,
        help="Delay between API calls"
    )

    args = parser.parse_args()

    token = os.environ.get(args.token_env)

    if not token:
        print("[warn] No GitHub token found. You may hit rate limits or get 401 errors.", file=sys.stderr)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = {}

    total = sum(len(repos) for repos in data.values())
    count = 0

    for category, repos in data.items():
        filtered = {}

        for repo, value in repos.items():
            count += 1
            repo = normalize_repo(repo)

            print(f"[{count}/{total}] Checking {repo}...", file=sys.stderr)

            size_mb = fetch_repo_size(repo, token)

            if size_mb is None:
                print("  -> unknown size (keeping)", file=sys.stderr)
                filtered[repo] = value
                continue

            print(f"  -> size: {size_mb:.2f} MB", file=sys.stderr)

            if size_mb <= args.max_size_mb:
                print("  -> kept", file=sys.stderr)
                filtered[repo] = value
            else:
                print("  -> removed (too large)", file=sys.stderr)

            time.sleep(args.sleep)

        if filtered:
            result[category] = filtered

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    else:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
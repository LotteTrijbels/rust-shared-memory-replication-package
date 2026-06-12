#!/usr/bin/env python3
"""Select representative Rust repos per shared-memory category."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_INPUT = SCRIPT_DIR / ".." / "intermediate" / "all-shared-memory.json"
DEFAULT_STARS = SCRIPT_DIR / ".." / "intermediate" / "awesome-rust-starred.json"

CATEGORIES = (
    "mutex",
    "rwlock",
    "atomic",
    "arc",
    "condvar",
)

FIELD_MAP = {
    "mutex": "mutex_usage",
    "rwlock": "rwlock_usage",
    "atomic": "atomic_operations",
    "arc": "arc_usage",
    "condvar": "interior_mutability",
}

USAGE_PRIORITY = {
    "UNUSED": 0,
    "USED_SPARINGLY": 1,
    "INSTRUMENTAL_TO_ARCHITECTURE": 2,
}

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_reviews(path: str) -> list[dict[str, Any]]:
    data = load_json(path)

    if not isinstance(data, list):
        raise ValueError("Input must be a JSON array")

    for r in data:
        repo = r.get("repository_name")
        if not repo:
            r["revision"] = None
            continue

        owner, name = repo.split("/")
        rev_path = Path("repos") / owner / name / "revision.txt"

        if rev_path.exists():
            r["revision"] = rev_path.read_text().strip()
        else:
            r["revision"] = None

    return data

def load_stars_from_starred(path: str) -> dict[str, int]:
    data = load_json(path)
    stars = {}
    for category, repos in data.items():
        for repo, star_count in repos.items():
            stars[repo] = star_count
    return stars

def score_repo(review: dict[str, Any], category: str, stars: dict[str, int]) -> tuple:
    repo = review["repository_name"]

    field = FIELD_MAP[category]
    value = review.get(field, "UNUSED")
    if value not in USAGE_PRIORITY:
        value = "UNUSED"

    return (
        USAGE_PRIORITY[value],
        stars.get(repo, 0),
        repo.lower(),
    )

def rank_per_category(
    reviews: list[dict[str, Any]],
    stars: dict[str, int],
) -> dict[str, list[dict[str, Any]]]:

    ranked = {}
    for cat in CATEGORIES:
        ranked[cat] = sorted(
            reviews,
            key=lambda r: score_repo(r, cat, stars),
            reverse=True,
        )
    return ranked

def select_repos(
    ranked: dict[str, list[dict[str, Any]]],
    stars: dict[str, int],
    target_size: int,
) -> list[dict[str, Any]]:

    selected = []
    used = set()

    for cat in CATEGORIES:
        for repo in ranked[cat]:
            name = repo["repository_name"]
            if name not in used:
                selected.append(repo)
                used.add(name)
                break

    while len(selected) < target_size:
        best_candidate = None
        best_score = None

        for cat in CATEGORIES:
            for repo in ranked[cat]:
                name = repo["repository_name"]

                if name in used:
                    continue

                score = score_repo(repo, cat, stars)

                if best_score is None or score > best_score:
                    best_candidate = repo
                    best_score = score

                break

        if best_candidate is None:
            break

        selected.append(best_candidate)
        used.add(best_candidate["repository_name"])

    return selected

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output")
    args = parser.parse_args()

    reviews = load_reviews(args.input)
    stars = load_stars_from_starred(DEFAULT_STARS)

    ranked = rank_per_category(reviews, stars)
    selected = select_repos(ranked, stars, args.limit)

    output = {
        "selected_repositories": [
            {
                "repository_name": r["repository_name"],
                "stars": stars.get(r["repository_name"], 0),
                "revision": r.get("revision")
            }
            for r in selected
        ]
    }

    result = json.dumps(output, indent=2)

    if args.output:
        Path(args.output).write_text(result + "\n", encoding="utf-8")
    else:
        print(result)

if __name__ == "__main__":
    main()
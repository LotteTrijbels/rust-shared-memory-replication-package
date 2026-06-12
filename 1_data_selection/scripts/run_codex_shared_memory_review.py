#!/usr/bin/env python3
"""Clone a GitHub repo and run a short Codex message-passing review."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

PROMPT_TEMPLATE = """Investigate the use of shared-memory concurrency patterns in this repository. This will be a cursory glance, not a full investigation.

I only require that you fill out the following form:

{{
    "repository_name": "{repository_name}",

    # Possible categories: "UNUSED", "USED_SPARINGLY", "INSTRUMENTAL_TO_ARCHITECTURE"

    "mutex_usage": "UNUSED",
    "rwlock_usage": "UNUSED",
    "atomic_operations": "UNUSED",
    "interior_mutability": "UNUSED",
    "arc_usage": "UNUSED",

    "other": "Specify here",
    "decision_notes": "Briefly explain the evidence behind your classifications."
}}

Here, marking a shared-memory concurrency pattern as UNUSED represents that the repository does not use the pattern outside of tests or benchmarks.
Marking a pattern as USED_SPARINGLY signifies that the pattern appears in parts of the codebase, but is not a central design choice. For example, a Mutex, RwLock, or Arc may be used only for isolated shared state or to satisfy a library requirement, rather than for core application logic.
INSTRUMENTAL_TO_ARCHITECTURE should be marked when shared-memory concurrency is a fundamental part of the system's design. For example, when shared state protected by Mutex or RwLock is used to coordinate core application logic, when Arc is used extensively to share state across threads, or when atomic types are used for critical coordination between worker threads. This includes cases where multiple threads actively read and modify shared state as part of the primary program workflow.
If the crate uses a pattern not specified in the template, add it to the other section. Only use this as an escape hatch when the pattern does not clearly fit the predefined categories or when you are unsure how to classify it.

Evidence includes explicit use of synchronization primitives, shared ownership patterns across threads, or concurrent mutation of shared state.

Please ensure your investigation concludes swiftly, and does not take up too many tokens.
Write the completed JSON object to a file named `shared_memory_review.json` in the repository root.
Your final response should be brief and mention that file was written.

Keywords to search for:

std::sync::Mutex
std::sync::RwLock
std::sync::Arc
std::sync::atomic
std::cell::RefCell
std::sync::OnceLock
tokio::sync::Mutex
parking_lot::Mutex

"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone a GitHub repository and run a short Codex shared memory review."
    )
    parser.add_argument(
        "repository",
        help="GitHub repository in owner/repo form or as a GitHub URL.",
    )
    parser.add_argument(
        "--clone-root",
        default="repos",
        help="Directory where repositories will be cloned (default: repos).",
    )
    parser.add_argument(
        "--output",
        help="Optional file to store Codex's final message.",
    )
    parser.add_argument(
        "--model",
        help="Optional Codex model override.",
    )
    parser.add_argument(
        "--codex-bin",
        default="codex",
        help="Codex executable to invoke (default: codex).",
    )
    parser.add_argument(
        "--git-bin",
        default="git",
        help="Git executable to invoke (default: git).",
    )
    parser.add_argument(
        "--reclone",
        action="store_true",
        help="Delete any existing clone before cloning again.",
    )
    return parser.parse_args()


def normalize_repository(value: str) -> str:
    repo = value.strip()
    if not repo:
        raise ValueError("Repository cannot be empty.")

    if repo.startswith(("http://", "https://", "git@github.com:")):
        if repo.startswith("git@github.com:"):
            path = repo.split(":", 1)[1]
        else:
            parsed = urlparse(repo)
            if parsed.netloc not in {"github.com", "www.github.com"}:
                raise ValueError(f"Unsupported GitHub host: {parsed.netloc}")
            path = parsed.path
        parts = [part for part in path.split("/") if part]
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub repository: {value}")
        owner, name = parts[0], parts[1]
    else:
        parts = [part for part in repo.split("/") if part]
        if len(parts) != 2:
            raise ValueError(f"Repository must look like owner/repo: {value}")
        owner, name = parts

    name = name.removesuffix(".git")
    return f"{owner}/{name}"


def clone_url(owner_repo: str) -> str:
    return f"https://github.com/{owner_repo}.git"


def ensure_executable(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required executable not found on PATH: {name}")


def prepare_clone(owner_repo: str, clone_root: Path, git_bin: str, reclone: bool) -> Path:
    owner, repo = owner_repo.split("/", 1)
    destination = clone_root / owner / repo
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        if reclone:
            shutil.rmtree(destination)
        elif (destination / ".git").is_dir():
            return destination
        else:
            raise RuntimeError(
                f"Destination exists and is not a git repository: {destination}"
            )

    cmd = [git_bin, "clone", "--depth", "1", clone_url(owner_repo), str(destination)]
    subprocess.run(cmd, check=True)
    # store commit hash
    commit = subprocess.run(
        [git_bin, "-C", str(destination), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True
    )

    (destination / "revision.txt").write_text(commit.stdout.strip() + "\n")
    
    return destination


def build_codex_command(args: argparse.Namespace, repo_dir: Path) -> list[str]:
    cmd = [
        args.codex_bin,
        "exec",
        "--cd",
        str(repo_dir),
        "--sandbox",
        "workspace-write",
        "--color",
        "never",
        "--ephemeral",
    ]
    if args.model:
        cmd.extend(["--model", args.model])
    if args.output:
        cmd.extend(["--output-last-message", args.output])
    cmd.append("-")
    return cmd


def main() -> int:
    args = parse_args()
    owner_repo = normalize_repository(args.repository)
    ensure_executable(args.git_bin)
    ensure_executable(args.codex_bin)

    clone_root = Path(args.clone_root).expanduser().resolve()
    repo_dir = prepare_clone(owner_repo, clone_root, args.git_bin, args.reclone)
    prompt = PROMPT_TEMPLATE.format(repository_name=owner_repo)

    cmd = build_codex_command(args, repo_dir)
    completed = subprocess.run(cmd, input=prompt, text=True)
    return completed.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"error: command failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        raise SystemExit(exc.returncode)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)

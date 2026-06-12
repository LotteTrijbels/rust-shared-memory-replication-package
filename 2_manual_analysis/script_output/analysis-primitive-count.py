import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(SCRIPT_DIR, "../../1_data_selection/ranked_repos.json")
BASE_DIR = os.path.join(SCRIPT_DIR, "../../repos") # Local clone directory used for analysis (not part of replication package)
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "primitive_counts.json")

PRIMITIVES = {
    "arc": re.compile(r"\bArc(<|::)"),
    "mutex": re.compile(r"\bMutex(<|::)"),
    "rwlock": re.compile(r"\bRwLock(<|::)"),
    "atomic": re.compile(r"\bAtomic\w+"),
    "condvar": re.compile(r"\bCondvar\b"),
    "barrier": re.compile(r"\bBarrier\b"),
}

EXCLUDE_DIRS = {
    "tests",
    "test",
    "benches",
    "bench",
    "examples",
    "example",
    "target",
}

def should_skip(path_parts: list[str]) -> bool:
    return any(part in EXCLUDE_DIRS for part in path_parts)

def clean_code(content: str) -> str:
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL) # block comments

    lines = []
    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("//"): # line comment
            continue

        if stripped.startswith("use "): # imports
            continue

        lines.append(line)

    return "\n".join(lines)

def count_primitives_in_file(filepath: str):
    counts = {k: 0 for k in PRIMITIVES}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        content = clean_code(content)

        for name, pattern in PRIMITIVES.items():
            counts[name] += len(pattern.findall(content))

    except Exception:
        pass

    return counts

def scan_repo(repo_path: str):
    total = {k: 0 for k in PRIMITIVES}
    file_results = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        rel_root = os.path.relpath(root, repo_path)
        path_parts = rel_root.split(os.sep)

        if should_skip(path_parts):
            continue

        for file in files:
            if not file.endswith(".rs"):
                continue

            filepath = os.path.join(root, file)
            counts = count_primitives_in_file(filepath)

            found = [k for k, v in counts.items() if v > 0]

            if found:
                file_results.append({
                    "file": os.path.relpath(filepath, repo_path), 
                    "primitives": found
                })

            for k in total:
                total[k] += counts[k]

    return total, file_results

def main():
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    results = []

    for repo in data["selected_repositories"]:
        name = repo["repository_name"]
        owner, repo_name = name.split("/")

        repo_path = os.path.join(BASE_DIR, owner, repo_name)

        print(f"Processing {name}")

        if not os.path.exists(repo_path):
            print(f"Skipping {name} (not cloned)")
            continue

        counts, files = scan_repo(repo_path)

        binary = {k: int(counts[k] > 0) for k in PRIMITIVES}

        results.append({
            "repository": name,
            "counts": counts,
            "binary": binary,
            "files": files
        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
# Data Selection Procedure
This reproduces the repository selection pipeline used in the study. Executing the steps below reproduces the process used to get the repositories for qualitative analysis.

All intermediate steps generated during the selection process are stored in the intermediate/ directory. To reproduce the exact dataset used in the study, these stored files can be used directly instead of rerunning the pipeline.

## 1. Fetch the Awesome Rust repository list
Download the current README.md from the Awesome Rust repository:

```bash
curl https://raw.githubusercontent.com/rust-unofficial/awesome-rust/refs/heads/main/README.md > ./intermediate/awesome-rust.md
```
Note: The awesome-rust.md file used during the study is preserved as an intermediate step. Using the stored version ensures reproducibility even if the repository changes.

## 2. Extract repository names
Parse the Markdown file into a JSON object grouped by category.

```bash
chmod +x ./scripts/extract-from-readme.sh
./scripts/extract-from-readme.sh ./intermediate/awesome-rust.md | tee ./intermediate/awesome-rust-unstarred.json
```

## 3. Retrieve GitHub star counts
This step requires a GitHub Personal Access Token (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

```bash
export GITHUB_TOKEN="<your_token>"

chmod +x ./scripts/fetch_github_stars.py
./scripts/fetch_github_stars.py --input ./intermediate/awesome-rust-unstarred.json | tee ./intermediate/awesome-rust-starred.json
```
The resulting file contains the same repositories together with their GitHub star counts.

## 4. Apply repository selection criteria
### Minimum star threshold
Curent amount of repositories:

```bash
jq '.[]' ./intermediate/awesome-rust-starred.json | grep ':' | wc -l
```

Repositories with fewer than 30 GitHub stars are removed.

```bash
chmod +x ./scripts/enforce_minimum_stars.py
./scripts/enforce_minimum_stars.py --min-stars 30 ./intermediate/awesome-rust-starred.json | tee ./intermediate/awesome-rust-min-stars.json
```

Repository count after GitHub star threshold:
```bash
jq '.[]' ./intermediate/awesome-rust-min-stars.json | grep ':' | wc -l
```

### Maximum repositories per category

Next, a maximum number of 5 repositories per category is enforced. Because repositories are sorted by stars, this step removes the least popular repositories within each category while ensuring a balanced representation across domains.

```bash
chmod +x ./scripts/enforce_maximum_per_category.py
./scripts/enforce_maximum_per_category.py --max-repos 5 ./intermediate/awesome-rust-min-stars.json | tee ./intermediate/awesome-rust-trimmed.json
```

Repository count after category threshold:
```bash
jq '.[]' ./intermediate/awesome-rust-trimmed.json | grep ':' | wc -l
```

### Repository size filter
Repositories larger than 100 MB are excluded to reduce processing overhead and keep manual analysis feasible.

```bash
chmod +x ./scripts/enforce_repo_size_filter.py
./scripts/enforce_repo_size_filter.py --max-size-mb 100 ./intermediate/awesome-rust-trimmed.json | tee ./intermediate/awesome-rust-filtered.json 
```

Repository count after size filter:
```bash
jq '.[]' ./intermediate/awesome-rust-filtered.json | grep ':' | wc -l
```

## 5. Convert to a plain-text repository list
Convert the filtered JSON representation into a plain text file suitable for batch processing.

```bash
jq -r '
  to_entries
  | map(.value | to_entries[])        # collect all repos across categories
  | group_by(.key)                    # group duplicates by repo name
  | map(max_by(.value))               # keep highest star count per repo
  | sort_by(.value) | reverse         # sort descending by stars
  | .[].key                           # output only repo names
' ./intermediate/awesome-rust-filtered.json | tee ./intermediate/awesome-rust-to-classify.txt
```

## 6. Run LLM-based repository classification
Process each selected repository:

```bash
chmod +x scripts/run_codex_shared_memory_review.py

while read repo; do
    owner=$(echo "$repo" | cut -d'/' -f1)
    name=$(echo "$repo" | cut -d'/' -f2)

    path="repos/$owner/$name/shared_memory_review.json"

    if [ -f "$path" ]; then
        echo "SKIP $repo"
        continue
    fi

    echo "RUN  $repo"
    ./scripts/run_codex_shared_memory_review.py "$repo"

done < ./intermediate/awesome-rust-to-classify.txt
```
Note: The LLM-based classification step may not reproduce the exact outputs reported in the study due to changes in the underlying model or nondeterministic generation. For exact replication of the repository selection process, use the preserved intermediate steps included in the intermediate/ directory, particularly all-shared-memory.json.

## 7. Merge classification results
Merge the individual repository reviews into a single file.
```bash
python3 ./scripts/merge_reviews.py
```
This produces:
```
./intermediate/all-shared-memory.json
```

## 8. Rank repositories
Generate the final repository ranking.

```bash
python3 ./scripts/rank_shared_memory_repos.py --input ./intermediate/all-shared-memory.json --output ./ranked_repos.json
```

The resulting ranked_repos.json file contains the final ranked repository list produced by the selection pipeline.

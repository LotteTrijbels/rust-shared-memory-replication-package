#!/usr/bin/env bash
set -euo pipefail

README="${1:-README.md}"

# Remove everything before Applications and everything after Libraries
sed -n '/^## Applications[[:space:]]*$/,/^## Libraries[[:space:]]*$/p' "$README" |
# Remove '## Applications' and '## Libraries'
sed '1d;$d' |
# Transform into "Category <tab> repo-owner/reponame" lines
awk '
  BEGIN { cat="uncategorized" }

  /^### / {
    cat=$0
    sub(/^### /, "", cat)
    next
  }

  /^\* / {
    if (match($0, /github\.com\/([^\/[:space:])]+)\/([^\/[:space:])\]#?]+)/, m)) {
      repo = m[1] "/" m[2]
      sub(/\.git$/, "", repo)
      print cat "\t" repo
    }
  }
' |
# Transform into JSON object
jq -Rn '
  reduce inputs as $line ({};
    ($line | split("\t")) as $p
    | .[$p[0]] += [$p[1]]
  )
'

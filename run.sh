#!/usr/bin/env bash

if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree is not clean."
    git status --short
    exit 1
fi

set -euo pipefail

while IFS='|' read -r role endpoint model files; do
  [[ -z "$role" || "$role" == \#* ]] && continue
  echo "== $role -> $endpoint ($model)"
  OLLAMA_API_BASE="$endpoint" aider \
    --model "ollama_chat/$model" \
    --message-file "prompts/$role.md" \
    --yes \
    --no-auto-commits \
    $files < /dev/null
  for f in $files; do echo "$f: $(wc -l < "$f") lines"; done
  git status --short
done < roles.conf
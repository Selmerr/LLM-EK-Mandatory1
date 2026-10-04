#!/usr/bin/env bash
set -euo pipefail

# Require a clean repository before starting
if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree is not clean."
    git status --short
    exit 1
fi

while IFS='|' read -r role endpoint model files; do
    [[ -z "$role" || "$role" == \#* ]] && continue

    echo
    echo "========================================"
    echo "Role:     $role"
    echo "Endpoint: $endpoint"
    echo "Model:    $model"
    echo "Files:    $files"
    echo "========================================"

    OLLAMA_API_BASE="$endpoint" aider \
        --model "ollama_chat/$model" \
        --message-file "prompts/$role.md" \
        --yes \
        --no-auto-commits \
        $files < /dev/null

    # Role-specific validation
    if [[ "$role" == "api" ]]; then
        echo
        echo "== Validating OpenAPI spec =="
        uv run openapi-spec-validator docs/openapi.yaml
    fi

    echo
    echo "== Result: $role =="

    for f in $files; do
        if [[ -f "$f" ]]; then
            echo "$f: $(wc -l < "$f") lines"
        fi
    done

    echo
    git status --short

    echo
    echo "== Git diff =="
    git diff -- $files

    echo
    echo "== Git diff check =="
    git diff --check

done < roles.conf
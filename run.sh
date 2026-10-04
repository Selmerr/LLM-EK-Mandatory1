#!/usr/bin/env bash
set -euo pipefail

if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree is not clean."
    git status --short
    exit 1
fi

run_aider() {
    local role="$1"
    local endpoint="$2"
    local model="$3"
    local files="$4"
    local message_file="$5"
    local read_files="${6:-}"

    local -a read_args=()
    local -a extra_args=()

    for f in $read_files; do
        read_args+=(--read "$f")
    done

    if [[ "$role" == "tech-lead" ]]; then
        extra_args+=(--map-tokens 0)
    fi

    OLLAMA_API_BASE="$endpoint" aider \
        --model "ollama_chat/$model" \
        --message-file "$message_file" \
        --no-auto-commits \
        "${extra_args[@]}" \
        "${read_args[@]}" \
        $files < /dev/null
}

while IFS='|' read -r role endpoint model files read_files; do
    [[ -z "$role" || "$role" == \#* ]] && continue

    echo
    echo "========================================"
    echo "Role:     $role"
    echo "Endpoint: $endpoint"
    echo "Model:    $model"
    echo "Files:    $files"
    echo "Read:     $read_files"
    echo "========================================"

    run_aider \
        "$role" \
        "$endpoint" \
        "$model" \
        "$files" \
        "prompts/$role.md" \
        "$read_files"

    if [[ "$role" == "api" ]]; then
        echo
        echo "== Validating OpenAPI spec =="

        if uv run openapi-spec-validator docs/openapi.yaml; then
            echo "OpenAPI validation PASSED."
        else
            echo "ERROR: OpenAPI validation failed."
            exit 1
        fi
    fi
    
    echo
    echo "== Result: $role =="

    for f in $files; do
        [[ -f "$f" ]] && echo "$f: $(wc -l < "$f") lines"
    done

    git status --short

    echo
    echo "== Git diff =="
    git diff -- $files

    echo
    echo "== Git diff check =="
    git diff --check

done < roles.conf
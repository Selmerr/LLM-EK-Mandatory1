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

    OLLAMA_API_BASE="$endpoint" aider \
        --model "ollama_chat/$model" \
        --message-file "$message_file" \
        --yes \
        --no-auto-commits \
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
    echo "========================================"

    run_aider "$role" "$endpoint" "$model" "$files" "prompts/$role.md"

    # API gets deterministic validation + repair attempts
    if [[ "$role" == "api" ]]; then
        max_attempts=3
        attempt=1

        while true; do
            echo
            echo "== Validating OpenAPI spec =="

            if validator_output=$(uv run openapi-spec-validator docs/openapi.yaml 2>&1); then
                echo "OpenAPI validation PASSED."
                break
            fi

            echo "OpenAPI validation FAILED:"
            echo "$validator_output"

            if (( attempt >= max_attempts )); then
                echo "ERROR: API worker failed after $max_attempts attempts."
                exit 1
            fi

            ((attempt++))

            echo
            echo "== Repair attempt $attempt/$max_attempts =="

            repair_prompt=$(mktemp)

            cat > "$repair_prompt" <<EOF
The OpenAPI specification you produced failed deterministic validation.

Validator output:

$validator_output

Fix docs/openapi.yaml so that it passes the validator.

Requirements:
- Keep GET /notes
- Keep POST /notes
- Keep DELETE /notes/{id}
- Use valid OpenAPI 3 syntax
- Path parameter id must be required
- POST must use requestBody
- Do not modify any other files
EOF

            run_aider "$role" "$endpoint" "$model" "$files" "$repair_prompt"

            rm -f "$repair_prompt"
        done
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
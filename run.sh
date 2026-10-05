#!/usr/bin/env bash
set -euo pipefail


if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree is not clean."
    git status --short
    exit 1
fi

mkdir -p artifacts
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

    if [[ "$role" == "tech-lead" ||
        "$role" == "storage-worker" ||
        "$role" == "storage-test" ||
        "$role" == "api-test" ||
        "$role" == "quality" ]]; then
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

run_quality() {
    local endpoint="$1"
    local model="$2"

    QUALITY_ENDPOINT="$endpoint" QUALITY_MODEL="$model" python3 <<'PY'
import json
import os
import urllib.request
from pathlib import Path

endpoint = os.environ["QUALITY_ENDPOINT"]
model = os.environ["QUALITY_MODEL"]

prompt = Path("prompts/quality.md").read_text()
pytest_output = Path("artifacts/pytest.txt").read_text()

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": f"{prompt}\n\nPYTEST OUTPUT:\n{pytest_output}"
        }
    ],
    "stream": False,
    "options": {
        "temperature": 0
    }
}

request = urllib.request.Request(
    f"{endpoint}/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

with urllib.request.urlopen(request) as response:
    result = json.load(response)

report = result["message"]["content"].strip()

if not report:
    raise RuntimeError("Quality model returned an empty report")

Path("docs/quality.md").write_text(report + "\n", encoding="utf-8")

print(report)
PY
}

validate_deployment() {
    local image="llm-man-1-validation"
    local container="llm-man-1-validation"

    docker rm -f "$container" >/dev/null 2>&1 || true

    docker build -t "$image" . || return 1

    docker run -d \
        --name "$container" \
        -p 127.0.0.1:5050:5000 \
        "$image" || return 1

    local status=1

    for _ in {1..10}; do
        if curl -fsS http://127.0.0.1:5050/notes; then
            status=0
            break
        fi

        sleep 1
    done

    echo
    docker logs "$container"

    docker rm -f "$container" >/dev/null 2>&1 || true

    return "$status"
}

while IFS='|' read -r role endpoint model files read_files || [[ -n "$role" ]]; do
    [[ -z "$role" || "$role" == \#* ]] && continue

    echo
    echo "========================================"
    echo "Role:     $role"
    echo "Endpoint: $endpoint"
    echo "Model:    $model"
    echo "Files:    $files"
    echo "Read:     $read_files"
    echo "========================================"

if [[ "$role" == "quality" ]]; then
    run_quality "$endpoint" "$model"
else
    run_aider \
        "$role" \
        "$endpoint" \
        "$model" \
        "$files" \
        "prompts/$role.md" \
        "$read_files"
fi

    if [[ "$role" == "api-test" ]]; then
        echo
        echo "== Running tests =="

        set +e
        uv run pytest 2>&1 | tee artifacts/pytest.txt
        pytest_status=${PIPESTATUS[0]}
        set -e

        echo "Pytest exit code: $pytest_status"

        if [[ $pytest_status -ne 0 ]]; then
            echo "WARNING: Some tests failed. Continuing to quality reporting."
        fi    
    fi
    if [[ "$role" == "deployment" ]]; then
    echo
    echo "== Validating deployment =="

    set +e
    validate_deployment 2>&1 | tee artifacts/deployment.txt
    deployment_status=${PIPESTATUS[0]}
    set -e

    if [[ $deployment_status -eq 0 ]]; then
        echo "Deployment validation PASSED."
    else
        echo "WARNING: Deployment validation FAILED. Continuing."
    fi
fi

if [[ "$role" == "api" ]]; then
echo
echo "== Validating OpenAPI spec =="

if uv run openapi-spec-validator docs/openapi.yaml 2>&1 | tee artifacts/openapi.txt; then
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

    if ! git diff --check; then
        echo "WARNING: Git diff check found formatting issues."
    fi

done < roles.conf
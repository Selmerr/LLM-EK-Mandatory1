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
          "$role" == "api-test" ]]; then
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

    QUALITY_ENDPOINT="$endpoint" \
    QUALITY_MODEL="$model" \
    python3 <<'PY'
import json
import os
import urllib.request
from pathlib import Path

endpoint = os.environ["QUALITY_ENDPOINT"]
model = os.environ["QUALITY_MODEL"]

prompt = Path("prompts/quality.md").read_text(encoding="utf-8")
pytest_output = Path("artifacts/pytest.txt").read_text(encoding="utf-8")

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": f"{prompt}\n\nPYTEST OUTPUT:\n{pytest_output}",
        }
    ],
    "stream": False,
    "options": {
        "temperature": 0,
        "num_ctx": 8192,
    },
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

Path("docs/quality.md").write_text(
    report + "\n",
    encoding="utf-8",
)

print(report)
PY
}


run_direct_file() {
    local endpoint="$1"
    local model="$2"
    local output_file="$3"
    local prompt_file="$4"
    local read_files="$5"
    local strip_outer_fence="${6:-false}"

    DIRECT_ENDPOINT="$endpoint" \
    DIRECT_MODEL="$model" \
    DIRECT_OUTPUT="$output_file" \
    DIRECT_PROMPT="$prompt_file" \
    DIRECT_READ_FILES="$read_files" \
    DIRECT_STRIP_FENCE="$strip_outer_fence" \
    python3 <<'PY'
import json
import os
import urllib.request
from pathlib import Path

endpoint = os.environ["DIRECT_ENDPOINT"]
model = os.environ["DIRECT_MODEL"]
output_file = Path(os.environ["DIRECT_OUTPUT"])
prompt_file = Path(os.environ["DIRECT_PROMPT"])
read_files = os.environ["DIRECT_READ_FILES"].split()
strip_outer_fence = os.environ["DIRECT_STRIP_FENCE"] == "true"

prompt = prompt_file.read_text(encoding="utf-8")

parts = [prompt]

for filename in read_files:
    path = Path(filename)

    if not path.exists():
        continue

    content = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    parts.append(
        f"\n\n===== {filename} =====\n{content}"
    )

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": "".join(parts),
        }
    ],
    "stream": False,
    "options": {
        "temperature": 0,
        "num_ctx": 8192,
    },
}

request = urllib.request.Request(
    f"{endpoint}/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

with urllib.request.urlopen(request) as response:
    result = json.load(response)

text = result["message"]["content"].strip()

if not text:
    raise RuntimeError(
        f"{model} returned an empty response"
    )

# Remove one outer Markdown fence if the model wrapped
# the whole generated file in one.
if strip_outer_fence:
    lines = text.splitlines()

    if (
        len(lines) >= 2
        and lines[0].strip().startswith("```")
        and lines[-1].strip() == "```"
    ):
        text = "\n".join(lines[1:-1]).strip()

output_file.parent.mkdir(
    parents=True,
    exist_ok=True,
)

output_file.write_text(
    text + "\n",
    encoding="utf-8",
)

print(text)
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
        if curl -fsS \
            http://127.0.0.1:5050/notes; then
            status=0
            break
        fi

        sleep 1
    done

    echo
    docker logs "$container" || true

    docker rm -f "$container" \
        >/dev/null 2>&1 || true

    return "$status"
}

stage_for_role() {
    local role="$1"

    case "$role" in
        architect|api|tech-lead)
            echo "planning"
            ;;

        storage-worker|api-worker)
            echo "implementation"
            ;;

        storage-test|api-test|quality)
            echo "verification"
            ;;

        deployment)
            echo "deployment"
            ;;

        documentation)
            echo "documentation"
            ;;

        *)
            echo "$role"
            ;;
    esac
}


approve_stage() {
    local stage="$1"

    echo
    echo "========================================"
    echo "NEXT STAGE: $stage"
    echo "========================================"

    case "$stage" in
        planning)
            echo "Roles:"
            echo "  architect"
            echo "  api"
            echo "  tech-lead"
            echo
            echo "This stage creates the architecture,"
            echo "OpenAPI contract, and implementation plan."
            ;;

        implementation)
            echo "Roles:"
            echo "  storage-worker"
            echo "  api-worker"
            echo
            echo "This stage modifies application source code."
            ;;

        verification)
            echo "Roles:"
            echo "  storage-test"
            echo "  api-test"
            echo "  quality"
            echo
            echo "This stage creates tests, runs pytest,"
            echo "and produces the quality report."
            ;;

        deployment)
            echo "Roles:"
            echo "  deployment"
            echo
            echo "This stage generates a Dockerfile and"
            echo "builds/runs the container for validation."
            ;;

        documentation)
            echo "Roles:"
            echo "  documentation"
            echo
            echo "This stage generates the final README."
            ;;
    esac

    if [[ -n "$previous_stage" ]]; then
        echo

        if [[ -z "$(git status --porcelain)" ]]; then
            echo "No uncommitted changes from the previous stage."
        else
            echo "== Changes from previous stage =="

            git status --short

            echo
            git --no-pager diff

            while IFS= read -r f; do
                git --no-pager diff --no-index /dev/null "$f" || true
            done < <(git ls-files --others --exclude-standard)
        fi

        echo
        echo "Review the output and diffs from the previous stage above."
    else
        echo
        echo "No previous stage to review."
    fi

    read -r -p "Approve '$stage' stage? [y/N] " answer < /dev/tty

    if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
        echo "Workflow stopped before '$stage'."
        exit 0
    fi
}

previous_stage=""
while IFS='|' read -r role endpoint model files read_files \
    || [[ -n "$role" ]]; do

    [[ -z "$role" || "$role" == \#* ]] && continue

    current_stage="$(stage_for_role "$role")"

    if [[ "$current_stage" != "$previous_stage" ]]; then
        approve_stage "$current_stage"
        previous_stage="$current_stage"
    fi
    echo
    echo "========================================"
    echo "Role:     $role"
    echo "Endpoint: $endpoint"
    echo "Model:    $model"
    echo "Files:    $files"
    echo "Read:     $read_files"
    echo "========================================"


    case "$role" in
        quality)
            run_quality \
                "$endpoint" \
                "$model"
            ;;

        deployment)
            run_direct_file \
                "$endpoint" \
                "$model" \
                "$files" \
                "prompts/$role.md" \
                "$read_files" \
                true
            ;;

        documentation)
            run_direct_file \
                "$endpoint" \
                "$model" \
                "$files" \
                "prompts/$role.md" \
                "$read_files" \
                true
            ;;

        *)
            run_aider \
                "$role" \
                "$endpoint" \
                "$model" \
                "$files" \
                "prompts/$role.md" \
                "$read_files"
            ;;
    esac


    if [[ "$role" == "api" ]]; then
        echo
        echo "== Validating OpenAPI spec =="

        if uv run openapi-spec-validator \
            docs/openapi.yaml \
            2>&1 | tee artifacts/openapi.txt; then

            echo "OpenAPI validation PASSED."
        else
            echo "ERROR: OpenAPI validation failed."
            exit 1
        fi
    fi


    if [[ "$role" == "api-test" ]]; then
        echo
        echo "== Running tests =="

        set +e

        uv run pytest \
            2>&1 | tee artifacts/pytest.txt

        pytest_status=${PIPESTATUS[0]}

        set -e

        echo "Pytest exit code: $pytest_status"

        if [[ $pytest_status -ne 0 ]]; then
            echo \
                "WARNING: Some tests failed. Continuing to quality reporting."
        fi
    fi


    if [[ "$role" == "deployment" ]]; then
        echo
        echo "== Validating deployment =="

        set +e

        validate_deployment \
            2>&1 | tee artifacts/deployment.txt

        deployment_status=${PIPESTATUS[0]}

        set -e

        if [[ $deployment_status -eq 0 ]]; then
            echo "Deployment validation PASSED."

            cat > artifacts/deployment-summary.txt <<'EOF'
Deployment validation: PASSED
Docker image built successfully.
Container started successfully.
GET /notes responded successfully.
EOF
        else
            echo \
                "WARNING: Deployment validation FAILED. Continuing."

            {
                echo "Deployment validation: FAILED"
                echo
                echo "Last validation output:"
                tail -n 10 artifacts/deployment.txt
            } > artifacts/deployment-summary.txt
        fi
    fi


    echo
    echo "== Result: $role =="

    for f in $files; do
        if [[ -f "$f" ]]; then
            echo "$f: $(wc -l < "$f") lines"
        fi
    done

git status --short

echo
echo "== Git diff =="

for f in $files; do
    if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        git --no-pager diff -- "$f"
    elif [[ -f "$f" ]]; then
        git --no-pager diff --no-index /dev/null "$f" || true
    fi
done

echo
echo "== Git diff check =="

if ! git --no-pager diff --check; then
    echo "WARNING: Git diff check found formatting issues."
fi

done < roles.conf
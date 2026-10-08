from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from local_multi_llm_workflow.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["run", *sys.argv[1:]] if sys.argv[1:2] != ["run"] else sys.argv[1:]))

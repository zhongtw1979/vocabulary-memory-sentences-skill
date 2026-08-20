import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_example import run_example  # noqa: E402


EXPECTED_FILES = {
    "coverage-audit.md",
    "risk-report.md",
    "risk-report.json",
    "language-review-packet.json",
    "meaning-fact-review-packet.json",
    "review-completeness.md",
    "vocabulary-memory-sentences.docx",
    "summary.json",
}


def test_run_example_generates_every_verified_artifact(tmp_path):
    result = run_example(ROOT / "examples", tmp_path)

    assert result["coverage"] == "PASS"
    assert result["risk_flags"] == 2
    assert result["reviews"] == "PASS"
    assert result["sentences"] == 4
    assert result["targets"] == 12
    assert result["docx_unresolved"] == 0
    assert EXPECTED_FILES <= {path.name for path in tmp_path.iterdir()}


def test_cli_prints_machine_readable_summary(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_example.py"),
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["coverage"] == "PASS"
    assert payload["reviews"] == "PASS"

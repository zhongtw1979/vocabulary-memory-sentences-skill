import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_review_completeness import audit_reviews, render_report as render_review_report  # noqa: E402
from audit_sentence_coverage import audit, read_sentences, render_report as render_coverage_report  # noqa: E402
from build_bilingual_docx import build_document  # noqa: E402
from lint_sentence_risks import lint_records, render_report as render_risk_report  # noqa: E402
from audit_sentence_coverage import read_inventory  # noqa: E402


EXAMPLE = ROOT / "examples"


def test_complete_example_pipeline_passes_without_mutating_fixtures(tmp_path):
    inventory = EXAMPLE / "sample-inventory.csv"
    sentences = EXAMPLE / "sample-sentences.json"
    reviews = [
        EXAMPLE / "reviews" / "language-review.json",
        EXAMPLE / "reviews" / "meaning-fact-review.json",
    ]

    coverage = audit(inventory, sentences)
    risk = lint_records(read_sentences(sentences), read_inventory(inventory))
    review = audit_reviews(sentences, reviews)

    assert coverage["result"] == "PASS"
    assert coverage["inventory_count"] == 12
    assert coverage["sentence_count"] == 4
    assert risk["flag_count"] == 2
    assert review["result"] == "PASS"

    (tmp_path / "coverage.md").write_text(
        render_coverage_report(coverage, "Synthetic example only."), encoding="utf-8"
    )
    (tmp_path / "risks.md").write_text(render_risk_report(risk), encoding="utf-8")
    (tmp_path / "reviews.md").write_text(render_review_report(review), encoding="utf-8")
    output = tmp_path / "study.docx"
    result = build_document(
        json.loads(sentences.read_text(encoding="utf-8")),
        output,
        "Vocabulary Memory Sentences",
        "v0.1.0",
        "Synthetic example only.",
    )

    assert output.exists()
    assert result["targets"] == 12
    assert all(path.stat().st_size > 0 for path in tmp_path.iterdir())

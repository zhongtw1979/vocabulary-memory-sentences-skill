import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_review_completeness import audit_reviews  # noqa: E402
from build_blind_review_packet import artifact_sha256  # noqa: E402


def sentence_payload() -> list[dict]:
    return [
        {
            "sentence_id": "S001",
            "scene": "Science class",
            "english": "Students test the water carefully in science class this morning.",
            "chinese": "学生们今天早晨在科学课上认真检测水样。",
            "targets": [{"entry_id": "E001", "surface": "test"}],
        }
    ]


def review_payload(focus: str, checksum: str) -> dict:
    checks = (
        {
            "grammar_ok": True,
            "collocation_ok": True,
            "idiomatic_ok": True,
            "actor_action_ok": True,
            "learner_model_ok": True,
        }
        if focus == "language"
        else {
            "translation_logic_ok": True,
            "fact_scope_ok": True,
        }
    )
    target_checks = (
        []
        if focus == "language"
        else [
            {
                "entry_id": "E001",
                "pos_ok": True,
                "sense_ok": True,
                "surface_ok": True,
                "translation_ok": True,
            }
        ]
    )
    return {
        "review_id": f"{focus}-final",
        "focus": focus,
        "artifact_sha256": checksum,
        "completed_at": "2026-08-20T12:00:00Z",
        "risk_adjudications": [],
        "sentences": [
            {
                "sentence_id": "S001",
                "verdict": "PASS",
                "checks": checks,
                "target_checks": target_checks,
                "issues": [],
            }
        ],
    }


def write_artifacts(tmp_path: Path) -> tuple[Path, Path, Path]:
    sentences_data = sentence_payload()
    checksum = artifact_sha256(sentences_data)
    sentences = tmp_path / "sentences.json"
    language = tmp_path / "language.json"
    meaning = tmp_path / "meaning.json"
    sentences.write_text(json.dumps(sentences_data, ensure_ascii=False), encoding="utf-8")
    language.write_text(json.dumps(review_payload("language", checksum)), encoding="utf-8")
    meaning.write_text(json.dumps(review_payload("meaning_fact", checksum)), encoding="utf-8")
    return sentences, language, meaning


def test_two_complete_clean_reviews_pass(tmp_path):
    sentences, language, meaning = write_artifacts(tmp_path)

    result = audit_reviews(sentences, [language, meaning])

    assert result["result"] == "PASS"
    assert result["failures"] == 0


def test_both_distinct_focuses_are_required(tmp_path):
    sentences, language, _ = write_artifacts(tmp_path)

    result = audit_reviews(sentences, [language])

    assert result["checks"]["missing_required_focus"] == 1


def test_stale_checksum_fails(tmp_path):
    sentences, language, meaning = write_artifacts(tmp_path)
    payload = json.loads(meaning.read_text(encoding="utf-8"))
    payload["artifact_sha256"] = "0" * 64
    meaning.write_text(json.dumps(payload), encoding="utf-8")

    result = audit_reviews(sentences, [language, meaning])

    assert result["checks"]["stale_artifact_checksum"] == 1


def test_incomplete_sentence_coverage_fails(tmp_path):
    sentences, language, meaning = write_artifacts(tmp_path)
    source = sentence_payload()
    source.append(
        {
            "sentence_id": "S002",
            "scene": "Library",
            "english": "Readers borrow useful books from the quiet library every week.",
            "chinese": "读者每周从安静的图书馆借阅有用的书。",
            "targets": [{"entry_id": "E002", "surface": "borrow"}],
        }
    )
    sentences.write_text(json.dumps(source), encoding="utf-8")
    checksum = artifact_sha256(source)
    for path in (language, meaning):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["artifact_sha256"] = checksum
        path.write_text(json.dumps(payload), encoding="utf-8")

    result = audit_reviews(sentences, [language, meaning])

    assert result["checks"]["incomplete_sentence_coverage"] == 2


def test_unresolved_p2_fails(tmp_path):
    sentences, language, meaning = write_artifacts(tmp_path)
    payload = json.loads(language.read_text(encoding="utf-8"))
    payload["sentences"][0]["issues"] = [
        {
            "severity": "P2",
            "category": "collocation",
            "reason": "The phrase is grammatical but unsuitable for learner imitation.",
            "status": "unresolved",
        }
    ]
    language.write_text(json.dumps(payload), encoding="utf-8")

    result = audit_reviews(sentences, [language, meaning])

    assert result["checks"]["unresolved_blocking_issues"] == 1


def test_unresolved_p3_is_allowed(tmp_path):
    sentences, language, meaning = write_artifacts(tmp_path)
    payload = json.loads(language.read_text(encoding="utf-8"))
    payload["sentences"][0]["issues"] = [
        {
            "severity": "P3",
            "category": "style",
            "reason": "An equally natural alternative exists.",
            "status": "unresolved",
        }
    ]
    language.write_text(json.dumps(payload), encoding="utf-8")

    result = audit_reviews(sentences, [language, meaning])

    assert result["result"] == "PASS"


def test_missing_target_meaning_check_fails(tmp_path):
    sentences, language, meaning = write_artifacts(tmp_path)
    payload = json.loads(meaning.read_text(encoding="utf-8"))
    payload["sentences"][0]["target_checks"] = []
    meaning.write_text(json.dumps(payload), encoding="utf-8")

    result = audit_reviews(sentences, [language, meaning])

    assert result["checks"]["incomplete_target_checks"] == 1


def test_false_required_check_fails(tmp_path):
    sentences, language, meaning = write_artifacts(tmp_path)
    payload = json.loads(language.read_text(encoding="utf-8"))
    payload["sentences"][0]["checks"]["learner_model_ok"] = False
    language.write_text(json.dumps(payload), encoding="utf-8")

    result = audit_reviews(sentences, [language, meaning])

    assert result["checks"]["failed_required_checks"] == 1

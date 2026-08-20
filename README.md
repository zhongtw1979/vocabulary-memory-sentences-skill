# Vocabulary Memory Sentences Skill

[简体中文](README.zh-CN.md)

A bilingual Codex skill for turning vocabulary lists into short, auditable memory sentences and study-ready Word handouts.

It accepts vocabulary extracted from PDF, image, Word, CSV, or spreadsheet sources and provides a reproducible workflow for source boundaries, deduplication, scene-based regrouping, structural coverage, independent language review, meaning/fact review, and DOCX generation.

## Why this project exists

Using every target word is a structural problem. Writing sentences that learners should imitate is a language-quality problem. This project keeps those gates separate:

- deterministic scripts prove coverage, mappings, length, target count, and review completeness;
- blind review packets support independent grammar, idiom, meaning, translation, logic, and fact checks;
- automated risk flags ask review questions without pretending to replace linguistic judgment;
- any final edit invalidates previous final reviews.

## Quick start

```bash
git clone https://github.com/zhongtw1979/vocabulary-memory-sentences-skill.git
cd vocabulary-memory-sentences-skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python scripts/run_example.py --output-dir build/example
```

The example generates coverage, risk, review-completeness, blind-review packet, and DOCX artifacts under `build/example`.

To install the Codex skill, see [Installation](docs/installation.md). For the complete workflow, see the [User Guide](docs/user-guide.md).

## Core commands

```bash
python scripts/audit_sentence_coverage.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --report coverage-audit.md

python scripts/lint_sentence_risks.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --report risk-report.md \
  --json-output risk-report.json

python scripts/audit_review_completeness.py \
  --sentences sentences.json \
  --reviews language-review.json meaning-fact-review.json \
  --risk-json risk-report.json \
  --report review-completeness.md
```

See the full [CLI reference](docs/cli-reference.md).

## Quality gate

Final delivery requires:

- current coverage audit: `PASS`;
- one independent `language` review tied to the current sentence checksum;
- one independent `meaning_fact` review tied to the same checksum;
- no unresolved `P0`, `P1`, or `P2` issue;
- current review-completeness audit: `PASS`;
- verified DOCX structure and target emphasis.

`CLEAN PASS` means no blocking issue was found under the required review dimensions. It is not a claim that no stylistic alternative exists.

Read [Quality Assurance](docs/quality-assurance.md) for the full model.

## Example

The repository includes an original synthetic example with 12 targets and four bilingual sentences:

- [sample inventory](examples/sample-inventory.csv)
- [sample sentence JSON](examples/sample-sentences.json)
- [review records](examples/reviews/)
- [expected reports and DOCX](examples/expected-output/)
- [complete walkthrough](docs/complete-example.md)

No private PDF, personal vocabulary list, or production workbook is included.

## Project boundaries

This project does not provide OCR, a graphical interface, hosted review, or a guarantee that automated checks can prove natural English. Codex may route source extraction and document inspection through the relevant PDF, spreadsheet, or document capabilities.

## Documentation

- [Installation](docs/installation.md)
- [User Guide](docs/user-guide.md)
- [Quality Assurance](docs/quality-assurance.md)
- [Complete Example](docs/complete-example.md)
- [CLI Reference](docs/cli-reference.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Data Schema](references/data-schema.md)
- [Review Rubric](references/review-rubric.md)
- [Failure Pattern Library](references/failure-library.md)

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE).

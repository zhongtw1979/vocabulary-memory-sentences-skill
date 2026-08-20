# Vocabulary Memory Sentences Open-Source Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, verify, and publish version `v0.1.0` of a bilingual open-source Codex skill for transforming vocabulary lists into audited memory sentences and DOCX handouts.

**Architecture:** Keep the installable skill concise and route detailed schemas and review rules to `references/`. Implement deterministic structural and review-completeness gates as standalone Python scripts, then demonstrate the complete pipeline with synthetic fixtures. Keep linguistic judgment explicit and reviewable; automated risk linting only flags candidates.

**Tech Stack:** Python 3.10+, standard library, `python-docx`, `pytest`, Markdown, YAML, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-20-vocabulary-memory-sentences-open-source-design.md`

## Global Constraints

- Publish as `zhongtw1979/vocabulary-memory-sentences-skill`, public, under the MIT License.
- Use English and Chinese documentation; keep code identifiers and command output in English.
- Do not include original PDFs, private vocabulary lists, the 1,000-word test corpus, personal paths, credentials, caches, or conversation exports.
- Require Python 3.10 or later.
- Treat coverage `PASS` as traceability only, never as proof of language quality.
- Permit no unresolved `P0`, `P1`, or `P2` issue at final delivery.
- Require a language-focused and a meaning/fact-focused full review after the last sentence edit.
- Use synthetic examples and generalized regression patterns only.
- Tag `v0.1.0` only after the public `main` GitHub Actions run succeeds.

---

### Task 1: Repository Foundation and Skill Contract

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `pyproject.toml`
- Create: `SKILL.md`
- Create: `agents/openai.yaml`
- Create: `references/data-schema.md`
- Test: `tests/test_skill_contract.py`

**Interfaces:**
- Consumes: the approved design spec and the current private skill as behavioral reference.
- Produces: an installable skill entrypoint, package metadata, authoritative data schemas, and test discovery configuration.

- [ ] **Step 1: Write the failing skill-contract test**

```python
def test_skill_routes_to_every_required_quality_resource():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for resource in (
        "references/quality-standard.md",
        "references/review-rubric.md",
        "references/failure-library.md",
        "references/data-schema.md",
    ):
        assert resource in text

def test_skill_requires_two_independent_final_reviews():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "language-focused" in text
    assert "meaning-and-fact-focused" in text
    assert "P0" in text and "P2" in text
```

- [ ] **Step 2: Run the contract test and verify RED**

Run: `python3 -m pytest tests/test_skill_contract.py -q`

Expected: failure because the public `SKILL.md` and referenced resources do not exist.

- [ ] **Step 3: Add the repository foundation and concise skill entrypoint**

Implement:

```yaml
---
name: building-vocabulary-memory-sentences
description: Use when a vocabulary list from PDF, image, Word, CSV, or spreadsheet must be extracted, deduplicated, regrouped, or converted into bilingual memory sentences and a verified study handout.
---
```

The body must define source scope, inventory, composition, deterministic audit, two independent final reviews, final audit, DOCX generation, and hard gates. Add `pyproject.toml` with `python-docx` and `pytest` dependencies and configure pytest for `tests/`.

- [ ] **Step 4: Run the contract test and verify GREEN**

Run: `python3 -m pytest tests/test_skill_contract.py -q`

Expected: all skill-contract tests pass.

- [ ] **Step 5: Commit the foundation**

```bash
git add -- .gitignore LICENSE pyproject.toml SKILL.md agents/openai.yaml references/data-schema.md tests/test_skill_contract.py
git commit -m "feat: establish public skill contract"
```

### Task 2: Deterministic Coverage Audit

**Files:**
- Create: `scripts/audit_sentence_coverage.py`
- Test: `tests/test_audit_sentence_coverage.py`

**Interfaces:**
- Consumes: inventory CSV and sentence JSON defined by `references/data-schema.md`.
- Produces: `audit(...) -> dict[str, Any]`, `render_report(result, scope_note) -> str`, JSON stdout, Markdown report, and exit status `1` on failure.

- [ ] **Step 1: Write failing tests for valid coverage and metadata conflict**

```python
def test_complete_dataset_passes(tmp_path):
    inventory, sentences = valid_fixture(tmp_path)
    assert audit(inventory, sentences)["result"] == "PASS"

def test_metadata_conflict_blocks_generation(tmp_path):
    inventory, sentences = valid_fixture(tmp_path, metadata_status="conflict")
    result = audit(inventory, sentences)
    assert result["checks"]["inventory_metadata_not_ok"] == 1
    assert result["result"] == "FAIL"
```

Add focused failing cases for duplicate IDs, missing assignments, unknown IDs, mapping mismatch, out-of-range length, target-count drift, and missing exact target surface.

- [ ] **Step 2: Run the coverage tests and verify RED**

Run: `python3 -m pytest tests/test_audit_sentence_coverage.py -q`

Expected: import failure because `audit_sentence_coverage.py` does not exist.

- [ ] **Step 3: Implement the smallest complete coverage audit**

Required public signatures:

```python
def word_count(text: str) -> int: ...
def read_inventory(path: str | Path) -> list[dict[str, str]]: ...
def read_sentences(path: str | Path) -> list[dict[str, Any]]: ...
def audit(inventory_path: str | Path, sentences_path: str | Path, *,
          min_words: int = 9, max_words: int = 12,
          min_targets: int = 3, max_targets: int = 4,
          expected_pages: set[str] | None = None) -> dict[str, Any]: ...
def render_report(result: dict[str, Any], scope_note: str) -> str: ...
```

Count exact target occurrences with token-boundary-aware matching so `art` does not pass inside `earth`. Require all retained inventory rows to have `metadata_status=ok`.

- [ ] **Step 4: Run coverage tests and verify GREEN**

Run: `python3 -m pytest tests/test_audit_sentence_coverage.py -q`

Expected: all coverage-audit tests pass.

- [ ] **Step 5: Commit the audit**

```bash
git add -- scripts/audit_sentence_coverage.py tests/test_audit_sentence_coverage.py
git commit -m "feat: add deterministic coverage audit"
```

### Task 3: Risk Linter and Blind-Review Packet

**Files:**
- Create: `scripts/lint_sentence_risks.py`
- Create: `scripts/build_blind_review_packet.py`
- Test: `tests/test_lint_sentence_risks.py`
- Test: `tests/test_build_blind_review_packet.py`

**Interfaces:**
- Consumes: valid inventory CSV and sentence JSON.
- Produces: `lint_sentences(...) -> dict`, risk Markdown/JSON; `build_packet(...) -> dict` with SHA-256 artifact checksum, target metadata, and reproducibly shuffled sentences.

- [ ] **Step 1: Write failing risk-linter tests**

```python
def test_flags_absolute_scientific_claim():
    result = lint_records([sentence("A test can identify every molecule accurately.")], inventory())
    codes = {flag["code"] for flag in result["flags"]}
    assert {"ABSOLUTE_QUANTIFIER", "SCIENTIFIC_CAPABILITY"} <= codes

def test_flags_ambiguous_control_structure():
    result = lint_records([sentence("The producer chose actors to produce the film.")], inventory())
    assert "AMBIGUOUS_ACTOR_CONTROL" in {flag["code"] for flag in result["flags"]}
```

Add tests proving ordinary sentences are not marked wrong and that flags use `needs_review`, never an automatic error verdict.

- [ ] **Step 2: Run the linter tests and verify RED**

Run: `python3 -m pytest tests/test_lint_sentence_risks.py -q`

Expected: import failure because the risk linter does not exist.

- [ ] **Step 3: Implement the risk linter**

Implement configurable pattern groups for absolute quantifiers, medical/scientific capability verbs, ambiguous control structures, translation-relation tokens, and inventory metadata conflicts. Each flag contains `sentence_id`, `code`, `severity_hint`, `message`, and `needs_review: true`.

- [ ] **Step 4: Run the linter tests and verify GREEN**

Run: `python3 -m pytest tests/test_lint_sentence_risks.py -q`

Expected: all risk-linter tests pass.

- [ ] **Step 5: Write failing blind-packet tests**

```python
def test_packet_is_reproducible_and_hides_prior_verdicts(tmp_path):
    first = build_packet(inventory_path, sentence_path, focus="language", seed=17)
    second = build_packet(inventory_path, sentence_path, focus="language", seed=17)
    assert first == second
    assert "previous_verdict" not in json.dumps(first)
    assert len(first["artifact_sha256"]) == 64
```

Add tests for invalid focus, metadata conflict, and authoritative target metadata attachment.

- [ ] **Step 6: Run packet tests and verify RED**

Run: `python3 -m pytest tests/test_build_blind_review_packet.py -q`

Expected: import failure because the packet builder does not exist.

- [ ] **Step 7: Implement the blind-review packet builder**

Required signature:

```python
def build_packet(inventory_path: str | Path, sentences_path: str | Path,
                 *, focus: str, seed: int = 0) -> dict[str, Any]: ...
```

Allowed focus values are `language` and `meaning_fact`. Serialize current sentence data canonically before computing SHA-256.

- [ ] **Step 8: Run packet tests and verify GREEN**

Run: `python3 -m pytest tests/test_build_blind_review_packet.py -q`

Expected: all packet-builder tests pass.

- [ ] **Step 9: Commit risk and packet tooling**

```bash
git add -- scripts/lint_sentence_risks.py scripts/build_blind_review_packet.py tests/test_lint_sentence_risks.py tests/test_build_blind_review_packet.py
git commit -m "feat: add risk linting and blind review packets"
```

### Task 4: Review-Completeness Gate and Quality References

**Files:**
- Create: `scripts/audit_review_completeness.py`
- Create: `references/quality-standard.md`
- Create: `references/review-rubric.md`
- Create: `references/failure-library.md`
- Test: `tests/test_audit_review_completeness.py`

**Interfaces:**
- Consumes: current sentence JSON and two review JSON files.
- Produces: `audit_reviews(...) -> dict`, Markdown report, JSON stdout, and failure exit status for stale, incomplete, or unresolved reviews.

- [ ] **Step 1: Write failing review-gate tests**

```python
def test_two_complete_clean_reviews_pass(tmp_path):
    result = audit_reviews(sentences, [language_review, meaning_review])
    assert result["result"] == "PASS"

def test_unresolved_p2_fails(tmp_path):
    meaning_review["sentences"][0]["issues"] = [
        {"severity": "P2", "status": "unresolved", "category": "collocation"}
    ]
    result = audit_reviews(sentences, [language_review, meaning_review])
    assert result["checks"]["unresolved_blocking_issues"] == 1
```

Add failures for missing focus, incomplete sentence coverage, stale checksum, missing target-level meaning checks, and duplicate focus.

- [ ] **Step 2: Run review-gate tests and verify RED**

Run: `python3 -m pytest tests/test_audit_review_completeness.py -q`

Expected: import failure because the review audit does not exist.

- [ ] **Step 3: Implement review-completeness auditing**

Required signatures:

```python
def artifact_sha256(sentences: list[dict[str, Any]]) -> str: ...
def audit_reviews(sentences_path: str | Path,
                  review_paths: Sequence[str | Path]) -> dict[str, Any]: ...
def render_report(result: dict[str, Any]) -> str: ...
```

Verify the exact required focuses, all sentence IDs, current checksum, target-level checks for `meaning_fact`, and zero unresolved `P0`–`P2` issues.

- [ ] **Step 4: Run review-gate tests and verify GREEN**

Run: `python3 -m pytest tests/test_audit_review_completeness.py -q`

Expected: all review-completeness tests pass.

- [ ] **Step 5: Write the detailed quality references**

Document schemas, `P0`–`P3` examples, independent-review instructions, stopping rules, risk-flag adjudication, grouping priorities, and generalized failure patterns. Include ambiguous infinitive actors, part-of-speech drift, path-relation mistranslation, intended-sense drift, and overly broad capability claims without copying private sentence corpora.

- [ ] **Step 6: Run contract and review tests together**

Run: `python3 -m pytest tests/test_skill_contract.py tests/test_audit_review_completeness.py -q`

Expected: all tests pass.

- [ ] **Step 7: Commit the quality gate and references**

```bash
git add -- scripts/audit_review_completeness.py references/quality-standard.md references/review-rubric.md references/failure-library.md tests/test_audit_review_completeness.py
git commit -m "feat: enforce independent review quality gates"
```

### Task 5: DOCX Builder and Complete Synthetic Example

**Files:**
- Create: `scripts/build_bilingual_docx.py`
- Create: `examples/sample-inventory.csv`
- Create: `examples/sample-sentences.json`
- Create: `examples/reviews/language-review.json`
- Create: `examples/reviews/meaning-fact-review.json`
- Create: `examples/expected-output/coverage-audit.md`
- Create: `examples/expected-output/risk-report.md`
- Create: `examples/expected-output/review-completeness.md`
- Test: `tests/test_build_bilingual_docx.py`
- Test: `tests/test_end_to_end_example.py`

**Interfaces:**
- Consumes: audited sentence JSON and verified synthetic example artifacts.
- Produces: learner-facing DOCX and reproducible example reports.

- [ ] **Step 1: Write failing DOCX and end-to-end tests**

```python
def test_docx_contains_bilingual_text_without_internal_ids(tmp_path):
    result = build_document(data, tmp_path / "study.docx", "Study", "v0.1.0", "Synthetic example")
    assert result["unresolved"] == 0
    assert "S001" not in extracted_docx_text(tmp_path / "study.docx")

def test_example_pipeline_passes(tmp_path):
    assert coverage_result["result"] == "PASS"
    assert review_result["result"] == "PASS"
    assert generated_docx.exists()
```

The end-to-end test regenerates all reports into `tmp_path`; it must not overwrite tracked fixtures.

- [ ] **Step 2: Run DOCX and example tests and verify RED**

Run: `python3 -m pytest tests/test_build_bilingual_docx.py tests/test_end_to_end_example.py -q`

Expected: import or fixture failure because the builder and example do not exist.

- [ ] **Step 3: Implement DOCX generation**

Port the proven bilingual structure with English first, Chinese below, scene headings, target underlining, no learner-facing IDs, and validation that every target surface resolves to a distinct occurrence. Use widely available Latin fonts and configurable East Asian fonts.

- [ ] **Step 4: Create the synthetic example and two clean review records**

Use 12–16 original vocabulary entries across four or five sentences. Include nouns, verbs, adjectives, one phrase, and one inflected surface. Keep all metadata `ok`, all sentence constraints valid, and both review checksums current.

- [ ] **Step 5: Generate expected reports with project scripts**

Run:

```bash
python3 scripts/audit_sentence_coverage.py --inventory examples/sample-inventory.csv --sentences examples/sample-sentences.json --report examples/expected-output/coverage-audit.md
python3 scripts/lint_sentence_risks.py --inventory examples/sample-inventory.csv --sentences examples/sample-sentences.json --report examples/expected-output/risk-report.md
python3 scripts/audit_review_completeness.py --sentences examples/sample-sentences.json --reviews examples/reviews/language-review.json examples/reviews/meaning-fact-review.json --report examples/expected-output/review-completeness.md
```

Expected: every command exits `0`.

- [ ] **Step 6: Run DOCX and end-to-end tests and verify GREEN**

Run: `python3 -m pytest tests/test_build_bilingual_docx.py tests/test_end_to_end_example.py -q`

Expected: all tests pass.

- [ ] **Step 7: Commit the document pipeline and example**

```bash
git add -- scripts/build_bilingual_docx.py examples tests/test_build_bilingual_docx.py tests/test_end_to_end_example.py
git commit -m "feat: add verified bilingual example pipeline"
```

### Task 6: Bilingual Documentation and Community Files

**Files:**
- Create: `README.md`
- Create: `README.zh-CN.md`
- Create: `CHANGELOG.md`
- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `CODE_OF_CONDUCT.md`
- Create: `docs/installation.md`
- Create: `docs/user-guide.md`
- Create: `docs/quality-assurance.md`
- Create: `docs/complete-example.md`
- Create: `docs/troubleshooting.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Create: `.github/pull_request_template.md`
- Test: `tests/test_documentation.py`

**Interfaces:**
- Consumes: final commands, schemas, and example artifacts from Tasks 1–5.
- Produces: independent English and Chinese onboarding paths and project governance documentation.

- [ ] **Step 1: Write failing documentation tests**

```python
def test_both_readmes_include_install_and_quick_start():
    for path in (ROOT / "README.md", ROOT / "README.zh-CN.md"):
        text = path.read_text(encoding="utf-8")
        assert "audit_sentence_coverage.py" in text
        assert "building-vocabulary-memory-sentences" in text

def test_docs_contain_no_private_paths_or_placeholders():
    text = all_tracked_docs()
    assert "/Users/" not in text
    assert "[PLACEHOLDER]" not in text
```

- [ ] **Step 2: Run documentation tests and verify RED**

Run: `python3 -m pytest tests/test_documentation.py -q`

Expected: failure because documentation files do not exist.

- [ ] **Step 3: Write the bilingual and community documentation**

Both README files must include project purpose, boundaries, installation, quick start, quality model, example links, limitations, license, and contribution links. Full docs must use commands verified against the repository and state that automated checks do not replace language review.

- [ ] **Step 4: Run documentation tests and link checks**

Run: `python3 -m pytest tests/test_documentation.py -q`

Expected: all documentation tests pass.

- [ ] **Step 5: Commit documentation**

```bash
git add -- README.md README.zh-CN.md CHANGELOG.md CONTRIBUTING.md SECURITY.md CODE_OF_CONDUCT.md docs .github/ISSUE_TEMPLATE .github/pull_request_template.md tests/test_documentation.py
git commit -m "docs: add bilingual open-source documentation"
```

### Task 7: CI, Release Verification, and GitHub Publication

**Files:**
- Create: `.github/workflows/tests.yml`
- Create: `scripts/run_example.py`
- Test: `tests/test_run_example.py`

**Interfaces:**
- Consumes: all scripts, fixtures, tests, and documentation.
- Produces: one-command example execution, clean CI, public repository, and post-CI `v0.1.0` tag.

- [ ] **Step 1: Write the failing one-command example test**

```python
def test_run_example_generates_all_artifacts(tmp_path):
    result = run_example(ROOT / "examples", tmp_path)
    assert result["coverage"] == "PASS"
    assert result["reviews"] == "PASS"
    assert (tmp_path / "vocabulary-memory-sentences.docx").exists()
```

- [ ] **Step 2: Run the test and verify RED**

Run: `python3 -m pytest tests/test_run_example.py -q`

Expected: import failure because `run_example.py` does not exist.

- [ ] **Step 3: Implement one-command example execution and CI**

Implement:

```python
def run_example(example_root: str | Path, output_dir: str | Path) -> dict[str, Any]: ...
```

GitHub Actions must install `.[dev]`, run `pytest`, run the synthetic example into a temporary directory, and validate the skill using the bundled validator when available or repository contract tests otherwise.

- [ ] **Step 4: Run all local verification commands**

Run:

```bash
python3 -m pytest -q
python3 scripts/run_example.py --output-dir build/example
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
git diff --check
rg -n "/Users/|g[h]p_|BEGIN (RSA|OPENSSH|PRIVATE) KEY|\[PLACEHOLDER\]" --glob '!.git/**' .
git status --short
```

Expected: tests and validators pass, example artifacts exist, no private path or secret match exists outside approved design/plan path references, and only intended files are modified.

- [ ] **Step 5: Commit CI and final implementation**

```bash
git add -- .github/workflows/tests.yml scripts/run_example.py tests/test_run_example.py
git commit -m "ci: verify the complete open-source workflow"
```

- [ ] **Step 6: Merge the verified feature branch to `main` and re-run tests**

Run the full test suite on the merged `main` checkout. Do not delete the feature worktree until the merged result passes.

- [ ] **Step 7: Create and push the public GitHub repository**

```bash
gh repo create zhongtw1979/vocabulary-memory-sentences-skill --public --source . --remote origin --push --description "A bilingual Codex skill for turning vocabulary lists into audited memory sentences and study-ready Word handouts."
```

Verify the exact repository URL and `main` branch before retrying any uncertain operation.

- [ ] **Step 8: Verify GitHub Actions**

Run:

```bash
gh run list --repo zhongtw1979/vocabulary-memory-sentences-skill --branch main --limit 1
gh run watch --repo zhongtw1979/vocabulary-memory-sentences-skill --exit-status
```

Expected: the latest `main` workflow completes successfully.

- [ ] **Step 9: Tag and push `v0.1.0` after green CI**

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

- [ ] **Step 10: Verify the public release state**

Confirm repository visibility, default branch, README rendering, license detection, tag, latest workflow conclusion, and absence of private artifacts through GitHub API and local tracked-file inspection.

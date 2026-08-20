# Vocabulary Memory Sentences Skill: Open-Source Project Design

## 1. Purpose

Package the existing `building-vocabulary-memory-sentences` Codex skill as a public, reusable, bilingual open-source project. The repository must let a new user install the skill, understand its quality model, run a complete synthetic example, verify outputs, and contribute changes without access to the original private vocabulary files.

The first public release is `v0.1.0` under the MIT License in the public GitHub repository `zhongtw1979/vocabulary-memory-sentences-skill`.

## 2. Product Boundary

The repository contains:

- one installable Codex skill;
- deterministic Python utilities for coverage, risk linting, blind-review packet generation, review-completeness auditing, and DOCX generation;
- bilingual project documentation;
- synthetic example data and expected reports;
- regression and integration tests;
- GitHub Actions and community contribution files.

The repository excludes:

- the user's original PDFs, extracted word lists, 1,000-word test corpus, and generated private workbooks;
- personal filesystem paths, credentials, caches, temporary files, and conversation exports;
- claims that automated checks can prove linguistic naturalness;
- a plugin layer, hosted service, graphical application, or external API in `v0.1.0`.

## 3. Intended Users

Primary users are teachers, parents, students, curriculum developers, and Codex users who need to turn a vocabulary list from PDF, image, Word, CSV, or spreadsheet sources into short bilingual memorization sentences.

Contributors should be able to run the test suite with a standard Python environment and inspect every output from the synthetic example.

## 4. Core Quality Model

The project separates structural correctness from language quality.

### 4.1 Structural gate

Deterministic checks verify:

- stable and unique vocabulary IDs;
- exactly one primary assignment for every retained entry;
- no unknown or duplicate target assignments;
- sentence IDs and inventory mappings;
- configurable sentence length and target-count bounds;
- exact target surfaces in the English sentence;
- final coverage after all language edits.

A structural `PASS` proves traceability only.

### 4.2 Language and meaning gates

Every sentence is assessed with four severity levels:

- `P0`: structural failure;
- `P1`: grammar, part-of-speech, intended-sense, translation, logic, or factual error;
- `P2`: learner-material failure such as unnatural collocation, forced grouping, or wording unsuitable for imitation;
- `P3`: optional stylistic improvement where the original remains correct and natural.

Final delivery permits no unresolved `P0`, `P1`, or `P2` issue. `P3` suggestions may remain recorded.

### 4.3 Independent final review

After the last sentence edit, two independent full-dataset review passes are required:

1. a language-dominant blind review covering grammar, idiom, collocation, actor-action logic, and learner suitability;
2. a meaning-and-fact blind review covering target part of speech, intended sense, translation relations, common knowledge, and scientific or medical claims.

Each pass uses the current artifacts without prior verdicts or diffs. Any accepted edit invalidates previous final-pass status. The coverage audit is rerun after the final language edit.

`CLEAN PASS` means that no unresolved `P0`–`P2` issue was found under the required review dimensions. It is not an absolute claim that no alternative wording exists.

## 5. Data Contracts

### 5.1 Inventory CSV

Required columns:

```text
entry_id,entry,meaning,entry_type,required_pos,required_sense_zh,allowed_surfaces,metadata_status,source_file,source_page,book,unit,decision,sentence_id
```

`metadata_status` is one of `ok`, `conflict`, or `unresolved`. Only `ok` entries may enter sentence generation. Optional source fields may be empty when the source does not provide them, but their columns remain present.

### 5.2 Sentence JSON

Each record contains:

```json
{
  "sentence_id": "S001",
  "scene": "At the research center",
  "english": "The specialist examined the sample and recorded the result carefully.",
  "chinese": "这位专家检查了样本，并认真记录了结果。",
  "targets": [
    {
      "entry_id": "E0001",
      "surface": "specialist"
    }
  ]
}
```

Target metadata stays authoritative in the inventory. Sentence records refer to it by stable ID and exact surface.

### 5.3 Review records

Review data uses JSON so completeness can be audited. Each full review records:

- reviewer or pass identifier;
- review focus;
- source sentence-artifact checksum;
- one verdict per sentence;
- target-level part-of-speech, sense, surface, and translation checks where required;
- issue severity, category, proposed revision, reason, and resolution status;
- review completion time.

Markdown review reports are generated views, not the source of truth.

## 6. Sentence Construction Policy

Default sentences contain 9–12 English word tokens and 3–4 target entries, express one clear proposition, and contain no more than two actions.

Grouping priority is:

1. natural and accurate English;
2. faithful target sense and part of speech;
3. coherent scene and actor-action relations;
4. four-target coverage;
5. minimizing sentence count.

Four-target groups are preferred only when natural. A group drops to three targets when a fourth target creates semantic strain. If two revisions cannot produce a learner-worthy sentence, the targets are regrouped.

## 7. Repository Structure

```text
vocabulary-memory-sentences-skill/
|-- README.md
|-- README.zh-CN.md
|-- LICENSE
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- SECURITY.md
|-- CODE_OF_CONDUCT.md
|-- pyproject.toml
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   |-- quality-standard.md
|   |-- review-rubric.md
|   |-- failure-library.md
|   `-- data-schema.md
|-- scripts/
|   |-- audit_sentence_coverage.py
|   |-- lint_sentence_risks.py
|   |-- build_blind_review_packet.py
|   |-- audit_review_completeness.py
|   `-- build_bilingual_docx.py
|-- examples/
|   |-- sample-inventory.csv
|   |-- sample-sentences.json
|   |-- reviews/
|   `-- expected-output/
|-- tests/
|-- docs/
|   |-- installation.md
|   |-- user-guide.md
|   |-- quality-assurance.md
|   |-- complete-example.md
|   `-- troubleshooting.md
`-- .github/
    |-- workflows/tests.yml
    |-- ISSUE_TEMPLATE/
    `-- pull_request_template.md
```

Only project-level documentation belongs at the repository root or under `docs/`. The installable skill itself remains concise and uses progressive disclosure through `references/`.

## 8. Command-Line Tools

All scripts use Python 3.10 or later, standard-library modules where practical, and clear nonzero exit codes on failure.

### 8.1 Coverage audit

`audit_sentence_coverage.py` validates inventory and sentence mappings and writes a human-readable Markdown report.

### 8.2 Risk linter

`lint_sentence_risks.py` creates review flags for absolute quantifiers, scientific or medical capability claims, ambiguous control structures, high-risk translation relations, and metadata conflicts. It never labels a flagged sentence as wrong automatically.

### 8.3 Blind-review packet builder

`build_blind_review_packet.py` produces a review JSON packet containing current sentences and authoritative target metadata while excluding prior verdicts and historical revisions. A deterministic seed supports reproducible randomized ordering.

### 8.4 Review-completeness audit

`audit_review_completeness.py` verifies that both required review focuses cover every sentence and target, reference the current sentence checksum, contain no unresolved `P0`–`P2` issues, and were completed after the final sentence artifact was created.

### 8.5 DOCX builder

`build_bilingual_docx.py` creates a study-ready Word handout with English first, Chinese below, highlighted target surfaces, scene headings, and no learner-facing internal IDs.

## 9. Documentation

`README.md` is the English landing page and links to `README.zh-CN.md`. Both explain the project value, limitations, installation, quick start, quality gates, and links to the full guide.

Supporting documentation covers:

- installation in Codex and generic local Python setup;
- full workflow from source boundary to verified DOCX;
- input and review schemas;
- the distinction between automated coverage and human or model language review;
- a complete synthetic walkthrough;
- troubleshooting and renderer limitations;
- contribution, conduct, security, and release expectations.

## 10. Examples and Privacy

The example uses synthetic vocabulary entries created for this repository. It must exercise ordinary words, multiple parts of speech, a phrase, target inflection, Chinese translations, risk flags, and both review passes.

Expected outputs include coverage, risk, and review-completeness reports plus a generated DOCX. No private artifact is copied or transformed into an example.

## 11. Tests

Tests use `pytest` and include:

- unit tests for token counting, assignment checks, surface matching, metadata conflicts, risk flags, packet checksums, and review completeness;
- negative fixtures proving each gate fails for the intended reason;
- regression cases derived from generalized failure patterns such as ambiguous infinitive actors, part-of-speech drift, path-relation mistranslation, intended-sense drift, and overly broad scientific claims;
- an end-to-end synthetic example test;
- DOCX archive and extracted-text checks;
- skill metadata validation.

Regression fixtures express reusable patterns and contain no private source data.

## 12. Continuous Integration

GitHub Actions runs on supported Python versions, installs the package in a clean environment, executes the full test suite, validates the skill folder, and regenerates the example reports into a temporary directory for comparison or invariant checks.

The public release is not considered verified until the first Actions run on `main` completes successfully.

## 13. Publishing

Publishing steps are:

1. implement and verify locally;
2. inspect the complete repository for secrets, personal paths, private source material, caches, and large binaries;
3. commit the verified project to `main`;
4. create the public GitHub repository `zhongtw1979/vocabulary-memory-sentences-skill`;
5. push `main`;
6. verify the repository metadata, default branch, rendered documentation, and Actions result;
7. create and push tag `v0.1.0` only after the main-branch CI result is green.

## 14. Acceptance Criteria

The project is ready for public release when:

- the installable skill passes Codex skill validation;
- every Python test passes in a clean local environment;
- the synthetic example runs from inventory to validated DOCX;
- known generalized failure patterns are caught by the appropriate gate;
- English and Chinese documentation independently support installation and first use;
- no unresolved placeholder, personal path, credential, private dataset, cache, or original PDF exists in tracked files;
- GitHub Actions passes on the public `main` branch;
- the repository is public under MIT and tagged `v0.1.0` after CI success.

## 15. Deferred Scope

The following are candidates for later releases:

- packaging as a full Codex plugin;
- a graphical interface;
- hosted linguistic review services;
- direct PDF OCR integrations beyond skill routing;
- multilingual translations beyond English and Chinese;
- publication to third-party skill marketplaces.

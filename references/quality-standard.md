# Vocabulary Memory Sentence Quality Standard

## 1. Source Boundary

- Use only content visible in user-provided files unless supplementation is explicitly authorized.
- Distinguish exact duplicate pages, partial duplicate pages, duplicate vocabulary entries, and repeated senses.
- Keep unique material from partial duplicates.
- Record missing, cut-off, blurred, or unreadable content instead of guessing.
- Record every exclusion and its reason.

## 2. Inventory Quality

Use the fields in [data-schema.md](data-schema.md). Every retained entry needs a stable ID, authoritative source meaning, required part of speech, required Chinese sense, allowed surfaces, and `metadata_status=ok`.

Deduplicate using headword, part of speech, and meaning together:

- keep identical spelling when grammatical function or sense differs;
- keep a phrase separately when both the phrase and a component are source entries;
- keep meaningful variants when the source teaches them independently;
- mark exclusions explicitly rather than deleting rows silently.

Stop before composition when the source label, part of speech, or translation conflicts. Resolve the metadata or mark the entry `unresolved`.

## 3. Sentence Construction

Defaults:

- 9–12 English word tokens;
- 3–4 primary target entries;
- one clear proposition;
- no more than two actions;
- one plausible scene with clear actors, actions, and objects.

Quality priority:

1. natural and accurate English;
2. faithful target part of speech and intended sense;
3. coherent scene and actor-action relations;
4. four-target coverage;
5. minimizing sentence count.

Use common collocations and ordinary syntax that a learner can reuse. Prefer three targets when a fourth creates semantic strain. If two revisions cannot produce learner-worthy English, regroup the targets.

Every retained entry has exactly one primary sentence assignment. An incidental occurrence elsewhere does not count as primary coverage.

## 4. Severity Model

| Level | Meaning | Examples | Final state |
|---|---|---|---|
| `P0` | Structural failure | Missing entry, duplicate assignment, stale checksum, broken surface | Must resolve |
| `P1` | Substantive error | Grammar error, wrong part of speech, sense drift, mistranslation, false claim | Must resolve |
| `P2` | Learner-material failure | Forced grouping, unnatural collocation, misleading actor logic | Must resolve |
| `P3` | Optional style | Original is already correct and natural; an equal alternative exists | May remain |

Do not downgrade a `P1` or `P2` merely because the sentence is understandable. The learner-material test is whether a student should imitate the sentence.

## 5. Deterministic Gates

Run `audit_sentence_coverage.py` before language review and again after the final edit. It checks inventory uniqueness, metadata status, assignments, sentence IDs, length, target count, exact target occurrences, allowed surfaces, mappings, and optional source pages.

Run `lint_sentence_risks.py` to surface sentences that deserve deliberate review. A flag is a question, not a verdict. Reviewers adjudicate every relevant flag in the final review records.

Run `audit_review_completeness.py` after both independent final reviews. It checks focuses, artifact checksums, full coverage, required sentence and target checks, issue resolution, and final verdicts.

## 6. Language Review Sequence

### Diagnostic revision

Review the full dataset for grammar, tense, agreement, articles, idiom, collocation, actor-action logic, intended sense, translation, and facts. Apply accepted revisions and regroup when editing cannot make the grouping natural.

### Independent final review: language

Use a fresh blind packet. Review every current sentence without prior verdicts or diffs. Check grammar, collocation, idiom, actor-action logic, and learner suitability.

### Independent final review: meaning and fact

Use a separate fresh blind packet. For every target, check part of speech, intended sense, allowed surface, and Chinese alignment. Check path, time, cause, common knowledge, and scientific or medical scope.

Any accepted English or Chinese edit invalidates both final review records. Rebuild the packets and repeat both reviews from the first sentence.

## 7. Clean-Pass Rule

Final delivery requires:

- coverage audit `PASS` on the current artifact;
- one complete `language` review tied to the current checksum;
- one complete `meaning_fact` review tied to the current checksum;
- no unresolved `P0`, `P1`, or `P2` issue;
- no incomplete or failed required check;
- all recorded risk adjudications resolved;
- review-completeness audit `PASS`.

Write the conclusion as: “No unresolved blocking issue was found under the required review dimensions.” Do not claim that no stylistic alternative exists.

## 8. Learner-Facing DOCX

Show English first and Chinese below it. Emphasize target surfaces, preserve scene headings, include the source-scope note, and hide internal IDs. Verify the archive, extracted text, sentence count, bilingual alignment, target emphasis, and unresolved-surface count.

Render only when layout risk justifies visual inspection. A renderer's missing CJK font does not invalidate structurally correct content; report the environment limitation.

## 9. Required Deliverables

- source-boundary and duplicate-page note;
- deduplicated inventory CSV;
- final sentence JSON;
- coverage report;
- risk report with adjudications;
- separate final language and meaning/fact review records;
- review-completeness report;
- verified bilingual DOCX.

---
name: building-vocabulary-memory-sentences
description: Use when a vocabulary list from PDF, image, Word, CSV, or spreadsheet must be extracted, deduplicated, regrouped, or converted into bilingual memory sentences and a verified study handout.
---

# Building Vocabulary Memory Sentences

## Overview

Turn a visible vocabulary source into a traceable inventory, natural bilingual sentences, auditable review evidence, and a learner-facing Word handout. Structural coverage and language quality are separate gates.

## Workflow

1. Freeze the visible source scope. Record duplicate, partial, missing, and illegible pages. Do not reconstruct missing content without user authorization.
2. Build the inventory defined in [the data schema](references/data-schema.md). Resolve every `metadata_status=conflict` or `unresolved` item before composition.
3. Deduplicate by headword, part of speech, and meaning. Keep identical spellings when their grammatical functions or senses differ.
4. Group targets by a plausible scene and actor-action relationship. Prefer 3 targets when a fourth makes the sentence forced. Default to 9–12 English words, 3–4 targets, one proposition, and at most two actions.
5. Store the exact target surface and stable inventory ID in sentence JSON. Assign every retained entry to one primary sentence.
6. Run `scripts/audit_sentence_coverage.py`. A coverage `PASS` proves traceability only.
7. Complete a diagnostic review and apply accepted revisions. Regroup targets when editing cannot produce learner-worthy English.
8. After the last edit, create fresh blind packets with `scripts/build_blind_review_packet.py` and complete two independent full-dataset reviews:
   - `language`: grammar, idiom, collocation, actor-action logic, and suitability for learner imitation;
   - `meaning_fact`: target part of speech and intended sense, translation relations, logic, facts, and scientific or medical scope.
9. Classify findings as `P0` structural, `P1` substantive error, `P2` learner-material failure, or `P3` optional style. Resolve every `P0`–`P2`. Any accepted edit invalidates both final reviews.
10. Run `scripts/audit_review_completeness.py`, then rerun coverage. Generate the DOCX only after both gates pass.

## Hard Gates

- Every retained entry has `metadata_status=ok` and exactly one primary assignment.
- Sentence constraints pass, or a documented exception explains the learner benefit.
- Risk-linter flags are adjudicated; a flag is never an automatic error verdict.
- Both independent final reviews reference the current sentence checksum and cover the whole dataset.
- No unresolved `P0`, `P1`, or `P2` issue remains.
- Coverage is rerun after the final language edit.
- The DOCX passes archive, text, count, bilingual-alignment, and target-emphasis checks.

`CLEAN PASS` means no blocking issue was found under the required review dimensions. It does not mean that no stylistic alternative exists.

## Resources

- Read [the quality standard](references/quality-standard.md) before composing or revising a dataset.
- Use [the review rubric](references/review-rubric.md) for both independent final passes.
- Consult [the failure library](references/failure-library.md) when calibrating reviewers or deciding whether to regroup.
- Follow [the data schema](references/data-schema.md) for interoperable inventory, sentence, and review artifacts.

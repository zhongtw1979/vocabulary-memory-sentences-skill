# Failure Pattern Library

Use these generalized cases to calibrate reviewers and regression tests. They illustrate reusable patterns, not a private source corpus.

## 1. Ambiguous Infinitive Actor

**Risky:** `The director chose assistants to produce the report.`

The nearest grammatical subject of `to produce` is `assistants`, although the intended producer may be the director. If the intended actor differs, front the purpose or name the actor explicitly.

**Safer:** `To produce the report, the director chose skilled assistants.`

Classification: `P1` when the actor meaning is wrong; `P2` when the ambiguity makes the learner model unreliable.

## 2. Part-of-Speech Drift

Inventory requires `record` as a verb, but the sentence uses `a record` as a noun. Surface coverage passes while the learning objective fails.

**Correction:** revise the sentence so the target performs the required grammatical function, then verify its allowed surface.

Classification: `P1`.

## 3. Path-Relation Mistranslation

English says an object moves `through the tunnel`; Chinese says it moves “over the tunnel.” The nouns match, but the path changes.

**Correction:** compare direction and path words separately from overall topic similarity.

Classification: `P1`.

## 4. Intended-Sense Drift

Inventory teaches an adjective meaning “friendly and comfortable with people,” while the sentence uses the same spelling in a phrase meaning “related to society.” The sentence is grammatical but teaches another sense.

**Correction:** rewrite the context to activate the authoritative sense or keep the spelling as a separate inventory entry with its own sense.

Classification: `P1`.

## 5. Overbroad Scientific Capability

**Risky:** `The device identifies every particle in the sample.`

Absolute scope and unspecified method make the claim stronger than the sentence can support.

**Safer:** `The device detects selected particles under controlled laboratory conditions.`

Classification: `P1`; escalate when the claim is central and cannot be safely qualified.

## 6. Grammatical but Poor Learner Model

A sentence may be parseable while using an uncommon collocation or placing an adjective on an unnatural noun. Reviewers often preserve it because no single grammar rule is broken.

**Correction:** ask whether a learner should memorize and reproduce the phrase. Revise or regroup when the answer is no.

Classification: `P2`.

## 7. Forced Four-Target Group

Four targets share a broad topic but not one believable proposition. Extra actions or implausible roles are added merely to keep all four.

**Correction:** use three targets or regroup across the inventory. Sentence count is subordinate to quality.

Classification: `P2`.

## 8. Optional Style Misclassified as Error

Two expressions are both grammatical, idiomatic, accurate, and suitable for learners. A reviewer prefers one without identifying a concrete defect in the other.

**Correction:** record the alternative as `P3` or leave the sentence unchanged. Excess rewriting can introduce new errors.

Classification: `P3`.

## Calibration Expectations

| Pattern | Expected action |
|---|---|
| Wrong actor, part of speech, sense, translation relation, or fact | `REVISE`, `REGROUP`, or `ESCALATE` |
| Understandable but unsuitable for imitation | `REVISE` or `REGROUP` |
| Correct and natural alternative only | `PASS`, optional `P3` note |

The automated risk linter should flag candidate patterns where practical. Final classification remains a language and fact review decision.

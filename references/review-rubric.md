# Independent Review Rubric

## Independence Contract

Each final reviewer receives the current blind packet, not the generation chat, old wording, previous verdicts, or a diff. Review from the first packet item to the last. Do not treat an earlier pass as evidence.

Use one of four verdicts:

- `PASS`: no blocking issue under this review focus;
- `REVISE`: wording or translation can be repaired without regrouping;
- `REGROUP`: the target combination itself prevents a learner-worthy sentence;
- `ESCALATE`: source metadata or a checkable fact cannot be safely resolved from the artifact.

Only `PASS` is valid in a final clean review record.

## Language-Focused Pass

Mark every field explicitly:

| Field | Pass question |
|---|---|
| `grammar_ok` | Are agreement, articles, number, tense, pronouns, punctuation, and capitalization correct? |
| `collocation_ok` | Are the word combinations ordinary in this meaning and scene? |
| `idiomatic_ok` | Would a proficient speaker naturally express the idea this way? |
| `actor_action_ok` | Is it unambiguous who performs each action and receives each effect? |
| `learner_model_ok` | Is the sentence suitable for a learner to memorize and imitate? |

An understandable but markedly awkward sentence fails `learner_model_ok` and is at least `P2`.

## Meaning-and-Fact Pass

Sentence-level checks:

| Field | Pass question |
|---|---|
| `translation_logic_ok` | Does Chinese preserve actor, object, path, direction, time, contrast, cause, and degree? |
| `fact_scope_ok` | Are common-knowledge, medical, and scientific claims accurate and properly limited? |

For every target:

| Field | Pass question |
|---|---|
| `pos_ok` | Does the target realize `required_pos` in this sentence? |
| `sense_ok` | Does the context express `required_sense_zh`, not another common sense? |
| `surface_ok` | Is the exact surface authorized and grammatically valid? |
| `translation_ok` | Does the Chinese sentence represent this target's actual contextual meaning? |

## Risk-Flag Adjudication

For every applicable risk flag, record:

```json
{
  "sentence_id": "S001",
  "code": "SCIENTIFIC_CAPABILITY",
  "status": "resolved",
  "decision": "revised",
  "reason": "Replaced an absolute capability claim with a limited observation."
}
```

Allowed decisions are `accepted`, `revised`, `regrouped`, and `escalated`. A false-positive flag can be `accepted` only with a specific reason.

## Issue Record

```json
{
  "severity": "P2",
  "category": "collocation",
  "reason": "The combination is possible but unsuitable for learner imitation.",
  "status": "resolved",
  "original_english": "...",
  "revised_english": "...",
  "original_chinese": "...",
  "revised_chinese": "..."
}
```

Use factual reasons. Do not use “sounds better” without identifying the grammar, collocation, logic, sense, translation, or pedagogical problem.

## Common Review Mistakes

| Mistake | Correction |
|---|---|
| Preserving a four-word group at all costs | Drop to three targets or regroup. |
| Accepting a sentence because it is interpretable | Apply the learner-imitation test. |
| Checking only changed sentences | Re-read the entire current dataset. |
| Checking only the English surface | Compare every target with authoritative metadata. |
| Treating a linter flag as an error | Adjudicate it; flags are review prompts. |
| Treating one clean round as proof | Require both independent focuses on the current checksum. |

## Review Completion

A review is complete when every packet sentence appears once, every required field is `true`, every `meaning_fact` target is checked once, every blocking issue is resolved, and the artifact checksum matches the current sentence JSON.

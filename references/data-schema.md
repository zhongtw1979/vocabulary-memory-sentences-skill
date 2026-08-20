# Data Schema

## Inventory CSV

Required columns:

```text
entry_id,entry,meaning,entry_type,required_pos,required_sense_zh,allowed_surfaces,metadata_status,source_file,source_page,book,unit,decision,sentence_id
```

| Field | Contract |
|---|---|
| `entry_id` | Stable, unique identifier. |
| `entry` | Source headword or phrase. |
| `meaning` | Source meaning as recorded. |
| `entry_type` | Source grammatical label, when available. |
| `required_pos` | Part of speech that the target must realize in its sentence. |
| `required_sense_zh` | Chinese sense that the sentence must preserve. |
| `allowed_surfaces` | Pipe-separated inflections or capitalized forms; blank means the source form only. |
| `metadata_status` | `ok`, `conflict`, or `unresolved`. Only `ok` entries may be composed. |
| `source_file` | Source filename without a user-specific absolute path. |
| `source_page` | Physical page or image identifier. |
| `book` | Optional source book or volume. |
| `unit` | Optional source unit. |
| `decision` | `retain` or an explicit exclusion decision. |
| `sentence_id` | Primary sentence assignment for retained entries. |

Save CSV as UTF-8 with a header row. Mark exclusions explicitly; do not silently delete them.

## Sentence JSON

```json
[
  {
    "sentence_id": "S001",
    "scene": "At the research center",
    "english": "The specialist examined the sample and recorded the result carefully.",
    "chinese": "这位专家检查了样本，并认真记录了结果。",
    "targets": [
      {"entry_id": "E0001", "surface": "specialist"},
      {"entry_id": "E0002", "surface": "sample"},
      {"entry_id": "E0003", "surface": "result"}
    ]
  }
]
```

`surface` is the exact form in `english`, including legitimate inflection or capitalization. Target metadata remains authoritative in the inventory.

## Review JSON

```json
{
  "review_id": "language-final",
  "focus": "language",
  "artifact_sha256": "64 lowercase hexadecimal characters",
  "completed_at": "2026-08-20T12:00:00Z",
  "sentences": [
    {
      "sentence_id": "S001",
      "verdict": "PASS",
      "checks": {
        "grammar_ok": true,
        "collocation_ok": true,
        "idiomatic_ok": true,
        "actor_action_ok": true,
        "learner_model_ok": true
      },
      "target_checks": [],
      "issues": []
    }
  ]
}
```

The `meaning_fact` review uses target-level records with `entry_id`, `pos_ok`, `sense_ok`, `surface_ok`, and `translation_ok`. Issues contain `severity`, `category`, `reason`, `status`, and optional proposed English and Chinese revisions.

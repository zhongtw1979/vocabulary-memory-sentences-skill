# Quality Assurance / 质量保障

## Separate claims

| Evidence | What it proves | What it does not prove |
|---|---|---|
| Coverage audit | Every retained ID is mapped once and structural constraints hold | Natural English, correct sense, accurate translation |
| Risk linter | A pattern deserves deliberate review | The sentence is wrong |
| Language review | Grammar, idiom, collocation, actor logic, learner suitability | Target metadata and factual scope alone |
| Meaning/fact review | Part of speech, intended sense, translation, logic, fact scope | That no stylistic alternative exists |
| Review audit | Required reviews cover the current checksum and have no blocking issue | Reviewer expertise beyond recorded evidence |
| DOCX verification | Output structure and content survived generation | Pedagogical outcomes in real classrooms |

## Severity threshold

- `P0`: structural failure; blocks release.
- `P1`: substantive language, meaning, translation, logic, or fact error; blocks release.
- `P2`: unsuitable learner model or forced grouping; blocks release.
- `P3`: optional style where the original is correct and natural; may remain.

The release threshold is zero unresolved `P0`–`P2`.

## Independent-review requirement

Both final reviews use the current artifact checksum. One focuses on language and learner imitation; the other focuses on target metadata, translation, logic, and facts. A reviewer should receive the blind packet rather than old review reports.

Any accepted edit invalidates both final reviews. This rule prevents a sentence corrected for one issue from bypassing the other review dimensions.

## Scientific and medical language

Review absolute quantifiers, claimed capabilities, causes, cures, diagnoses, safety, and measurements. Prefer specific actors, methods, conditions, and limited scope. When a fact is not needed for vocabulary learning, replace it with a modest ordinary proposition. Escalate claims that cannot be responsibly resolved from the artifact.

## Translation alignment

Compare actor, action, object, path, direction, time, contrast, cause, degree, and target sense. Overall topic similarity is insufficient. Words such as `through`, `over`, `before`, `during`, and `despite` deserve explicit relation checks.

## Regression calibration

Use the [failure pattern library](../references/failure-library.md) to distinguish:

- surface coverage from correct part of speech;
- grammatical possibility from learner-worthy collocation;
- translation topic match from relation match;
- a common alternative sense from the assigned learning sense;
- a review flag from an established error.

## 中文要点

机械覆盖、英语自然度、词义与翻译、科学事实、Word结构需要分别提供证据。最终允许存在P3风格建议，不能存在P0—P2问题。两份最终复核必须绑定当前句子校验和；任何修改后都要重新生成盲审包并从头全量复核。

风险扫描器只负责提醒，不能自动替代语言判断。翻译复核应逐项检查人物、动作、对象、路径、时间、因果和程度，不能只看中英文主题是否大致相同。

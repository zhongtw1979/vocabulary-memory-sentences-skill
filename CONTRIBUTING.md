# Contributing

Thank you for improving vocabulary learning materials and their quality controls.

## Before opening a change

1. Read the [quality standard](references/quality-standard.md) and [review rubric](references/review-rubric.md).
2. Keep private vocabulary sources, copyrighted PDFs, personal paths, and generated learner records out of the repository.
3. Open an issue for large behavior or schema changes.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

## Change requirements

- Add a failing test before changing script behavior.
- Generalize regression cases; do not copy a private corpus.
- Keep automated flags advisory. Linguistic errors require review evidence.
- Update English and Chinese entry documentation when commands or user-visible behavior change.
- Regenerate synthetic expected outputs when schemas or reports change.
- Run the complete test suite and synthetic example before requesting review.

## Commit and pull request guidance

Use focused commits with clear messages. In the pull request, explain the problem, observable behavior change, tests, example impact, privacy check, and documentation changes.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Security issues follow [SECURITY.md](SECURITY.md), not public issue discussion.

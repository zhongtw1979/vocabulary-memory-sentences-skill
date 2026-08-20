# Security Policy

## Supported version

Security fixes are provided for the latest tagged release.

## Reporting a vulnerability

Do not open a public issue for credentials, path traversal, unsafe file handling, malicious document behavior, dependency compromise, or accidental private-data exposure.

Use GitHub's private security advisory workflow for this repository. Include affected version, operating system, reproduction steps, expected and observed behavior, and the minimum artifact needed to reproduce the issue. Remove real student names, vocabulary sources, PDFs, credentials, and personal filesystem paths.

The maintainer will acknowledge a complete report when reviewed, assess impact, and coordinate a fix and disclosure. Do not publicly disclose an unresolved report.

## Scope reminder

The scripts process local files supplied by the user. Review source provenance and file permissions before running untrusted artifacts. Generated DOCX files should be opened with current document software and ordinary protected-view practices.

# Security

## Reporting a vulnerability

Do **not** open a public GitHub issue for security-sensitive reports (credentials, PHI leakage, RCE).

Email **translationalML@gmail.com** with:

- Affected component (CLI, Docker image, de-ID integration, etc.)
- Steps to reproduce
- Impact assessment

We aim to acknowledge within a few business days.

## Supported versions

Security fixes are applied on the latest release tag and `master`. Hospital deployments should pin the **Quay image by digest**, not `latest`.

## Automated checks

Pull requests run:

- `pip-audit` on `pip install ".[all]"`
- Bandit on the `pacsifier` package
- Ruff syntax-level checks
- CodeQL (on GitHub)

Local: `pre-commit run --all-files` (includes Gitleaks).

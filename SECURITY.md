# Security

## Reporting a vulnerability

Do **not** open a public GitHub issue for security-sensitive reports (credentials, PHI leakage, RCE).

Use GitHub's private vulnerability reporting:
<https://github.com/TranslationalML/pacsifier/security/advisories/new>

Please include:

- Affected component (CLI, Docker image, de-ID integration, etc.)
- Steps to reproduce
- Impact assessment

We aim to acknowledge within a few business days.

## Supported versions

Security fixes are applied on the latest release tag and `master`. Hospital deployments should pin the **Quay image by digest**, not `latest`.

## Automated checks

Pull requests, a monthly schedule on `master`, and every release (the publish job waits for them), run:

- `pip-audit` on the full installed environment (`pip install ".[all]"`), transitive dependencies included
- Bandit on the `pacsifier` package
- Ruff syntax-level checks
- Trivy on the built Docker image (CRITICAL and HIGH, fixable findings)
- CodeQL (on GitHub)

GitHub Actions are pinned to full commit SHAs; Dependabot proposes updates.

Local: `pre-commit run --all-files` (includes Betterleaks).

# Tooling Reference

**Checked:** 2026-08-19

Tool versions below are volatile and should be rechecked when CI fails or the OS is materially updated.

## GitHub Actions

Official repositories:

- checkout: https://github.com/actions/checkout
- setup-python: https://github.com/actions/setup-python

At the review date both official READMEs use major `v7`. The repo CI therefore uses:

- `actions/checkout@v7`
- `actions/setup-python@v7`
- Python 3.13 explicitly selected

Do not treat these major versions as permanent knowledge; update this file and CI together when upstream changes.

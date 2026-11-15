Plum repository hygiene patch bundle

Target branch: chore/repository-hygiene (create from main)
Base commit reviewed: b313b47af6c58bfbcafcb73ff2be86c8386c2f92

1. Copy LICENSE, .gitignore, pyproject.toml and README.md into the repository root.
2. Copy docs_v0.9.md to docs/v0.9.md.
3. Run cleanup_tracked_artifacts.sh from the repository root.
4. Review the changes, then commit on the feature branch.

Important:
- The GitHub connection currently permits reads but rejects branch creation and writes (HTTP 403).
- The test suite is intentionally not added in this hygiene-only patch. Existing interpreter behavior has correctness issues that should be characterized first; adding guessed tests before validating the current API could create misleading failures.
- The MIT copyright holder is written as "Plum contributors". Replace it with the actual copyright holder/name if you want a named owner.
- package-lock.json is removed because this is a Python project and the checked-in file is an empty npm lockfile.

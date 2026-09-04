# Contributing Guidelines

We welcome contributions to SanjarBot!

## Code Style
- Follow PEP 8 guidelines.
- Use `ruff` for linting and formatting.
- Ensure strict type hints (`mypy` must pass).
- Use `async` everywhere for IO operations.

## Testing
Run the test suite before submitting a PR:
```bash
pytest
```
Coverage should not decrease.

## Commits
Use Conventional Commits formatting:
- `feat: add new command`
- `fix: resolve db deadlock`
- `docs: update API documentation`

Submit PRs against the `main` branch.

# Contributing to MCP Google Suite

We love your input! We want to make contributing to MCP Google Suite as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`
2. Set up your development environment:
   ```bash
   uv venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   uv pip install -e ".[dev]"
   pre-commit install
   ```
3. Make your changes
4. Run tests and ensure code quality:
   ```bash
   pytest
   black .
   ruff check --fix .
   ```
5. Submit a pull request

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the version number in pyproject.toml following [Semantic Versioning](https://semver.org/)
3. Your PR will be merged once you have the sign-off of at least one maintainer

## Any Contributions You Make Will Be Under the MIT License
When you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report Bugs Using GitHub's [Issue Tracker](../../issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](../../issues/new).

## Write Bug Reports With Detail, Background, and Sample Code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its MIT License.

# Contributing to Commandeck

Thank you for your interest in contributing! Here's what you need to know before opening a pull request.

## What we welcome

- Bug fixes
- Improvements to existing free-tier features
- New default buttons (Linux Essentials, Development categories)
- Documentation improvements
- Translations (new languages or corrections)
- Performance and accessibility improvements

## What we won't accept

Commandeck uses an open-core model — Pro features fund ongoing development. Contributions that implement or replicate Pro-only features in the free tier will not be merged. This includes:

- SSH machine management
- Multi-machine button execution
- Config backup / restore
- Button themes (Neon, Retro, etc.)
- Multi-select and group actions

If you're unsure whether your idea overlaps with Pro, open an issue first and ask.

## How to contribute

1. Fork the repository
2. Create a branch: `git checkout -b fix/my-fix`
3. Make your changes
4. Test with `./run_dev.sh`
5. Open a pull request with a clear description

## Code style

- Python 3.10+, follow existing patterns
- PySide6 (Qt6) conventions — `commandeck_core/` stays UI-free (no Qt imports); the UI lives in `commandeck_qt/`
- No new dependencies without prior discussion
- Comments only when the *why* is non-obvious

## Reporting bugs

Open an issue with:
- Your OS (Linux, macOS, or Windows) and version
- Steps to reproduce
- What you expected vs what happened
- Relevant terminal output if any

## License & CLA

The open-source core is licensed under the **GNU AGPLv3** (see [LICENSE](LICENSE)). By submitting a pull request you agree to the [Contributor License Agreement](CLA.md), which lets the project use your contribution in **both** the AGPL core and the proprietary Commandeck Pro build. The `commandeck_core/pro/` directory is proprietary and not open for contributions.

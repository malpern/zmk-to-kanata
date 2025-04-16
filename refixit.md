# Recovery and Refactor Checklist (May 2025)

This checklist outlines the step-by-step plan for restoring a working, testable state to the codebase. Check off each item as you complete it.

- [ ] **Restore Missing Files from Git**
    - [ ] Retrieve `converter/behaviors/hold_tap.py` (and/or `holdtap.py`) from Git history
    - [ ] Retrieve `converter/transformer/sticky_key_transformer.py` from Git history
    - [ ] Retrieve `converter/transformer/key_sequence_transformer.py` from Git history
    - [ ] Review each restored file for compatibility with the current codebase

- [ ] **Resolve Circular Dependencies**
    - [ ] Identify all circular import chains (e.g., involving `Binding`, `KeyMapping`, and behavior modules)
    - [ ] Refactor by moving shared interfaces or base classes to a new module if needed
    - [ ] Use type hints as strings or `if TYPE_CHECKING:` blocks to avoid runtime imports
    - [ ] Minimize cross-module dependencies
    - [ ] Test imports in isolation after each change

- [ ] **Verify and Update All Import Paths**
    - [ ] Search for all import statements referencing the restored files
    - [ ] Update import paths to match actual file names and locations
    - [ ] Run `pytest --collect-only` to check for import errors

- [ ] **Run and Fix the Test Suite**
    - [ ] Run `pytest` after restoring files and fixing imports
    - [ ] Address any test failures (update tests or fix implementation as needed)
    - [ ] Use `pytest -v` and `pytest --maxfail=5` for focused debugging

- [ ] **Document All Changes and Decisions**
    - [ ] Update `IMPLEMENTATION.md` after each major step
    - [ ] Note which files were restored and from which commit
    - [ ] Document significant refactors
    - [ ] Update the progress tracker and audit sections as issues are resolved

- [ ] **Push and Review**
    - [ ] Commit and push all changes to the remote repository
    - [ ] Optionally, open a pull request for peer review

- [ ] **Retrospective and Next Steps**
    - [ ] Add a section to `IMPLEMENTATION.md` or a new `CONTRIBUTING.md` with lessons learned and best practices
    - [ ] Consider adding pre-commit hooks or CI checks for import errors and missing files

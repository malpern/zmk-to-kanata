# Contributing to ZMK to Kanata Converter

Thank you for your interest in contributing! This document provides
guidelines and information for contributors. Please read it fully before
submitting a pull request.

---

## Contributor Workflow Summary

1. **Fork and clone** the repository.
2. **Create a new branch** for your changes.
3. **Install dependencies** and set up your environment.
4. **Write code and tests** (with type hints and docstrings).
5. **Format and lint** your code (`black .` and `ruff check . --fix`).
6. **Run all tests** and ensure coverage is high.
7. **Update documentation** as needed.
8. **Push your branch** and open a pull request (PR).
9. **Respond to review feedback** and iterate as needed.
10. **Celebrate your merged PR!**

---

## Development Setup

1. **Prerequisites**
   - Python 3.11+
   - C preprocessor (cpp)
   - uv package manager (recommended)

2. **Setting Up Development Environment**
   ```bash
   git clone https://github.com/yourusername/zmk-to-kanata.git
   cd zmk-to-kanata
   uv pip install -r requirements.txt
   uv pip install -e .
   ```

3. **Running Tests**
   ```bash
   python -m pytest tests/
   python -m pytest --cov=converter tests/
   ```
   - See [Testing Guide](docs/testing_guide.md) for more details.

---

## Code Style

- Use **Black** for formatting (line length ≤ 79 chars)
- Use **Ruff** for linting
- Add **type hints** to all new code
- Use `@dataclass` for data models (no Pydantic, attrs, etc.)
- Add docstrings to all functions/classes
- See [API Documentation](docs/api_documentation.md) for style examples

---

## Example: Test, Docstring, and PR

**Test Example:**
```python
def test_holdtap_behavior():
    result = convert_zmk_to_kanata("tests/fixtures/holdtap.dts")
    assert "hold-tap" in result
```

**Docstring Example:**
```python
def parse_layer(node: Node) -> Layer:
    """Parse a ZMK layer node into a Layer object.
    Args:
        node: The parsed DTS node.
    Returns:
        Layer: The parsed layer.
    Raises:
        ParseError: If the node is invalid.
    """
    # ...
```

**PR Example:**
- Title: "Add support for sticky keys"
- Description: "Implements sticky key parsing and output. Adds tests for
  sticky key edge cases. Updates user guide."

---

## Pull Request Process

- Ensure all tests pass and code is formatted/linted
- Add/Update tests and documentation for new features
- Keep PRs focused and atomic
- Link to related issues if applicable
- See [CONTRIBUTING.md](CONTRIBUTING.md) and [Testing Guide](docs/testing_guide.md)

---

## Contributor FAQ

**Q: How do I run only one test file?**
A: `python -m pytest tests/test_somefile.py`

**Q: How do I check code style?**
A: Run `black .` and `ruff check . --fix` before committing.

**Q: Where do I add new documentation?**
A: Update `README.md` for user-facing changes, and add details/examples to
`docs/user_guide.md` or `docs/api_documentation.md` as appropriate.

**Q: What if my PR fails CI?**
A: Check the error logs, fix issues, and push again. Ask for help if stuck.

**Q: Who can review my PR?**
A: Any project maintainer. PRs require at least one approval.

---

## More Resources
- [User Guide](docs/user_guide.md)
- [API Documentation](docs/api_documentation.md)
- [Testing Guide](docs/testing_guide.md)
- [Known Limitations](docs/known_limitations.md)

---

By contributing, you agree your work is licensed under the MIT License. 
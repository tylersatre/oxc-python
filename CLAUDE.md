# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

oxc-python provides Python bindings for the [oxc](https://github.com/oxc-project/oxc) JavaScript/TypeScript parser. This is v0.1 in early development - architectural decisions are still being made and patterns are not yet solidified. Think carefully about design choices when implementing new features.

**Core Technology Stack:**
- **Rust + PyO3 0.27**: Bindings with `extension-module` and `abi3-py310` features
- **Maturin 1.x**: Build tool for PyO3 projects
- **oxc 0.97**: The underlying Rust parser
- **Target**: Python 3.10+ (abi3 for wheel compatibility)

**Key Architectural Decisions:**
- AST nodes will be represented as Python **dataclasses** (not dicts or custom classes)
- Parser must support **error recovery** - return partial AST + error list as `(ast, errors)` tuple
- **Comments must be preserved** - both attached to nodes and in a separate list
- Location tracking required: line numbers (1-indexed), column numbers, byte offsets for every node
- Support JavaScript (all ES versions), TypeScript (including decorators, generics, .d.ts), JSX/TSX, and all module systems

## Project Structure

```
oxc-python/
├── src/
│   ├── lib.rs                    # PyO3 module definition (Rust entry point)
│   └── oxc_python/               # Python package
│       ├── __init__.py           # Python API exports
│       └── _version.py           # Version management
├── tests/                        # Python test suite (no Rust tests needed)
├── Cargo.toml                    # Rust dependencies
└── pyproject.toml                # Python package config (maturin build)
```

## Development Commands

**Setup:**
```bash
# Install uv if needed, then sync dependencies
uv sync

# Or install with pip
pip install -e ".[dev]"
```

**Building:**
```bash
# Development build (creates .so in venv)
maturin develop

# Release build
maturin develop --release

# Build wheel
maturin build --release
```

**Testing:**
```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_smoke.py::test_import_oxc_python

# Run with verbose output
pytest -v
```

**Code Quality:**
```bash
# Format and lint Python code
ruff format .
ruff check .

# Auto-fix issues
ruff check --fix .
```

## Architecture Notes

### AST Conversion (Rust → Python)

The core challenge is converting oxc's Rust AST to Python dataclasses via PyO3. Key considerations:

- **Rust enums → Python**: Not yet decided. Options include Union types with Literal discriminators, Python Enum, or tagged dataclasses. Research and choose based on ergonomics and type safety.
- **Memory management**: Decide when to clone vs borrow. Small files (<10KB) are primary workload, so eager conversion is acceptable.
- **Auto-generation vs manual**: Consider whether Python dataclasses should be auto-generated from Rust definitions or manually maintained.

### Error Handling Pattern

Parse errors should NOT raise exceptions. Return tuple: `(ast, errors)` where:
- `ast` is the root AST node (possibly partial if errors occurred)
- `errors` is a list of ParseError objects (empty if no errors)

This allows callers to inspect partial ASTs even when parsing fails.

### API Design Philosophy

The primary parse function signature (to be implemented):
```python
def parse(
    source: str,
    *,
    filename: str = "<unknown>",
    source_type: Literal["module", "script", "auto"] = "auto",
    language: Literal["js", "ts", "jsx", "tsx"] = "js",
    strict_mode: bool | None = None,
    ecmascript_version: int | Literal["latest"] = "latest",
) -> tuple[AST, list[ParseError]]:
    ...
```

Expose essential oxc options but avoid exposing every internal flag. Provide sensible defaults.

### Helper Utilities (v0.1 Scope)

Provide both high-level extraction helpers AND low-level traversal:

**Extraction helpers:**
- `extract_imports()`, `extract_exports()`, `extract_functions()`, `extract_classes()`, `extract_variables()`, `extract_comments()`

**Traversal utilities:**
- `walk()` - iterator for depth-first traversal
- `visit()` - visitor pattern implementation with pre/post-order hooks

### Type Safety

Generate `.pyi` stub files for full type checking support. Every public API should have complete type annotations compatible with mypy and pyright.

## Research Areas for Implementation

When implementing features, research these areas:

1. **PyO3 patterns**: How to efficiently convert Rust structs to Python dataclasses, handling of Rust enums
2. **AST structure**: Survey oxc's internal AST, mapping Rust nodes to Python dataclass hierarchy
3. **Error recovery**: How oxc handles partial parsing, representing error nodes in AST
4. **Comment attachment**: Algorithms for attaching comments to appropriate AST nodes
5. **Similar projects**: Study `tree-sitter-python`, `rustpython-parser` for architectural patterns

## Out of Scope for v0.1

v0.1 is **parser only**. These are explicitly NOT included:
- Linting, formatting, minification
- AST mutation/modification APIs
- Source maps, pretty printing
- Scope analysis, symbol resolution
- Any non-parser oxc features

## Development Notes

- Use `uv` for dependency management (faster than pip)
- After modifying Rust code, run `maturin develop` to rebuild
- Python tests only - no Rust tests needed (testing via Python API is sufficient)
- Keep conversion logic simple and straightforward - performance is important but correctness comes first
- **Remember:** All build/test commands run inside the container via `<command>`

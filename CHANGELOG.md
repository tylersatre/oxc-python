# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-21

### Added

- Initial release of oxc-python parser bindings
- `parse()` function for parsing JavaScript, TypeScript, JSX, and TSX
- Full AST support with dataclass-based node representations
- `ParseResult` object with `program` and `errors` fields
- Error recovery - returns partial AST even when syntax errors occur
- `walk()` function for depth-first AST traversal
- `get_text()` method on all nodes for extracting source code
- `get_line_range()` method on all nodes for line number extraction
- `Allocator` for memory-efficient parsing of multiple files
- Full TypeScript support:
  - Type aliases (`type`)
  - Interfaces
  - Enums
  - Type annotations
  - Generics/type parameters
  - Decorators
- Full JSX/TSX support
- Complete type stubs (`.pyi` files) for IDE type checking
- PEP 561 `py.typed` marker for type checker recognition
- Python 3.10+ support with abi3 wheels
- Comprehensive test suite (447 tests)

### Technical Details

- Built with PyO3 0.27 for Rust ↔ Python bindings
- Uses oxc 0.97 parser (Rust)
- Maturin 1.x for building wheels
- Targets abi3-py310 for broad wheel compatibility
- Devcontainer setup for consistent development environment

[0.1.0]: https://github.com/tylersatre/oxc-python/releases/tag/v0.1.0

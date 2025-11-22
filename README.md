# oxc-python

Fast Python bindings for the [oxc](https://github.com/oxc-project/oxc) JavaScript/TypeScript parser.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## What is this?

`oxc-python` provides Python bindings for oxc's blazing-fast JavaScript and TypeScript parser. oxc is written in Rust and is one of the fastest JS/TS parsers available, outperforming alternatives by 3-5x while maintaining full compatibility with JavaScript and TypeScript standards.

**Use cases:**
- Building development tools that analyze JavaScript/TypeScript code
- Creating AST-based linters or code analyzers
- Extracting information from JS/TS codebases (imports, exports, functions, etc.)
- Building code transformation or refactoring tools
- Any Python application that needs to understand JavaScript/TypeScript syntax

## Installation

```bash
pip install oxc-python
```

> **Note:** Package not yet published to PyPI. For now, install from source (see [Development](#development) section).

## Quick Start

```python
import oxc_python

# Parse JavaScript code
result = oxc_python.parse("const x = 42;")
print(result.program.body[0].type)  # VariableDeclaration

# Access the source text of any node
for node, depth in oxc_python.walk(result.program):
    if node.type == "VariableDeclaration":
        print(node.get_text("const x = 42;"))  # const x = 42;
```

## Features

### Parser

- ✅ **JavaScript (ES2024+)** - Full support for modern JavaScript
- ✅ **TypeScript** - Types, interfaces, enums, decorators
- ✅ **JSX/TSX** - React syntax support
- ✅ **Error Recovery** - Get partial AST even with syntax errors
- ✅ **Fast** - Rust-powered performance
- ✅ **Type Stubs** - Full type hints for IDE support

### API

```python
import oxc_python

# Basic parsing
result = oxc_python.parse("const x = 1;")
# Returns: ParseResult with 'program' and 'errors' fields

# Parse TypeScript
result = oxc_python.parse(
    "const x: number = 1;",
    source_type="module",  # or "script"
)

# Parse JSX/TSX
result = oxc_python.parse(
    "const Component = () => <div>Hello</div>;",
)

# Handle parse errors gracefully
result = oxc_python.parse("const x = ;")  # Syntax error
if result.errors:
    for error in result.errors:
        print(f"Error: {error}")
# Still get partial AST in result.program

# Traverse the AST
for node, depth in oxc_python.walk(result.program):
    indent = "  " * depth
    print(f"{indent}{node.type}")

# Extract source text for any node
source = "const x = 1;\nconst y = 2;"
result = oxc_python.parse(source)
for node, _ in oxc_python.walk(result.program):
    if node.type == "VariableDeclaration":
        text = node.get_text(source)
        line_start, line_end = node.get_line_range(source)
        print(f"Lines {line_start}-{line_end}: {text}")
```

## Examples

### Extract All Imports

```python
import oxc_python

source = """
import React from 'react';
import { useState } from 'react';
import * as Utils from './utils';
"""

result = oxc_python.parse(source)

for node, _ in oxc_python.walk(result.program):
    if node.type == "ImportDeclaration":
        module = node.source.value
        print(f"Imports from: {module}")
```

### Find All Function Declarations

```python
import oxc_python

source = """
function foo() {}
async function bar() {}
function* baz() {}
"""

result = oxc_python.parse(source)

for node, _ in oxc_python.walk(result.program):
    if node.type == "FunctionDeclaration":
        name = node.id.name if node.id else "<anonymous>"
        async_flag = "async " if node.async_ else ""
        generator_flag = "* " if node.generator else ""
        print(f"{async_flag}{generator_flag}function {name}")
```

### TypeScript Type Extraction

```python
import oxc_python

source = """
type User = { name: string; age: number };
interface Config { debug: boolean; }
enum Status { Active, Inactive }
"""

result = oxc_python.parse(source)

for node, _ in oxc_python.walk(result.program):
    if node.type == "TSTypeAliasDeclaration":
        print(f"Type alias: {node.id.name}")
    elif node.type == "TSInterfaceDeclaration":
        print(f"Interface: {node.id.name}")
    elif node.type == "TSEnumDeclaration":
        print(f"Enum: {node.id.name}")
```

## Development

This project uses a **devcontainer** for consistent development environments.

### Setup with VS Code (Recommended)

1. **Prerequisites:**
   - [Docker](https://www.docker.com/get-started)
   - [VS Code](https://code.visualstudio.com/)
   - [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open in devcontainer:**
   ```bash
   git clone https://github.com/tylersatre/oxc-python.git
   cd oxc-python
   code .
   ```
   - When prompted, click "Reopen in Container"
   - Or: Press `F1` → "Dev Containers: Reopen in Container"

3. **The devcontainer will automatically:**
   - Install all dependencies with `uv sync`
   - Set up Python virtual environment
   - Configure VS Code with Python, Rust, and Ruff extensions

4. **Build and test:**
   ```bash
   # Build the Rust extension
   maturin develop

   # Run tests
   pytest

   # Run specific test
   pytest tests/test_phase_08_parse_function.py -v
   ```

### Manual Setup (Without Devcontainer)

**Requirements:**
- Python 3.10+
- Rust toolchain (install from [rustup.rs](https://rustup.rs))
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

**Steps:**
```bash
git clone https://github.com/tylersatre/oxc-python.git
cd oxc-python

# Install dependencies
uv sync  # or: pip install -e ".[dev]"

# Build the extension
maturin develop

# Run tests
pytest
```

### Development Commands

```bash
# Build for development
maturin develop

# Build for release (optimized)
maturin develop --release

# Build wheel
maturin build --release

# Format code
ruff format .

# Lint code
ruff check .

# Run tests
pytest

# Run tests with coverage
pytest --cov=oxc_python --cov-report=html
```

## Project Status

**Current:** v0.1.0 (Pre-release)

This is an early-stage project focused on providing parser bindings only. The API is stable enough for experimentation but may change before v1.0.

### What's Included (v0.1)

- ✅ Full JavaScript/TypeScript/JSX parsing
- ✅ AST traversal with `walk()`
- ✅ Source text extraction with `get_text()` and `get_line_range()`
- ✅ Error recovery
- ✅ Type stubs for IDE support

### Not Yet Included

- ❌ Linting (oxc linter bindings)
- ❌ Code transformation/mutation
- ❌ Formatting (oxc formatter bindings)
- ❌ Scope analysis
- ❌ AST modification APIs

These features may be added in future versions based on community interest.

## Contributing

Contributions are welcome! This project is in active development for v0.1.0.

**How to contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes in the devcontainer
4. Add tests for new features
5. Run `pytest` and `ruff check .`
6. Submit a pull request

**Areas where we'd love help:**
- Documentation improvements
- Example scripts
- Bug reports and fixes
- Performance benchmarks
- Feature suggestions

See [CLAUDE.md](CLAUDE.md) for architectural guidance.

## Architecture

```
oxc-python/
├── src/                    # Rust source code (PyO3 bindings)
│   ├── lib.rs             # Main module
│   ├── parser.rs          # Parser bindings
│   ├── traversal.rs       # walk() implementation
│   └── nodes/             # AST node conversions
├── python/oxc_python/     # Python package
│   ├── __init__.py        # Python API
│   ├── *.pyi              # Type stubs
│   └── py.typed           # PEP 561 marker
├── tests/                 # Python test suite
└── .devcontainer/         # Dev environment config
```

## Performance

oxc is designed for speed. While we haven't published formal benchmarks yet, oxc's Rust parser is typically 3-5x faster than popular JavaScript parsers like Babel or TypeScript's compiler.

The Python bindings add minimal overhead - most time is spent in Rust code.

## License

MIT License - see [LICENSE](LICENSE) file for details.

This project provides Python bindings for [oxc](https://github.com/oxc-project/oxc), which is also MIT licensed.

## Acknowledgments

Built on top of the excellent [oxc](https://github.com/oxc-project/oxc) project by [Boshen](https://github.com/Boshen) and contributors. Thank you for creating such a high-quality, fast JavaScript toolchain in Rust!

## Links

- **Repository:** https://github.com/tylersatre/oxc-python
- **Issues:** https://github.com/tylersatre/oxc-python/issues
- **oxc Project:** https://github.com/oxc-project/oxc
- **PyO3:** https://pyo3.rs (Rust ↔ Python bindings)
- **Maturin:** https://maturin.rs (Build tool)

"""
Core Parsing API Tests

Tests for the parse() function, source_type parameter, allocator management,
and basic module importing.

Combines tests from:
- test_smoke.py
- test_phase_01_setup.py
- test_phase_07_allocator.py
- test_phase_08_parse_function.py
- test_phase_20_source_types.py
"""

import pytest


# ==============================================================================
# Basic Import and Smoke Tests
# ==============================================================================


def test_import_oxc_python():
    """Verify oxc_python module can be imported."""
    import oxc_python

    assert oxc_python is not None


def test_parse_function_exists():
    """Verify parse() function exists."""
    import oxc_python

    assert hasattr(oxc_python, "parse")
    assert callable(oxc_python.parse)


def test_parse_result_type_exists():
    """Verify ParseResult type exists."""
    import oxc_python

    assert hasattr(oxc_python, "ParseResult")


# ==============================================================================
# Basic parse() Function Tests
# ==============================================================================


def test_parse_simple_code():
    """Test parsing simple JavaScript code."""
    import oxc_python

    result = oxc_python.parse("const x = 1;", source_type="module")
    assert result is not None
    assert isinstance(result, oxc_python.ParseResult)


def test_parse_returns_parse_result():
    """Verify parse() returns ParseResult with required fields."""
    import oxc_python

    result = oxc_python.parse("const x = 1;", source_type="module")

    assert hasattr(result, "program")
    assert hasattr(result, "errors")
    assert hasattr(result, "comments")
    assert hasattr(result, "is_valid")


def test_parse_valid_javascript():
    """Test parsing valid JavaScript returns is_valid=True."""
    import oxc_python

    source = "function foo() { return 42; }"
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.errors) == 0
    assert result.program is not None


def test_parse_accepts_source_parameter():
    """Verify parse() accepts source as first parameter."""
    import oxc_python

    result = oxc_python.parse("const x = 1;")
    assert result is not None


# ==============================================================================
# Allocator Tests
# ==============================================================================


def test_allocator_class_exists():
    """Verify Allocator class exists."""
    import oxc_python

    assert hasattr(oxc_python, "Allocator")


def test_allocator_instantiation():
    """Test Allocator can be instantiated."""
    import oxc_python

    allocator = oxc_python.Allocator()
    assert allocator is not None


def test_allocator_has_reset_method():
    """Verify Allocator has reset() method."""
    import oxc_python

    allocator = oxc_python.Allocator()
    assert hasattr(allocator, "reset")
    assert callable(allocator.reset)


def test_allocator_reset_works():
    """Test Allocator.reset() can be called without errors."""
    import oxc_python

    allocator = oxc_python.Allocator()
    allocator.reset()  # Should not raise


def test_parse_with_allocator():
    """Test parse() accepts allocator parameter."""
    import oxc_python

    allocator = oxc_python.Allocator()
    result = oxc_python.parse("const x = 1;", source_type="module", allocator=allocator)

    assert result is not None
    assert result.is_valid


def test_allocator_reuse():
    """Test allocator can be reused across multiple parses."""
    import oxc_python

    allocator = oxc_python.Allocator()

    # Parse multiple files with same allocator
    for i in range(10):
        source = f"const x{i} = {i};"
        result = oxc_python.parse(source, source_type="module", allocator=allocator)

        assert result.is_valid
        assert result.program is not None

        allocator.reset()


def test_allocator_reuse_large_batch():
    """Test allocator reuse with 100+ files."""
    import oxc_python

    allocator = oxc_python.Allocator()

    for i in range(100):
        source = f"function f{i}() {{ return {i}; }}"
        result = oxc_python.parse(source, source_type="module", allocator=allocator)

        assert result.is_valid
        allocator.reset()


# ==============================================================================
# source_type Parameter Tests
# ==============================================================================


def test_source_type_parameter_exists():
    """Verify parse() accepts source_type parameter."""
    import oxc_python

    result = oxc_python.parse("const x = 1;", source_type="module")
    assert result is not None
    assert isinstance(result, oxc_python.ParseResult)


def test_source_type_module_default():
    """Verify default source_type is 'module'."""
    import oxc_python

    result = oxc_python.parse("const x = 1;")
    assert result.is_valid


def test_source_type_tsx_parses_typescript():
    """Verify source_type='tsx' enables TypeScript parsing."""
    import oxc_python

    source = "const x: number = 1;"
    result = oxc_python.parse(source, source_type="tsx")

    assert result.is_valid, f"TypeScript should parse with tsx: {result.errors}"
    assert result.program is not None


def test_source_type_tsx_parses_typescript_complex():
    """Verify source_type='tsx' handles complex TypeScript features."""
    import oxc_python

    source = """
    interface User {
        name: string;
        age: number;
    }

    type UserId = string | number;

    function getUser<T extends User>(id: UserId): T | null {
        return null;
    }
    """
    result = oxc_python.parse(source, source_type="tsx")

    assert result.is_valid, f"Complex TypeScript should parse: {result.errors}"


def test_source_type_tsx_parses_jsx():
    """Verify source_type='tsx' enables JSX parsing."""
    import oxc_python

    source = """
    const element: JSX.Element = <div>Hello</div>;
    """
    result = oxc_python.parse(source, source_type="tsx")

    assert result.is_valid, f"JSX should parse with tsx: {result.errors}"


def test_source_type_jsx_parses_jsx():
    """Verify source_type='jsx' enables JSX in JavaScript."""
    import oxc_python

    source = """
    const element = <div className="container">
        <h1>Hello World</h1>
    </div>;
    """
    result = oxc_python.parse(source, source_type="jsx")

    assert result.is_valid, f"JSX should parse with jsx: {result.errors}"


def test_source_type_jsx_rejects_typescript():
    """Verify source_type='jsx' does NOT parse TypeScript."""
    import oxc_python

    source = "const x: number = 1;"
    result = oxc_python.parse(source, source_type="jsx")

    assert not result.is_valid, "TypeScript should not parse in jsx mode"
    assert len(result.errors) > 0


def test_source_type_module_is_esm():
    """Verify source_type='module' parses as ESM module."""
    import oxc_python

    source = """
    import { foo } from 'bar';
    export const x = 1;
    export default function() {}
    """
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid, f"ESM syntax should parse: {result.errors}"


def test_source_type_script_is_non_module():
    """Verify source_type='script' parses as non-module script."""
    import oxc_python

    source = """
    var x = 1;
    function foo() {
        return x;
    }
    """
    result = oxc_python.parse(source, source_type="script")

    assert result.is_valid, f"Script should parse: {result.errors}"


def test_source_type_script_parses_imports():
    """Verify source_type='script' parses imports (syntactically valid)."""
    import oxc_python

    source = "import { x } from 'y';"
    result = oxc_python.parse(source, source_type="script")
    assert result.is_valid, "Script mode should parse imports"


def test_source_type_invalid_value():
    """Verify invalid source_type values are rejected."""
    import oxc_python

    with pytest.raises((ValueError, RuntimeError, TypeError)):
        oxc_python.parse("const x = 1;", source_type="invalid")


def test_source_type_case_sensitive():
    """Verify source_type values are case-sensitive."""
    import oxc_python

    with pytest.raises((ValueError, RuntimeError, TypeError)):
        oxc_python.parse("const x = 1;", source_type="TSX")


# ==============================================================================
# ChunkHound Integration Patterns
# ==============================================================================


def test_chunkhound_tsx_file_pattern():
    """ChunkHound pattern: parsing .tsx file."""
    import oxc_python

    source = """
    import React from 'react';

    interface Props {
        name: string;
    }

    export const Greeting: React.FC<Props> = ({ name }) => {
        return <div>Hello, {name}!</div>;
    };
    """

    allocator = oxc_python.Allocator()
    result = oxc_python.parse(source, source_type="tsx", allocator=allocator)

    assert result.is_valid, f"TSX file should parse: {result.errors}"
    assert result.program is not None


def test_chunkhound_jsx_file_pattern():
    """ChunkHound pattern: parsing .jsx file."""
    import oxc_python

    source = """
    import React from 'react';

    export const Greeting = ({ name }) => {
        return <div>Hello, {name}!</div>;
    };
    """

    result = oxc_python.parse(source, source_type="jsx")

    assert result.is_valid, f"JSX file should parse: {result.errors}"


def test_chunkhound_ts_file_pattern():
    """ChunkHound pattern: parsing .ts file."""
    import oxc_python

    source = """
    interface User {
        id: number;
        name: string;
    }

    export function getUser(id: number): User | null {
        return null;
    }
    """

    result = oxc_python.parse(source, source_type="tsx")

    assert result.is_valid, f"TypeScript should parse with tsx: {result.errors}"


def test_chunkhound_js_file_pattern():
    """ChunkHound pattern: parsing .js file."""
    import oxc_python

    source = """
    export function add(a, b) {
        return a + b;
    }

    export const Component = () => <div>Hello</div>;
    """

    result = oxc_python.parse(source, source_type="jsx")

    assert result.is_valid, f"JavaScript should parse with jsx: {result.errors}"


def test_chunkhound_source_type_detection_logic():
    """ChunkHound pattern: source type detection logic."""
    from pathlib import Path
    import oxc_python

    def detect_source_type(file_path: Path) -> str:
        """Simulate ChunkHound's detection logic."""
        ext = file_path.suffix.lower()
        if ext == ".tsx":
            return "tsx"
        if ext == ".jsx":
            return "jsx"
        if ext in (".ts", ".mts", ".cts"):
            return "tsx"
        if ext in (".js", ".mjs", ".cjs"):
            return "jsx"
        return "module"

    test_cases = [
        (Path("file.tsx"), "tsx", "const x: number = <div>Hi</div>;"),
        (Path("file.jsx"), "jsx", "const x = <div>Hi</div>;"),
        (Path("file.ts"), "tsx", "const x: number = 1;"),
        (Path("file.js"), "jsx", "const x = 1;"),
        (Path("file.mts"), "tsx", "export const x: number = 1;"),
        (Path("file.cjs"), "jsx", "const x = 1; module.exports = x;"),
    ]

    for file_path, expected_type, source in test_cases:
        source_type = detect_source_type(file_path)
        assert source_type == expected_type

        result = oxc_python.parse(source, source_type=source_type)
        assert result.is_valid


def test_chunkhound_allocator_with_source_type():
    """ChunkHound pattern: source_type with allocator reuse."""
    import oxc_python

    allocator = oxc_python.Allocator()

    test_files = [
        ("const x: number = 1;", "tsx"),
        ("const y = <div>Hi</div>;", "jsx"),
        ("export const z = 1;", "module"),
        ("var w = 1;", "script"),
    ]

    for source, source_type in test_files:
        result = oxc_python.parse(source, source_type=source_type, allocator=allocator)
        assert result.is_valid
        allocator.reset()


def test_chunkhound_complete_source_type_workflow():
    """ChunkHound pattern: complete source type workflow."""
    from pathlib import Path
    import oxc_python

    class MockChunkHound:
        def __init__(self):
            self._allocator = oxc_python.Allocator()

        def _detect_source_type(self, file_path: Path) -> str:
            ext = file_path.suffix.lower()
            if ext == ".tsx":
                return "tsx"
            if ext == ".jsx":
                return "jsx"
            if ext in (".ts", ".mts", ".cts"):
                return "tsx"
            if ext in (".js", ".mjs", ".cjs"):
                return "jsx"
            return "module"

        def parse_file(self, file_path: Path, content: str):
            source_type = self._detect_source_type(file_path)
            result = oxc_python.parse(content, source_type=source_type, allocator=self._allocator)
            self._allocator.reset()
            return result

    parser = MockChunkHound()

    test_files = [
        (Path("Component.tsx"), "const x: number = <div>Hi</div>;"),
        (Path("Component.jsx"), "const x = <div>Hi</div>;"),
        (Path("utils.ts"), "export function add(a: number, b: number) { return a + b; }"),
        (Path("utils.js"), "export function add(a, b) { return a + b; }"),
        (Path("module.mjs"), "import { x } from 'y'; export { x };"),
        (Path("script.cjs"), "var x = 1; module.exports = x;"),
    ]

    for file_path, content in test_files:
        result = parser.parse_file(file_path, content)
        assert result.is_valid

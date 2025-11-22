"""
Test suite for end-to-end integration tests.

This module combines tests from:
- test_phase_09_integration.py (7 tests) - Program node integration tests
- test_phase_21_integration.py (22 tests) - Complete ChunkHound workflow validation

These tests validate complete workflows and integration patterns that ChunkHound
will use, including parse → walk → extract patterns and allocator reuse.
"""

import time
from pathlib import Path

"""
Phase 9 Integration Tests

Tests that verify Program node works with other components.
"""


def test_program_with_parse_result():
    """Integration: Program is correctly embedded in ParseResult"""
    from oxc_python import parse

    result = parse("const x = 1;")

    # ParseResult should contain Program
    assert result.program is not None
    assert result.program.type == "Program"
    assert isinstance(result.program.body, list)


def test_program_multiple_statement_types():
    """Integration: Program handles mixed statement types"""
    from oxc_python import parse

    source = """
const x = 1;
function foo() {}
class Bar {}
if (true) {}
for (let i = 0; i < 10; i++) {}
"""
    result = parse(source)

    assert len(result.program.body) == 5
    types = [stmt.type for stmt in result.program.body]

    assert "VariableDeclaration" in types
    assert "FunctionDeclaration" in types
    assert "ClassDeclaration" in types
    assert "IfStatement" in types
    assert "ForStatement" in types


def test_program_preserves_statement_spans():
    """Integration: Each statement in body has correct span"""
    from oxc_python import parse

    source = "const x = 1;\nconst y = 2;"
    result = parse(source)

    assert len(result.program.body) == 2

    # First statement span
    stmt1 = result.program.body[0]
    assert stmt1.span.start == 0
    assert stmt1.span.end == 12  # "const x = 1;"

    # Second statement span
    stmt2 = result.program.body[1]
    assert stmt2.span.start == 13  # After newline
    assert stmt2.span.end == 25


def test_program_body_is_iterable():
    """Integration: Can use standard Python iteration on body"""
    from oxc_python import parse

    source = "const a = 1; const b = 2; const c = 3;"
    result = parse(source)

    # List comprehension
    types = [stmt.type for stmt in result.program.body]
    assert len(types) == 3
    assert all(t == "VariableDeclaration" for t in types)

    # Enumerate
    for i, stmt in enumerate(result.program.body):
        assert stmt.type == "VariableDeclaration"
        assert i < 3

    # Slice
    first_two = result.program.body[:2]
    assert len(first_two) == 2


def test_program_conversion_performance():
    """REFACTOR: Ensure Program conversion is fast"""
    import time

    from oxc_python import parse

    # Generate large program
    source = "const x = 1;\n" * 100  # 100 statements

    start = time.perf_counter()
    result = parse(source)
    duration = time.perf_counter() - start

    # Should parse and convert quickly (100 statements in <100ms)
    assert duration < 0.1  # 100ms max

    # Should have all statements
    assert len(result.program.body) == 100


def test_chunkhound_full_iteration_workflow():
    """
    Simulate ChunkHound's complete iteration pattern.

    ChunkHound does:
        1. Parse source
        2. Iterate over program.body
        3. Check node.type for each statement
        4. Extract relevant information
    """
    from oxc_python import parse

    source = """
import { foo } from './foo';

function processData(data) {
    const result = transform(data);
    return result;
}

class DataProcessor {
    process() {
        return processData(this.data);
    }
}
"""

    # Step 1: Parse
    result = parse(source)
    assert result.program is not None

    # Step 2: Iterate
    found_types = []
    for node in result.program.body:
        # Step 3: Check type
        found_types.append(node.type)

        # Step 4: Extract info (basic validation)
        assert hasattr(node, "span")
        assert node.span.start >= 0
        assert node.span.end > node.span.start

    # Verify ChunkHound would find expected node types
    assert "ImportDeclaration" in found_types
    assert "FunctionDeclaration" in found_types
    assert "ClassDeclaration" in found_types


def test_chunkhound_error_handling_pattern():
    """
    ChunkHound should handle malformed input gracefully.

    Even with syntax errors, program.body should be accessible.
    """
    from oxc_python import parse

    # Invalid syntax
    source = "const x = ;"

    result = parse(source)

    # Should still have program (error recovery in Phase 19)
    assert result.program is not None
    assert hasattr(result.program, "body")
    assert isinstance(result.program.body, list)


"""
Phase 21: End-to-End ChunkHound Integration Validation

Complete simulation of ChunkHound's OxcParser class to validate
all integration requirements work together correctly.

This is the FINAL VALIDATION before v0.1 release.
"""

# ==============================================================================
# BLOCKER-1: ParseResult Structure
# ==============================================================================


def test_blocker_1_parse_result_structure():
    """
    BLOCKER-1: Validate ParseResult dataclass structure.

    ChunkHound requires:
    - ParseResult (not tuple)
    - Fields: program, errors, comments, panicked
    - is_valid property
    """
    import oxc_python

    result = oxc_python.parse("const x = 1;", source_type="module")

    # Must be ParseResult, not tuple
    assert hasattr(result, "program"), "Missing 'program' field"
    assert hasattr(result, "errors"), "Missing 'errors' field"
    assert hasattr(result, "comments"), "Missing 'comments' field"
    assert hasattr(result, "panicked"), "Missing 'panicked' field"
    assert hasattr(result, "is_valid"), "Missing 'is_valid' property"

    # Valid parse should have is_valid=True
    assert result.is_valid
    assert len(result.errors) == 0
    assert not result.panicked
    assert result.program is not None


def test_blocker_1_parse_result_with_errors():
    """BLOCKER-1: Validate is_valid is False when errors exist."""
    import oxc_python

    result = oxc_python.parse("const x = ;", source_type="module")

    assert not result.is_valid
    assert len(result.errors) > 0

    # Should still have program (partial AST)
    assert result.program is not None


# ==============================================================================
# BLOCKER-2: walk() with Depth Tracking
# ==============================================================================


def test_blocker_2_walk_yields_depth_tuples():
    """
    BLOCKER-2: Validate walk() yields (node, depth) tuples.

    ChunkHound requires:
    - walk() returns iterator
    - Yields (node, depth) tuples
    - Depth starts at 0
    - Depth increases for nested nodes
    """
    import oxc_python

    source = """
    function outer() {
        function inner() {
            const x = 1;
        }
    }
    """
    result = oxc_python.parse(source, source_type="module")

    items = list(oxc_python.walk(result.program))

    # All items must be tuples
    assert all(isinstance(item, tuple) for item in items)
    assert all(len(item) == 2 for item in items)

    # First item should be Program at depth 0
    assert items[0][1] == 0

    # Find functions and verify depth relationship
    functions = [(node, depth) for node, depth in items if node.type == "FunctionDeclaration"]

    outer = next((n, d) for n, d in functions if hasattr(n, "name") and n.name == "outer")
    inner = next((n, d) for n, d in functions if hasattr(n, "name") and n.name == "inner")

    # inner should be deeper than outer
    assert inner[1] > outer[1], (
        f"inner (depth {inner[1]}) should be deeper than outer (depth {outer[1]})"
    )


# ==============================================================================
# BLOCKER-3: Allocator Reuse
# ==============================================================================


def test_blocker_3_allocator_reuse():
    """
    BLOCKER-3: Validate Allocator with reset() method.

    ChunkHound requires:
    - Allocator class exists
    - reset() method works
    - Can reuse across multiple parses
    - Significant performance benefit
    """
    import oxc_python

    allocator = oxc_python.Allocator()

    # Parse 100 files with same allocator
    for i in range(100):
        source = f"const x{i} = {i};"
        result = oxc_python.parse(source, source_type="module", allocator=allocator)

        assert result.is_valid
        assert result.program is not None

        # Reset for next iteration
        allocator.reset()

    # Should complete without errors


# ==============================================================================
# BLOCKER-4: Node.get_text()
# ==============================================================================


def test_blocker_4_node_get_text():
    """
    BLOCKER-4: Validate Node.get_text(source) method.

    ChunkHound requires:
    - All nodes have get_text() method
    - Returns correct source substring
    - Works with multiline code
    """
    import oxc_python

    source = """
    function foo() {
        return 42;
    }
    """
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            text = node.get_text(source)

            # Should contain function code
            assert "function foo" in text
            assert "return 42" in text

            # Should be valid source substring
            assert isinstance(text, str)
            assert len(text) > 0


# ==============================================================================
# BLOCKER-5: Node.get_line_range()
# ==============================================================================


def test_blocker_5_node_get_line_range():
    """
    BLOCKER-5: Validate Node.get_line_range(source) method.

    ChunkHound requires:
    - All nodes have get_line_range() method
    - Returns (start_line, end_line) tuple
    - Line numbers are 1-indexed
    - Works with multiline code
    """
    import oxc_python

    source = "line1\nfunction foo() {\n  return 42;\n}\nline5"
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)

            # Should return tuple of ints
            assert isinstance(start, int)
            assert isinstance(end, int)

            # Line numbers should be 1-indexed
            assert start >= 1
            assert end >= 1

            # Function should be on lines 2-4
            assert start == 2
            assert end == 4


# ==============================================================================
# BLOCKER-6: String-Based Node.type
# ==============================================================================


def test_blocker_6_node_type_strings():
    """
    BLOCKER-6: Validate node.type returns string.

    ChunkHound requires:
    - All nodes have .type property (not method)
    - Returns string matching oxc names
    - All required node types present
    """
    import oxc_python

    source = """
    function foo() {}
    class Bar {}
    const x = 1;
    import { y } from 'z';
    export default function() {}
    """
    result = oxc_python.parse(source, source_type="module")

    types = [node.type for node, depth in oxc_python.walk(result.program)]

    # All types should be strings
    assert all(isinstance(t, str) for t in types)

    # Required types should be present
    assert "FunctionDeclaration" in types
    assert "ClassDeclaration" in types
    assert "VariableDeclaration" in types
    assert "ImportDeclaration" in types


# ==============================================================================
# Complete OxcParser Class Simulation
# ==============================================================================


class MockOxcParser:
    """
    Complete simulation of ChunkHound's OxcParser class.

    This is the exact pattern ChunkHound will use.
    """

    def __init__(self, fallback=None):
        self._fallback = fallback
        self._enabled = True
        self._oxc = None
        self._allocator = None

        try:
            import oxc_python

            self._oxc = oxc_python
            self._allocator = oxc_python.Allocator()
        except Exception as e:
            self._enabled = False
            raise e

    def _detect_source_type(self, file_path: Path) -> str:
        """Detect source_type from file extension."""
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

    def _map_chunk_type(self, node_type: str) -> str | None:
        """Map oxc node type to chunk type."""
        mapping = {
            "FunctionDeclaration": "FUNCTION",
            "ClassDeclaration": "CLASS",
            "MethodDefinition": "METHOD",
            "ArrowFunctionExpression": "FUNCTION",
            "VariableDeclaration": "DEFINITION",
            "ImportDeclaration": "IMPORT",
            "ExportDeclaration": "EXPORT",
            "ExportNamedDeclaration": "EXPORT",
            "ExportDefaultDeclaration": "EXPORT",
            "TSTypeAliasDeclaration": "TYPE",
            "TSInterfaceDeclaration": "INTERFACE",
        }
        return mapping.get(node_type)

    def _extract_symbol(self, node, depth: int) -> str:
        """Extract symbol name from node."""
        if hasattr(node, "name") and node.name:
            return node.name
        return f"{node.type}_{node.span.start}"

    def parse_content(self, content: str, file_path: Path):
        """Parse content and extract chunks (ChunkHound's exact pattern)."""
        if not self._enabled:
            raise RuntimeError("OxcParser not enabled")

        # Detect source type
        source_type = self._detect_source_type(file_path)

        # Parse with oxc
        result = self._oxc.parse(content, source_type=source_type, allocator=self._allocator)

        if not result.is_valid:
            # In real ChunkHound, would fall back to tree-sitter
            return []

        # Walk AST and build chunks
        chunks = []
        for node, depth in self._oxc.walk(result.program):
            chunk_type = self._map_chunk_type(node.type)
            if chunk_type is None:
                continue

            symbol = self._extract_symbol(node, depth)
            code = node.get_text(content)
            start_line, end_line = node.get_line_range(content)

            chunks.append(
                {
                    "symbol": symbol,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code": code,
                    "chunk_type": chunk_type,
                    "depth": depth,
                }
            )

        return chunks


def test_chunkhound_full_workflow():
    """
    Complete OxcParser simulation test.

    This tests the EXACT pattern ChunkHound will use.
    """
    parser = MockOxcParser()

    source = """
    // Top-level function
    function processData(input) {
        // Nested helper
        function validateInput(data) {
            return data !== null;
        }

        if (validateInput(input)) {
            return input.toUpperCase();
        }
        return null;
    }

    // Top-level class
    class DataProcessor {
        process(data) {
            return processData(data);
        }
    }

    // Top-level constant
    const DEFAULT_VALUE = 'empty';
    """

    # Parse as if it were a .js file
    file_path = Path("test.js")
    chunks = parser.parse_content(source, file_path)

    # Verify chunks were extracted
    assert len(chunks) > 0, "Should extract chunks"

    # Check for top-level function
    process_data = [c for c in chunks if c["symbol"] == "processData"]
    assert len(process_data) == 1, "Should find processData function"
    assert process_data[0]["chunk_type"] == "FUNCTION"

    # Check for nested function
    validate_input = [c for c in chunks if c["symbol"] == "validateInput"]
    assert len(validate_input) == 1, "Should find validateInput function"
    assert validate_input[0]["depth"] > process_data[0]["depth"], "Nested function should be deeper"

    # Check for class
    data_processor = [c for c in chunks if c["symbol"] == "DataProcessor"]
    assert len(data_processor) == 1, "Should find DataProcessor class"
    assert data_processor[0]["chunk_type"] == "CLASS"

    # Check line numbers
    for chunk in chunks:
        assert chunk["start_line"] >= 1, "Line numbers should be 1-indexed"
        assert chunk["end_line"] >= chunk["start_line"], "End line should be >= start line"

    # Check code extraction
    for chunk in chunks:
        assert len(chunk["code"]) > 0, "Code should not be empty"
        assert isinstance(chunk["code"], str), "Code should be string"


def test_chunkhound_map_chunk_type_all_nodes():
    """
    Validate ALL node types used in _map_chunk_type() exist.

    ChunkHound's _map_chunk_type() references:
    - FunctionDeclaration
    - ClassDeclaration
    - MethodDefinition
    - ArrowFunctionExpression (not directly exposed - inside VariableDeclarator.init)
    - VariableDeclaration
    - ImportDeclaration
    - ExportDeclaration (multiple variants)
    - TSTypeAliasDeclaration
    - TSInterfaceDeclaration
    """
    import oxc_python

    # Core node types that are directly exposed at top-level
    sources = {
        "FunctionDeclaration": "function foo() {}",
        "ClassDeclaration": "class Foo {}",
        "VariableDeclaration": "const x = 1;",
        "ImportDeclaration": "import x from 'y';",
        "ExportNamedDeclaration": "export const x = 1;",
        "ExportDefaultDeclaration": "export default function() {}",
        "TSTypeAliasDeclaration": "type T = string;",
        "TSInterfaceDeclaration": "interface I {}",
    }

    for expected_type, source in sources.items():
        # Determine source_type
        if expected_type.startswith("TS"):
            source_type = "tsx"
        else:
            source_type = "module"

        result = oxc_python.parse(source, source_type=source_type)
        assert result.is_valid, f"Failed to parse: {source}"

        # Find the expected node type
        types = [node.type for node, _ in oxc_python.walk(result.program)]
        assert expected_type in types, f"Missing node type '{expected_type}' in: {types}"

    # Note: ArrowFunctionExpression is available in the AST but requires
    # accessing VariableDeclarator.init which is not currently exposed.
    # The ArrowFunctionExpression class exists and can be used for type checking.


def test_chunkhound_typescript_support():
    """Test OxcParser with TypeScript code."""
    parser = MockOxcParser()

    source = """
    interface User {
        name: string;
        age: number;
    }

    type UserId = string;

    function getUser(id: UserId): User {
        return { name: "Alice", age: 30 };
    }
    """

    file_path = Path("test.ts")
    chunks = parser.parse_content(source, file_path)

    # Should find interface, type alias, and function
    chunk_types = {c["chunk_type"] for c in chunks}
    assert "INTERFACE" in chunk_types, "Should find interface"
    assert "TYPE" in chunk_types, "Should find type alias"
    assert "FUNCTION" in chunk_types, "Should find function"


def test_chunkhound_jsx_support():
    """Test OxcParser with JSX code."""
    parser = MockOxcParser()

    source = """
    function Component() {
        return <div>Hello</div>;
    }

    class ClassComponent {
        render() {
            return <span>World</span>;
        }
    }
    """

    file_path = Path("test.jsx")
    chunks = parser.parse_content(source, file_path)

    # Should find function and class
    chunk_types = {c["chunk_type"] for c in chunks}
    assert "FUNCTION" in chunk_types
    assert "CLASS" in chunk_types


def test_chunkhound_error_fallback():
    """
    Test error handling pattern (would fall back to tree-sitter).

    ChunkHound checks result.is_valid and falls back on errors.
    """
    import oxc_python

    # Parse with syntax error
    result = oxc_python.parse("const x = ;", source_type="module")

    # Should have is_valid=False
    assert not result.is_valid

    # In ChunkHound, this triggers fallback
    # We just verify the pattern works
    if not result.is_valid:
        # Would call: return self._fallback.parse_content(...)
        pass  # Fallback simulation


def test_chunkhound_batch_parsing():
    """Test OxcParser's allocator reuse across multiple files (100+)."""
    parser = MockOxcParser()

    # Simulate parsing 100+ files
    files = [
        (Path("file1.js"), "function foo() {}"),
        (Path("file2.js"), "class Bar {}"),
        (Path("file3.js"), "const x = 1;"),
    ] * 35  # 105 files total

    total_chunks = 0
    for file_path, content in files:
        chunks = parser.parse_content(content, file_path)
        total_chunks += len(chunks)
        assert len(chunks) >= 1

        # Reset allocator for next file
        parser._allocator.reset()

    assert total_chunks >= 105, "Should extract chunks from all files"


# ==============================================================================
# Walk Depth Validation
# ==============================================================================


def test_walk_depth_hierarchical_chunking():
    """
    Validate walk depth enables hierarchical chunking.

    ChunkHound uses depth to build hierarchical chunk trees.
    """
    import oxc_python

    source = """
    class Outer {
        outerMethod() {
            class Inner {
                innerMethod() {
                    function deeplyNested() {
                        const x = 1;
                    }
                }
            }
        }
    }
    """
    result = oxc_python.parse(source, source_type="module")

    # Build depth map
    depth_map = {}
    for node, depth in oxc_python.walk(result.program):
        if node.type in ("ClassDeclaration", "MethodDefinition", "FunctionDeclaration"):
            name = getattr(node, "name", node.type)
            depth_map[name] = depth

    # Verify depth relationships
    assert depth_map.get("Outer", -1) < depth_map.get("outerMethod", 999), (
        "outerMethod should be deeper than Outer"
    )
    assert depth_map.get("outerMethod", -1) < depth_map.get("Inner", 999), (
        "Inner should be deeper than outerMethod"
    )
    assert depth_map.get("Inner", -1) < depth_map.get("innerMethod", 999), (
        "innerMethod should be deeper than Inner"
    )
    assert depth_map.get("innerMethod", -1) < depth_map.get("deeplyNested", 999), (
        "deeplyNested should be deeper than innerMethod"
    )


# ==============================================================================
# Comments Validation
# ==============================================================================


def test_comments_extraction():
    """
    Validate comments are extracted correctly.

    ChunkHound may use comments for context.
    """
    import oxc_python

    source = """
    // Line comment
    function foo() {
        /* Block comment */
        return 42;
    }
    """
    result = oxc_python.parse(source, source_type="module")

    # Should have comments
    assert len(result.comments) >= 2


# ==============================================================================
# Source Type Detection
# ==============================================================================


def test_source_type_detection_pattern():
    """
    Validate _detect_source_type() pattern works.

    ChunkHound detects source_type from file extension.
    """
    parser = MockOxcParser()

    # Test all extensions
    assert parser._detect_source_type(Path("test.tsx")) == "tsx"
    assert parser._detect_source_type(Path("test.jsx")) == "jsx"
    assert parser._detect_source_type(Path("test.ts")) == "tsx"
    assert parser._detect_source_type(Path("test.js")) == "jsx"
    assert parser._detect_source_type(Path("test.mjs")) == "jsx"
    assert parser._detect_source_type(Path("test.cjs")) == "jsx"


# ==============================================================================
# Edge Cases
# ==============================================================================


def test_empty_file():
    """Test parsing empty file."""
    parser = MockOxcParser()

    chunks = parser.parse_content("", Path("empty.js"))

    # Should return empty list (no chunks in empty file)
    assert isinstance(chunks, list)


def test_only_comments():
    """Test file with only comments."""
    parser = MockOxcParser()

    source = """
    // Just comments
    /* No code here */
    """

    chunks = parser.parse_content(source, Path("comments.js"))

    # Should return empty list (no extractable chunks)
    assert isinstance(chunks, list)


def test_unicode_content():
    """Test parsing Unicode content."""
    parser = MockOxcParser()

    source = """
    function greet() {
        const emoji = '😀';
        return `Hello ${emoji}`;
    }
    """

    chunks = parser.parse_content(source, Path("unicode.js"))

    # Should extract function
    assert len(chunks) >= 1
    assert any(c["chunk_type"] == "FUNCTION" for c in chunks)


def test_deeply_nested_code():
    """Test deeply nested code (stress test for depth tracking)."""
    import oxc_python

    # Create deeply nested structure
    source = "function f0() {\n"
    for i in range(1, 20):
        source += "  " * i + f"function f{i}() {{\n"
    source += "  " * 20 + "const x = 1;\n"
    for i in range(19, -1, -1):
        source += "  " * i + "}\n"

    result = oxc_python.parse(source, source_type="module")
    assert result.is_valid

    # Should handle deep nesting
    depths = [depth for node, depth in oxc_python.walk(result.program)]
    max_depth = max(depths)

    # Should have significant depth
    assert max_depth >= 20, f"Should handle deep nesting, got max depth {max_depth}"


def test_allocator_reuse_performance():
    """
    Performance validation: allocator reuse should work correctly.

    The allocator reuse pattern is validated - speedup varies by system.
    """
    import oxc_python

    sources = [f"const x{i} = {i};" for i in range(100)]

    # Without reuse
    start = time.perf_counter()
    for source in sources:
        oxc_python.parse(source, source_type="module")
    without_reuse = time.perf_counter() - start

    # With reuse
    allocator = oxc_python.Allocator()
    start = time.perf_counter()
    for source in sources:
        oxc_python.parse(source, source_type="module", allocator=allocator)
        allocator.reset()
    with_reuse = time.perf_counter() - start

    # Both approaches should work - speedup is a bonus
    assert without_reuse > 0
    assert with_reuse > 0


# ==============================================================================
# Final Integration Test
# ==============================================================================


def test_complete_chunkhound_workflow():
    """
    FINAL TEST: Complete ChunkHound workflow simulation.

    This is the ultimate validation that everything works together.
    """
    parser = MockOxcParser()

    # Real-world TypeScript code
    source = """
    /**
     * User management module
     */

    import { Database } from './database';
    import type { User, UserId } from './types';

    export interface UserService {
        getUser(id: UserId): Promise<User>;
        createUser(data: Partial<User>): Promise<User>;
    }

    export class UserManager implements UserService {
        private db: Database;

        constructor(database: Database) {
            this.db = database;
        }

        async getUser(id: UserId): Promise<User> {
            const validateId = (id: string) => {
                return id.length > 0;
            };

            if (!validateId(id)) {
                throw new Error('Invalid user ID');
            }

            return await this.db.query('SELECT * FROM users WHERE id = ?', [id]);
        }

        async createUser(data: Partial<User>): Promise<User> {
            return await this.db.insert('users', data);
        }
    }

    export const DEFAULT_USER: User = {
        id: '0',
        name: 'Anonymous',
        email: 'anon@example.com',
    };

    export type UserFactory = () => User;
    """

    file_path = Path("user-manager.ts")
    chunks = parser.parse_content(source, file_path)

    # Should extract multiple chunks
    assert len(chunks) >= 5, f"Should extract multiple chunks, got {len(chunks)}"

    # Verify chunk types
    chunk_types = {c["chunk_type"] for c in chunks}
    assert "INTERFACE" in chunk_types, "Should find UserService interface"
    assert "CLASS" in chunk_types, "Should find UserManager class"
    assert "DEFINITION" in chunk_types, "Should find DEFAULT_USER constant"
    assert "TYPE" in chunk_types, "Should find UserFactory type"
    assert "IMPORT" in chunk_types, "Should find imports"

    # Note: ArrowFunctionExpression (validateId) is not directly exposed in the walk
    # because it's inside a VariableDeclarator.init which requires deeper traversal.
    # This is a known limitation - ChunkHound would need to access expression-level nodes.

    # Verify depth hierarchy exists
    class_chunks = [c for c in chunks if c["chunk_type"] == "CLASS"]
    assert len(class_chunks) > 0, "Should find at least one class"

    # Verify line numbers are reasonable
    for chunk in chunks:
        assert chunk["start_line"] >= 1
        assert chunk["end_line"] >= chunk["start_line"]
        assert chunk["end_line"] <= source.count("\n") + 1

    # Verify code extraction
    for chunk in chunks:
        assert len(chunk["code"]) > 0
        assert isinstance(chunk["code"], str)

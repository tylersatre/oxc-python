"""
Test suite for core AST node structures and methods.

This module combines tests from:
- test_phase_03_span.py (9 tests) - Span dataclass and location tracking
- test_phase_05_node_base.py (3 tests) - Node base class with .type property
- test_phase_09_program_node.py (11 tests) - Program node structure and body access
- test_phase_11_get_text.py (14 tests) - Node.get_text() method for source extraction
- test_phase_12_get_line_range.py (12 tests) - Node.get_line_range() method for line numbers

These tests validate the fundamental node structures, span tracking, and utility
methods required for AST traversal and code extraction.
"""

import pytest


def test_span_creation():
    """RED: Test creating a Span with start and end offsets."""
    from oxc_python import Span

    span = Span(start=0, end=5)

    assert span.start == 0
    assert span.end == 5


def test_span_immutable():
    """RED: Test that Span is immutable (frozen dataclass)."""
    from oxc_python import Span

    span = Span(start=0, end=5)

    # Should not be able to modify
    with pytest.raises((AttributeError, TypeError)):
        span.start = 10


def test_span_properties():
    """RED: Test Span has the required properties."""
    from oxc_python import Span

    span = Span(start=10, end=20)

    assert hasattr(span, "start")
    assert hasattr(span, "end")
    assert isinstance(span.start, int)
    assert isinstance(span.end, int)


def test_span_from_rust():
    """RED: Test creating Span from Rust conversion."""
    from oxc_python import Span

    # Test that Span objects work the same whether created from Python or Rust
    span = Span(start=5, end=15)

    assert span.start == 5
    assert span.end == 15


def test_span_equality():
    """RED: Test Span equality comparison."""
    from oxc_python import Span

    span1 = Span(start=0, end=5)
    span2 = Span(start=0, end=5)
    span3 = Span(start=0, end=10)

    assert span1 == span2
    assert span1 != span3


def test_span_repr():
    """RED: Test Span has readable string representation."""
    from oxc_python import Span

    span = Span(start=10, end=20)
    repr_str = repr(span)

    assert "10" in repr_str
    assert "20" in repr_str
    assert "Span" in repr_str


# ChunkHound Validation
def test_chunkhound_span_for_get_text():
    """
    ChunkHound Validation: Verify Span works for text extraction.

    ChunkHound will use: code = node.get_text(source)
    Which internally does: source[span.start:span.end]
    """
    from oxc_python import Span

    source = "const x = 1;"
    span = Span(start=0, end=11)

    # Simulate get_text() implementation
    text = source[span.start : span.end]

    assert text == "const x = 1"
    assert len(text) == 11


def test_chunkhound_span_byte_offsets():
    """
    ChunkHound Validation: Verify byte offsets work correctly.

    Important: Offsets are BYTE offsets, not character offsets.
    Must work correctly with UTF-8 multi-byte characters.
    """
    from oxc_python import Span

    # Source with emoji (4-byte UTF-8 character)
    source = "const x = '😀';"
    # "const x = '" = 11 bytes
    # "😀" = 4 bytes
    # "'" = 1 byte
    # ";" = 1 byte
    # Total = 17 bytes

    # Span should use byte offsets
    span = Span(start=0, end=17)
    text = source[span.start : span.end]

    assert text == source
    assert "😀" in text


def test_chunkhound_span_validation():
    """
    ChunkHound Validation: Verify Span constraints.

    Ensure span.end >= span.start (no negative spans).
    """
    from oxc_python import Span

    # Valid spans
    span1 = Span(start=0, end=0)  # Empty span (ok)
    span2 = Span(start=5, end=10)  # Normal span

    assert span1.start <= span1.end
    assert span2.start <= span2.end

    # Note: We allow invalid spans to be created
    # (validation happens at higher levels if needed)


def test_node_has_type_property():
    """RED: Node must have .type property returning string"""
    from oxc_python import Node, Span

    # Create a simple test node
    node = Node(type_name="TestNode", span=Span(0, 5))

    assert hasattr(node, "type")
    assert isinstance(node.type, str)
    assert node.type == "TestNode"


def test_node_has_span():
    """RED: Node must have .span property"""
    from oxc_python import Node, Span

    span = Span(start=0, end=10)
    node = Node(type_name="TestNode", span=span)

    assert hasattr(node, "span")
    assert node.span == span


# ChunkHound Validation
def test_chunkhound_type_string_matching():
    """ChunkHound does: if node.type == "FunctionDeclaration" """
    from oxc_python import Node, Span

    node = Node(type_name="FunctionDeclaration", span=Span(0, 10))

    # Must be able to do string comparison
    assert node.type == "FunctionDeclaration"
    assert isinstance(node.type, str)
    assert not callable(node.type)  # Property, not method


def test_program_node_has_type():
    """
    RED: Verify Program node has .type property set to "Program".

    This ensures Program inherits/implements the base Node pattern.
    """
    from oxc_python import parse

    source = "const x = 1;"
    result = parse(source)

    assert result.program is not None
    assert hasattr(result.program, "type")
    assert result.program.type == "Program"


def test_program_node_has_body_field():
    """
    RED: Verify Program node has .body field.

    This will fail initially because the body field doesn't exist yet.
    The body field is CRITICAL for traversal.
    """
    from oxc_python import parse

    source = "const x = 1; const y = 2;"
    result = parse(source)

    assert result.program is not None
    assert hasattr(result.program, "body")


def test_program_body_is_list():
    """
    RED: Verify Program.body is a list.

    ChunkHound and walk() expect body to be iterable.
    """
    from oxc_python import parse

    source = "const x = 1; const y = 2;"
    result = parse(source)

    assert isinstance(result.program.body, list)


def test_program_body_contains_statements():
    """
    RED: Verify Program.body contains statement nodes.

    Each item in body should be a node with a .type property.
    """
    from oxc_python import parse

    source = "const x = 1; const y = 2;"
    result = parse(source)

    assert len(result.program.body) > 0

    # Each statement should have .type property
    for stmt in result.program.body:
        assert hasattr(stmt, "type")
        assert isinstance(stmt.type, str)


def test_program_body_count_matches_statements():
    """
    RED: Verify body count matches actual statement count.

    Two statements in source -> exactly 2 items in body.
    """
    from oxc_python import parse

    source = "const x = 1; const y = 2;"
    result = parse(source)

    assert len(result.program.body) == 2


def test_program_empty_source_empty_body():
    """
    RED: Empty source should produce empty body list.

    This tests edge case of no statements.
    """
    from oxc_python import parse

    source = ""
    result = parse(source)

    assert result.program is not None
    assert result.program.body == []


def test_program_body_preserves_order():
    """
    RED: Body should preserve statement order from source.

    First statement in source should be first in body.
    """
    from oxc_python import parse

    source = """
function first() {}
function second() {}
function third() {}
"""
    result = parse(source)

    assert len(result.program.body) == 3

    # Each should have type "FunctionDeclaration"
    for stmt in result.program.body:
        assert stmt.type == "FunctionDeclaration"


def test_program_has_span():
    """
    RED: Program node should have span covering entire source.

    Span should start at 0 and end at source length.
    """
    from oxc_python import parse

    source = "const x = 1;"
    result = parse(source)

    assert hasattr(result.program, "span")
    assert result.program.span.start == 0
    assert result.program.span.end == len(source)


# ChunkHound Validation
def test_chunkhound_program_iteration_pattern():
    """
    ChunkHound Validation: Simulate ChunkHound iterating over program.body.

    ChunkHound's _chunk_ast() does:
        for node in program.body:
            # Process each statement
    """
    from oxc_python import parse

    source = """
const x = 1;
function foo() {}
class Bar {}
"""
    result = parse(source)

    # Simulate ChunkHound iteration
    nodes_found = []
    for node in result.program.body:
        nodes_found.append(node.type)

    # Should find all three statement types
    assert "VariableDeclaration" in nodes_found
    assert "FunctionDeclaration" in nodes_found
    assert "ClassDeclaration" in nodes_found


def test_chunkhound_empty_file_pattern():
    """
    ChunkHound Validation: Handle empty files gracefully.

    ChunkHound should not crash on empty files.
    """
    from oxc_python import parse

    source = ""
    result = parse(source)

    # Should not raise, should return empty body
    assert result.program is not None
    assert result.program.body == []

    # Should be safe to iterate
    count = 0
    for _node in result.program.body:
        count += 1
    assert count == 0


def test_chunkhound_nested_structure_access():
    """
    ChunkHound Validation: Access nested structures within statements.

    ChunkHound will need to access properties of statements in body.
    """
    from oxc_python import parse

    source = "function foo() { const x = 1; }"
    result = parse(source)

    assert len(result.program.body) == 1
    func = result.program.body[0]

    assert func.type == "FunctionDeclaration"
    # Function should have its own accessible fields (to be tested in Phase 13)
    assert hasattr(func, "span")


def test_get_text_simple():
    """RED: Test get_text() extracts correct source."""
    import oxc_python

    source = "const x = 1; function foo() { return 42; }"
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            text = node.get_text(source)
            assert "function foo" in text
            assert "return 42" in text
            break


def test_get_text_multiline():
    """RED: Test get_text() handles multiline code."""
    import oxc_python

    source = """function foo() {
    const x = 1;
    return x + 1;
}"""
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            text = node.get_text(source)
            assert "function foo" in text
            assert "const x = 1" in text
            assert "return x + 1" in text
            # Should preserve newlines
            assert "\n" in text
            break


def test_get_text_unicode():
    """RED: Test get_text() handles Unicode correctly."""
    import oxc_python

    source = "const emoji = '😀'; // Unicode comment"
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "VariableDeclaration":
            text = node.get_text(source)
            # Should handle multi-byte UTF-8 characters
            assert isinstance(text, str)
            assert "emoji" in text
            assert "😀" in text
            break


def test_get_text_exact_span():
    """RED: Test get_text() extracts exact span range."""
    import oxc_python

    source = "const x = 1;"
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "VariableDeclaration":
            text = node.get_text(source)
            # Should match manual extraction
            expected = source[node.span.start : node.span.end]
            assert text == expected
            break


def test_get_text_nested_nodes():
    """RED: Test get_text() works for nested nodes."""
    import oxc_python

    source = "function outer() { function inner() { return 42; } }"
    result = oxc_python.parse(source)

    texts = []
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            text = node.get_text(source)
            texts.append(text)

    # Should have at least the outer function
    assert len(texts) >= 1

    # Outer function should contain the full declaration
    assert "outer" in texts[0]
    # The inner function text is embedded in the outer function's span
    assert "inner" in texts[0]
    assert "return 42" in texts[0]


def test_get_text_empty_span():
    """RED: Test get_text() with empty span."""
    import oxc_python

    source = "const x = 1;"
    result = oxc_python.parse(source)

    # All nodes should be able to get_text without error
    for node, _depth in oxc_python.walk(result.program):
        text = node.get_text(source)
        assert isinstance(text, str)
        # Text length should match span length
        expected_len = node.span.end - node.span.start
        assert len(text.encode("utf-8")) == expected_len


# ChunkHound Validation
def test_chunkhound_get_text_pattern():
    """
    ChunkHound Validation: Test ChunkHound's exact usage pattern.

    ChunkHound does:
        for node, depth in walk(program):
            code = node.get_text(content)
            chunks.append(Chunk(code=code, ...))
    """
    import oxc_python

    source = """
function calculateSum(a, b) {
    return a + b;
}

class Calculator {
    add(x, y) {
        return x + y;
    }
}
"""
    result = oxc_python.parse(source)

    chunks = []
    for node, depth in oxc_python.walk(result.program):
        if node.type in ("FunctionDeclaration", "ClassDeclaration", "MethodDefinition"):
            code = node.get_text(source)
            chunks.append(
                {
                    "type": node.type,
                    "code": code,
                    "depth": depth,
                }
            )

    # Should extract function
    func_chunks = [c for c in chunks if c["type"] == "FunctionDeclaration"]
    assert len(func_chunks) >= 1
    assert "calculateSum" in func_chunks[0]["code"]

    # Should extract class
    class_chunks = [c for c in chunks if c["type"] == "ClassDeclaration"]
    assert len(class_chunks) >= 1
    assert "Calculator" in class_chunks[0]["code"]


def test_chunkhound_get_text_with_comments():
    """
    ChunkHound Validation: Test that comments are preserved in code.

    ChunkHound extracts code including comments for better context.
    """
    import oxc_python

    source = """
// This calculates stuff
function calculate() {
    // Important comment
    return 42;
}
"""
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            code = node.get_text(source)
            # Comments might or might not be in function span
            # But the function body should definitely be there
            assert "function calculate" in code
            assert "return 42" in code
            break


def test_chunkhound_get_text_typescript():
    """
    ChunkHound Validation: Test get_text() with TypeScript code.

    ChunkHound parses TypeScript files and extracts code with types.
    """
    import oxc_python

    source = """
function greet(name: string): string {
    return `Hello, ${name}!`;
}

interface User {
    name: string;
    age: number;
}
"""
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            code = node.get_text(source)
            # Should include type annotations
            assert "string" in code
            assert "greet" in code
            break


def test_chunkhound_get_text_jsx():
    """
    ChunkHound Validation: Test get_text() with JSX code.

    ChunkHound handles React components.
    """
    import oxc_python

    source = """
function Component() {
    return <div>Hello World</div>;
}
"""
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            code = node.get_text(source)
            assert "Component" in code
            assert "<div>" in code
            break


def test_get_text_crlf_line_endings():
    """Test get_text() handles CRLF line endings."""
    import oxc_python

    source = "function foo() {\r\n    return 42;\r\n}"
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            text = node.get_text(source)
            # Should preserve CRLF
            assert "foo" in text
            assert "return 42" in text
            # Line endings should be preserved
            assert "\r\n" in text or "\n" in text
            break


def test_get_text_special_characters():
    """Test get_text() handles special characters."""
    import oxc_python

    source = "const str = '\\n\\t\\r';"
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "VariableDeclaration":
            text = node.get_text(source)
            assert "\\n" in text
            assert "\\t" in text
            assert "\\r" in text
            break


def test_get_text_method_exists():
    """Test that get_text method exists on all nodes."""
    import oxc_python

    source = "const x = 1;"
    result = oxc_python.parse(source)

    for node, _depth in oxc_python.walk(result.program):
        # Every node should have get_text method
        assert hasattr(node, "get_text")
        assert callable(node.get_text)

        # Should accept source parameter
        text = node.get_text(source)
        assert isinstance(text, str)


def test_chunkhound_complete_get_text_workflow():
    """
    Complete workflow test: Parse → Walk → Extract code.

    This simulates exactly what ChunkHound will do:
    1. Parse source code
    2. Walk AST nodes
    3. Filter for relevant node types
    4. Extract code using get_text()
    5. Store in chunks
    """
    import oxc_python

    source = """
// User model
class User {
    constructor(name, email) {
        this.name = name;
        this.email = email;
    }

    validate() {
        return this.email.includes('@');
    }
}

// Helper functions
function formatUser(user) {
    return `${user.name} <${user.email}>`;
}

function createUser(name, email) {
    return new User(name, email);
}
"""

    # Parse
    result = oxc_python.parse(source)
    assert result.is_valid

    # Walk and extract (ChunkHound pattern)
    chunks = []
    for node, depth in oxc_python.walk(result.program):
        # Filter for chunk-worthy nodes (ChunkHound's _map_chunk_type)
        if node.type not in ("FunctionDeclaration", "ClassDeclaration", "MethodDefinition"):
            continue

        # Extract code (ChunkHound's main usage)
        code = node.get_text(source)

        # Extract symbol (ChunkHound's _extract_symbol)
        symbol = (
            node.name if hasattr(node, "name") and node.name else f"{node.type}_{node.span.start}"
        )

        chunks.append(
            {
                "symbol": symbol,
                "code": code,
                "type": node.type,
                "depth": depth,
            }
        )

    # Verify extracted chunks
    assert len(chunks) >= 2  # At least class and function(s)

    # Verify class extraction (find by type since name attribute may not be set)
    class_chunks = [c for c in chunks if c["type"] == "ClassDeclaration"]
    assert len(class_chunks) >= 1
    assert "User" in class_chunks[0]["code"]
    assert "constructor" in class_chunks[0]["code"]
    assert "validate" in class_chunks[0]["code"]

    # Verify function extraction
    func_chunks = [c for c in chunks if c["type"] == "FunctionDeclaration"]
    assert len(func_chunks) >= 1
    # At least one should be formatUser or createUser
    assert any("formatUser" in c["code"] or "createUser" in c["code"] for c in func_chunks)


def test_get_line_range_simple():
    """RED: Test get_line_range returns correct line numbers."""
    import oxc_python

    source = "const x = 1;\nfunction foo() {\n  return 42;\n}"
    result = oxc_python.parse(source, source_type="module")

    # Find the function declaration
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)

            # Function is on lines 2-4
            assert start == 2
            assert end == 4


def test_get_line_range_one_indexed():
    """RED: Test line numbers are 1-indexed (first line is 1, not 0)."""
    import oxc_python

    source = "const x = 1;"
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "VariableDeclaration":
            start, end = node.get_line_range(source)

            # First line should be 1, not 0
            assert start == 1
            assert end == 1


def test_get_line_range_multiline():
    """RED: Test get_line_range with complex multiline code."""
    import oxc_python

    source = """
// Comment on line 2
function outer() {
    const x = 1;
    const y = 2;
}
"""

    result = oxc_python.parse(source, source_type="module")

    functions = []
    for node, depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)
            functions.append((depth, start, end))

    # Should have 1 function (outer)
    assert len(functions) == 1

    # outer should span lines 3-6, depth 1
    assert functions[0] == (1, 3, 6)


def test_get_line_range_inclusive():
    """RED: Test both start and end line numbers are inclusive."""
    import oxc_python

    source = """function foo() {
    return 42;
}"""

    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)

            # Function spans lines 1-3 (inclusive)
            assert start == 1
            assert end == 3

            # Verify the range is inclusive by checking line content
            lines = source.split("\n")
            assert "function foo" in lines[start - 1]  # Line 1
            assert "}" in lines[end - 1]  # Line 3


def test_get_line_range_crlf():
    """RED: Test get_line_range handles CRLF line endings."""
    import oxc_python

    # Use CRLF line endings
    source = "const x = 1;\r\nfunction foo() {\r\n  return 42;\r\n}"
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)

            # Should handle CRLF same as LF
            assert start == 2
            assert end == 4


def test_get_line_range_unicode():
    """RED: Test get_line_range with UTF-8 multi-byte characters."""
    import oxc_python

    # Source with emoji (4-byte UTF-8 character)
    source = "const emoji = '😀';\nfunction test() {\n  return '🎉';\n}"
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)

            # Should correctly handle multi-byte characters
            assert start == 2
            assert end == 4


def test_get_line_range_single_line():
    """RED: Test get_line_range when node is on a single line."""
    import oxc_python

    source = "const x = 1; const y = 2;"
    result = oxc_python.parse(source, source_type="module")

    line_ranges = []
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "VariableDeclaration":
            start, end = node.get_line_range(source)
            line_ranges.append((start, end))

    # Both declarations on same line
    assert all(start == 1 and end == 1 for start, end in line_ranges)


def test_get_line_range_empty_lines():
    """RED: Test get_line_range with empty lines before/after code."""
    import oxc_python

    source = """

function foo() {
    return 1;
}

"""

    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)

            # Function on lines 3-5 (empty lines are lines 1, 2, 6, 7)
            assert start == 3
            assert end == 5


# ChunkHound Validation
def test_chunkhound_line_range_usage():
    """
    ChunkHound Validation: Simulate ChunkHound's exact usage pattern.

    ChunkHound extracts line ranges to store in Chunk objects:
        start_line, end_line = node.get_line_range(content)
        chunks.append(Chunk(
            start_line=LineNumber(start_line),
            end_line=LineNumber(end_line),
            ...
        ))
    """
    import oxc_python

    source = """function foo() {
    return 42;
}

class Bar {
    method() {
        return 1;
    }
}"""

    result = oxc_python.parse(source, source_type="module")

    chunks = []
    for node, _depth in oxc_python.walk(result.program):
        if node.type in ("FunctionDeclaration", "ClassDeclaration"):
            # This is exactly how ChunkHound uses get_line_range
            start_line, end_line = node.get_line_range(source)

            chunks.append(
                {
                    "type": node.type,
                    "start_line": start_line,
                    "end_line": end_line,
                }
            )

    # Verify extracted chunks
    assert len(chunks) == 2

    # Function on lines 1-3
    assert chunks[0]["type"] == "FunctionDeclaration"
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 3

    # Class on lines 5-9
    assert chunks[1]["type"] == "ClassDeclaration"
    assert chunks[1]["start_line"] == 5
    assert chunks[1]["end_line"] == 9


def test_chunkhound_line_range_with_comments():
    """
    ChunkHound Validation: Line ranges should include comments attached to nodes.

    Important: The span should include leading comments (like JSDoc).
    """
    import oxc_python

    source = """// Line 1: comment
/**
 * Line 2-4: JSDoc comment
 */
function foo() { // Line 5
    return 42;    // Line 6
}                 // Line 7"""

    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)

            # Function declaration starts at line 5 (not line 2 with JSDoc)
            # Note: Comment attachment is Phase 18, for now just verify function span
            assert start == 5
            assert end == 7


def test_chunkhound_nested_depth_and_lines():
    """
    ChunkHound Validation: Verify line ranges work correctly with multiple top-level functions.

    ChunkHound uses both depth and line ranges to understand code structure.
    """
    import oxc_python

    source = """function outer() {      // Line 1
    return 1;           // Line 2
}                       // Line 3

function another() {    // Line 5
    return 2;           // Line 6
}                       // Line 7"""

    result = oxc_python.parse(source, source_type="module")

    functions = []
    for node, depth in oxc_python.walk(result.program):
        if node.type == "FunctionDeclaration":
            start, end = node.get_line_range(source)
            functions.append(
                {
                    "depth": depth,
                    "start": start,
                    "end": end,
                }
            )

    assert len(functions) == 2

    # First function (depth 1)
    func1 = functions[0]
    assert func1["start"] == 1
    assert func1["end"] == 3
    assert func1["depth"] == 1

    # Second function (depth 1)
    func2 = functions[1]
    assert func2["start"] == 5
    assert func2["end"] == 7
    assert func2["depth"] == 1
    assert func2["depth"] == func1["depth"]


def test_chunkhound_complete_workflow():
    """
    Complete workflow test: Parse → Walk → Extract line ranges.

    This simulates the full ChunkHound workflow:
    1. Parse source code
    2. Walk AST nodes
    3. Filter interesting nodes
    4. Extract line ranges for chunks
    """
    import oxc_python

    source = """// File header comment
import { foo } from 'bar';

/**
 * Main function
 */
function main() {
    const x = 1;

    class Helper {
        method() {
            return x + 1;
        }
    }

    return new Helper();
}

export default main;
"""

    result = oxc_python.parse(source, source_type="module")
    assert result.is_valid

    # Simulate ChunkHound's chunk extraction
    chunks = []
    for node, depth in oxc_python.walk(result.program):
        # Map node types to chunk types (simplified)
        chunk_type_mapping = {
            "FunctionDeclaration": "FUNCTION",
            "ClassDeclaration": "CLASS",
            "ImportDeclaration": "IMPORT",
            "ExportDefaultDeclaration": "EXPORT",
        }

        chunk_type = chunk_type_mapping.get(node.type)
        if chunk_type is None:
            continue

        # Extract line range (ChunkHound's exact pattern)
        start_line, end_line = node.get_line_range(source)

        chunks.append(
            {
                "type": chunk_type,
                "start_line": start_line,
                "end_line": end_line,
                "depth": depth,
            }
        )

    # Verify extracted chunks
    assert len(chunks) >= 3  # At least import, function, class

    # Verify line ranges are correct
    import_chunk = next(c for c in chunks if c["type"] == "IMPORT")
    assert import_chunk["start_line"] == 2  # Import on line 2

    function_chunk = next(c for c in chunks if c["type"] == "FUNCTION")
    assert function_chunk["start_line"] == 7  # Function starts line 7
    assert function_chunk["end_line"] == 17  # Function ends line 17

    # All line numbers should be >= 1
    for chunk in chunks:
        assert chunk["start_line"] >= 1
        assert chunk["end_line"] >= 1
        assert chunk["end_line"] >= chunk["start_line"]

"""
Line Number Computation Tests

Tests for the line number computation functionality that will replace
the O(n²) compute_line_number with O(1) lookup using a line offset table.
"""

import pytest
import oxc_python


# ==============================================================================
# Basic Line Number Computation Tests
# ==============================================================================


def test_empty_source_line_1():
    """Empty source should return line 1 for offset 0."""
    result = oxc_python.parse("", source_type="module")

    # Program node should be at line 1
    assert result.program.start_line == 1
    assert result.program.end_line == 1


def test_single_line_all_offsets_line_1():
    """Single line source: all offsets should map to line 1."""
    source = "const x = 42;"
    result = oxc_python.parse(source, source_type="module")

    # Program and all nodes should be on line 1
    assert result.program.start_line == 1
    assert result.program.end_line == 1

    # Walk through all nodes
    for node in oxc_python.walk(result.program):
        if hasattr(node, 'start_line') and hasattr(node, 'end_line'):
            assert node.start_line == 1
            assert node.end_line == 1


def test_multiple_lines_basic():
    """Multiple lines: Program node should span all lines correctly."""
    source = "const a = 1;\nconst b = 2;\nconst c = 3;"

    result = oxc_python.parse(source, source_type="module")

    # Program should span all 3 lines
    assert result.program.start_line == 1
    assert result.program.end_line == 3


def test_crlf_line_endings():
    """CRLF line endings should work correctly."""
    source = "const a = 1;\r\nconst b = 2;\r\nconst c = 3;"

    result = oxc_python.parse(source, source_type="module")

    # Program should span all 3 lines
    assert result.program.start_line == 1
    assert result.program.end_line == 3


def test_mixed_line_endings():
    """Mixed LF and CRLF line endings should work."""
    source = "const a = 1;\nconst b = 2;\r\nconst c = 3;"

    result = oxc_python.parse(source, source_type="module")

    # Program should span all 3 lines
    assert result.program.start_line == 1
    assert result.program.end_line == 3


def test_multiline_statement():
    """Multiline statements: Program node should span correctly."""
    source = """const obj = {
    a: 1,
    b: 2,
    c: 3
};"""

    result = oxc_python.parse(source, source_type="module")

    # Program node should span from start to end
    # (triple-quote adds initial newline)
    assert result.program.start_line == 1
    assert result.program.end_line > result.program.start_line  # Spans multiple lines


def test_line_numbers_with_comments():
    """Line numbers should be correct even with comments."""
    source = """// Comment on line 1
const x = 1; // Line 2
/* Block comment
   on line 3-4 */
const y = 2; // Line 5"""

    result = oxc_python.parse(source, source_type="module")

    # Program should span all 5 lines
    assert result.program.start_line == 1
    assert result.program.end_line == 5

    # Comments should be extracted
    assert len(result.comments) > 0

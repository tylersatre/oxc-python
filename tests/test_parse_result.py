"""
ParseResult Structure Tests

Tests for the ParseResult dataclass returned by parse().

Combines tests from:
- test_phase_04_parse_result.py
"""


def test_parse_result_dataclass_fields():
    """Verify ParseResult has all required fields."""
    import oxc_python

    result = oxc_python.parse("const x = 1;", source_type="module")

    # Required fields
    assert hasattr(result, "program"), "ParseResult must have 'program' field"
    assert hasattr(result, "errors"), "ParseResult must have 'errors' field"
    assert hasattr(result, "comments"), "ParseResult must have 'comments' field"
    assert hasattr(result, "panicked"), "ParseResult must have 'panicked' field"

    # is_valid property
    assert hasattr(result, "is_valid"), "ParseResult must have 'is_valid' property"


def test_parse_result_is_valid_property():
    """Verify is_valid property works correctly."""
    import oxc_python

    # Valid code
    valid_result = oxc_python.parse("const x = 1;", source_type="module")
    assert valid_result.is_valid is True
    assert len(valid_result.errors) == 0

    # Invalid code
    invalid_result = oxc_python.parse("const x = ;", source_type="module")
    assert invalid_result.is_valid is False
    assert len(invalid_result.errors) > 0


def test_parse_result_not_tuple():
    """Verify parse() returns ParseResult, not tuple."""
    import oxc_python

    result = oxc_python.parse("const x = 1;", source_type="module")

    # Must be ParseResult with fields, not tuple
    assert not isinstance(result, tuple)
    assert hasattr(result, "program")
    assert hasattr(result, "errors")

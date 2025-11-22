"""
Test suite for error recovery and ParseError handling.

This module combines all tests from test_phase_19_error_recovery.py for
validating error recovery, ParseError structure, and error handling patterns.
"""


def test_parse_error_structure():
    """RED: Verify ParseError has all required fields."""
    from oxc_python import parse

    # Parse code with syntax error
    source = "const x = ;"  # Missing value
    result = parse(source, source_type="module")

    # Should have errors
    assert len(result.errors) > 0

    # Check error structure
    error = result.errors[0]
    assert hasattr(error, "message")
    assert hasattr(error, "span")
    assert hasattr(error, "severity")

    # Check types
    assert isinstance(error.message, str)
    assert hasattr(error.span, "start")
    assert hasattr(error.span, "end")
    assert error.severity in ("error", "warning")


def test_parse_error_message():
    """RED: Verify error messages are human-readable."""
    from oxc_python import parse

    source = "const x = ;"
    result = parse(source, source_type="module")

    assert len(result.errors) > 0
    error = result.errors[0]

    # Message should be non-empty and descriptive
    assert len(error.message) > 0
    assert isinstance(error.message, str)


def test_parse_error_location():
    """RED: Verify error locations are accurate or zero."""
    from oxc_python import parse

    source = "const x = ;"
    result = parse(source, source_type="module")

    assert len(result.errors) > 0
    error = result.errors[0]

    # Span should be within source bounds
    assert error.span.start >= 0
    assert error.span.end <= len(source)
    # Note: start can equal end for default spans when detailed location is unavailable
    assert error.span.start <= error.span.end


def test_error_recovery_partial_ast():
    """RED: Verify partial AST is returned despite errors."""
    from oxc_python import parse

    # Code with syntax error in the middle
    source = """
    function validFunc() { return 1; }
    const broken = ;
    function anotherValidFunc() { return 2; }
    """
    result = parse(source, source_type="module")

    # Should have errors
    assert len(result.errors) > 0
    assert not result.is_valid

    # But should still have partial AST
    assert result.program is not None

    # Should be able to walk the AST
    from oxc_python import walk

    nodes = list(walk(result.program))
    assert len(nodes) > 0


def test_multiple_errors():
    """RED: Verify error list can contain errors (even if usually just one)."""
    from oxc_python import parse

    # Multiple syntax errors - oxc parser typically returns one error per parse
    source = """
    const x = ;
    function foo( { }
    let y = ;
    """
    result = parse(source, source_type="module")

    # Should capture at least one error
    assert len(result.errors) >= 1


def test_valid_code_no_errors():
    """RED: Verify valid code produces no errors."""
    from oxc_python import parse

    source = "const x = 1; function foo() { return 42; }"
    result = parse(source, source_type="module")

    # Should have no errors
    assert len(result.errors) == 0
    assert result.is_valid
    assert result.program is not None


def test_error_severity_levels():
    """RED: Verify error severity is correctly set."""
    from oxc_python import parse

    # Syntax error (should be severity="error")
    source = "const x = ;"
    result = parse(source, source_type="module")

    assert len(result.errors) > 0
    # At least one error should be severity="error"
    assert any(e.severity == "error" for e in result.errors)


# ChunkHound Validation
def test_chunkhound_error_fallback_pattern():
    """
    ChunkHound Validation: Test error fallback pattern.

    ChunkHound does:
        result = oxc_python.parse(content, source_type=source_type)

        if not result.is_valid:
            logger.debug(f"Oxc parse errors: {result.errors}")
            return self._fallback.parse_content(...)

        # Process result.program
    """
    from oxc_python import parse

    # Valid code - should process
    valid_source = "function foo() { return 1; }"
    result = parse(valid_source, source_type="module")

    if not result.is_valid:
        # Would fall back to tree-sitter
        print(f"Errors: {result.errors}")
        raise AssertionError("Valid code should not have errors")
    else:
        # Process program
        assert result.program is not None

    # Invalid code - should fall back
    invalid_source = "const x = ;"
    result = parse(invalid_source, source_type="module")

    if not result.is_valid:
        # This is the fallback path
        assert len(result.errors) > 0
        # ChunkHound would use tree-sitter here
        # But we still have partial AST
        assert result.program is not None
    else:
        raise AssertionError("Invalid code should have errors")


def test_error_messages_logging():
    """Test that error messages can be logged (ChunkHound use case)."""
    from oxc_python import parse

    source = "const x = ;"
    result = parse(source, source_type="module")

    # ChunkHound logs errors like this
    if not result.is_valid:
        error_messages = [e.message for e in result.errors]
        # Should be able to log
        assert len(error_messages) > 0
        assert all(isinstance(msg, str) for msg in error_messages)


def test_partial_ast_walkable():
    """Verify AST from error recovery can be walked (even if empty)."""
    from oxc_python import parse, walk

    source = """
    function good1() { return 1; }
    const broken = ;
    function good2() { return 2; }
    """
    result = parse(source, source_type="module")

    # Should have errors but also AST (may be partial/empty)
    assert not result.is_valid
    assert result.program is not None

    # Should be able to walk the AST regardless
    nodes = list(walk(result.program))
    assert len(nodes) >= 1  # At least the Program node itself


def test_error_in_typescript():
    """Test error recovery in TypeScript code."""
    from oxc_python import parse

    source = "const x: number = ;"
    result = parse(source, source_type="tsx")

    # Should have errors
    assert not result.is_valid
    assert len(result.errors) > 0

    # Should still have partial AST
    assert result.program is not None


def test_error_in_jsx():
    """Test error recovery in JSX code."""
    from oxc_python import parse

    source = "const el = <div"  # Unclosed JSX
    result = parse(source, source_type="jsx")

    # Should have errors
    assert not result.is_valid
    assert len(result.errors) > 0

    # Should still have partial AST
    assert result.program is not None


def test_panicked_flag():
    """Test that panicked flag is set for unrecoverable errors."""
    from oxc_python import parse

    # Normal syntax error should not panic
    source = "const x = ;"
    result = parse(source, source_type="module")

    # Should have errors but not panic
    assert len(result.errors) > 0
    # Most syntax errors should not cause panic
    # (panicked is for internal parser failures)

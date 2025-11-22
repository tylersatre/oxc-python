"""
Test suite for comment extraction and parsing.

This module combines all tests from test_phase_18_comments.py for
validating comment extraction, cleaning, and accessibility.
"""


def test_extract_line_comments():
    """RED: Test line comment extraction."""
    import oxc_python

    source = """// Line comment 1
const x = 1; // Line comment 2"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 2

    # First comment
    assert result.comments[0].text == " Line comment 1"
    assert result.comments[0].is_block is False
    assert "//" not in result.comments[0].text

    # Second comment
    assert result.comments[1].text == " Line comment 2"
    assert result.comments[1].is_block is False
    assert "//" not in result.comments[1].text


def test_extract_block_comments():
    """RED: Test block comment extraction."""
    import oxc_python

    source = """/* Block comment 1 */
const x = 1; /* Block comment 2 */"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 2

    # First comment
    assert result.comments[0].text == " Block comment 1 "
    assert result.comments[0].is_block is True
    assert "/*" not in result.comments[0].text
    assert "*/" not in result.comments[0].text

    # Second comment
    assert result.comments[1].text == " Block comment 2 "
    assert result.comments[1].is_block is True


def test_extract_jsdoc_comments():
    """RED: Test JSDoc comment extraction."""
    import oxc_python

    source = """/**
 * JSDoc comment
 * @param x - The parameter
 */
function foo(x) {
    return x;
}"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) >= 1

    # JSDoc comment (is still a block comment)
    jsdoc = result.comments[0]
    assert jsdoc.is_block is True
    assert "*" in jsdoc.text  # Interior * preserved
    assert "JSDoc comment" in jsdoc.text
    assert "@param" in jsdoc.text
    assert "/**" not in jsdoc.text  # Delimiter stripped
    assert "*/" not in jsdoc.text  # Delimiter stripped


def test_multiline_block_comments():
    """RED: Test multiline block comment extraction."""
    import oxc_python

    source = """/*
 * Line 1
 * Line 2
 * Line 3
 */
const x = 1;"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 1

    comment = result.comments[0]
    assert comment.is_block is True
    # Should preserve interior newlines and asterisks
    assert "\n" in comment.text
    assert "Line 1" in comment.text
    assert "Line 2" in comment.text
    assert "Line 3" in comment.text
    # Should not have delimiters
    assert not comment.text.startswith("/*")
    assert not comment.text.endswith("*/")


def test_comment_span_accuracy():
    """RED: Test comment span locations are accurate."""
    import oxc_python

    source = "// Comment\nconst x = 1;"
    result = oxc_python.parse(source, source_type="module")

    assert len(result.comments) == 1
    comment = result.comments[0]

    # Span should be valid
    assert hasattr(comment, "span")
    assert comment.span.start >= 0
    assert comment.span.end <= len(source)
    assert comment.span.start < comment.span.end

    # Span should cover the comment in source (including delimiters)
    comment_source = source[comment.span.start : comment.span.end]
    assert "//" in comment_source
    assert "Comment" in comment_source


def test_empty_comments():
    """RED: Test empty comment handling."""
    import oxc_python

    source = "// \n/* */"
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 2

    # Empty line comment
    assert result.comments[0].text == " "
    assert result.comments[0].is_block is False

    # Empty block comment
    assert result.comments[1].text == " "
    assert result.comments[1].is_block is True


def test_no_comments():
    """RED: Test code with no comments."""
    import oxc_python

    source = "const x = 1; function foo() { return 42; }"
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 0
    assert result.comments == []


def test_mixed_comments():
    """RED: Test mix of line and block comments."""
    import oxc_python

    source = """// Line 1
/* Block 1 */
const x = 1; // Line 2
/* Block 2 */ const y = 2;"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 4

    # Verify types
    types = [c.is_block for c in result.comments]
    assert types.count(False) == 2  # Two line comments
    assert types.count(True) == 2  # Two block comments

    # Verify all cleaned
    for comment in result.comments:
        assert "//" not in comment.text
        assert "/*" not in comment.text
        assert "*/" not in comment.text


def test_comments_with_special_chars():
    """RED: Test comments containing special characters."""
    import oxc_python

    source = """// Comment with émojis 😀 and ñ
/* Block with 中文 and עברית */"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 2

    # Unicode should be preserved
    assert "😀" in result.comments[0].text
    assert "ñ" in result.comments[0].text
    assert "中文" in result.comments[1].text
    assert "עברית" in result.comments[1].text


def test_comment_in_string_not_extracted():
    """RED: Test that comments in strings are not extracted as comments."""
    import oxc_python

    source = 'const str = "// not a comment"'
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    # Should have zero comments (the // is inside a string)
    assert len(result.comments) == 0


def test_comment_order_preserved():
    """RED: Test comments are in source order."""
    import oxc_python

    source = """// First
/* Second */
// Third"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 3

    # Verify order by checking spans
    assert result.comments[0].span.start < result.comments[1].span.start
    assert result.comments[1].span.start < result.comments[2].span.start

    # Verify content matches order
    assert "First" in result.comments[0].text
    assert "Second" in result.comments[1].text
    assert "Third" in result.comments[2].text


# ChunkHound Validation
def test_chunkhound_comment_access():
    """
    ChunkHound Validation: Test accessing comments from ParseResult.

    ChunkHound needs access to ParseResult.comments for context.
    """
    import oxc_python

    source = """
// User authentication module
function authenticate(username, password) {
    // Validate credentials
    return checkCredentials(username, password);
}
"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert hasattr(result, "comments")
    assert isinstance(result.comments, list)

    # Should have comments
    assert len(result.comments) >= 2

    # Verify comments are cleaned
    for comment in result.comments:
        assert hasattr(comment, "text")
        assert hasattr(comment, "span")
        assert hasattr(comment, "is_block")
        assert "//" not in comment.text
        assert "/*" not in comment.text
        assert "*/" not in comment.text


def test_chunkhound_typescript_comments():
    """
    ChunkHound Validation: Test comments in TypeScript code.

    ChunkHound parses TypeScript files.
    """
    import oxc_python

    source = """
// Type definitions
interface User {
    name: string; // User's full name
    age: number;  /* Age in years */
}

/**
 * Creates a new user
 * @param name - The user's name
 * @param age - The user's age
 */
function createUser(name: string, age: number): User {
    return { name, age };
}
"""
    result = oxc_python.parse(source, source_type="tsx")

    assert result.is_valid
    assert len(result.comments) >= 4

    # Verify JSDoc comment
    jsdoc_comments = [c for c in result.comments if "@param" in c.text]
    assert len(jsdoc_comments) >= 1


def test_chunkhound_jsx_comments():
    """
    ChunkHound Validation: Test comments in JSX code.

    ChunkHound handles React components.
    """
    import oxc_python

    source = """
// Component definition
function Component() {
    /* Render logic */
    return <div>Hello</div>;
}
"""
    result = oxc_python.parse(source, source_type="jsx")

    assert result.is_valid
    assert len(result.comments) >= 2

    # Verify both comment types
    line_comments = [c for c in result.comments if not c.is_block]
    block_comments = [c for c in result.comments if c.is_block]
    assert len(line_comments) >= 1
    assert len(block_comments) >= 1


def test_comment_text_stripping_edge_cases():
    """Test edge cases in comment text stripping."""
    import oxc_python

    # Various edge cases
    test_cases = [
        ("//", ""),  # Just delimiter
        ("//x", "x"),  # No space
        ("//  ", "  "),  # Just spaces
        ("/**/", ""),  # Empty block
        ("/*x*/", "x"),  # No space in block
        ("/* */", " "),  # Just space
    ]

    for source, expected_text in test_cases:
        result = oxc_python.parse(source, source_type="module")
        if len(result.comments) > 0:
            assert result.comments[0].text == expected_text


def test_comment_structures():
    """Test Comment dataclass structure."""
    import oxc_python

    source = "// Test"
    result = oxc_python.parse(source, source_type="module")

    assert len(result.comments) == 1
    comment = result.comments[0]

    # Verify structure
    assert hasattr(comment, "text")
    assert hasattr(comment, "span")
    assert hasattr(comment, "is_block")

    # Verify types
    assert isinstance(comment.text, str)
    assert isinstance(comment.is_block, bool)
    assert hasattr(comment.span, "start")
    assert hasattr(comment.span, "end")


def test_comment_with_code_like_content():
    """Test comments containing code-like content."""
    import oxc_python

    source = """
// const x = 1;
/* function foo() { return 42; } */
const y = 2;
"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 2

    # Comments should contain the code-like text
    assert "const x = 1;" in result.comments[0].text
    assert "function foo()" in result.comments[1].text


def test_crlf_in_comments():
    """Test comments with CRLF line endings."""
    import oxc_python

    source = "// Comment 1\r\n/* Block\r\ncomment */\r\nconst x = 1;"
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) >= 2

    # Block comment should preserve internal CRLF
    block_comments = [c for c in result.comments if c.is_block]
    if block_comments:
        # Should have newline (might be \r\n or \n)
        assert "\n" in block_comments[0].text or "\r" in block_comments[0].text


def test_comment_at_eof():
    """Test comment at end of file."""
    import oxc_python

    source = "const x = 1;\n// EOF comment"
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) >= 1

    # Last comment should be the EOF comment
    last_comment = result.comments[-1]
    assert "EOF comment" in last_comment.text


def test_nested_comment_delimiters():
    """Test comment containing other comment delimiters."""
    import oxc_python

    source = """
// This has /* in it
/* This has // in it */
"""
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid
    assert len(result.comments) == 2

    # Verify interior delimiters are preserved
    assert "/*" in result.comments[0].text  # Interior /* preserved
    assert "//" in result.comments[1].text  # Interior // preserved

    # But outer delimiters should be stripped
    assert not result.comments[0].text.startswith("//")
    assert not result.comments[1].text.startswith("/*")
    assert not result.comments[1].text.endswith("*/")


def test_chunkhound_comment_integration():
    """
    ChunkHound Integration: Complete workflow with comments.

    This tests the exact pattern ChunkHound will use:
    1. Parse source code
    2. Access ParseResult.comments
    3. Use comments for context
    """
    import oxc_python

    source = """
// Configuration module
/**
 * Application configuration
 * @const {Object}
 */
const config = {
    // API endpoint
    apiUrl: 'https://api.example.com',

    /* Database settings */
    db: {
        host: 'localhost',  // DB host
        port: 5432          /* DB port */
    }
};

/**
 * Initialize the application
 * @returns {Promise<void>}
 */
async function initialize() {
    // Connect to database
    await db.connect();

    /*
     * Load configuration
     * This is important
     */
    await loadConfig();
}
"""

    # Parse (ChunkHound pattern)
    result = oxc_python.parse(source, source_type="module")

    # Verify ParseResult has comments
    assert hasattr(result, "comments")
    assert isinstance(result.comments, list)
    assert len(result.comments) >= 7  # Multiple comments in source

    # Verify comment structure
    for comment in result.comments:
        assert hasattr(comment, "text")
        assert hasattr(comment, "span")
        assert hasattr(comment, "is_block")

        # Verify text is cleaned
        assert "//" not in comment.text
        assert not comment.text.startswith("/*")
        assert not comment.text.endswith("*/")

    # Verify both types present
    line_comments = [c for c in result.comments if not c.is_block]
    block_comments = [c for c in result.comments if c.is_block]
    assert len(line_comments) >= 3
    assert len(block_comments) >= 4

    # Verify JSDoc comments
    jsdoc_comments = [c for c in result.comments if "@" in c.text]
    assert len(jsdoc_comments) >= 2

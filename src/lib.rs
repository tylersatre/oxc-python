//! oxc-python: Python bindings for the oxc JavaScript/TypeScript parser
//!
//! This module provides Python bindings for oxc, a high-performance JavaScript/TypeScript parser
//! written in Rust. It exposes a simple API for parsing JS/TS code and working with ASTs.
//!
//! # Architecture
//!
//! The implementation is organized into several modules:
//! - `core`: Core types (Program, Node, Span, Allocator, Comment, ParseError, ParseResult)
//! - `parser`: Parsing functions and comment extraction
//! - `traversal`: AST traversal utilities (walk iterator)
//! - `nodes`: AST node types (statements, expressions, JSX, TypeScript)
//! - `conversion`: Conversion functions from oxc AST to Python objects
//!
//! # Example
//!
//! ```python
//! import oxc_python
//!
//! source = "const x = 42;"
//! result = oxc_python.parse(source)
//! print(result.program)
//! ```

use pyo3::prelude::*;

// Module declarations
mod core;
mod parser;
mod traversal;
mod nodes;
mod conversion;

// =============================================================================
// Public re-exports: Core Types
// =============================================================================

pub use core::{
    Allocator,
    Comment,
    Node,
    ParseError,
    ParseResult,
    Program,
    Span,
};

// =============================================================================
// Public re-exports: Parser Functions
// =============================================================================

pub use parser::{
    parse,
    extract_comments,
};

// =============================================================================
// Public re-exports: Traversal
// =============================================================================

pub use traversal::{
    walk,
    WalkIterator,
};

// =============================================================================
// Public re-exports: Statement Node Types
// =============================================================================

pub use nodes::statements::{
    BlockStatement,
    BreakStatement,
    CatchClause,
    ClassBody,
    ClassDeclaration,
    ContinueStatement,
    DebuggerStatement,
    DoWhileStatement,
    EmptyStatement,
    ExpressionStatement,
    ForInStatement,
    ForOfStatement,
    ForStatement,
    FormalParameter,
    FunctionDeclaration,
    IfStatement,
    LabeledStatement,
    MethodDefinition,
    ReturnStatement,
    SwitchCase,
    SwitchStatement,
    ThrowStatement,
    TryStatement,
    VariableDeclaration,
    VariableDeclarator,
    WhileStatement,
    WithStatement,
};

// =============================================================================
// Public re-exports: Expression Node Types
// =============================================================================

pub use nodes::expressions::{
    ArrayExpression,
    ArrowFunctionExpression,
    BinaryExpression,
    CallExpression,
    ConditionalExpression,
    Identifier,
    Literal,
    MemberExpression,
    ObjectExpression,
    UnaryExpression,
};

// =============================================================================
// Public re-exports: Import/Export Node Types
// =============================================================================

pub use nodes::statements::{
    ExportAllDeclaration,
    ExportDefaultDeclaration,
    ExportNamedDeclaration,
    ExportSpecifier,
    ImportDeclaration,
    ImportDefaultSpecifier,
    ImportNamespaceSpecifier,
    ImportSpecifier,
};

// =============================================================================
// Public re-exports: TypeScript Node Types
// =============================================================================

pub use nodes::typescript::{
    TSEnumDeclaration,
    TSEnumMember,
    TSInterfaceBody,
    TSInterfaceDeclaration,
    TSIntersectionType,
    TSMethodSignature,
    TSPropertySignature,
    TSTypeAliasDeclaration,
    TSTypeAnnotation,
    TSTypeParameter,
    TSTypeParameterDeclaration,
    TSTypeReference,
    TSUnionType,
};

// =============================================================================
// Public re-exports: JSX Node Types
// =============================================================================

pub use nodes::jsx::{
    JSXAttribute,
    JSXClosingElement,
    JSXElement,
    JSXExpressionContainer,
    JSXFragment,
    JSXIdentifier,
    JSXMemberExpression,
    JSXOpeningElement,
    JSXSpreadAttribute,
    JSXText,
};

// =============================================================================
// Public re-exports: Conversion Functions
// =============================================================================

pub use conversion::{
    convert_statement,
    convert_expression,
    convert_import_specifier,
    convert_export_specifier,
    convert_binding_identifier,
    convert_literal,
    convert_identifier_name,
    convert_jsx_name,
    convert_jsx_member_expression,
    convert_jsx_attribute,
    convert_jsx_spread_attribute,
    convert_jsx_opening_element,
    convert_jsx_closing_element,
    convert_jsx_text,
    convert_jsx_expression_container,
    convert_jsx_child,
    convert_jsx_element,
    convert_jsx_fragment,
    convert_function_body,
    convert_class_body,
    convert_ts_type,
    convert_ts_type_annotation,
    convert_ts_type_parameter_declaration,
    convert_ts_type_parameter,
    convert_ts_type_parameter_instantiation,
    convert_ts_interface_body,
    convert_ts_signature,
    convert_ts_property_key,
    convert_ts_interface_heritage,
    convert_ts_enum_member,
    convert_for_statement_init,
    convert_for_statement_left,
    convert_switch_case,
    convert_catch_clause,
    convert_block_statement,
    convert_errors,
    compute_line_number,
};

// =============================================================================
// PyO3 Module Registration
// =============================================================================

/// Python module definition for oxc_python
#[pymodule]
fn oxc_python(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add version from Cargo.toml
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    // Add module docstring
    m.add("__doc__", "Python bindings for the oxc JavaScript/TypeScript parser")?;

    // Phase 3: Span & Location Structures
    m.add_class::<Span>()?;

    // Phase 18: Comment Extraction
    m.add_class::<Comment>()?;

    // Phase 19: Error Recovery & ParseError Structure
    m.add_class::<ParseError>()?;

    // Phase 4: ParseResult Structure
    m.add_class::<ParseResult>()?;

    // Phase 5: Node Base Class
    m.add_class::<Node>()?;

    // Phase 7: Allocator & Memory Management
    m.add_class::<Allocator>()?;

    // Phase 8: parse() Function
    m.add_function(wrap_pyfunction!(parse, m)?)?;

    // Phase 9: Program Node
    m.add_class::<Program>()?;

    // Phase 10: Walk Iterator
    m.add_class::<WalkIterator>()?;
    m.add_function(wrap_pyfunction!(walk, m)?)?;

    // Phase 13: Specialized Statement Node Types
    m.add_class::<FunctionDeclaration>()?;
    m.add_class::<MethodDefinition>()?;
    m.add_class::<ClassBody>()?;
    m.add_class::<ClassDeclaration>()?;
    m.add_class::<VariableDeclaration>()?;
    m.add_class::<VariableDeclarator>()?;
    m.add_class::<FormalParameter>()?;
    m.add_class::<BlockStatement>()?;
    m.add_class::<BreakStatement>()?;
    m.add_class::<ContinueStatement>()?;
    m.add_class::<LabeledStatement>()?;
    m.add_class::<EmptyStatement>()?;
    m.add_class::<WithStatement>()?;
    m.add_class::<ForStatement>()?;
    m.add_class::<IfStatement>()?;
    m.add_class::<ExpressionStatement>()?;
    m.add_class::<WhileStatement>()?;
    m.add_class::<DoWhileStatement>()?;
    m.add_class::<ForInStatement>()?;
    m.add_class::<ForOfStatement>()?;
    m.add_class::<SwitchStatement>()?;
    m.add_class::<SwitchCase>()?;
    m.add_class::<TryStatement>()?;
    m.add_class::<CatchClause>()?;
    m.add_class::<ThrowStatement>()?;
    m.add_class::<ReturnStatement>()?;
    m.add_class::<DebuggerStatement>()?;

    // Phase 14: Expression Node Types
    m.add_class::<ArrowFunctionExpression>()?;
    m.add_class::<CallExpression>()?;
    m.add_class::<MemberExpression>()?;
    m.add_class::<BinaryExpression>()?;
    m.add_class::<UnaryExpression>()?;
    m.add_class::<ConditionalExpression>()?;
    m.add_class::<ObjectExpression>()?;
    m.add_class::<ArrayExpression>()?;
    m.add_class::<Identifier>()?;
    m.add_class::<Literal>()?;

    // Phase 15: Import/Export Declaration Node Types
    m.add_class::<ImportDeclaration>()?;
    m.add_class::<ImportSpecifier>()?;
    m.add_class::<ImportDefaultSpecifier>()?;
    m.add_class::<ImportNamespaceSpecifier>()?;
    m.add_class::<ExportNamedDeclaration>()?;
    m.add_class::<ExportDefaultDeclaration>()?;
    m.add_class::<ExportAllDeclaration>()?;
    m.add_class::<ExportSpecifier>()?;

    // Phase 16: TypeScript-Specific AST Nodes
    m.add_class::<TSTypeAliasDeclaration>()?;
    m.add_class::<TSInterfaceDeclaration>()?;
    m.add_class::<TSEnumDeclaration>()?;
    m.add_class::<TSTypeAnnotation>()?;
    m.add_class::<TSTypeReference>()?;
    m.add_class::<TSTypeParameter>()?;
    m.add_class::<TSPropertySignature>()?;
    m.add_class::<TSMethodSignature>()?;
    m.add_class::<TSInterfaceBody>()?;
    m.add_class::<TSEnumMember>()?;
    m.add_class::<TSTypeParameterDeclaration>()?;
    m.add_class::<TSUnionType>()?;
    m.add_class::<TSIntersectionType>()?;

    // Phase 17: JSX Node Types
    m.add_class::<JSXElement>()?;
    m.add_class::<JSXOpeningElement>()?;
    m.add_class::<JSXClosingElement>()?;
    m.add_class::<JSXFragment>()?;
    m.add_class::<JSXAttribute>()?;
    m.add_class::<JSXSpreadAttribute>()?;
    m.add_class::<JSXIdentifier>()?;
    m.add_class::<JSXMemberExpression>()?;
    m.add_class::<JSXText>()?;
    m.add_class::<JSXExpressionContainer>()?;

    Ok(())
}

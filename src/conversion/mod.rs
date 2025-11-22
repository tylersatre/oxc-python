//! AST conversion functions
//!
//! This module contains functions that convert from oxc's Rust AST types to Python-bound node types.

// Conversion function modules
pub mod helpers;
pub mod statements;
pub mod expressions;
pub mod jsx;
pub mod typescript;

// Re-export helper conversion functions
pub use helpers::{
    convert_binding_identifier, convert_export_specifier, convert_identifier_name,
    convert_import_specifier, convert_literal, compute_line_number,
};

// Re-export statement conversion functions
pub use statements::{
    convert_block_statement, convert_catch_clause, convert_for_statement_init,
    convert_for_statement_left, convert_statement, convert_switch_case,
    convert_function_body, convert_class_body,
};

// Re-export expression conversion functions
pub use expressions::convert_expression;

// Re-export JSX conversion functions
pub use jsx::{
    convert_jsx_attribute, convert_jsx_child, convert_jsx_closing_element, convert_jsx_element,
    convert_jsx_expression_container, convert_jsx_fragment, convert_jsx_member_expression,
    convert_jsx_name, convert_jsx_opening_element, convert_jsx_spread_attribute, convert_jsx_text,
};

// Re-export TypeScript conversion functions
pub use typescript::{
    convert_ts_enum_member, convert_ts_interface_body, convert_ts_interface_heritage,
    convert_ts_property_key, convert_ts_signature, convert_ts_type, convert_ts_type_annotation,
    convert_ts_type_parameter, convert_ts_type_parameter_declaration,
    convert_ts_type_parameter_instantiation,
};

// Re-export convert_errors from core
pub use crate::core::convert_errors;

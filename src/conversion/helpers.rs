//! Helper conversion functions for imports, exports, identifiers, and literals

use pyo3::prelude::*;
use oxc_ast::ast::{
    ImportDeclarationSpecifier, ExportSpecifier, BindingIdentifier, StringLiteral,
    IdentifierName,
};
use oxc_span::GetSpan;
use crate::nodes::expressions::{self as expressions, Identifier, Literal};
use crate::Span;

// Re-export compute_line_number from parser module
pub use crate::parser::compute_line_number;

/// Helper to convert import specifier (Phase 6 helpers + Phase 15 helpers)
pub fn convert_import_specifier(
    py: Python,
    spec: &oxc_ast::ast::ImportDeclarationSpecifier<'_>,
    source: &str,
) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::ImportDeclarationSpecifier as IDS;

    match spec {
        IDS::ImportSpecifier(named) => {
            let span = named.span();
            let span_converted = Span::from(span);
            let start_line = compute_line_number(source, span.start as usize);
            let end_line = compute_line_number(source, span.end as usize);

            let imported_name = named.imported.name().to_string();

            let local = convert_binding_identifier(py, &named.local, source)?;
            let imported = {
                let node = expressions::Identifier::new(span_converted.clone(), imported_name);
                Py::new(py, node)?.into_any()
            };

            let node = crate::ImportSpecifier {
                span: span_converted,
                start_line,
                end_line,
                imported,
                local,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        IDS::ImportDefaultSpecifier(default) => {
            let span = default.span();
            let span_converted = Span::from(span);
            let start_line = compute_line_number(source, span.start as usize);
            let end_line = compute_line_number(source, span.end as usize);

            let local = convert_binding_identifier(py, &default.local, source)?;

            let node = crate::ImportDefaultSpecifier {
                span: span_converted,
                start_line,
                end_line,
                local,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        IDS::ImportNamespaceSpecifier(namespace) => {
            let span = namespace.span();
            let span_converted = Span::from(span);
            let start_line = compute_line_number(source, span.start as usize);
            let end_line = compute_line_number(source, span.end as usize);

            let local = convert_binding_identifier(py, &namespace.local, source)?;

            let node = crate::ImportNamespaceSpecifier {
                span: span_converted,
                start_line,
                end_line,
                local,
            };
            Ok(Py::new(py, node)?.into_any())
        }
    }
}

// Phase 15: Helper to convert export specifier
pub fn convert_export_specifier(
    py: Python,
    spec: &oxc_ast::ast::ExportSpecifier<'_>,
    source: &str,
) -> PyResult<Py<PyAny>> {
    let span = spec.span();
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);

    // Convert local and exported identifiers
    let local_name = spec.local.name().to_string();
    let exported_name = spec.exported.name().to_string();

    let local = {
        let node = expressions::Identifier::new(span_converted.clone(), local_name);
        Py::new(py, node)?.into_any()
    };

    let exported = {
        let node = expressions::Identifier::new(span_converted.clone(), exported_name);
        Py::new(py, node)?.into_any()
    };

    let node = crate::ExportSpecifier {
        span: span_converted,
        start_line,
        end_line,
        local,
        exported,
    };
    Ok(Py::new(py, node)?.into_any())
}

// Phase 15: Helper to convert BindingIdentifier to Python Identifier object
pub fn convert_binding_identifier(py: Python, ident: &oxc_ast::ast::BindingIdentifier<'_>, _source: &str) -> PyResult<Py<PyAny>> {
    let span = ident.span;
    let span_converted = Span::from(span);
    let name = ident.name.to_string();

    let node = expressions::Identifier::new(span_converted, name);
    Ok(Py::new(py, node)?.into_any())
}

// Phase 15: Helper to convert StringLiteral to Python object
pub fn convert_literal(py: Python, lit: &oxc_ast::ast::StringLiteral<'_>, _source: &str) -> PyResult<Py<PyAny>> {
    use pyo3::types::PyString;

    let span = lit.span;
    let span_converted = Span::from(span);
    let value = lit.value.to_string();
    let raw = lit.raw.as_ref().map(|r| r.to_string()).unwrap_or_default();

    // Convert value to PyObject
    let value_py = PyString::new(py, &value).into();

    let node = expressions::Literal::new(
        span_converted,
        value_py,
        raw,
    );
    Ok(Py::new(py, node)?.into_any())
}

// Phase 15: Helper to convert IdentifierName to Python Identifier object
pub fn convert_identifier_name(py: Python, ident: &oxc_ast::ast::IdentifierName<'_>, _source: &str) -> PyResult<Py<PyAny>> {
    let span = ident.span;
    let span_converted = Span::from(span);
    let name = ident.name.to_string();

    let node = expressions::Identifier::new(span_converted, name);
    Ok(Py::new(py, node)?.into_any())
}

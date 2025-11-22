//! Phase 17: JSX Node Types
//!
//! Implements JSX AST node types as PyO3 classes for React/JSX support.

use pyo3::prelude::*;
use crate::Span;

// =============================================================================
// JSX Element Nodes
// =============================================================================

/// JSX element: <div>children</div>
///
/// Represents a complete JSX element with opening tag, children, and
/// optional closing tag (self-closing elements have no closing tag).
#[pyclass]
pub struct JSXElement {
    #[pyo3(get)]
    pub span: Span,

    /// Opening element: <div className="...">
    #[pyo3(get)]
    pub opening_element: Py<JSXOpeningElement>,

    /// Child nodes (JSXElement, JSXText, JSXExpressionContainer, etc.)
    #[pyo3(get)]
    pub children: Vec<Py<PyAny>>,

    /// Closing element: </div> (None for self-closing)
    #[pyo3(get)]
    pub closing_element: Option<Py<JSXClosingElement>>,
}

#[pymethods]
impl JSXElement {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXElement"
    }

    fn __repr__(&self) -> String {
        format!("JSXElement(span={})", self.span.start)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

/// JSX opening element: <div className="container">
///
/// Represents the opening tag of a JSX element including the element name,
/// attributes, and whether it's self-closing.
#[pyclass]
pub struct JSXOpeningElement {
    #[pyo3(get)]
    pub span: Span,

    /// Element name (JSXIdentifier or JSXMemberExpression)
    #[pyo3(get)]
    pub name: Py<PyAny>,

    /// Attributes (JSXAttribute or JSXSpreadAttribute)
    #[pyo3(get)]
    pub attributes: Vec<Py<PyAny>>,

    /// Whether this is self-closing (<img />)
    #[pyo3(get)]
    pub self_closing: bool,
}

#[pymethods]
impl JSXOpeningElement {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXOpeningElement"
    }

    fn __repr__(&self) -> String {
        format!("JSXOpeningElement(self_closing={})", self.self_closing)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

/// JSX closing element: </div>
///
/// Represents the closing tag of a JSX element.
#[pyclass]
pub struct JSXClosingElement {
    #[pyo3(get)]
    pub span: Span,

    /// Element name (JSXIdentifier or JSXMemberExpression)
    #[pyo3(get)]
    pub name: Py<PyAny>,
}

#[pymethods]
impl JSXClosingElement {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXClosingElement"
    }

    fn __repr__(&self) -> String {
        format!("JSXClosingElement(span={})", self.span.start)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

// =============================================================================
// JSX Fragment
// =============================================================================

/// JSX fragment: <>children</>
///
/// Represents a JSX fragment, which groups multiple children without
/// adding an extra DOM node.
#[pyclass]
pub struct JSXFragment {
    #[pyo3(get)]
    pub span: Span,

    /// Child nodes
    #[pyo3(get)]
    pub children: Vec<Py<PyAny>>,
}

#[pymethods]
impl JSXFragment {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXFragment"
    }

    fn __repr__(&self) -> String {
        format!("JSXFragment(children={})", self.children.len())
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

// =============================================================================
// JSX Attributes
// =============================================================================

/// JSX attribute: className="container"
///
/// Represents a named attribute on a JSX element.
#[pyclass]
pub struct JSXAttribute {
    #[pyo3(get)]
    pub span: Span,

    /// Attribute name (JSXIdentifier)
    #[pyo3(get)]
    pub name: Py<PyAny>,

    /// Attribute value (string literal, JSXExpressionContainer, or None)
    #[pyo3(get)]
    pub value: Option<Py<PyAny>>,
}

#[pymethods]
impl JSXAttribute {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXAttribute"
    }

    fn __repr__(&self) -> String {
        format!("JSXAttribute(span={})", self.span.start)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

/// JSX spread attribute: {...props}
///
/// Represents spreading an object as attributes on a JSX element.
#[pyclass]
pub struct JSXSpreadAttribute {
    #[pyo3(get)]
    pub span: Span,

    /// Expression being spread
    #[pyo3(get)]
    pub argument: Py<PyAny>,
}

#[pymethods]
impl JSXSpreadAttribute {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXSpreadAttribute"
    }

    fn __repr__(&self) -> String {
        format!("JSXSpreadAttribute(span={})", self.span.start)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

// =============================================================================
// JSX Names
// =============================================================================

/// JSX identifier: div, Component, className, etc.
///
/// Represents a simple identifier in JSX context.
#[pyclass]
pub struct JSXIdentifier {
    #[pyo3(get)]
    pub span: Span,

    /// Identifier name
    #[pyo3(get)]
    pub name: String,
}

#[pymethods]
impl JSXIdentifier {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXIdentifier"
    }

    fn __repr__(&self) -> String {
        format!("JSXIdentifier(name='{}')", self.name)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

/// JSX member expression: React.Fragment, lib.Component
///
/// Represents a member access in JSX element names.
#[pyclass]
pub struct JSXMemberExpression {
    #[pyo3(get)]
    pub span: Span,

    /// Object (JSXIdentifier or JSXMemberExpression)
    #[pyo3(get)]
    pub object: Py<PyAny>,

    /// Property (JSXIdentifier)
    #[pyo3(get)]
    pub property: Py<JSXIdentifier>,
}

#[pymethods]
impl JSXMemberExpression {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXMemberExpression"
    }

    fn __repr__(&self) -> String {
        format!("JSXMemberExpression(span={})", self.span.start)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

// =============================================================================
// JSX Content
// =============================================================================

/// JSX text content
///
/// Represents text content within JSX elements.
#[pyclass]
pub struct JSXText {
    #[pyo3(get)]
    pub span: Span,

    /// Decoded text value
    #[pyo3(get)]
    pub value: String,

    /// Raw text as it appears in source
    #[pyo3(get)]
    pub raw: String,
}

#[pymethods]
impl JSXText {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXText"
    }

    fn __repr__(&self) -> String {
        format!("JSXText(value='{}')", self.value)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

/// JSX expression container: {expression}
///
/// Represents a JavaScript expression embedded in JSX.
#[pyclass]
pub struct JSXExpressionContainer {
    #[pyo3(get)]
    pub span: Span,

    /// The JavaScript expression
    #[pyo3(get)]
    pub expression: Py<PyAny>,
}

#[pymethods]
impl JSXExpressionContainer {
    #[getter]
    pub fn r#type(&self) -> &str {
        "JSXExpressionContainer"
    }

    fn __repr__(&self) -> String {
        format!("JSXExpressionContainer(span={})", self.span.start)
    }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, source: &str) -> (usize, usize) {
        let start_line = source[..self.span.start.min(source.len())].matches('\n').count() + 1;
        let end_line = source[..self.span.end.min(source.len())].matches('\n').count() + 1;
        (start_line, end_line)
    }
}

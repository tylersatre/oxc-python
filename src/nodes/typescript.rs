//! Phase 16: TypeScript-Specific AST Nodes
//!
//! Implements TypeScript AST node types as PyO3 classes.
//! These nodes are critical for ChunkHound integration which maps
//! TSTypeAliasDeclaration -> ChunkType.TYPE
//! TSInterfaceDeclaration -> ChunkType.INTERFACE

use pyo3::prelude::*;
use crate::Span;

// =============================================================================
// TypeScript Declaration Nodes
// =============================================================================

/// TSTypeAliasDeclaration node for TypeScript type aliases.
/// Represents: type UserId = string;
/// ChunkHound maps this to ChunkType.TYPE
#[pyclass]
pub struct TSTypeAliasDeclaration {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub type_annotation: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub type_parameters: Option<Py<PyAny>>,
}

#[pymethods]
impl TSTypeAliasDeclaration {
    #[getter]
    pub fn r#type(&self) -> &str { "TSTypeAliasDeclaration" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSTypeAliasDeclaration(name={:?}, span={}..{})", self.name, self.span.start, self.span.end)
    }
}

/// TSInterfaceDeclaration node for TypeScript interfaces.
/// Represents: interface User { id: number; }
/// ChunkHound maps this to ChunkType.INTERFACE
#[pyclass]
pub struct TSInterfaceDeclaration {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub extends: Option<Vec<Py<PyAny>>>,
    #[pyo3(get)]
    pub type_parameters: Option<Py<PyAny>>,
}

#[pymethods]
impl TSInterfaceDeclaration {
    #[getter]
    pub fn r#type(&self) -> &str { "TSInterfaceDeclaration" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSInterfaceDeclaration(name={:?}, span={}..{})", self.name, self.span.start, self.span.end)
    }
}

/// TSEnumDeclaration node for TypeScript enums.
/// Represents: enum Color { Red, Green, Blue }
#[pyclass]
pub struct TSEnumDeclaration {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub members: Vec<Py<PyAny>>,
    #[pyo3(get)]
    pub is_const: bool,
}

#[pymethods]
impl TSEnumDeclaration {
    #[getter]
    pub fn r#type(&self) -> &str { "TSEnumDeclaration" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSEnumDeclaration(name={:?}, span={}..{})", self.name, self.span.start, self.span.end)
    }
}

// =============================================================================
// TypeScript Type Nodes
// =============================================================================

/// TSTypeAnnotation node for TypeScript type annotations.
/// Represents: : number (in const x: number = 1)
#[pyclass]
pub struct TSTypeAnnotation {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub type_annotation: Option<Py<PyAny>>,
}

#[pymethods]
impl TSTypeAnnotation {
    #[getter]
    pub fn r#type(&self) -> &str { "TSTypeAnnotation" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSTypeAnnotation(span={}..{})", self.span.start, self.span.end)
    }
}

/// TSTypeReference node for TypeScript type references.
/// Represents: User or Array<string>
#[pyclass]
pub struct TSTypeReference {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub type_name: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub type_parameters: Option<Py<PyAny>>,
}

#[pymethods]
impl TSTypeReference {
    #[getter]
    pub fn r#type(&self) -> &str { "TSTypeReference" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSTypeReference(span={}..{})", self.span.start, self.span.end)
    }
}

/// TSTypeParameter node for TypeScript type parameters.
/// Represents: T in function foo<T>()
#[pyclass]
pub struct TSTypeParameter {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub constraint: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub default: Option<Py<PyAny>>,
}

#[pymethods]
impl TSTypeParameter {
    #[getter]
    pub fn r#type(&self) -> &str { "TSTypeParameter" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSTypeParameter(name={:?}, span={}..{})", self.name, self.span.start, self.span.end)
    }
}

/// TSTypeParameterDeclaration node for TypeScript type parameter lists.
/// Represents <T, U> in generic declarations.
#[pyclass]
pub struct TSTypeParameterDeclaration {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub params: Vec<Py<PyAny>>,
}

#[pymethods]
impl TSTypeParameterDeclaration {
    #[getter]
    pub fn r#type(&self) -> &str { "TSTypeParameterDeclaration" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSTypeParameterDeclaration(params={}, span={}..{})", self.params.len(), self.span.start, self.span.end)
    }
}

// =============================================================================
// TypeScript Interface/Object Type Nodes
// =============================================================================

/// TSInterfaceBody node for TypeScript interface body.
#[pyclass]
pub struct TSInterfaceBody {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub body: Vec<Py<PyAny>>,
}

#[pymethods]
impl TSInterfaceBody {
    #[getter]
    pub fn r#type(&self) -> &str { "TSInterfaceBody" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSInterfaceBody(members={}, span={}..{})", self.body.len(), self.span.start, self.span.end)
    }
}

/// TSPropertySignature node for TypeScript interface properties.
/// Represents: readonly name: string; in interface
#[pyclass]
pub struct TSPropertySignature {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub key: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub optional: bool,
    #[pyo3(get)]
    pub readonly: bool,
    #[pyo3(get)]
    pub type_annotation: Option<Py<PyAny>>,
}

#[pymethods]
impl TSPropertySignature {
    #[getter]
    pub fn r#type(&self) -> &str { "TSPropertySignature" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSPropertySignature(span={}..{})", self.span.start, self.span.end)
    }
}

/// TSMethodSignature node for TypeScript interface methods.
/// Represents: log(message: string): void; in interface
#[pyclass]
pub struct TSMethodSignature {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub key: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub params: Vec<Py<PyAny>>,
    #[pyo3(get)]
    pub return_type: Option<Py<PyAny>>,
}

#[pymethods]
impl TSMethodSignature {
    #[getter]
    pub fn r#type(&self) -> &str { "TSMethodSignature" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSMethodSignature(span={}..{})", self.span.start, self.span.end)
    }
}

// =============================================================================
// TypeScript Enum Nodes
// =============================================================================

/// TSEnumMember node for TypeScript enum members.
#[pyclass]
pub struct TSEnumMember {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub id: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub initializer: Option<Py<PyAny>>,
}

#[pymethods]
impl TSEnumMember {
    #[getter]
    pub fn r#type(&self) -> &str { "TSEnumMember" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSEnumMember(span={}..{})", self.span.start, self.span.end)
    }
}

// =============================================================================
// TypeScript Union/Intersection Types
// =============================================================================

/// TSUnionType node for TypeScript union types.
/// Represents: string | number
#[pyclass]
pub struct TSUnionType {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub types: Vec<Py<PyAny>>,
}

#[pymethods]
impl TSUnionType {
    #[getter]
    pub fn r#type(&self) -> &str { "TSUnionType" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSUnionType(types={}, span={}..{})", self.types.len(), self.span.start, self.span.end)
    }
}

/// TSIntersectionType node for TypeScript intersection types.
/// Represents: TypeA & TypeB
#[pyclass]
pub struct TSIntersectionType {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub types: Vec<Py<PyAny>>,
}

#[pymethods]
impl TSIntersectionType {
    #[getter]
    pub fn r#type(&self) -> &str { "TSIntersectionType" }

    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }

    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!("TSIntersectionType(types={}, span={}..{})", self.types.len(), self.span.start, self.span.end)
    }
}

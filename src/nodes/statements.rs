//! Statement node definitions for oxc-python AST.
//!
//! This module contains all the statement node types used in the AST representation,
//! including declarations (functions, classes, variables), control flow (if, loops, try-catch),
//! and import/export statements.

use pyo3::prelude::*;
use crate::Span;

// =============================================================================
// Phase 13: Specialized Statement Node Types
// =============================================================================

/// FunctionDeclaration node with specialized fields.
///
/// Contains function-specific information like name, async/generator flags.
#[pyclass]
pub struct FunctionDeclaration {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Function name (None for anonymous)
    #[pyo3(get)]
    pub name: Option<String>,

    /// True if async function
    #[pyo3(get)]
    pub is_async: bool,

    /// True if generator function
    #[pyo3(get)]
    pub is_generator: bool,

    /// Function body (BlockStatement with statements)
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,

    /// Function parameters
    #[pyo3(get)]
    pub params: Vec<Py<PyAny>>,

    /// Type parameters for generics
    #[pyo3(get)]
    pub type_parameters: Option<Py<PyAny>>,

    /// Return type annotation
    #[pyo3(get)]
    pub return_type: Option<Py<PyAny>>,
}

#[pymethods]
impl FunctionDeclaration {
    #[getter]
    fn r#type(&self) -> &'static str {
        "FunctionDeclaration"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        let body_info = if self.body.is_some() { "with body" } else { "no body" };
        format!(
            "FunctionDeclaration(name={:?}, is_async={}, is_generator={}, {}, span={}..{})",
            self.name, self.is_async, self.is_generator, body_info, self.span.start, self.span.end
        )
    }
}

/// MethodDefinition node for class methods.
///
/// Similar to FunctionDeclaration but specifically for class methods.
/// This distinction is important for tools like ChunkHound that need to
/// differentiate between top-level functions and class methods.
#[pyclass]
pub struct MethodDefinition {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub name: Option<String>,
    #[pyo3(get)]
    pub is_async: bool,
    #[pyo3(get)]
    pub is_generator: bool,
    /// Named function_body so walk() can traverse it
    #[pyo3(get)]
    pub function_body: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub params: Vec<Py<PyAny>>,
}

#[pymethods]
impl MethodDefinition {
    #[getter]
    fn r#type(&self) -> &'static str {
        "MethodDefinition"
    }
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }
    fn __repr__(&self) -> String {
        format!(
            "MethodDefinition(name={:?}, is_async={}, span={}..{})",
            self.name, self.is_async, self.span.start, self.span.end
        )
    }
}

/// ClassBody node containing class methods and properties.
///
/// Represents the body of a class, which contains methods, properties,
/// and other class elements. The methods field allows walk() to traverse
/// into the class body and find nested JSX, functions, etc.
#[pyclass]
pub struct ClassBody {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    /// List of methods in this class body
    #[pyo3(get)]
    pub methods: Vec<Py<PyAny>>,
}

#[pymethods]
impl ClassBody {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ClassBody"
    }
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }
    fn __repr__(&self) -> String {
        format!(
            "ClassBody(methods={}, span={}..{})",
            self.methods.len(), self.span.start, self.span.end
        )
    }
}

/// ClassDeclaration node with specialized fields.
///
/// Contains class-specific information like name and superclass.
#[pyclass]
pub struct ClassDeclaration {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Class name (None for anonymous)
    #[pyo3(get)]
    pub name: Option<String>,

    /// Superclass name (None if no extends)
    #[pyo3(get)]
    pub superclass: Option<String>,

    /// Type parameters for generics
    #[pyo3(get)]
    pub type_parameters: Option<Py<PyAny>>,

    /// Class body (list of methods, properties, etc.)
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
}

#[pymethods]
impl ClassDeclaration {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ClassDeclaration"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ClassDeclaration(name={:?}, superclass={:?}, span={}..{})",
            self.name, self.superclass, self.span.start, self.span.end
        )
    }
}

/// VariableDeclaration node with specialized fields.
///
/// Contains the kind of declaration (const/let/var).
#[pyclass]
pub struct VariableDeclaration {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Declaration kind: "const", "let", or "var"
    #[pyo3(get)]
    pub kind: String,

    /// List of declarators
    #[pyo3(get)]
    pub declarations: Vec<Py<PyAny>>,
}

/// VariableDeclarator node for individual variable declarations.
#[pyclass]
pub struct VariableDeclarator {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub id: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub init: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub type_annotation: Option<Py<PyAny>>,
}

#[pymethods]
impl VariableDeclarator {
    #[getter]
    fn r#type(&self) -> &'static str { "VariableDeclarator" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("VariableDeclarator(span={}..{})", self.span.start, self.span.end) }
}

/// FormalParameter node for function parameters.
#[pyclass]
pub struct FormalParameter {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub name: Option<String>,
    #[pyo3(get)]
    pub type_annotation: Option<Py<PyAny>>,
}

#[pymethods]
impl FormalParameter {
    #[getter]
    fn r#type(&self) -> &'static str { "FormalParameter" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("FormalParameter(name={:?}, span={}..{})", self.name, self.span.start, self.span.end) }
}

#[pymethods]
impl VariableDeclaration {
    #[getter]
    fn r#type(&self) -> &'static str {
        "VariableDeclaration"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "VariableDeclaration(kind={:?}, span={}..{})",
            self.kind, self.span.start, self.span.end
        )
    }
}

/// BlockStatement node (function body, if body, etc.)
///
/// Contains a list of statements that form the block.
#[pyclass]
pub struct BlockStatement {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Statements in the block
    #[pyo3(get)]
    pub body: Vec<Py<PyAny>>,
}

#[pymethods]
impl BlockStatement {
    #[getter]
    fn r#type(&self) -> &'static str {
        "BlockStatement"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "BlockStatement(statements={}, span={}..{})",
            self.body.len(), self.span.start, self.span.end
        )
    }
}

// =============================================================================
// Phase 13: Additional Statement Node Types
// =============================================================================

/// BreakStatement node for loop/switch breaking.
#[pyclass]
pub struct BreakStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub label: Option<Py<PyAny>>,
}

#[pymethods]
impl BreakStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "BreakStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("BreakStatement(span={}..{})", self.span.start, self.span.end) }
}

/// ContinueStatement node for loop continuation.
#[pyclass]
pub struct ContinueStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub label: Option<Py<PyAny>>,
}

#[pymethods]
impl ContinueStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "ContinueStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("ContinueStatement(span={}..{})", self.span.start, self.span.end) }
}

/// LabeledStatement node for labeled statements.
#[pyclass]
pub struct LabeledStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub label: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
}

#[pymethods]
impl LabeledStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "LabeledStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("LabeledStatement(span={}..{})", self.span.start, self.span.end) }
}

/// EmptyStatement node for empty statements (just a semicolon).
#[pyclass]
pub struct EmptyStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
}

#[pymethods]
impl EmptyStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "EmptyStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("EmptyStatement(span={}..{})", self.span.start, self.span.end) }
}

/// WithStatement node for with statements (deprecated but valid).
#[pyclass]
pub struct WithStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub object: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
}

#[pymethods]
impl WithStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "WithStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("WithStatement(span={}..{})", self.span.start, self.span.end) }
}

/// ForStatement node for for loops.
#[pyclass]
pub struct ForStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub init: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub test: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub update: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
}

#[pymethods]
impl ForStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "ForStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("ForStatement(span={}..{})", self.span.start, self.span.end) }
}

/// IfStatement node for if statements.
#[pyclass]
pub struct IfStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub test: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub consequent: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub alternate: Option<Py<PyAny>>,
}

#[pymethods]
impl IfStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "IfStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("IfStatement(span={}..{})", self.span.start, self.span.end) }
}

/// ExpressionStatement node for expression statements.
#[pyclass]
pub struct ExpressionStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub expression: Option<Py<PyAny>>,
}

#[pymethods]
impl ExpressionStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "ExpressionStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("ExpressionStatement(span={}..{})", self.span.start, self.span.end) }
}

/// WhileStatement node for while loops.
#[pyclass]
pub struct WhileStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub test: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
}

#[pymethods]
impl WhileStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "WhileStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("WhileStatement(span={}..{})", self.span.start, self.span.end) }
}

/// DoWhileStatement node for do-while loops.
#[pyclass]
pub struct DoWhileStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub test: Option<Py<PyAny>>,
}

#[pymethods]
impl DoWhileStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "DoWhileStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("DoWhileStatement(span={}..{})", self.span.start, self.span.end) }
}

/// ForInStatement node for for-in loops.
#[pyclass]
pub struct ForInStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub left: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub right: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
}

#[pymethods]
impl ForInStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "ForInStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("ForInStatement(span={}..{})", self.span.start, self.span.end) }
}

/// ForOfStatement node for for-of loops.
#[pyclass]
pub struct ForOfStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub left: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub right: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub is_await: bool,
}

#[pymethods]
impl ForOfStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "ForOfStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("ForOfStatement(span={}..{})", self.span.start, self.span.end) }
}

/// SwitchStatement node for switch statements.
#[pyclass]
pub struct SwitchStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub discriminant: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub cases: Vec<Py<PyAny>>,
}

#[pymethods]
impl SwitchStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "SwitchStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("SwitchStatement(span={}..{})", self.span.start, self.span.end) }
}

/// SwitchCase node for switch case clauses.
#[pyclass]
pub struct SwitchCase {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub test: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub consequent: Vec<Py<PyAny>>,
}

#[pymethods]
impl SwitchCase {
    #[getter]
    fn r#type(&self) -> &'static str { "SwitchCase" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("SwitchCase(span={}..{})", self.span.start, self.span.end) }
}

/// TryStatement node for try-catch-finally statements.
#[pyclass]
pub struct TryStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub block: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub handler: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub finalizer: Option<Py<PyAny>>,
}

#[pymethods]
impl TryStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "TryStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("TryStatement(span={}..{})", self.span.start, self.span.end) }
}

/// CatchClause node for catch clauses.
#[pyclass]
pub struct CatchClause {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub param: Option<Py<PyAny>>,
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,
}

#[pymethods]
impl CatchClause {
    #[getter]
    fn r#type(&self) -> &'static str { "CatchClause" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("CatchClause(span={}..{})", self.span.start, self.span.end) }
}

/// ThrowStatement node for throw statements.
#[pyclass]
pub struct ThrowStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub argument: Option<Py<PyAny>>,
}

#[pymethods]
impl ThrowStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "ThrowStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("ThrowStatement(span={}..{})", self.span.start, self.span.end) }
}

/// ReturnStatement node for return statements.
#[pyclass]
pub struct ReturnStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
    #[pyo3(get)]
    pub argument: Option<Py<PyAny>>,
}

#[pymethods]
impl ReturnStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "ReturnStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("ReturnStatement(span={}..{})", self.span.start, self.span.end) }
}

/// DebuggerStatement node for debugger statements.
#[pyclass]
pub struct DebuggerStatement {
    #[pyo3(get)]
    pub span: Span,
    #[pyo3(get)]
    pub start_line: usize,
    #[pyo3(get)]
    pub end_line: usize,
}

#[pymethods]
impl DebuggerStatement {
    #[getter]
    fn r#type(&self) -> &'static str { "DebuggerStatement" }
    pub fn get_text(&self, source: &str) -> String {
        source[self.span.start.min(source.len())..self.span.end.min(source.len())].to_string()
    }
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) { (self.start_line, self.end_line) }
    fn __repr__(&self) -> String { format!("DebuggerStatement(span={}..{})", self.span.start, self.span.end) }
}

// =============================================================================
// Phase 15: Import/Export Declaration Node Types
// =============================================================================

/// ImportDeclaration node for ES module imports.
///
/// Represents: import ... from 'module'
/// Examples:
///     import foo from 'module';
///     import { bar, baz } from 'module';
///     import * as utils from 'module';
///
/// ChunkHound Usage:
///     Maps to ChunkType.IMPORT for dependency tracking.
#[pyclass]
pub struct ImportDeclaration {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Module path (StringLiteral object with .value property)
    #[pyo3(get)]
    pub source: Py<PyAny>,

    /// Import specifiers (list of ImportSpecifier, ImportDefaultSpecifier, ImportNamespaceSpecifier)
    #[pyo3(get)]
    pub specifiers: Vec<Py<PyAny>>,
}

#[pymethods]
impl ImportDeclaration {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ImportDeclaration"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ImportDeclaration(specifiers={}, span={}..{})",
            self.specifiers.len(), self.span.start, self.span.end
        )
    }
}

/// ImportSpecifier node for named imports.
///
/// Represents: { foo } or { foo as bar } in import statement
/// Examples:
///     import { foo } from 'module';  // imported='foo', local='foo'
///     import { foo as bar } from 'module';  // imported='foo', local='bar'
#[pyclass]
pub struct ImportSpecifier {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Original name being imported (Identifier)
    #[pyo3(get)]
    pub imported: Py<PyAny>,

    /// Local binding name (Identifier)
    #[pyo3(get)]
    pub local: Py<PyAny>,
}

#[pymethods]
impl ImportSpecifier {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ImportSpecifier"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ImportSpecifier(span={}..{})",
            self.span.start, self.span.end
        )
    }
}

/// ImportDefaultSpecifier node for default imports.
///
/// Represents: foo in import foo from 'module'
/// Examples:
///     import React from 'react';  // local='React'
#[pyclass]
pub struct ImportDefaultSpecifier {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Local binding name (Identifier)
    #[pyo3(get)]
    pub local: Py<PyAny>,
}

#[pymethods]
impl ImportDefaultSpecifier {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ImportDefaultSpecifier"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ImportDefaultSpecifier(span={}..{})",
            self.span.start, self.span.end
        )
    }
}

/// ImportNamespaceSpecifier node for namespace imports.
///
/// Represents: * as foo in import * as foo from 'module'
/// Examples:
///     import * as utils from './utils';  // local='utils'
#[pyclass]
pub struct ImportNamespaceSpecifier {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Local binding name (Identifier)
    #[pyo3(get)]
    pub local: Py<PyAny>,
}

#[pymethods]
impl ImportNamespaceSpecifier {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ImportNamespaceSpecifier"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ImportNamespaceSpecifier(span={}..{})",
            self.span.start, self.span.end
        )
    }
}

/// ExportNamedDeclaration node for named exports.
///
/// Represents various export forms:
/// - export { foo, bar };
/// - export function foo() {}
/// - export const bar = 1;
/// - export { foo } from 'module';
///
/// ChunkHound Usage:
///     Maps to ChunkType.EXPORT for API surface tracking.
#[pyclass]
pub struct ExportNamedDeclaration {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Declaration (Function/Class/Variable declaration or None)
    #[pyo3(get)]
    pub declaration: Option<Py<PyAny>>,

    /// Export specifiers (list of ExportSpecifier)
    #[pyo3(get)]
    pub specifiers: Vec<Py<PyAny>>,

    /// Module path for re-exports (StringLiteral for re-exports, None otherwise)
    #[pyo3(get)]
    pub source: Option<Py<PyAny>>,
}

#[pymethods]
impl ExportNamedDeclaration {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ExportNamedDeclaration"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ExportNamedDeclaration(specifiers={}, span={}..{})",
            self.specifiers.len(), self.span.start, self.span.end
        )
    }
}

/// ExportDefaultDeclaration node for default exports.
///
/// Represents: export default ...
/// Examples:
///     export default function() {}
///     export default class Foo {}
///     export default 42;
///
/// ChunkHound Usage:
///     Maps to ChunkType.EXPORT for API surface tracking.
#[pyclass]
pub struct ExportDefaultDeclaration {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Expression or Declaration being exported
    #[pyo3(get)]
    pub declaration: Py<PyAny>,
}

#[pymethods]
impl ExportDefaultDeclaration {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ExportDefaultDeclaration"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ExportDefaultDeclaration(span={}..{})",
            self.span.start, self.span.end
        )
    }
}

/// ExportAllDeclaration node for export * syntax.
///
/// Represents: export * from 'module'
/// Examples:
///     export * from './other';
///     export * as utils from './utils';
///
/// ChunkHound Usage:
///     Maps to ChunkType.EXPORT for API surface tracking.
#[pyclass]
pub struct ExportAllDeclaration {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Module path (StringLiteral)
    #[pyo3(get)]
    pub source: Py<PyAny>,

    /// Identifier for 'export * as name', None otherwise
    #[pyo3(get)]
    pub exported: Option<Py<PyAny>>,
}

#[pymethods]
impl ExportAllDeclaration {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ExportAllDeclaration"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ExportAllDeclaration(span={}..{})",
            self.span.start, self.span.end
        )
    }
}

/// ExportSpecifier node for named export specifiers.
///
/// Represents: { foo } or { foo as bar } in export statement
/// Examples:
///     export { foo };  // local='foo', exported='foo'
///     export { foo as bar };  // local='foo', exported='bar'
#[pyclass]
pub struct ExportSpecifier {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Start line number (1-indexed)
    #[pyo3(get)]
    pub start_line: usize,

    /// End line number (1-indexed)
    #[pyo3(get)]
    pub end_line: usize,

    /// Local binding name (Identifier)
    #[pyo3(get)]
    pub local: Py<PyAny>,

    /// Exported name (Identifier)
    #[pyo3(get)]
    pub exported: Py<PyAny>,
}

#[pymethods]
impl ExportSpecifier {
    #[getter]
    fn r#type(&self) -> &'static str {
        "ExportSpecifier"
    }

    /// Extract source text for this node.
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node.
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (self.start_line, self.end_line)
    }

    fn __repr__(&self) -> String {
        format!(
            "ExportSpecifier(span={}..{})",
            self.span.start, self.span.end
        )
    }
}

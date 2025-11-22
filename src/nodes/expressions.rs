//! Phase 14: Expression Node Types
//!
//! Implements Python classes for expression nodes with focus on ArrowFunctionExpression
//! which is critical for ChunkHound integration.
//!
//! Expression types:
//! - ArrowFunctionExpression: (x) => x + 1 (CRITICAL for ChunkHound)
//! - CallExpression: foo(a, b, c)
//! - MemberExpression: obj.property or obj[computed]
//! - BinaryExpression: a + b, x == y, etc.
//! - UnaryExpression: !x, -y, typeof z
//! - ConditionalExpression: test ? consequent : alternate
//! - ObjectExpression: {key: value}
//! - ArrayExpression: [1, 2, 3]
//! - Identifier: variable or function names
//! - Literal: numbers, strings, booleans, null

use pyo3::prelude::*;
use crate::Span;

/// Arrow function expression: (x) => x + 1
///
/// CRITICAL: ChunkHound uses this for extracting arrow functions and mapping to FUNCTION type.
///
/// Example in source code:
///     const add = (a, b) => a + b;
///     const square = x => x * x;
///     const asyncFn = async (x) => { return await process(x); };
#[pyclass]
pub struct ArrowFunctionExpression {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Function parameters (list of parameter nodes)
    #[pyo3(get)]
    pub params: Vec<Py<PyAny>>,

    /// Function body (Expression or BlockStatement)
    #[pyo3(get)]
    pub body: Option<Py<PyAny>>,

    /// Whether function is async
    #[pyo3(get)]
    pub is_async: bool,

    /// Whether function is generator (rare for arrows, but possible)
    #[pyo3(get)]
    pub is_generator: bool,
}

#[pymethods]
impl ArrowFunctionExpression {
    /// Create a new ArrowFunctionExpression node
    #[new]
    pub fn new(
        span: Span,
        params: Vec<Py<PyAny>>,
        body: Option<Py<PyAny>>,
        is_async: bool,
        is_generator: bool,
    ) -> Self {
        Self {
            span,
            params,
            body,
            is_async,
            is_generator,
        }
    }

    /// Node type property (always "ArrowFunctionExpression")
    #[getter]
    pub fn r#type(&self) -> &str {
        "ArrowFunctionExpression"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        // Placeholder: will compute from span in future phases
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!(
            "ArrowFunctionExpression(async={}, generator={}, span={}..{})",
            self.is_async, self.is_generator, self.span.start, self.span.end
        )
    }
}

/// Call expression: foo(a, b, c)
///
/// Represents a function call with a callee and arguments.
///
/// Example in source code:
///     foo();
///     add(1, 2);
///     obj.method(x, y);
#[pyclass]
pub struct CallExpression {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Function being called (Identifier, MemberExpression, etc.)
    #[pyo3(get)]
    pub callee: Option<Py<PyAny>>,

    /// Arguments passed to the function
    #[pyo3(get)]
    pub arguments: Vec<Py<PyAny>>,
}

#[pymethods]
impl CallExpression {
    /// Create a new CallExpression node
    #[new]
    pub fn new(
        span: Span,
        callee: Option<Py<PyAny>>,
        arguments: Vec<Py<PyAny>>,
    ) -> Self {
        Self {
            span,
            callee,
            arguments,
        }
    }

    /// Node type property (always "CallExpression")
    #[getter]
    pub fn r#type(&self) -> &str {
        "CallExpression"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!("CallExpression(args={}, span={}..{})", self.arguments.len(), self.span.start, self.span.end)
    }
}

/// Member expression: obj.property or obj[computed]
///
/// Represents property access in two forms:
/// - Static access: obj.property (computed=false)
/// - Computed access: obj[property] (computed=true)
///
/// Example in source code:
///     obj.method
///     arr[0]
///     obj['key']
///     deeply.nested.property
#[pyclass]
pub struct MemberExpression {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Object being accessed
    #[pyo3(get)]
    pub object: Option<Py<PyAny>>,

    /// Property being accessed
    #[pyo3(get)]
    pub property: Option<Py<PyAny>>,

    /// Whether access is computed (obj[x]) vs static (obj.x)
    #[pyo3(get)]
    pub computed: bool,
}

#[pymethods]
impl MemberExpression {
    /// Create a new MemberExpression node
    #[new]
    pub fn new(
        span: Span,
        object: Option<Py<PyAny>>,
        property: Option<Py<PyAny>>,
        computed: bool,
    ) -> Self {
        Self {
            span,
            object,
            property,
            computed,
        }
    }

    /// Node type property (always "MemberExpression")
    #[getter]
    pub fn r#type(&self) -> &str {
        "MemberExpression"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        let access_type = if self.computed { "computed" } else { "static" };
        format!("MemberExpression({}, span={}..{})", access_type, self.span.start, self.span.end)
    }
}

/// Binary expression: left op right
///
/// Represents operations with two operands and an operator.
///
/// Example in source code:
///     x + y
///     a - b
///     x * y
///     x === y
///     a && b
#[pyclass]
pub struct BinaryExpression {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Left operand
    #[pyo3(get)]
    pub left: Option<Py<PyAny>>,

    /// Operator: "+", "-", "*", "/", "%", "==", "!=", "===", "!==", "<", ">", "<=", ">=", "&&", "||", etc.
    #[pyo3(get)]
    pub operator: String,

    /// Right operand
    #[pyo3(get)]
    pub right: Option<Py<PyAny>>,
}

#[pymethods]
impl BinaryExpression {
    /// Create a new BinaryExpression node
    #[new]
    pub fn new(
        span: Span,
        left: Option<Py<PyAny>>,
        operator: String,
        right: Option<Py<PyAny>>,
    ) -> Self {
        Self {
            span,
            left,
            operator,
            right,
        }
    }

    /// Node type property (always "BinaryExpression")
    #[getter]
    pub fn r#type(&self) -> &str {
        "BinaryExpression"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!("BinaryExpression(op='{}', span={}..{})", self.operator, self.span.start, self.span.end)
    }
}

/// Unary expression: op argument
///
/// Represents operations with one operand and an operator.
///
/// Example in source code:
///     !x
///     -y
///     +z
///     ~bits
///     typeof value
///     void 0
///     delete obj.prop
#[pyclass]
pub struct UnaryExpression {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Operator: "!", "-", "+", "~", "typeof", "void", "delete"
    #[pyo3(get)]
    pub operator: String,

    /// Operand
    #[pyo3(get)]
    pub argument: Option<Py<PyAny>>,
}

#[pymethods]
impl UnaryExpression {
    /// Create a new UnaryExpression node
    #[new]
    pub fn new(
        span: Span,
        operator: String,
        argument: Option<Py<PyAny>>,
    ) -> Self {
        Self {
            span,
            operator,
            argument,
        }
    }

    /// Node type property (always "UnaryExpression")
    #[getter]
    pub fn r#type(&self) -> &str {
        "UnaryExpression"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!("UnaryExpression(op='{}', span={}..{})", self.operator, self.span.start, self.span.end)
    }
}

/// Conditional expression: test ? consequent : alternate
///
/// The ternary operator expression.
///
/// Example in source code:
///     x > 0 ? 'positive' : 'non-positive'
///     isAdmin ? showAdminPanel() : showUserPanel()
#[pyclass]
pub struct ConditionalExpression {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Condition to test
    #[pyo3(get)]
    pub test: Option<Py<PyAny>>,

    /// Value if condition is true
    #[pyo3(get)]
    pub consequent: Option<Py<PyAny>>,

    /// Value if condition is false
    #[pyo3(get)]
    pub alternate: Option<Py<PyAny>>,
}

#[pymethods]
impl ConditionalExpression {
    /// Create a new ConditionalExpression node
    #[new]
    pub fn new(
        span: Span,
        test: Option<Py<PyAny>>,
        consequent: Option<Py<PyAny>>,
        alternate: Option<Py<PyAny>>,
    ) -> Self {
        Self {
            span,
            test,
            consequent,
            alternate,
        }
    }

    /// Node type property (always "ConditionalExpression")
    #[getter]
    pub fn r#type(&self) -> &str {
        "ConditionalExpression"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!("ConditionalExpression(span={}..{})", self.span.start, self.span.end)
    }
}

/// Object expression: {key: value, ...}
///
/// Represents object literals.
///
/// Example in source code:
///     {a: 1, b: 2}
///     {x, y, z}
///     {[computed]: value}
#[pyclass]
pub struct ObjectExpression {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Object properties
    #[pyo3(get)]
    pub properties: Vec<Py<PyAny>>,
}

#[pymethods]
impl ObjectExpression {
    /// Create a new ObjectExpression node
    #[new]
    pub fn new(span: Span, properties: Vec<Py<PyAny>>) -> Self {
        Self { span, properties }
    }

    /// Node type property (always "ObjectExpression")
    #[getter]
    pub fn r#type(&self) -> &str {
        "ObjectExpression"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!("ObjectExpression(props={}, span={}..{})", self.properties.len(), self.span.start, self.span.end)
    }
}

/// Array expression: [1, 2, 3]
///
/// Represents array literals.
///
/// Example in source code:
///     [1, 2, 3]
///     []
///     [a, b, c]
#[pyclass]
pub struct ArrayExpression {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Array elements
    #[pyo3(get)]
    pub elements: Vec<Py<PyAny>>,
}

#[pymethods]
impl ArrayExpression {
    /// Create a new ArrayExpression node
    #[new]
    pub fn new(span: Span, elements: Vec<Py<PyAny>>) -> Self {
        Self { span, elements }
    }

    /// Node type property (always "ArrayExpression")
    #[getter]
    pub fn r#type(&self) -> &str {
        "ArrayExpression"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!("ArrayExpression(elements={}, span={}..{})", self.elements.len(), self.span.start, self.span.end)
    }
}

/// Identifier: variable or function name
///
/// Represents variable or function references by name.
///
/// Example in source code:
///     x
///     myVariable
///     functionName
#[pyclass]
pub struct Identifier {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Name of the identifier
    #[pyo3(get)]
    pub name: String,
}

#[pymethods]
impl Identifier {
    /// Create a new Identifier node
    #[new]
    pub fn new(span: Span, name: String) -> Self {
        Self { span, name }
    }

    /// Node type property (always "Identifier")
    #[getter]
    pub fn r#type(&self) -> &str {
        "Identifier"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!("Identifier('{}', span={}..{})", self.name, self.span.start, self.span.end)
    }
}

/// Literal value: number, string, boolean, null
///
/// Represents literal values in the source code.
///
/// Example in source code:
///     42
///     3.14
///     "hello"
///     true
///     false
///     null
#[pyclass]
pub struct Literal {
    /// Source location
    #[pyo3(get)]
    pub span: Span,

    /// Parsed value (int, float, string, bool, None)
    #[pyo3(get)]
    pub value: Py<PyAny>,

    /// Raw source text representation
    #[pyo3(get)]
    pub raw: String,
}

#[pymethods]
impl Literal {
    /// Create a new Literal node
    #[new]
    pub fn new(span: Span, value: Py<PyAny>, raw: String) -> Self {
        Self { span, value, raw }
    }

    /// Node type property (always "Literal")
    #[getter]
    pub fn r#type(&self) -> &str {
        "Literal"
    }

    /// Extract source text for this node
    pub fn get_text(&self, source: &str) -> String {
        let start = self.span.start.min(source.len());
        let end = self.span.end.min(source.len());
        source.get(start..end).unwrap_or("").to_string()
    }

    /// Get line range for this node
    pub fn get_line_range(&self, _source: &str) -> (usize, usize) {
        (1, 1)
    }

    fn __repr__(&self) -> String {
        format!("Literal(raw='{}', span={}..{})", self.raw, self.span.start, self.span.end)
    }
}

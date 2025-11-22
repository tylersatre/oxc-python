//! AST traversal utilities

use pyo3::prelude::*;
use std::collections::VecDeque;

// =============================================================================
// Phase 10: Walk Iterator with Depth Tracking
// =============================================================================

/// Iterator that yields (node, depth) tuples during AST traversal.
///
/// Performs depth-first, pre-order traversal of the AST.
/// Depth starts at 0 for the root Program node.
///
/// CRITICAL: Depth tracking is BLOCKER-2 for ChunkHound integration.
/// ChunkHound uses depth for:
/// - Hierarchical chunk organization
/// - Symbol naming (nested vs top-level)
/// - Filtering (show only top-level declarations)
/// - Tree reconstruction for context
///
/// Example:
///     for node, depth in walk(program):
///         print(f"{'  ' * depth}{node.type}")
#[pyclass]
pub struct WalkIterator {
    /// Queue of (node, depth) to visit (using VecDeque for efficient front operations)
    queue: VecDeque<(Py<PyAny>, usize)>,
}

impl WalkIterator {
    /// Create new iterator starting at program node with depth 0
    pub fn new(program: Py<PyAny>) -> Self {
        let mut queue = VecDeque::new();
        queue.push_back((program, 0));
        Self { queue }
    }
}

#[pymethods]
impl WalkIterator {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(&mut self, py: Python) -> PyResult<Option<(Py<PyAny>, usize)>> {
        // Pop next node from front of queue
        if let Some((node, depth)) = self.queue.pop_front() {
            // Get children of this node and add them to the queue
            let node_ref = node.bind(py);

            // Collect children to add (avoid borrow conflicts)
            let mut children_to_add: Vec<(Py<PyAny>, usize)> = Vec::new();

            // Single node attributes to traverse
            // Note: 'body' is handled specially below since it can be a single node or list
            let node_attrs = [
                "init", "declaration", "function_body", "class_body", "value", "key",
                "super_class", "consequent", "alternate", "test", "update", "discriminant",
                "block", "handler", "finalizer", "param", "left", "right", "expression",
                "callee", "object", "property", "argument", "quasi", "tag", "source",
                "local", "imported", "exported", "type_annotation", "type_parameters",
                "extends", "opening_element", "closing_element", "return_type", "id",
                "constraint", "default", "initializer",
            ];

            for attr_name in node_attrs {
                if let Ok(attr) = node_ref.getattr(attr_name) {
                    if !attr.is_none() {
                        // Only traverse if this is an AST node (has 'type' attribute)
                        // This filters out primitive values like strings and numbers
                        if let Ok(child) = attr.extract::<Py<PyAny>>() {
                            let child_bound = child.bind(py);
                            if child_bound.hasattr("type").unwrap_or(false) {
                                children_to_add.push((child, depth + 1));
                            }
                        }
                    }
                }
            }

            // List attributes to traverse
            let list_attrs = [
                "statements", "declarations", "params", "methods", "decorators",
                "cases", "arguments", "properties", "elements", "quasis", "expressions",
                "specifiers", "members", "implements", "children", "attributes",
            ];

            for attr_name in list_attrs {
                if let Ok(attr) = node_ref.getattr(attr_name) {
                    if let Ok(list) = attr.extract::<Vec<Py<PyAny>>>() {
                        for child in list {
                            // Only traverse if this is an AST node (has 'type' attribute)
                            let child_bound = child.bind(py);
                            if child_bound.hasattr("type").unwrap_or(false) {
                                children_to_add.push((child, depth + 1));
                            }
                        }
                    }
                }
            }

            // 'body' is special - can be a single node (FunctionDeclaration.body = BlockStatement)
            // or a list (Program.body = list[Statement], BlockStatement.body = list[Statement])
            if let Ok(body) = node_ref.getattr("body") {
                // Try as list first
                if let Ok(list) = body.extract::<Vec<Py<PyAny>>>() {
                    for child in list {
                        let child_bound = child.bind(py);
                        if child_bound.hasattr("type").unwrap_or(false) {
                            children_to_add.push((child, depth + 1));
                        }
                    }
                } else if !body.is_none() {
                    // If not a list, try as single node
                    if let Ok(child) = body.extract::<Py<PyAny>>() {
                        let child_bound = child.bind(py);
                        if child_bound.hasattr("type").unwrap_or(false) {
                            children_to_add.push((child, depth + 1));
                        }
                    }
                }
            }

            // 'extends' can be both single node and list (TSInterfaceDeclaration)
            if let Ok(extends) = node_ref.getattr("extends") {
                if let Ok(list) = extends.extract::<Vec<Py<PyAny>>>() {
                    for child in list {
                        let child_bound = child.bind(py);
                        if child_bound.hasattr("type").unwrap_or(false) {
                            children_to_add.push((child, depth + 1));
                        }
                    }
                }
            }

            // 'consequent' can be both single node (IfStatement) and list (SwitchCase)
            if let Ok(consequent) = node_ref.getattr("consequent") {
                if let Ok(list) = consequent.extract::<Vec<Py<PyAny>>>() {
                    for child in list {
                        let child_bound = child.bind(py);
                        if child_bound.hasattr("type").unwrap_or(false) {
                            children_to_add.push((child, depth + 1));
                        }
                    }
                }
            }

            // Check if node has 'name' attribute and traverse it (for JSX nodes only)
            if let Ok(name) = node_ref.getattr("name") {
                if !name.is_none() {
                    if let Ok(name_node) = name.extract::<Py<PyAny>>() {
                        let name_bound = name_node.bind(py);
                        if let Ok(name_type) = name_bound.getattr("type") {
                            if let Ok(type_str) = name_type.extract::<String>() {
                                if type_str == "JSXIdentifier" || type_str == "JSXMemberExpression" {
                                    children_to_add.push((name_node, depth + 1));
                                }
                            }
                        }
                    }
                }
            }

            // Now add all collected children to the queue
            for child in children_to_add {
                self.queue.push_back(child);
            }

            // Return current node with its depth
            Ok(Some((node, depth)))
        } else {
            // Queue is empty, iteration complete
            Ok(None)
        }
    }
}

/// Walk AST in depth-first, pre-order traversal.
///
/// Yields (node, depth) tuples where:
/// - node: AST node (Program, FunctionDeclaration, etc.)
/// - depth: Nesting level (0 = root, 1 = direct child, etc.)
///
/// CRITICAL: Depth tracking is essential for ChunkHound integration.
///
/// Args:
///     program: Root Program node to start traversal
///
/// Returns:
///     Iterator yielding (node, depth) tuples
///
/// Example:
///     >>> result = oxc_python.parse("function foo() { const x = 1; }")
///     >>> for node, depth in oxc_python.walk(result.program):
///     ...     print(f"{'  ' * depth}{node.type}")
///     Program
///       FunctionDeclaration
#[pyfunction]
pub fn walk(program: Py<PyAny>) -> PyResult<WalkIterator> {
    Ok(WalkIterator::new(program))
}

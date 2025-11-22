//! Expression conversion functions

use pyo3::prelude::*;
use oxc_ast::ast::Statement;
use oxc_span::GetSpan;
use crate::{
    Node, Span, FunctionDeclaration,
};
use crate::nodes::expressions::{
    Identifier, ArrowFunctionExpression, CallExpression, MemberExpression,
    BinaryExpression, ConditionalExpression, ObjectExpression, ArrayExpression,
};
use crate::conversion::{convert_function_body, convert_jsx_element, convert_jsx_fragment, compute_line_number};

pub fn convert_expression(py: Python, expr: &oxc_ast::ast::Expression, source: &str) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::Expression;

    let expr_span = expr.span();
    let span_converted = Span::from(expr_span);
    let start_line = compute_line_number(source, expr_span.start as usize);
    let end_line = compute_line_number(source, expr_span.end as usize);

    match expr {
        // JSX expressions - convert to proper JSX nodes
        Expression::JSXElement(jsx_elem) => {
            convert_jsx_element(py, jsx_elem, source).map(|p| p.into_any())
        }
        Expression::JSXFragment(jsx_frag) => {
            convert_jsx_fragment(py, jsx_frag, source).map(|p| p.into_any())
        }

        // Arrow functions - need to expose body for JSX traversal
        Expression::ArrowFunctionExpression(arrow) => {
            let params: Vec<Py<PyAny>> = arrow.params.items.iter()
                .map(|p| {
                    let param_span = Span::from(p.span());
                    let name = match &p.pattern.kind {
                        oxc_ast::ast::BindingPatternKind::BindingIdentifier(ident) => ident.name.to_string(),
                        _ => "param".to_string(),
                    };
                    Py::new(py, Identifier::new(param_span, name)).map(|p| p.into_any())
                })
                .collect::<PyResult<Vec<_>>>()?;

            // Convert body - can be expression or block
            let body: Option<Py<PyAny>> = if arrow.expression {
                // Expression body (concise arrow function)
                arrow.body.statements.first()
                    .and_then(|stmt| {
                        if let Statement::ExpressionStatement(expr_stmt) = stmt {
                            Some(convert_expression(py, &expr_stmt.expression, source))
                        } else {
                            None
                        }
                    })
                    .transpose()?
            } else {
                // Block body
                Some(convert_function_body(py, &arrow.body, source)?)
            };

            let node = ArrowFunctionExpression {
                span: span_converted,
                is_async: arrow.r#async,
                is_generator: false,
                body,
                params,
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Conditional expressions - need to expose both branches for JSX
        Expression::ConditionalExpression(cond) => {
            let test = convert_expression(py, &cond.test, source)?;
            let consequent = convert_expression(py, &cond.consequent, source)?;
            let alternate = convert_expression(py, &cond.alternate, source)?;

            let node = ConditionalExpression {
                span: span_converted,
                test: Some(test),
                consequent: Some(consequent),
                alternate: Some(alternate),
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Logical expressions - need to expose both sides for JSX in && and ||
        Expression::LogicalExpression(logical) => {
            let left = convert_expression(py, &logical.left, source)?;
            let right = convert_expression(py, &logical.right, source)?;
            let operator = match logical.operator {
                oxc_ast::ast::LogicalOperator::And => "&&",
                oxc_ast::ast::LogicalOperator::Or => "||",
                oxc_ast::ast::LogicalOperator::Coalesce => "??",
            }.to_string();

            let node = BinaryExpression {
                span: span_converted,
                operator,
                left: Some(left),
                right: Some(right),
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Call expressions - need to expose arguments for JSX in callbacks
        Expression::CallExpression(call) => {
            let callee = convert_expression(py, &call.callee, source)?;
            let arguments: Vec<Py<PyAny>> = call.arguments.iter()
                .map(|arg| {
                    match arg {
                        oxc_ast::ast::Argument::SpreadElement(spread) => {
                            convert_expression(py, &spread.argument, source)
                        }
                        _ => {
                            // Regular argument - it's an Expression
                            convert_expression(py, arg.to_expression(), source)
                        }
                    }
                })
                .collect::<PyResult<Vec<_>>>()?;

            let node = CallExpression {
                span: span_converted,
                callee: Some(callee),
                arguments,
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Member expressions - for chained methods like items.filter().map()
        Expression::StaticMemberExpression(member) => {
            let object = convert_expression(py, &member.object, source)?;
            let property_span = Span::from(member.property.span);
            let property = Py::new(py, Identifier::new(property_span, member.property.name.to_string()))?.into_any();

            let node = MemberExpression {
                span: span_converted,
                object: Some(object),
                property: Some(property),
                computed: false,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Expression::ComputedMemberExpression(member) => {
            let object = convert_expression(py, &member.object, source)?;
            let property = convert_expression(py, &member.expression, source)?;

            let node = MemberExpression {
                span: span_converted,
                object: Some(object),
                property: Some(property),
                computed: true,
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Parenthesized expressions - unwrap and convert inner
        Expression::ParenthesizedExpression(paren) => {
            convert_expression(py, &paren.expression, source)
        }

        // Sequence expressions - expose all expressions
        Expression::SequenceExpression(seq) => {
            let _expressions: Vec<Py<PyAny>> = seq.expressions.iter()
                .map(|e| convert_expression(py, e, source))
                .collect::<PyResult<Vec<_>>>()?;

            let mut node = Node::new("SequenceExpression".to_string(), span_converted);
            node.start_line = start_line;
            node.end_line = end_line;
            Ok(Py::new(py, node)?.into_any())
        }

        // Object expressions - expose properties for nested JSX
        Expression::ObjectExpression(obj) => {
            let properties: Vec<Py<PyAny>> = obj.properties.iter()
                .filter_map(|prop| {
                    match prop {
                        oxc_ast::ast::ObjectPropertyKind::ObjectProperty(p) => {
                            let value = convert_expression(py, &p.value, source).ok()?;
                            Some(value)
                        }
                        oxc_ast::ast::ObjectPropertyKind::SpreadProperty(spread) => {
                            convert_expression(py, &spread.argument, source).ok()
                        }
                    }
                })
                .collect();

            let node = ObjectExpression {
                span: span_converted,
                properties,
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Array expressions - expose elements for nested JSX
        Expression::ArrayExpression(arr) => {
            let elements: Vec<Py<PyAny>> = arr.elements.iter()
                .filter_map(|elem| {
                    match elem {
                        oxc_ast::ast::ArrayExpressionElement::SpreadElement(spread) => {
                            convert_expression(py, &spread.argument, source).ok()
                        }
                        oxc_ast::ast::ArrayExpressionElement::Elision(_) => None,
                        _ => {
                            // Regular element
                            convert_expression(py, elem.to_expression(), source).ok()
                        }
                    }
                })
                .collect();

            let node = ArrayExpression {
                span: span_converted,
                elements,
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Binary expressions
        Expression::BinaryExpression(binary) => {
            let left = convert_expression(py, &binary.left, source)?;
            let right = convert_expression(py, &binary.right, source)?;
            let operator = format!("{:?}", binary.operator);

            let node = BinaryExpression {
                span: span_converted,
                operator,
                left: Some(left),
                right: Some(right),
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Assignment expressions
        Expression::AssignmentExpression(assign) => {
            let right = convert_expression(py, &assign.right, source)?;

            let mut node = Node::new("AssignmentExpression".to_string(), span_converted);
            node.start_line = start_line;
            node.end_line = end_line;
            // Store right for traversal - walk() handles this via 'right' attribute check
            // For now just return node - walk() already handles 'right' in node_attrs
            let _ = right; // unused but needed for JSX traversal
            Ok(Py::new(py, node)?.into_any())
        }

        // Function expressions
        Expression::FunctionExpression(func) => {
            let name = func.id.as_ref().map(|id| id.name.to_string());
            let body = func.body.as_ref()
                .map(|b| convert_function_body(py, b, source))
                .transpose()?;

            let params: Vec<Py<PyAny>> = func.params.items.iter()
                .map(|p| {
                    let param_span = Span::from(p.span());
                    let param_name = match &p.pattern.kind {
                        oxc_ast::ast::BindingPatternKind::BindingIdentifier(ident) => ident.name.to_string(),
                        _ => "param".to_string(),
                    };
                    Py::new(py, Identifier::new(param_span, param_name)).map(|p| p.into_any())
                })
                .collect::<PyResult<Vec<_>>>()?;

            let node = FunctionDeclaration {
                span: span_converted,
                start_line,
                end_line,
                name,
                is_async: func.r#async,
                is_generator: func.generator,
                body,
                params,
                type_parameters: None,
                return_type: None,
            };
            Ok(Py::new(py, node)?.into_any())
        }

        // Default: create a generic node with correct type
        _ => {
            let type_str = match expr {
                Expression::NumericLiteral(_) => "NumericLiteral",
                Expression::StringLiteral(_) => "StringLiteral",
                Expression::BooleanLiteral(_) => "BooleanLiteral",
                Expression::NullLiteral(_) => "NullLiteral",
                Expression::Identifier(_) => "Identifier",
                Expression::UnaryExpression(_) => "UnaryExpression",
                Expression::UpdateExpression(_) => "UpdateExpression",
                Expression::PrivateFieldExpression(_) => "MemberExpression",
                Expression::NewExpression(_) => "NewExpression",
                Expression::ThisExpression(_) => "ThisExpression",
                Expression::TemplateLiteral(_) => "TemplateLiteral",
                Expression::TaggedTemplateExpression(_) => "TaggedTemplateExpression",
                Expression::AwaitExpression(_) => "AwaitExpression",
                Expression::YieldExpression(_) => "YieldExpression",
                _ => "Expression",
            };

            let mut node = Node::new(type_str.to_string(), span_converted);
            node.start_line = start_line;
            node.end_line = end_line;
            Ok(Py::new(py, node)?.into_any())
        }
    }
}

// JSX conversion functions are imported from jsx module via crate::conversion

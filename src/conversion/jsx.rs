//! JSX element conversion functions

use crate::nodes::expressions;
use crate::nodes::jsx::{
    JSXAttribute, JSXClosingElement, JSXElement, JSXExpressionContainer, JSXFragment,
    JSXIdentifier, JSXMemberExpression, JSXOpeningElement, JSXSpreadAttribute, JSXText,
};
use crate::Span;
use crate::conversion::{convert_literal, convert_expression};
use pyo3::prelude::*;
use oxc_span::GetSpan;

/// Convert JSX element name to Python representation
pub fn convert_jsx_name(py: Python, name: &oxc_ast::ast::JSXElementName, _source: &str) -> PyResult<Py<PyAny>> {
    match name {
        oxc_ast::ast::JSXElementName::Identifier(ident) => {
            let span = ident.span;
            let span_converted = Span::from(span);
            let name_str = ident.name.to_string();
            let node = JSXIdentifier {
                span: span_converted,
                name: name_str,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        oxc_ast::ast::JSXElementName::IdentifierReference(ident) => {
            let span = ident.span;
            let span_converted = Span::from(span);
            let name_str = ident.name.to_string();
            let node = JSXIdentifier {
                span: span_converted,
                name: name_str,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        oxc_ast::ast::JSXElementName::MemberExpression(member) => {
            convert_jsx_member_expression(py, member)
        }
        oxc_ast::ast::JSXElementName::NamespacedName(ns) => {
            // For now, treat as generic identifier - namespaces not fully supported
            let name_str = format!("{}:{}", ns.namespace.name, ns.name);
            Ok(Py::new(py, JSXIdentifier {
                span: Span { start: 0, end: 0 },
                name: name_str,
            })?.into_any())
        }
        oxc_ast::ast::JSXElementName::ThisExpression(_) => {
            // thisexpression is rarely used in JSX names
            Ok(Py::new(py, JSXIdentifier {
                span: Span { start: 0, end: 0 },
                name: "this".to_string(),
            })?.into_any())
        }
    }
}

/// Convert JSX member expression (e.g., React.Fragment)
pub fn convert_jsx_member_expression(py: Python, member: &oxc_ast::ast::JSXMemberExpression) -> PyResult<Py<PyAny>> {
    let span = member.span;
    let span_converted = Span::from(span);

    // Convert object (can be identifier or nested member expression)
    let object = if let Some(ident) = member.object.get_identifier() {
        let ident_span = ident.span;
        let ident_span_converted = Span::from(ident_span);
        let ident_name = ident.name.to_string();
        let ident_node = JSXIdentifier {
            span: ident_span_converted,
            name: ident_name,
        };
        Py::new(py, ident_node)?.into_any()
    } else {
        // For now, return a placeholder for complex object expressions
        Py::new(py, JSXIdentifier {
            span: Span { start: 0, end: 0 },
            name: "<object>".to_string(),
        })?.into_any()
    };

    let property = {
        let prop_span = member.property.span;
        let prop_span_converted = Span::from(prop_span);
        let prop_name = member.property.name.to_string();
        let prop_node = JSXIdentifier {
            span: prop_span_converted,
            name: prop_name,
        };
        Py::new(py, prop_node)?
    };

    let node = JSXMemberExpression {
        span: span_converted,
        object,
        property,
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Convert JSX attribute (name="value")
pub fn convert_jsx_attribute(py: Python, attr: &oxc_ast::ast::JSXAttribute, source: &str) -> PyResult<Py<PyAny>> {
    let span = attr.span;
    let span_converted = Span::from(span);

    // Convert attribute name (JSXAttributeName -> JSXIdentifier)
    let name = {
        // JSXAttributeName is an enum, get string representation
        let (name_span, name_str) = match &attr.name {
            oxc_ast::ast::JSXAttributeName::Identifier(ident) => {
                (ident.span, ident.name.to_string())
            }
            oxc_ast::ast::JSXAttributeName::NamespacedName(ns) => {
                (ns.span, format!("{}:{}", ns.namespace.name, ns.name))
            }
        };
        let name_span_converted = Span::from(name_span);
        let name_node = JSXIdentifier {
            span: name_span_converted,
            name: name_str,
        };
        Py::new(py, name_node)?
    };

    // Convert attribute value (if present)
    let value = attr.value.as_ref().map(|v| {
        match v {
            oxc_ast::ast::JSXAttributeValue::StringLiteral(lit) => {
                // Return as Python string through Literal
                convert_literal(py, lit, source)
            }
            oxc_ast::ast::JSXAttributeValue::ExpressionContainer(container) => {
                convert_jsx_expression_container(py, container, source)
            }
            oxc_ast::ast::JSXAttributeValue::Element(elem) => {
                convert_jsx_element(py, elem, source).map(|p| p.into_any())
            }
            oxc_ast::ast::JSXAttributeValue::Fragment(frag) => {
                convert_jsx_fragment(py, frag, source).map(|p| p.into_any())
            }
        }
    }).transpose()?;

    let node = JSXAttribute {
        span: span_converted,
        name: name.into_any(),
        value,
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Convert JSX spread attribute {...props}
pub fn convert_jsx_spread_attribute(py: Python, attr: &oxc_ast::ast::JSXSpreadAttribute, source: &str) -> PyResult<Py<PyAny>> {
    let span = attr.span;
    let span_converted = Span::from(span);

    // For now, create a simple representation of the argument
    // Full expression conversion would require more infrastructure
    let argument = {
        let arg_span = attr.argument.span();
        let arg_span_converted = Span::from(arg_span);
        let arg_name = "<expression>";
        let arg_node = expressions::Identifier::new(arg_span_converted, arg_name.to_string());
        Py::new(py, arg_node)?
    };

    let node = JSXSpreadAttribute {
        span: span_converted,
        argument: argument.into_any(),
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Convert JSX opening element
/// self_closing is passed from the parent JSXElement (based on whether closing_element is None)
pub fn convert_jsx_opening_element(py: Python, opening: &oxc_ast::ast::JSXOpeningElement, source: &str, self_closing: bool) -> PyResult<Py<JSXOpeningElement>> {
    let span = opening.span;
    let span_converted = Span::from(span);

    let name = convert_jsx_name(py, &opening.name, source)?;

    // Convert attributes
    let mut attributes = Vec::new();
    for attr in &opening.attributes {
        let attr_node = match attr {
            oxc_ast::ast::JSXAttributeItem::Attribute(attr) => {
                convert_jsx_attribute(py, attr, source)?
            }
            oxc_ast::ast::JSXAttributeItem::SpreadAttribute(spread) => {
                convert_jsx_spread_attribute(py, spread, source)?
            }
        };
        attributes.push(attr_node);
    }

    let node = JSXOpeningElement {
        span: span_converted,
        name,
        attributes,
        self_closing,
    };
    Py::new(py, node)
}

/// Convert JSX closing element
pub fn convert_jsx_closing_element(py: Python, closing: &oxc_ast::ast::JSXClosingElement, source: &str) -> PyResult<Py<JSXClosingElement>> {
    let span = closing.span;
    let span_converted = Span::from(span);

    let name = convert_jsx_name(py, &closing.name, source)?;

    let node = JSXClosingElement {
        span: span_converted,
        name,
    };
    Py::new(py, node)
}

/// Convert JSX text node
pub fn convert_jsx_text(py: Python, text: &oxc_ast::ast::JSXText, _source: &str) -> PyResult<Py<PyAny>> {
    let span = text.span;
    let span_converted = Span::from(span);

    let value = text.value.to_string();
    let raw = text.raw.as_ref().map(|r| r.to_string()).unwrap_or_else(|| value.clone());

    let node = JSXText {
        span: span_converted,
        value,
        raw,
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Convert JSX expression container {expr}
pub fn convert_jsx_expression_container(py: Python, container: &oxc_ast::ast::JSXExpressionContainer, source: &str) -> PyResult<Py<PyAny>> {
    let span = container.span;
    let span_converted = Span::from(span);

    // Properly convert the expression inside the container
    // This allows walk() to traverse into the expression and find nested JSX
    let expression = match &container.expression {
        oxc_ast::ast::JSXExpression::EmptyExpression(_) => {
            // Empty expression {} - create a placeholder
            let expr_span = Span::from(container.expression.span());
            Py::new(py, expressions::Identifier::new(expr_span, "<empty>".to_string()))?.into_any()
        }
        _ => {
            // Convert as regular expression using convert_expression
            // JSXExpression can be converted to Expression via to_expression()
            convert_expression(py, container.expression.to_expression(), source)?
        }
    };

    let node = JSXExpressionContainer {
        span: span_converted,
        expression,
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Convert JSX child (element, text, expression container, fragment)
pub fn convert_jsx_child(py: Python, child: &oxc_ast::ast::JSXChild, source: &str) -> PyResult<Py<PyAny>> {
    match child {
        oxc_ast::ast::JSXChild::Element(elem) => {
            convert_jsx_element(py, elem, source).map(|p| p.into_any())
        }
        oxc_ast::ast::JSXChild::Fragment(frag) => {
            convert_jsx_fragment(py, frag, source).map(|p| p.into_any())
        }
        oxc_ast::ast::JSXChild::Text(text) => {
            convert_jsx_text(py, text, source)
        }
        oxc_ast::ast::JSXChild::ExpressionContainer(container) => {
            convert_jsx_expression_container(py, container, source)
        }
        oxc_ast::ast::JSXChild::Spread(_) => {
            // JSX spread children {...items} - treat as expression container for now
            Ok(Py::new(py, JSXExpressionContainer {
                span: Span { start: 0, end: 0 },
                expression: Py::new(py, expressions::Identifier::new(Span { start: 0, end: 0 }, "<spread>".to_string()))?.into_any(),
            })?.into_any())
        }
    }
}

/// Convert JSX element
pub fn convert_jsx_element(py: Python, element: &oxc_ast::ast::JSXElement, source: &str) -> PyResult<Py<JSXElement>> {
    let span = element.span;
    let span_converted = Span::from(span);

    // Determine if self-closing based on whether there's a closing element
    let self_closing = element.closing_element.is_none();
    let opening_element = convert_jsx_opening_element(py, &element.opening_element, source, self_closing)?;

    let mut children = Vec::new();
    for child in &element.children {
        let child_node = convert_jsx_child(py, child, source)?;
        children.push(child_node);
    }

    let closing_element = element.closing_element.as_ref()
        .map(|closing| convert_jsx_closing_element(py, closing, source))
        .transpose()?;

    let node = JSXElement {
        span: span_converted,
        opening_element,
        children,
        closing_element,
    };
    Py::new(py, node)
}

/// Convert JSX fragment
pub fn convert_jsx_fragment(py: Python, fragment: &oxc_ast::ast::JSXFragment, source: &str) -> PyResult<Py<JSXFragment>> {
    let span = fragment.span;
    let span_converted = Span::from(span);

    let mut children = Vec::new();
    for child in &fragment.children {
        let child_node = convert_jsx_child(py, child, source)?;
        children.push(child_node);
    }

    let node = JSXFragment {
        span: span_converted,
        children,
    };
    Py::new(py, node)
}

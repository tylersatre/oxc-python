//! TypeScript type conversion functions

use pyo3::prelude::*;
use crate::{Node, Span};
use crate::nodes::typescript::{
    TSTypeReference, TSUnionType, TSIntersectionType,
    TSTypeAnnotation, TSTypeParameterDeclaration, TSTypeParameter,
    TSPropertySignature, TSMethodSignature,
    TSInterfaceBody, TSEnumMember,
};
use crate::nodes::expressions;
use crate::conversion::helpers::compute_line_number;

// =============================================================================
// Phase 16: TypeScript Type Conversion Functions
// =============================================================================

/// Convert a TypeScript type to a Python node
pub fn convert_ts_type(py: Python, ts_type: &oxc_ast::ast::TSType, source: &str) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::TSType;
    use oxc_span::GetSpan;

    let span = ts_type.span();
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);

    match ts_type {
        TSType::TSTypeReference(type_ref) => {
            let type_name = match &type_ref.type_name {
                oxc_ast::ast::TSTypeName::IdentifierReference(ident) => {
                    let ident_span = Span::from(ident.span);
                    Some(Py::new(py, expressions::Identifier::new(ident_span, ident.name.to_string()))?.into_any())
                }
                oxc_ast::ast::TSTypeName::QualifiedName(qname) => {
                    let ident_span = Span::from(qname.span());
                    Some(Py::new(py, expressions::Identifier::new(ident_span, format!("{}.{}", qname.left, qname.right.name)))?.into_any())
                }
                _ => None,
            };
            let type_parameters = type_ref.type_arguments.as_ref()
                .map(|tp| convert_ts_type_parameter_instantiation(py, tp, source))
                .transpose()?;
            Ok(Py::new(py, TSTypeReference { span: span_converted, start_line, end_line, type_name, type_parameters })?.into_any())
        }
        TSType::TSUnionType(union) => {
            let types: Vec<Py<PyAny>> = union.types.iter().filter_map(|t| convert_ts_type(py, t, source).ok()).collect();
            Ok(Py::new(py, TSUnionType { span: span_converted, start_line, end_line, types })?.into_any())
        }
        TSType::TSIntersectionType(intersection) => {
            let types: Vec<Py<PyAny>> = intersection.types.iter().filter_map(|t| convert_ts_type(py, t, source).ok()).collect();
            Ok(Py::new(py, TSIntersectionType { span: span_converted, start_line, end_line, types })?.into_any())
        }
        _ => {
            let type_str = match ts_type {
                TSType::TSAnyKeyword(_) => "TSAnyKeyword",
                TSType::TSBooleanKeyword(_) => "TSBooleanKeyword",
                TSType::TSNeverKeyword(_) => "TSNeverKeyword",
                TSType::TSNullKeyword(_) => "TSNullKeyword",
                TSType::TSNumberKeyword(_) => "TSNumberKeyword",
                TSType::TSStringKeyword(_) => "TSStringKeyword",
                TSType::TSUndefinedKeyword(_) => "TSUndefinedKeyword",
                TSType::TSUnknownKeyword(_) => "TSUnknownKeyword",
                TSType::TSVoidKeyword(_) => "TSVoidKeyword",
                _ => "TSType",
            };
            let mut node = Node::new(type_str.to_string(), span_converted);
            node.start_line = start_line;
            node.end_line = end_line;
            Ok(Py::new(py, node)?.into_any())
        }
    }
}

pub fn convert_ts_type_annotation(py: Python, ts_ann: &oxc_ast::ast::TSTypeAnnotation, source: &str) -> PyResult<Py<PyAny>> {
    let span = ts_ann.span;
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);
    let type_annotation = convert_ts_type(py, &ts_ann.type_annotation, source)?;
    Ok(Py::new(py, TSTypeAnnotation { span: span_converted, start_line, end_line, type_annotation: Some(type_annotation) })?.into_any())
}

pub fn convert_ts_type_parameter_declaration(py: Python, tp_decl: &oxc_ast::ast::TSTypeParameterDeclaration, source: &str) -> PyResult<Py<PyAny>> {
    let span = tp_decl.span;
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);
    let params: Vec<Py<PyAny>> = tp_decl.params.iter().filter_map(|p| convert_ts_type_parameter(py, p, source).ok()).collect();
    Ok(Py::new(py, TSTypeParameterDeclaration { span: span_converted, start_line, end_line, params })?.into_any())
}

pub fn convert_ts_type_parameter(py: Python, param: &oxc_ast::ast::TSTypeParameter, source: &str) -> PyResult<Py<PyAny>> {
    let span = param.span;
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);
    let name = param.name.name.to_string();
    let constraint = param.constraint.as_ref().map(|c| convert_ts_type(py, c, source)).transpose()?;
    let default = param.default.as_ref().map(|d| convert_ts_type(py, d, source)).transpose()?;
    Ok(Py::new(py, TSTypeParameter { span: span_converted, start_line, end_line, name, constraint, default })?.into_any())
}

pub fn convert_ts_type_parameter_instantiation(py: Python, tp_inst: &oxc_ast::ast::TSTypeParameterInstantiation, source: &str) -> PyResult<Py<PyAny>> {
    let span = tp_inst.span;
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);
    let params: Vec<Py<PyAny>> = tp_inst.params.iter().filter_map(|p| convert_ts_type(py, p, source).ok()).collect();
    Ok(Py::new(py, TSTypeParameterDeclaration { span: span_converted, start_line, end_line, params })?.into_any())
}

pub fn convert_ts_interface_body(py: Python, body: &oxc_ast::ast::TSInterfaceBody, source: &str) -> PyResult<Py<PyAny>> {
    let span = body.span;
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);
    let members: Vec<Py<PyAny>> = body.body.iter().filter_map(|s| convert_ts_signature(py, s, source).ok()).collect();
    Ok(Py::new(py, TSInterfaceBody { span: span_converted, start_line, end_line, body: members })?.into_any())
}

pub fn convert_ts_signature(py: Python, sig: &oxc_ast::ast::TSSignature, source: &str) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::TSSignature;
    use oxc_span::GetSpan;
    let span = sig.span();
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);

    match sig {
        TSSignature::TSPropertySignature(prop) => {
            let key = convert_ts_property_key(py, &prop.key, source)?;
            let type_annotation = prop.type_annotation.as_ref().map(|ta| convert_ts_type_annotation(py, ta, source)).transpose()?;
            Ok(Py::new(py, TSPropertySignature { span: span_converted, start_line, end_line, key: Some(key), optional: prop.optional, readonly: prop.readonly, type_annotation })?.into_any())
        }
        TSSignature::TSMethodSignature(method) => {
            let key = convert_ts_property_key(py, &method.key, source)?;
            let params: Vec<Py<PyAny>> = Vec::new();
            let return_type = method.return_type.as_ref().map(|rt| convert_ts_type_annotation(py, rt, source)).transpose()?;
            Ok(Py::new(py, TSMethodSignature { span: span_converted, start_line, end_line, key: Some(key), params, return_type })?.into_any())
        }
        _ => {
            let mut node = Node::new("TSSignature".to_string(), span_converted);
            node.start_line = start_line;
            node.end_line = end_line;
            Ok(Py::new(py, node)?.into_any())
        }
    }
}

pub fn convert_ts_property_key(py: Python, key: &oxc_ast::ast::PropertyKey, _source: &str) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::PropertyKey;
    use oxc_span::GetSpan;
    let span = key.span();
    let span_converted = Span::from(span);
    match key {
        PropertyKey::StaticIdentifier(ident) => Ok(Py::new(py, expressions::Identifier::new(span_converted, ident.name.to_string()))?.into_any()),
        PropertyKey::PrivateIdentifier(ident) => Ok(Py::new(py, expressions::Identifier::new(span_converted, format!("#{}", ident.name)))?.into_any()),
        _ => Ok(Py::new(py, expressions::Identifier::new(span_converted, "computed".to_string()))?.into_any()),
    }
}

pub fn convert_ts_interface_heritage(py: Python, heritage: &oxc_ast::ast::TSInterfaceHeritage, source: &str) -> PyResult<Py<PyAny>> {
    let span = heritage.span;
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);
    let mut node = Node::new("TSInterfaceHeritage".to_string(), span_converted);
    node.start_line = start_line;
    node.end_line = end_line;
    Ok(Py::new(py, node)?.into_any())
}

pub fn convert_ts_enum_member(py: Python, member: &oxc_ast::ast::TSEnumMember, source: &str) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::Expression;
    use oxc_span::GetSpan;
    let span = member.span;
    let span_converted = Span::from(span);
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);
    let id = match &member.id {
        oxc_ast::ast::TSEnumMemberName::Identifier(ident) => Some(Py::new(py, expressions::Identifier::new(Span::from(ident.span), ident.name.to_string()))?.into_any()),
        oxc_ast::ast::TSEnumMemberName::String(s) => Some(Py::new(py, expressions::Identifier::new(Span::from(s.span), s.value.to_string()))?.into_any()),
        _ => None,
    };
    // Convert initializer to a generic Node (preserves that initializer exists)
    let initializer = member.initializer.as_ref().map(|init| {
        let init_span = Span::from(init.span());
        let type_str = match init {
            Expression::NumericLiteral(_) => "NumericLiteral",
            Expression::StringLiteral(_) => "StringLiteral",
            _ => "Expression",
        };
        let mut node = Node::new(type_str.to_string(), init_span);
        node.start_line = compute_line_number(source, init.span().start as usize);
        node.end_line = compute_line_number(source, init.span().end as usize);
        Py::new(py, node).map(|p| p.into_any())
    }).transpose()?;
    Ok(Py::new(py, TSEnumMember { span: span_converted, start_line, end_line, id, initializer })?.into_any())
}

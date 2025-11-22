//! Statement conversion functions

use oxc_ast::ast::Statement;
use oxc_span::GetSpan;
use pyo3::prelude::*;

use crate::{
    Span,
    Node,
    FunctionDeclaration,
    ClassDeclaration,
    VariableDeclaration,
    VariableDeclarator,
    FormalParameter,
    BlockStatement,
    BreakStatement,
    ContinueStatement,
    LabeledStatement,
    EmptyStatement,
    WithStatement,
    ForStatement,
    ForInStatement,
    ForOfStatement,
    IfStatement,
    WhileStatement,
    DoWhileStatement,
    SwitchStatement,
    SwitchCase,
    TryStatement,
    CatchClause,
    ThrowStatement,
    ReturnStatement,
    ExpressionStatement,
    DebuggerStatement,
    ImportDeclaration,
    ExportNamedDeclaration,
    ExportDefaultDeclaration,
    ExportAllDeclaration,
    TSTypeAliasDeclaration,
    TSInterfaceDeclaration,
    TSEnumDeclaration,
};
use crate::nodes::expressions;

use super::{
    compute_line_number,
    convert_expression,
    convert_literal,
    convert_import_specifier,
    convert_export_specifier,
    convert_ts_type,
    convert_ts_type_annotation,
    convert_ts_type_parameter_declaration,
    convert_ts_interface_body,
    convert_ts_interface_heritage,
    convert_ts_enum_member,
};

pub fn convert_statement(stmt: &Statement, py: Python, source: &str) -> PyResult<Py<PyAny>> {
    let span = stmt.span();
    let span_converted = Span::from(span);

    // Compute line numbers
    let start_line = compute_line_number(source, span.start as usize);
    let end_line = compute_line_number(source, span.end as usize);

    // Phase 13: Return specialized node types for key statement types
    match stmt {
        Statement::FunctionDeclaration(func) => {
            let name = func.id.as_ref().map(|id| id.name.to_string());
            // Convert function body (BlockStatement)
            let body = if let Some(func_body) = &func.body {
                Some(convert_function_body(py, func_body, source)?)
            } else {
                None
            };
            // Convert parameters
            let params: Vec<Py<PyAny>> = func.params.items.iter().map(|param| {
                let param_span = Span::from(param.span);
                let param_start = compute_line_number(source, param.span.start as usize);
                let param_end = compute_line_number(source, param.span.end as usize);
                let param_name = match &param.pattern.kind {
                    oxc_ast::ast::BindingPatternKind::BindingIdentifier(ident) => Some(ident.name.to_string()),
                    _ => None,
                };
                let type_annotation = param.pattern.type_annotation.as_ref()
                    .map(|ta| convert_ts_type_annotation(py, ta, source))
                    .transpose().ok().flatten();
                Py::new(py, FormalParameter {
                    span: param_span,
                    start_line: param_start,
                    end_line: param_end,
                    name: param_name,
                    type_annotation,
                }).unwrap().into_any()
            }).collect();
            // Convert type parameters
            let type_parameters = func.type_parameters.as_ref()
                .map(|tp| convert_ts_type_parameter_declaration(py, tp, source))
                .transpose()?;
            // Convert return type
            let return_type = func.return_type.as_ref()
                .map(|rt| convert_ts_type_annotation(py, rt, source))
                .transpose()?;
            let node = FunctionDeclaration {
                span: span_converted,
                start_line,
                end_line,
                name,
                is_async: func.r#async,
                is_generator: func.generator,
                body,
                params,
                type_parameters,
                return_type,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ClassDeclaration(class) => {
            let name = class.id.as_ref().map(|id| id.name.to_string());
            // Extract superclass name if present
            let superclass = class.super_class.as_ref().and_then(|expr| {
                // Try to get identifier name from superclass expression
                if let oxc_ast::ast::Expression::Identifier(ident) = expr {
                    Some(ident.name.to_string())
                } else {
                    Some("<expression>".to_string())
                }
            });
            // Convert type parameters
            let type_parameters = class.type_parameters.as_ref()
                .map(|tp| convert_ts_type_parameter_declaration(py, tp, source))
                .transpose()?;
            // Convert class body (methods)
            let body = Some(convert_class_body(py, &class.body, source)?);
            let node = ClassDeclaration {
                span: span_converted,
                start_line,
                end_line,
                name,
                superclass,
                type_parameters,
                body,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::VariableDeclaration(var) => {
            let kind = match var.kind {
                oxc_ast::ast::VariableDeclarationKind::Const => "const",
                oxc_ast::ast::VariableDeclarationKind::Let => "let",
                oxc_ast::ast::VariableDeclarationKind::Var => "var",
                oxc_ast::ast::VariableDeclarationKind::Using => "using",
                oxc_ast::ast::VariableDeclarationKind::AwaitUsing => "await using",
            }.to_string();
            // Convert declarators
            let declarations: Vec<Py<PyAny>> = var.declarations.iter().map(|decl| {
                let decl_span = Span::from(decl.span);
                let decl_start_line = compute_line_number(source, decl.span.start as usize);
                let decl_end_line = compute_line_number(source, decl.span.end as usize);
                // Convert id (identifier)
                let id = match &decl.id.kind {
                    oxc_ast::ast::BindingPatternKind::BindingIdentifier(ident) => {
                        Some(Py::new(py, expressions::Identifier::new(Span::from(ident.span), ident.name.to_string())).unwrap().into_any())
                    }
                    _ => None,
                };
                // Convert type annotation if present
                let type_annotation = decl.id.type_annotation.as_ref()
                    .map(|ta| convert_ts_type_annotation(py, ta, source))
                    .transpose().ok().flatten();
                // Convert init expression if present using full expression conversion
                // This properly handles JSX, arrow functions, conditionals, etc.
                let init: Option<Py<PyAny>> = decl.init.as_ref()
                    .map(|init_expr| convert_expression(py, init_expr, source))
                    .transpose()
                    .ok()
                    .flatten();
                Py::new(py, VariableDeclarator {
                    span: decl_span,
                    start_line: decl_start_line,
                    end_line: decl_end_line,
                    id,
                    init,
                    type_annotation,
                }).unwrap().into_any()
            }).collect();
            let node = VariableDeclaration {
                span: span_converted,
                start_line,
                end_line,
                kind,
                declarations,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        // Phase 15: Import/Export Declarations
        Statement::ImportDeclaration(import_decl) => {
            // Convert source module path (StringLiteral)
            let source_literal = convert_literal(py, &import_decl.source, source)?;

            // Convert specifiers list
            let mut specifiers = Vec::new();
            // import_decl.specifiers is an Option<Vec>
            if let Some(specs) = &import_decl.specifiers {
                for i in 0..specs.len() {
                    let spec = &specs[i];
                    let spec_node = convert_import_specifier(py, spec, source)?;
                    specifiers.push(spec_node);
                }
            }

            let node = ImportDeclaration {
                span: span_converted,
                start_line,
                end_line,
                source: source_literal,
                specifiers,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ExportNamedDeclaration(export_named) => {
            // Convert optional declaration
            // export_named.declaration is an Option<Declaration>
            let declaration = export_named.declaration
                .as_ref()
                .map(|decl| {
                    // Convert Declaration to a Node
                    // Declaration can be FunctionDeclaration or VariableDeclaration
                    let decl_span = decl.span();
                    let span_converted = Span::from(decl_span);
                    let start_line = compute_line_number(source, decl_span.start as usize);
                    let end_line = compute_line_number(source, decl_span.end as usize);

                    match decl {
                        oxc_ast::ast::Declaration::FunctionDeclaration(func) => {
                            let name = func.id.as_ref().map(|id| id.name.to_string());
                            // Convert function body if present
                            let body = func.body.as_ref().and_then(|fb| convert_function_body(py, fb, source).ok());
                            let decl_node = FunctionDeclaration {
                                span: span_converted,
                                start_line,
                                end_line,
                                name,
                                is_async: func.r#async,
                                is_generator: func.generator,
                                body,
                                params: Vec::new(),
                                type_parameters: None,
                                return_type: None,
                            };
                            Py::new(py, decl_node).map(|p| p.into_any())
                        }
                        oxc_ast::ast::Declaration::ClassDeclaration(class) => {
                            let name = class.id.as_ref().map(|id| id.name.to_string());
                            let superclass = class.super_class.as_ref().and_then(|expr| {
                                if let oxc_ast::ast::Expression::Identifier(ident) = expr {
                                    Some(ident.name.to_string())
                                } else {
                                    Some("<expression>".to_string())
                                }
                            });
                            let body = convert_class_body(py, &class.body, source).ok();
                            let decl_node = ClassDeclaration {
                                span: span_converted,
                                start_line,
                                end_line,
                                name,
                                superclass,
                                type_parameters: None,
                                body,
                            };
                            Py::new(py, decl_node).map(|p| p.into_any())
                        }
                        oxc_ast::ast::Declaration::VariableDeclaration(var) => {
                            let kind = match var.kind {
                                oxc_ast::ast::VariableDeclarationKind::Const => "const",
                                oxc_ast::ast::VariableDeclarationKind::Let => "let",
                                oxc_ast::ast::VariableDeclarationKind::Var => "var",
                                oxc_ast::ast::VariableDeclarationKind::Using => "using",
                                oxc_ast::ast::VariableDeclarationKind::AwaitUsing => "await using",
                            }.to_string();
                            let decl_node = VariableDeclaration {
                                span: span_converted,
                                start_line,
                                end_line,
                                kind,
                                declarations: Vec::new(),
                            };
                            Py::new(py, decl_node).map(|p| p.into_any())
                        }
                        oxc_ast::ast::Declaration::TSInterfaceDeclaration(ts_interface) => {
                            let name = ts_interface.id.name.to_string();
                            let decl_node = TSInterfaceDeclaration {
                                span: span_converted,
                                start_line,
                                end_line,
                                name,
                                body: None,
                                extends: None,
                                type_parameters: None,
                            };
                            Py::new(py, decl_node).map(|p| p.into_any())
                        }
                        oxc_ast::ast::Declaration::TSTypeAliasDeclaration(ts_type) => {
                            let name = ts_type.id.name.to_string();
                            let decl_node = TSTypeAliasDeclaration {
                                span: span_converted,
                                start_line,
                                end_line,
                                name,
                                type_annotation: None,
                                type_parameters: None,
                            };
                            Py::new(py, decl_node).map(|p| p.into_any())
                        }
                        _ => {
                            // Unknown declaration type
                            let mut generic_node = Node::new("Declaration".to_string(), span_converted);
                            generic_node.start_line = start_line;
                            generic_node.end_line = end_line;
                            Py::new(py, generic_node).map(|p| p.into_any())
                        }
                    }
                })
                .transpose()?;

            // Convert specifiers
            let mut specifiers = Vec::new();
            for spec in &export_named.specifiers {
                let spec_node = convert_export_specifier(py, spec, source)?;
                specifiers.push(spec_node);
            }

            // Convert optional source for re-exports
            let source_literal = export_named.source
                .as_ref()
                .map(|src| convert_literal(py, src, source))
                .transpose()?;

            let node = ExportNamedDeclaration {
                span: span_converted,
                start_line,
                end_line,
                declaration,
                specifiers,
                source: source_literal,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ExportDefaultDeclaration(export_default) => {
            // Convert declaration (function, class, or expression)
            let decl_span = export_default.declaration.span();

            let decl_type = match &export_default.declaration {
                oxc_ast::ast::ExportDefaultDeclarationKind::FunctionDeclaration(func) => {
                    let name = func.id.as_ref().map(|id| id.name.to_string());
                    // Convert function body if present
                    let body = func.body.as_ref().and_then(|fb| convert_function_body(py, fb, source).ok());
                    let decl_node = FunctionDeclaration {
                        span: Span::from(decl_span),
                        start_line: compute_line_number(source, decl_span.start as usize),
                        end_line: compute_line_number(source, decl_span.end as usize),
                        name,
                        is_async: func.r#async,
                        is_generator: func.generator,
                        body,
                        params: Vec::new(),
                        type_parameters: None,
                        return_type: None,
                    };
                    Py::new(py, decl_node)?.into_any()
                }
                oxc_ast::ast::ExportDefaultDeclarationKind::ClassDeclaration(class) => {
                    let name = class.id.as_ref().map(|id| id.name.to_string());
                    let superclass = class.super_class.as_ref().and_then(|expr| {
                        if let oxc_ast::ast::Expression::Identifier(ident) = expr {
                            Some(ident.name.to_string())
                        } else {
                            Some("<expression>".to_string())
                        }
                    });
                    let body = convert_class_body(py, &class.body, source).ok();
                    let decl_node = ClassDeclaration {
                        span: Span::from(decl_span),
                        start_line: compute_line_number(source, decl_span.start as usize),
                        end_line: compute_line_number(source, decl_span.end as usize),
                        name,
                        superclass,
                        type_parameters: None,
                        body,
                    };
                    Py::new(py, decl_node)?.into_any()
                }
                _ => {
                    // For all other cases (expressions, etc.), create a generic Node
                    let mut generic_node = Node::new("Expression".to_string(), Span::from(decl_span));
                    generic_node.start_line = compute_line_number(source, decl_span.start as usize);
                    generic_node.end_line = compute_line_number(source, decl_span.end as usize);
                    Py::new(py, generic_node)?.into_any()
                }
            };

            let node = ExportDefaultDeclaration {
                span: span_converted,
                start_line,
                end_line,
                declaration: decl_type,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ExportAllDeclaration(export_all) => {
            // Convert source module path
            let source_literal = convert_literal(py, &export_all.source, source)?;

            // Convert optional exported identifier (ModuleExportName)
            let exported = export_all.exported
                .as_ref()
                .map(|export_name| {
                    let span = export_name.span();
                    let span_converted = Span::from(span);
                    let name = export_name.name().to_string();
                    let node = expressions::Identifier::new(span_converted, name);
                    Py::new(py, node).map(|p| p.into_any())
                })
                .transpose()?;

            let node = ExportAllDeclaration {
                span: span_converted,
                start_line,
                end_line,
                source: source_literal,
                exported,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        // Phase 16: TypeScript declarations
        Statement::TSTypeAliasDeclaration(ts_type_alias) => {
            let name = ts_type_alias.id.name.to_string();
            let type_annotation = convert_ts_type(py, &ts_type_alias.type_annotation, source)?;
            let type_parameters = ts_type_alias.type_parameters.as_ref()
                .map(|tp| convert_ts_type_parameter_declaration(py, tp, source))
                .transpose()?;
            let node = TSTypeAliasDeclaration {
                span: span_converted,
                start_line,
                end_line,
                name,
                type_annotation: Some(type_annotation),
                type_parameters,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::TSInterfaceDeclaration(ts_interface) => {
            let name = ts_interface.id.name.to_string();
            let body = convert_ts_interface_body(py, &ts_interface.body, source)?;
            let extends = if ts_interface.extends.is_empty() {
                None
            } else {
                Some(ts_interface.extends.iter().filter_map(|ext| convert_ts_interface_heritage(py, ext, source).ok()).collect::<Vec<_>>())
            };
            let type_parameters = ts_interface.type_parameters.as_ref()
                .map(|tp| convert_ts_type_parameter_declaration(py, tp, source))
                .transpose()?;
            let node = TSInterfaceDeclaration {
                span: span_converted,
                start_line,
                end_line,
                name,
                body: Some(body),
                extends,
                type_parameters,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::TSEnumDeclaration(ts_enum) => {
            let name = ts_enum.id.name.to_string();
            let members: Vec<Py<PyAny>> = ts_enum.body.members.iter()
                .filter_map(|m| convert_ts_enum_member(py, m, source).ok())
                .collect();
            let is_const = ts_enum.r#const;
            let node = TSEnumDeclaration {
                span: span_converted,
                start_line,
                end_line,
                name,
                members,
                is_const,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        // Phase 13: Additional statement types
        Statement::BreakStatement(break_stmt) => {
            let label = break_stmt.label.as_ref().map(|l| {
                let label_span = Span::from(l.span);
                Py::new(py, expressions::Identifier::new(label_span, l.name.to_string())).unwrap().into_any()
            });
            let node = BreakStatement {
                span: span_converted,
                start_line,
                end_line,
                label,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ContinueStatement(continue_stmt) => {
            let label = continue_stmt.label.as_ref().map(|l| {
                let label_span = Span::from(l.span);
                Py::new(py, expressions::Identifier::new(label_span, l.name.to_string())).unwrap().into_any()
            });
            let node = ContinueStatement {
                span: span_converted,
                start_line,
                end_line,
                label,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::LabeledStatement(labeled_stmt) => {
            let label = {
                let label_span = Span::from(labeled_stmt.label.span);
                Some(Py::new(py, expressions::Identifier::new(label_span, labeled_stmt.label.name.to_string())).unwrap().into_any())
            };
            let body = Some(convert_statement(&labeled_stmt.body, py, source)?);
            let node = LabeledStatement {
                span: span_converted,
                start_line,
                end_line,
                label,
                body,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::EmptyStatement(_) => {
            let node = EmptyStatement {
                span: span_converted,
                start_line,
                end_line,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::WithStatement(with_stmt) => {
            // Convert expression to a generic node for now
            let object_span = Span::from(with_stmt.object.span());
            let object_start = compute_line_number(source, with_stmt.object.span().start as usize);
            let object_end = compute_line_number(source, with_stmt.object.span().end as usize);
            let mut object_node = Node::new("Expression".to_string(), object_span);
            object_node.start_line = object_start;
            object_node.end_line = object_end;
            let object = Some(Py::new(py, object_node)?.into_any());
            let body = Some(convert_statement(&with_stmt.body, py, source)?);
            let node = WithStatement {
                span: span_converted,
                start_line,
                end_line,
                object,
                body,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ForStatement(for_stmt) => {
            // Convert init (can be VariableDeclaration or Expression)
            let init = for_stmt.init.as_ref().map(|i| {
                let init_span = i.span();
                convert_for_statement_init(py, i, source).unwrap_or_else(|_| {
                    let mut node = Node::new("Expression".to_string(), Span::from(init_span));
                    node.start_line = compute_line_number(source, init_span.start as usize);
                    node.end_line = compute_line_number(source, init_span.end as usize);
                    Py::new(py, node).unwrap().into_any()
                })
            });
            // Convert test expression
            let test = for_stmt.test.as_ref().map(|t| {
                convert_expression(py, t, source).unwrap_or_else(|_| {
                    let mut node = Node::new("Expression".to_string(), Span::from(t.span()));
                    node.start_line = compute_line_number(source, t.span().start as usize);
                    node.end_line = compute_line_number(source, t.span().end as usize);
                    Py::new(py, node).unwrap().into_any()
                })
            });
            // Convert update expression
            let update = for_stmt.update.as_ref().map(|u| {
                convert_expression(py, u, source).unwrap_or_else(|_| {
                    let mut node = Node::new("Expression".to_string(), Span::from(u.span()));
                    node.start_line = compute_line_number(source, u.span().start as usize);
                    node.end_line = compute_line_number(source, u.span().end as usize);
                    Py::new(py, node).unwrap().into_any()
                })
            });
            let body = Some(convert_statement(&for_stmt.body, py, source)?);
            let node = ForStatement {
                span: span_converted,
                start_line,
                end_line,
                init,
                test,
                update,
                body,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ForInStatement(for_in_stmt) => {
            let left = Some(convert_for_statement_left(py, &for_in_stmt.left, source)?);
            let right = Some(convert_expression(py, &for_in_stmt.right, source)?);
            let body = Some(convert_statement(&for_in_stmt.body, py, source)?);
            let node = ForInStatement {
                span: span_converted,
                start_line,
                end_line,
                left,
                right,
                body,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ForOfStatement(for_of_stmt) => {
            let left = Some(convert_for_statement_left(py, &for_of_stmt.left, source)?);
            let right = Some(convert_expression(py, &for_of_stmt.right, source)?);
            let body = Some(convert_statement(&for_of_stmt.body, py, source)?);
            let node = ForOfStatement {
                span: span_converted,
                start_line,
                end_line,
                left,
                right,
                body,
                is_await: for_of_stmt.r#await,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::IfStatement(if_stmt) => {
            let test = Some(convert_expression(py, &if_stmt.test, source)?);
            let consequent = Some(convert_statement(&if_stmt.consequent, py, source)?);
            let alternate = if_stmt.alternate.as_ref()
                .map(|alt| convert_statement(alt, py, source))
                .transpose()?;
            let node = IfStatement {
                span: span_converted,
                start_line,
                end_line,
                test,
                consequent,
                alternate,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::WhileStatement(while_stmt) => {
            let test = Some(convert_expression(py, &while_stmt.test, source)?);
            let body = Some(convert_statement(&while_stmt.body, py, source)?);
            let node = WhileStatement {
                span: span_converted,
                start_line,
                end_line,
                test,
                body,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::DoWhileStatement(do_while_stmt) => {
            let body = Some(convert_statement(&do_while_stmt.body, py, source)?);
            let test = Some(convert_expression(py, &do_while_stmt.test, source)?);
            let node = DoWhileStatement {
                span: span_converted,
                start_line,
                end_line,
                body,
                test,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::SwitchStatement(switch_stmt) => {
            let discriminant = Some(convert_expression(py, &switch_stmt.discriminant, source)?);
            let cases: Vec<Py<PyAny>> = switch_stmt.cases.iter()
                .map(|case| convert_switch_case(py, case, source))
                .collect::<PyResult<Vec<_>>>()?;
            let node = SwitchStatement {
                span: span_converted,
                start_line,
                end_line,
                discriminant,
                cases,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::TryStatement(try_stmt) => {
            let block = Some(convert_block_statement(py, &try_stmt.block, source)?);
            let handler = try_stmt.handler.as_ref()
                .map(|h| convert_catch_clause(py, h, source))
                .transpose()?;
            let finalizer = try_stmt.finalizer.as_ref()
                .map(|f| convert_block_statement(py, f, source))
                .transpose()?;
            let node = TryStatement {
                span: span_converted,
                start_line,
                end_line,
                block,
                handler,
                finalizer,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ThrowStatement(throw_stmt) => {
            let argument = Some(convert_expression(py, &throw_stmt.argument, source)?);
            let node = ThrowStatement {
                span: span_converted,
                start_line,
                end_line,
                argument,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ReturnStatement(return_stmt) => {
            let argument = return_stmt.argument.as_ref()
                .map(|a| convert_expression(py, a, source))
                .transpose()?;
            let node = ReturnStatement {
                span: span_converted,
                start_line,
                end_line,
                argument,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::ExpressionStatement(expr_stmt) => {
            let expression = Some(convert_expression(py, &expr_stmt.expression, source)?);
            let node = ExpressionStatement {
                span: span_converted,
                start_line,
                end_line,
                expression,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::DebuggerStatement(_) => {
            let node = DebuggerStatement {
                span: span_converted,
                start_line,
                end_line,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        Statement::BlockStatement(block_stmt) => {
            // Convert all statements in the block
            let mut body_stmts = Vec::new();
            for stmt in &block_stmt.body {
                let converted = convert_statement(stmt, py, source)?;
                body_stmts.push(converted);
            }
            let node = BlockStatement {
                span: span_converted,
                start_line,
                end_line,
                body: body_stmts,
            };
            Ok(Py::new(py, node)?.into_any())
        }
        // Default: return generic Node for other statement types
        _ => {
            let type_str = get_statement_type_str(stmt);
            let mut node = Node::new(type_str.to_string(), span_converted);
            node.start_line = start_line;
            node.end_line = end_line;
            Ok(Py::new(py, node)?.into_any())
        }
    }
}

pub fn convert_for_statement_init(py: Python, init: &oxc_ast::ast::ForStatementInit, source: &str) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::ForStatementInit;
    match init {
        ForStatementInit::VariableDeclaration(var) => {
            let span_converted = Span::from(var.span);
            let start_line = compute_line_number(source, var.span.start as usize);
            let end_line = compute_line_number(source, var.span.end as usize);
            let kind = match var.kind {
                oxc_ast::ast::VariableDeclarationKind::Const => "const",
                oxc_ast::ast::VariableDeclarationKind::Let => "let",
                oxc_ast::ast::VariableDeclarationKind::Var => "var",
                oxc_ast::ast::VariableDeclarationKind::Using => "using",
                oxc_ast::ast::VariableDeclarationKind::AwaitUsing => "await using",
            }.to_string();
            let node = VariableDeclaration {
                span: span_converted,
                start_line,
                end_line,
                kind,
                declarations: Vec::new(),
            };
            Ok(Py::new(py, node)?.into_any())
        }
        _ => {
            // Expression init
            let expr_span = init.span();
            let mut node = Node::new("Expression".to_string(), Span::from(expr_span));
            node.start_line = compute_line_number(source, expr_span.start as usize);
            node.end_line = compute_line_number(source, expr_span.end as usize);
            Ok(Py::new(py, node)?.into_any())
        }
    }
}

/// Helper function to convert ForStatementLeft
pub fn convert_for_statement_left(py: Python, left: &oxc_ast::ast::ForStatementLeft, source: &str) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::ForStatementLeft;
    match left {
        ForStatementLeft::VariableDeclaration(var) => {
            let span_converted = Span::from(var.span);
            let start_line = compute_line_number(source, var.span.start as usize);
            let end_line = compute_line_number(source, var.span.end as usize);
            let kind = match var.kind {
                oxc_ast::ast::VariableDeclarationKind::Const => "const",
                oxc_ast::ast::VariableDeclarationKind::Let => "let",
                oxc_ast::ast::VariableDeclarationKind::Var => "var",
                oxc_ast::ast::VariableDeclarationKind::Using => "using",
                oxc_ast::ast::VariableDeclarationKind::AwaitUsing => "await using",
            }.to_string();
            let node = VariableDeclaration {
                span: span_converted,
                start_line,
                end_line,
                kind,
                declarations: Vec::new(),
            };
            Ok(Py::new(py, node)?.into_any())
        }
        _ => {
            // AssignmentTarget
            let target_span = left.span();
            let mut node = Node::new("AssignmentTarget".to_string(), Span::from(target_span));
            node.start_line = compute_line_number(source, target_span.start as usize);
            node.end_line = compute_line_number(source, target_span.end as usize);
            Ok(Py::new(py, node)?.into_any())
        }
    }
}

/// Helper function to convert SwitchCase
pub fn convert_switch_case(py: Python, case: &oxc_ast::ast::SwitchCase, source: &str) -> PyResult<Py<PyAny>> {
    let case_span = case.span;
    let span_converted = Span::from(case_span);
    let start_line = compute_line_number(source, case_span.start as usize);
    let end_line = compute_line_number(source, case_span.end as usize);

    let test = case.test.as_ref()
        .map(|t| convert_expression(py, t, source))
        .transpose()?;

    let consequent: Vec<Py<PyAny>> = case.consequent.iter()
        .map(|stmt| convert_statement(stmt, py, source))
        .collect::<PyResult<Vec<_>>>()?;

    let node = SwitchCase {
        span: span_converted,
        start_line,
        end_line,
        test,
        consequent,
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Helper function to convert CatchClause
pub fn convert_catch_clause(py: Python, clause: &oxc_ast::ast::CatchClause, source: &str) -> PyResult<Py<PyAny>> {
    let clause_span = clause.span;
    let span_converted = Span::from(clause_span);
    let start_line = compute_line_number(source, clause_span.start as usize);
    let end_line = compute_line_number(source, clause_span.end as usize);

    let param = clause.param.as_ref().map(|p| {
        let param_span = p.span();
        let name = match &p.pattern.kind {
            oxc_ast::ast::BindingPatternKind::BindingIdentifier(ident) => ident.name.to_string(),
            _ => "param".to_string(),
        };
        Py::new(py, expressions::Identifier::new(Span::from(param_span), name)).unwrap().into_any()
    });

    let body = Some(convert_block_statement(py, &clause.body, source)?);

    let node = CatchClause {
        span: span_converted,
        start_line,
        end_line,
        param,
        body,
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Helper function to convert BlockStatement
pub fn convert_block_statement(py: Python, block: &oxc_ast::ast::BlockStatement, source: &str) -> PyResult<Py<PyAny>> {
    let span_converted = Span::from(block.span);
    let start_line = compute_line_number(source, block.span.start as usize);
    let end_line = compute_line_number(source, block.span.end as usize);

    let body: Vec<Py<PyAny>> = block.body.iter()
        .map(|stmt| convert_statement(stmt, py, source))
        .collect::<PyResult<Vec<_>>>()?;

    let node = BlockStatement {
        span: span_converted,
        start_line,
        end_line,
        body,
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Helper function to get statement type string
pub fn get_statement_type_str(stmt: &Statement) -> &'static str {
    use oxc_ast::ast::Statement as S;
    match stmt {
        S::BlockStatement(_) => "BlockStatement",
        S::BreakStatement(_) => "BreakStatement",
        S::ContinueStatement(_) => "ContinueStatement",
        S::DebuggerStatement(_) => "DebuggerStatement",
        S::DoWhileStatement(_) => "DoWhileStatement",
        S::EmptyStatement(_) => "EmptyStatement",
        S::ExpressionStatement(_) => "ExpressionStatement",
        S::ForInStatement(_) => "ForInStatement",
        S::ForOfStatement(_) => "ForOfStatement",
        S::ForStatement(_) => "ForStatement",
        S::IfStatement(_) => "IfStatement",
        S::LabeledStatement(_) => "LabeledStatement",
        S::ReturnStatement(_) => "ReturnStatement",
        S::SwitchStatement(_) => "SwitchStatement",
        S::ThrowStatement(_) => "ThrowStatement",
        S::TryStatement(_) => "TryStatement",
        S::WhileStatement(_) => "WhileStatement",
        S::WithStatement(_) => "WithStatement",
        S::VariableDeclaration(_) => "VariableDeclaration",
        S::FunctionDeclaration(_) => "FunctionDeclaration",
        S::ClassDeclaration(_) => "ClassDeclaration",
        S::ImportDeclaration(_) => "ImportDeclaration",
        S::ExportAllDeclaration(_) => "ExportAllDeclaration",
        S::ExportDefaultDeclaration(_) => "ExportDefaultDeclaration",
        S::ExportNamedDeclaration(_) => "ExportNamedDeclaration",
        S::TSTypeAliasDeclaration(_) => "TSTypeAliasDeclaration",
        S::TSInterfaceDeclaration(_) => "TSInterfaceDeclaration",
        S::TSEnumDeclaration(_) => "TSEnumDeclaration",
        S::TSModuleDeclaration(_) => "TSModuleDeclaration",
        S::TSImportEqualsDeclaration(_) => "TSImportEqualsDeclaration",
        S::TSExportAssignment(_) => "TSExportAssignment",
        S::TSNamespaceExportDeclaration(_) => "TSNamespaceExportDeclaration",
    }
}

/// Helper function to convert function body (FunctionBody -> BlockStatement)
pub fn convert_function_body(
    py: Python,
    body: &oxc_ast::ast::FunctionBody,
    source: &str,
) -> PyResult<Py<PyAny>> {
    let span_converted = Span::from(body.span);
    let start_line = compute_line_number(source, body.span.start as usize);
    let end_line = compute_line_number(source, body.span.end as usize);

    let body_stmts: Vec<Py<PyAny>> = body.statements.iter()
        .map(|stmt| convert_statement(stmt, py, source))
        .collect::<PyResult<Vec<_>>>()?;

    let node = BlockStatement {
        span: span_converted,
        start_line,
        end_line,
        body: body_stmts,
    };
    Ok(Py::new(py, node)?.into_any())
}

/// Helper function to convert class body (ClassBody -> list of methods/properties)
pub fn convert_class_body(
    py: Python,
    body: &oxc_ast::ast::ClassBody,
    source: &str,
) -> PyResult<Py<PyAny>> {
    use oxc_ast::ast::ClassElement;

    let span_converted = Span::from(body.span);
    let start_line = compute_line_number(source, body.span.start as usize);
    let end_line = compute_line_number(source, body.span.end as usize);

    let mut methods: Vec<Py<PyAny>> = Vec::new();

    for element in &body.body {
        match element {
            ClassElement::MethodDefinition(method) => {
                let method_span = Span::from(method.span);
                let method_start = compute_line_number(source, method.span.start as usize);
                let method_end = compute_line_number(source, method.span.end as usize);

                let name = method.key.static_name().map(|n| n.to_string());
                let is_async = method.value.r#async;
                let is_generator = method.value.generator;

                let function_body = method.value.body.as_ref()
                    .and_then(|fb| convert_function_body(py, fb, source).ok());

                let params: Vec<Py<PyAny>> = method.value.params.items.iter().map(|param| {
                    let param_span = Span::from(param.span);
                    let param_start = compute_line_number(source, param.span.start as usize);
                    let param_end = compute_line_number(source, param.span.end as usize);
                    let param_name = match &param.pattern.kind {
                        oxc_ast::ast::BindingPatternKind::BindingIdentifier(ident) => Some(ident.name.to_string()),
                        _ => None,
                    };
                    Py::new(py, FormalParameter {
                        span: param_span,
                        start_line: param_start,
                        end_line: param_end,
                        name: param_name,
                        type_annotation: None,
                    }).unwrap().into_any()
                }).collect();

                let method_node = crate::MethodDefinition {
                    span: method_span,
                    start_line: method_start,
                    end_line: method_end,
                    name,
                    is_async,
                    is_generator,
                    function_body,
                    params,
                };
                methods.push(Py::new(py, method_node)?.into_any());
            }
            _ => {
                // Skip other class elements for now (properties, static blocks, etc.)
            }
        }
    }

    // Return ClassBody struct with methods exposed
    let class_body = crate::ClassBody {
        span: span_converted,
        start_line,
        end_line,
        methods,
    };
    Ok(Py::new(py, class_body)?.into_any())
}

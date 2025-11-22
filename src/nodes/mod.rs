//! AST node type definitions
//!
//! This module contains all AST node struct definitions for JavaScript, TypeScript, and JSX.

// Node definition modules
pub mod statements;
pub mod expressions;
pub mod jsx;
pub mod typescript;

// Re-export all statement node types
pub use statements::{
    BlockStatement, BreakStatement, CatchClause, ClassBody, ClassDeclaration, ContinueStatement,
    DebuggerStatement, DoWhileStatement, EmptyStatement, ExportAllDeclaration,
    ExportDefaultDeclaration, ExportNamedDeclaration, ExportSpecifier, ExpressionStatement,
    ForInStatement, ForOfStatement, ForStatement, FormalParameter, FunctionDeclaration,
    IfStatement, ImportDeclaration, ImportDefaultSpecifier, ImportNamespaceSpecifier,
    ImportSpecifier, LabeledStatement, MethodDefinition, ReturnStatement, SwitchCase,
    SwitchStatement, ThrowStatement, TryStatement, VariableDeclaration, VariableDeclarator,
    WhileStatement, WithStatement,
};

// Re-export all expression node types
pub use expressions::{
    ArrowFunctionExpression, ArrayExpression, BinaryExpression, CallExpression,
    ConditionalExpression, Identifier, Literal, MemberExpression, ObjectExpression,
    UnaryExpression,
};

// Re-export all JSX node types
pub use jsx::{
    JSXAttribute, JSXClosingElement, JSXElement, JSXExpressionContainer, JSXFragment,
    JSXIdentifier, JSXMemberExpression, JSXOpeningElement, JSXSpreadAttribute, JSXText,
};

// Re-export all TypeScript node types
pub use typescript::{
    TSEnumDeclaration, TSEnumMember, TSInterfaceBody, TSInterfaceDeclaration,
    TSIntersectionType, TSMethodSignature, TSPropertySignature, TSTypeAliasDeclaration,
    TSTypeAnnotation, TSTypeParameter, TSTypeParameterDeclaration, TSTypeReference,
    TSUnionType,
};

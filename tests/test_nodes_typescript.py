"""
Test suite for TypeScript-specific AST node types.

This module combines tests from test_phase_16_typescript_nodes.py (76 tests),
validating TypeScript-specific AST nodes including type annotations, interfaces,
type aliases, enums, and TypeScript-only syntax.
"""

from oxc_python import parse, walk

"""
Phase 16: TypeScript-Specific AST Nodes

Tests for TypeScript-specific node types including type aliases, interfaces,
enums, type annotations, and type parameters.

This phase is critical for ChunkHound integration, as it explicitly maps:
- TSTypeAliasDeclaration -> ChunkType.TYPE
- TSInterfaceDeclaration -> ChunkType.INTERFACE
"""


def find_node(program, node_type):
    """Helper to find first node of given type in AST."""
    for node, _ in walk(program):
        if node.type == node_type:
            return node
    return None


def find_all_nodes(program, node_type):
    """Helper to find all nodes of given type in AST."""
    return [node for node, _ in walk(program) if node.type == node_type]


def test_ts_type_alias_declaration():
    """RED: Parse TypeScript type alias declarations"""
    source = "type UserId = string;"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Find TSTypeAliasDeclaration node
    type_alias = find_node(result.program, "TSTypeAliasDeclaration")

    assert type_alias is not None, "Should find TSTypeAliasDeclaration"
    assert hasattr(type_alias, "name")
    assert type_alias.name == "UserId"
    assert type_alias.type == "TSTypeAliasDeclaration"


def test_ts_type_alias_complex():
    """RED: Parse complex type aliases with generics"""
    source = """
type Result<T, E = Error> =
    | { ok: true; value: T }
    | { ok: false; error: E };
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    type_alias = find_node(result.program, "TSTypeAliasDeclaration")

    assert type_alias is not None
    assert type_alias.name == "Result"


def test_ts_interface_declaration():
    """RED: Parse TypeScript interface declarations"""
    source = """
interface User {
    id: number;
    name: string;
    email?: string;
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Find TSInterfaceDeclaration node
    interface = find_node(result.program, "TSInterfaceDeclaration")

    assert interface is not None, "Should find TSInterfaceDeclaration"
    assert hasattr(interface, "name")
    assert interface.name == "User"
    assert interface.type == "TSInterfaceDeclaration"


def test_ts_interface_extends():
    """RED: Parse interfaces with extends clause"""
    source = """
interface Admin extends User {
    role: string;
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    interface = find_node(result.program, "TSInterfaceDeclaration")

    assert interface is not None
    assert interface.name == "Admin"


def test_ts_enum_declaration():
    """RED: Parse TypeScript enum declarations"""
    source = """
enum Color {
    Red,
    Green,
    Blue
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Find TSEnumDeclaration node
    enum = find_node(result.program, "TSEnumDeclaration")

    assert enum is not None, "Should find TSEnumDeclaration"
    assert hasattr(enum, "name")
    assert enum.name == "Color"
    assert enum.type == "TSEnumDeclaration"


def test_ts_enum_with_values():
    """RED: Parse enum with explicit values"""
    source = """
enum HttpStatus {
    OK = 200,
    NotFound = 404,
    ServerError = 500
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    enum = find_node(result.program, "TSEnumDeclaration")

    assert enum is not None
    assert enum.name == "HttpStatus"


def test_ts_type_annotation():
    """RED: Parse type annotations on variables"""
    source = "const count: number = 42;"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Should find TSTypeAnnotation node in AST
    type_annotation = find_node(result.program, "TSTypeAnnotation")

    assert type_annotation is not None, "Should find TSTypeAnnotation"


def test_ts_type_annotation_function():
    """RED: Parse type annotations on function parameters"""
    source = "function greet(name: string): void {}"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Should have type annotations for param and return type
    annotations = find_all_nodes(result.program, "TSTypeAnnotation")
    assert len(annotations) >= 2  # param type + return type


def test_ts_type_reference():
    """RED: Parse type references"""
    source = "const user: User = { id: 1 };"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Find TSTypeReference node
    type_ref = find_node(result.program, "TSTypeReference")

    assert type_ref is not None, "Should find TSTypeReference"


def test_ts_type_reference_generic():
    """RED: Parse generic type references"""
    source = "const items: Array<string> = [];"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    type_ref = find_node(result.program, "TSTypeReference")

    assert type_ref is not None


def test_ts_type_parameter():
    """RED: Parse type parameters on generics"""
    source = "function identity<T>(value: T): T { return value; }"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Find TSTypeParameter node
    type_param = find_node(result.program, "TSTypeParameter")

    assert type_param is not None, "Should find TSTypeParameter"


def test_ts_type_parameter_constraint():
    """RED: Parse type parameters with constraints"""
    source = "function extend<T extends object>(obj: T): T & { id: number } { return obj; }"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    type_param = find_node(result.program, "TSTypeParameter")

    assert type_param is not None


def test_ts_type_parameter_default():
    """RED: Parse type parameters with defaults"""
    source = "class Container<T = string> {}"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    type_param = find_node(result.program, "TSTypeParameter")

    assert type_param is not None


def test_ts_property_signature():
    """RED: Parse interface property signatures"""
    source = """
interface Config {
    readonly port: number;
    host?: string;
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Find TSPropertySignature nodes
    prop_sigs = find_all_nodes(result.program, "TSPropertySignature")

    assert len(prop_sigs) >= 2


def test_ts_method_signature():
    """RED: Parse interface method signatures"""
    source = """
interface Logger {
    log(message: string): void;
    error(message: string, code?: number): void;
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Find TSMethodSignature nodes
    method_sigs = find_all_nodes(result.program, "TSMethodSignature")

    assert len(method_sigs) >= 2


def test_ts_decorator():
    """RED: Parse TypeScript decorators"""
    source = """
@sealed
class BugReport {
    @required
    title: string;

    @validate
    submit() {}
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Decorators should be in AST (exact node type may vary)
    # This test ensures decorators don't cause parse errors
    class_decl = find_node(result.program, "ClassDeclaration")

    assert class_decl is not None


def test_chunkhound_ts_type_mapping():
    """ChunkHound: Verify node types for chunk mapping"""
    source = """
type UserId = string;

interface User {
    id: UserId;
    name: string;
}

enum Role {
    Admin,
    User
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # ChunkHound's _map_chunk_type() expects these node types
    node_types = [node.type for node, _ in walk(result.program)]

    assert "TSTypeAliasDeclaration" in node_types
    assert "TSInterfaceDeclaration" in node_types
    assert "TSEnumDeclaration" in node_types


def test_chunkhound_ts_symbol_extraction():
    """ChunkHound: Verify nodes have name property for symbol extraction"""
    source = """
type UserId = string;

interface User {
    id: UserId;
    name: string;
}

enum Role {
    Admin,
    User
}
"""
    result = parse(source, source_type="tsx")

    assert result.is_valid

    # Verify nodes have name property for symbol extraction
    for node, _ in walk(result.program):
        if node.type in ["TSTypeAliasDeclaration", "TSInterfaceDeclaration", "TSEnumDeclaration"]:
            assert hasattr(node, "name"), f"{node.type} should have 'name' property"
            assert isinstance(node.name, str), f"{node.type}.name should be string"
            assert len(node.name) > 0, f"{node.type}.name should be non-empty"


def test_ts_type_alias_has_span():
    """RED: TSTypeAliasDeclaration should have span properties"""
    source = "type UserId = string;"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    type_alias = find_node(result.program, "TSTypeAliasDeclaration")

    assert type_alias is not None
    assert hasattr(type_alias, "span")
    assert hasattr(type_alias, "start_line")
    assert hasattr(type_alias, "end_line")
    assert type_alias.start_line > 0
    assert type_alias.end_line >= type_alias.start_line


def test_ts_type_alias_get_text():
    """RED: TSTypeAliasDeclaration should have get_text() method"""
    source = "type UserId = string;"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    type_alias = find_node(result.program, "TSTypeAliasDeclaration")

    assert type_alias is not None
    assert hasattr(type_alias, "get_text")
    text = type_alias.get_text(source)
    assert "type UserId" in text or "UserId" in text


def test_ts_type_alias_get_line_range():
    """RED: TSTypeAliasDeclaration should have get_line_range() method"""
    source = "type UserId = string;"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    type_alias = find_node(result.program, "TSTypeAliasDeclaration")

    assert type_alias is not None
    assert hasattr(type_alias, "get_line_range")
    start_line, end_line = type_alias.get_line_range(source)
    assert start_line > 0
    assert end_line >= start_line


def test_ts_interface_has_span():
    """RED: TSInterfaceDeclaration should have span properties"""
    source = "interface User { id: number; }"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    interface = find_node(result.program, "TSInterfaceDeclaration")

    assert interface is not None
    assert hasattr(interface, "span")
    assert hasattr(interface, "start_line")
    assert hasattr(interface, "end_line")


def test_ts_enum_has_span():
    """RED: TSEnumDeclaration should have span properties"""
    source = "enum Color { Red, Green, Blue }"
    result = parse(source, source_type="tsx")

    assert result.is_valid

    enum = find_node(result.program, "TSEnumDeclaration")

    assert enum is not None
    assert hasattr(enum, "span")
    assert hasattr(enum, "start_line")
    assert hasattr(enum, "end_line")


# =============================================================================
# PHASE 16 TDD RED PHASE - MISSING INTERMEDIATE TYPE NODES
# =============================================================================
# These tests verify that intermediate TypeScript type nodes appear in walk()
# traversal. Currently these are FAILING because the implementation doesn't
# expose these nodes during tree traversal.
# =============================================================================


class TestTSTypeAnnotationInWalk:
    """Tests for TSTypeAnnotation appearing in walk() traversal"""

    def test_ts_type_annotation_on_variable_in_walk(self):
        """RED: TSTypeAnnotation should appear when variables have type annotations"""
        source = 'const x: string = "hello";'
        result = parse(source, source_type="tsx")

        assert result.is_valid

        # Collect all node types from walk
        node_types = [node.type for node, _ in walk(result.program)]

        assert "TSTypeAnnotation" in node_types, (
            "TSTypeAnnotation should appear in walk() for typed variable. "
            f"Found types: {node_types}"
        )

    def test_ts_type_annotation_has_type_annotation_field(self):
        """RED: TSTypeAnnotation node should have type_annotation field"""
        source = "const count: number = 42;"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_annotation = find_node(result.program, "TSTypeAnnotation")

        assert type_annotation is not None, "Should find TSTypeAnnotation in walk()"
        assert hasattr(type_annotation, "type_annotation"), (
            "TSTypeAnnotation should have 'type_annotation' field for the inner type"
        )

    def test_ts_type_annotation_on_function_param_in_walk(self):
        """RED: TSTypeAnnotation should appear for function parameter types"""
        source = "function greet(name: string, age: number): void {}"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        # Should have at least 3 type annotations: name, age, return type
        type_annotations = find_all_nodes(result.program, "TSTypeAnnotation")

        assert len(type_annotations) >= 3, (
            f"Should have 3+ TSTypeAnnotation nodes (2 params + return type). "
            f"Found: {len(type_annotations)}"
        )

    def test_ts_type_annotation_get_text(self):
        """RED: TSTypeAnnotation should support get_text()"""
        source = "const x: string = 'hello';"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_annotation = find_node(result.program, "TSTypeAnnotation")

        assert type_annotation is not None, "Should find TSTypeAnnotation"
        assert hasattr(type_annotation, "get_text"), "TSTypeAnnotation should have get_text()"
        text = type_annotation.get_text(source)
        assert "string" in text, f"get_text() should include 'string', got: {text}"

    def test_ts_type_annotation_get_line_range(self):
        """RED: TSTypeAnnotation should support get_line_range()"""
        source = "const x: string = 'hello';"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_annotation = find_node(result.program, "TSTypeAnnotation")

        assert type_annotation is not None, "Should find TSTypeAnnotation"
        assert hasattr(type_annotation, "get_line_range"), (
            "TSTypeAnnotation should have get_line_range()"
        )
        start_line, end_line = type_annotation.get_line_range(source)
        assert start_line == 1
        assert end_line >= start_line


class TestTSTypeReferenceInWalk:
    """Tests for TSTypeReference appearing in walk() traversal"""

    def test_ts_type_reference_in_walk(self):
        """RED: TSTypeReference should appear for named type references"""
        source = "const user: User = { id: 1 };"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node_types = [node.type for node, _ in walk(result.program)]

        assert "TSTypeReference" in node_types, (
            f"TSTypeReference should appear in walk() for 'User' type. Found types: {node_types}"
        )

    def test_ts_type_reference_has_type_name(self):
        """RED: TSTypeReference should have type_name property"""
        source = "const user: MyType = null;"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_ref = find_node(result.program, "TSTypeReference")

        assert type_ref is not None, "Should find TSTypeReference in walk()"
        assert hasattr(type_ref, "type_name"), "TSTypeReference should have 'type_name' field"
        # type_name could be string or an Identifier node
        name = type_ref.type_name
        if hasattr(name, "name"):
            name = name.name
        assert name == "MyType" or "MyType" in str(name), (
            f"TSTypeReference.type_name should be 'MyType', got: {name}"
        )

    def test_ts_type_reference_generic_has_type_parameters(self):
        """RED: TSTypeReference for generics should have type_parameters"""
        source = "const items: Array<string> = [];"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_ref = find_node(result.program, "TSTypeReference")

        assert type_ref is not None, "Should find TSTypeReference in walk()"
        assert hasattr(type_ref, "type_parameters"), (
            "TSTypeReference should have 'type_parameters' field for generic types"
        )

    def test_ts_type_reference_qualified_name(self):
        """RED: TSTypeReference with qualified name (React.FC)"""
        source = "const App: React.FC<Props> = () => null;"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_ref = find_node(result.program, "TSTypeReference")

        assert type_ref is not None, "Should find TSTypeReference for React.FC"

    def test_ts_type_reference_get_text(self):
        """RED: TSTypeReference should support get_text()"""
        source = "const items: Array<string> = [];"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_ref = find_node(result.program, "TSTypeReference")

        assert type_ref is not None, "Should find TSTypeReference"
        assert hasattr(type_ref, "get_text"), "TSTypeReference should have get_text()"
        text = type_ref.get_text(source)
        assert "Array" in text, f"get_text() should include 'Array', got: {text}"


class TestTSTypeParameterInWalk:
    """Tests for TSTypeParameter appearing in walk() traversal"""

    def test_ts_type_parameter_on_function_in_walk(self):
        """RED: TSTypeParameter should appear for generic functions"""
        source = "function identity<T>(value: T): T { return value; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node_types = [node.type for node, _ in walk(result.program)]

        assert "TSTypeParameter" in node_types, (
            "TSTypeParameter should appear in walk() for generic function. "
            f"Found types: {node_types}"
        )

    def test_ts_type_parameter_has_name(self):
        """RED: TSTypeParameter should have name property"""
        source = "function identity<T>(value: T): T { return value; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_param = find_node(result.program, "TSTypeParameter")

        assert type_param is not None, "Should find TSTypeParameter in walk()"
        assert hasattr(type_param, "name"), "TSTypeParameter should have 'name' field"
        name = type_param.name
        if hasattr(name, "name"):
            name = name.name
        assert name == "T" or "T" in str(name), f"TSTypeParameter.name should be 'T', got: {name}"

    def test_ts_type_parameter_with_constraint_has_constraint_field(self):
        """RED: TSTypeParameter with constraint should have constraint field"""
        source = "function clone<T extends object>(obj: T): T { return obj; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_param = find_node(result.program, "TSTypeParameter")

        assert type_param is not None, "Should find TSTypeParameter in walk()"
        assert hasattr(type_param, "constraint"), (
            "TSTypeParameter should have 'constraint' field for 'extends' clause"
        )
        # The constraint should be non-None for "T extends object"
        assert type_param.constraint is not None, (
            "TSTypeParameter.constraint should be non-None for 'T extends object'"
        )

    def test_ts_type_parameter_with_default_has_default_field(self):
        """RED: TSTypeParameter with default should have default field"""
        source = "class Container<T = string> { value: T; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_param = find_node(result.program, "TSTypeParameter")

        assert type_param is not None, "Should find TSTypeParameter in walk()"
        assert hasattr(type_param, "default"), (
            "TSTypeParameter should have 'default' field for default type"
        )
        # The default should be non-None for "T = string"
        assert type_param.default is not None, (
            "TSTypeParameter.default should be non-None for 'T = string'"
        )

    def test_ts_type_parameter_on_interface_in_walk(self):
        """RED: TSTypeParameter should appear for generic interfaces"""
        source = "interface Box<T, U> { first: T; second: U; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_params = find_all_nodes(result.program, "TSTypeParameter")

        assert len(type_params) >= 2, (
            f"Should find 2 TSTypeParameter nodes (T and U). Found: {len(type_params)}"
        )

    def test_ts_type_parameter_get_text(self):
        """RED: TSTypeParameter should support get_text()"""
        source = "function identity<T extends object>(x: T): T { return x; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_param = find_node(result.program, "TSTypeParameter")

        assert type_param is not None, "Should find TSTypeParameter"
        assert hasattr(type_param, "get_text"), "TSTypeParameter should have get_text()"
        text = type_param.get_text(source)
        # Should contain "T extends object" or at least "T"
        assert "T" in text, f"get_text() should include 'T', got: {text}"


class TestTSPropertySignatureInWalk:
    """Tests for TSPropertySignature appearing in walk() traversal"""

    def test_ts_property_signature_in_walk(self):
        """RED: TSPropertySignature should appear for interface properties"""
        source = """
interface User {
    name: string;
    age: number;
}
"""
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node_types = [node.type for node, _ in walk(result.program)]

        assert "TSPropertySignature" in node_types, (
            "TSPropertySignature should appear in walk() for interface properties. "
            f"Found types: {node_types}"
        )

    def test_ts_property_signature_has_key(self):
        """RED: TSPropertySignature should have key property"""
        source = "interface Config { port: number; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        prop_sig = find_node(result.program, "TSPropertySignature")

        assert prop_sig is not None, "Should find TSPropertySignature in walk()"
        assert hasattr(prop_sig, "key"), "TSPropertySignature should have 'key' field"

    def test_ts_property_signature_optional(self):
        """RED: TSPropertySignature should have optional flag"""
        source = "interface Config { host?: string; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        prop_sig = find_node(result.program, "TSPropertySignature")

        assert prop_sig is not None, "Should find TSPropertySignature in walk()"
        assert hasattr(prop_sig, "optional"), "TSPropertySignature should have 'optional' field"
        assert prop_sig.optional is True, "TSPropertySignature.optional should be True for 'host?'"

    def test_ts_property_signature_readonly(self):
        """RED: TSPropertySignature should have readonly flag"""
        source = "interface Config { readonly port: number; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        prop_sig = find_node(result.program, "TSPropertySignature")

        assert prop_sig is not None, "Should find TSPropertySignature in walk()"
        assert hasattr(prop_sig, "readonly"), "TSPropertySignature should have 'readonly' field"
        assert prop_sig.readonly is True, (
            "TSPropertySignature.readonly should be True for 'readonly port'"
        )

    def test_ts_property_signature_get_text(self):
        """RED: TSPropertySignature should support get_text()"""
        source = "interface Config { port: number; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        prop_sig = find_node(result.program, "TSPropertySignature")

        assert prop_sig is not None, "Should find TSPropertySignature"
        assert hasattr(prop_sig, "get_text"), "TSPropertySignature should have get_text()"
        text = prop_sig.get_text(source)
        assert "port" in text, f"get_text() should include 'port', got: {text}"


class TestTSMethodSignatureInWalk:
    """Tests for TSMethodSignature appearing in walk() traversal"""

    def test_ts_method_signature_in_walk(self):
        """RED: TSMethodSignature should appear for interface methods"""
        source = """
interface Logger {
    log(message: string): void;
}
"""
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node_types = [node.type for node, _ in walk(result.program)]

        assert "TSMethodSignature" in node_types, (
            "TSMethodSignature should appear in walk() for interface methods. "
            f"Found types: {node_types}"
        )

    def test_ts_method_signature_has_key(self):
        """RED: TSMethodSignature should have key property"""
        source = "interface Logger { log(msg: string): void; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        method_sig = find_node(result.program, "TSMethodSignature")

        assert method_sig is not None, "Should find TSMethodSignature in walk()"
        assert hasattr(method_sig, "key"), "TSMethodSignature should have 'key' field"

    def test_ts_method_signature_has_params(self):
        """RED: TSMethodSignature should have params field"""
        source = "interface Logger { log(msg: string, level: number): void; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        method_sig = find_node(result.program, "TSMethodSignature")

        assert method_sig is not None, "Should find TSMethodSignature in walk()"
        assert hasattr(method_sig, "params"), "TSMethodSignature should have 'params' field"

    def test_ts_method_signature_has_return_type(self):
        """RED: TSMethodSignature should have return_type field"""
        source = "interface Logger { log(msg: string): void; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        method_sig = find_node(result.program, "TSMethodSignature")

        assert method_sig is not None, "Should find TSMethodSignature in walk()"
        assert hasattr(method_sig, "return_type"), (
            "TSMethodSignature should have 'return_type' field"
        )

    def test_ts_method_signature_get_text(self):
        """RED: TSMethodSignature should support get_text()"""
        source = "interface Logger { log(msg: string): void; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        method_sig = find_node(result.program, "TSMethodSignature")

        assert method_sig is not None, "Should find TSMethodSignature"
        assert hasattr(method_sig, "get_text"), "TSMethodSignature should have get_text()"
        text = method_sig.get_text(source)
        assert "log" in text, f"get_text() should include 'log', got: {text}"


class TestTSInterfaceDeclarationDetails:
    """Tests for detailed TSInterfaceDeclaration node structure"""

    def test_ts_interface_has_body_field(self):
        """RED: TSInterfaceDeclaration should have body field"""
        source = "interface User { id: number; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        interface = find_node(result.program, "TSInterfaceDeclaration")

        assert interface is not None
        assert hasattr(interface, "body"), "TSInterfaceDeclaration should have 'body' field"

    def test_ts_interface_has_extends_field(self):
        """RED: TSInterfaceDeclaration should have extends field"""
        source = """
interface Base { id: number; }
interface Admin extends Base { role: string; }
"""
        result = parse(source, source_type="tsx")

        assert result.is_valid

        interface = None
        for node, _ in walk(result.program):
            if (
                node.type == "TSInterfaceDeclaration"
                and hasattr(node, "name")
                and node.name == "Admin"
            ):
                interface = node
                break

        assert interface is not None, "Should find Admin interface"
        assert hasattr(interface, "extends"), "TSInterfaceDeclaration should have 'extends' field"
        # extends should be non-empty for Admin interface
        assert interface.extends is not None, (
            "TSInterfaceDeclaration.extends should be non-None for 'Admin extends Base'"
        )

    def test_ts_interface_has_type_parameters_field(self):
        """RED: TSInterfaceDeclaration should have type_parameters field"""
        source = "interface Box<T> { value: T; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        interface = find_node(result.program, "TSInterfaceDeclaration")

        assert interface is not None
        assert hasattr(interface, "type_parameters"), (
            "TSInterfaceDeclaration should have 'type_parameters' field"
        )
        assert interface.type_parameters is not None, (
            "TSInterfaceDeclaration.type_parameters should be non-None for 'Box<T>'"
        )


class TestTSTypeAliasDeclarationDetails:
    """Tests for detailed TSTypeAliasDeclaration node structure"""

    def test_ts_type_alias_has_type_annotation_field(self):
        """RED: TSTypeAliasDeclaration should have type_annotation field"""
        source = "type UserId = string;"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_alias = find_node(result.program, "TSTypeAliasDeclaration")

        assert type_alias is not None
        assert hasattr(type_alias, "type_annotation"), (
            "TSTypeAliasDeclaration should have 'type_annotation' field"
        )

    def test_ts_type_alias_has_type_parameters_field(self):
        """RED: TSTypeAliasDeclaration should have type_parameters field"""
        source = "type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_alias = find_node(result.program, "TSTypeAliasDeclaration")

        assert type_alias is not None
        assert hasattr(type_alias, "type_parameters"), (
            "TSTypeAliasDeclaration should have 'type_parameters' field"
        )
        assert type_alias.type_parameters is not None, (
            "TSTypeAliasDeclaration.type_parameters should be non-None for 'Result<T, E>'"
        )


class TestTSInterfaceBodyInWalk:
    """Tests for TSInterfaceBody appearing in walk() traversal"""

    def test_ts_interface_body_in_walk(self):
        """RED: TSInterfaceBody should appear in walk() for interfaces"""
        source = """
interface Point {
    x: number;
    y: number;
}
"""
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node_types = [node.type for node, _ in walk(result.program)]

        assert "TSInterfaceBody" in node_types, (
            f"TSInterfaceBody should appear in walk() for interface body. Found types: {node_types}"
        )

    def test_ts_interface_body_has_body_list(self):
        """RED: TSInterfaceBody should have body list of members"""
        source = """
interface Point {
    x: number;
    y: number;
    distance(): number;
}
"""
        result = parse(source, source_type="tsx")

        assert result.is_valid

        interface_body = find_node(result.program, "TSInterfaceBody")

        assert interface_body is not None, "Should find TSInterfaceBody in walk()"
        assert hasattr(interface_body, "body"), "TSInterfaceBody should have 'body' field"
        assert isinstance(interface_body.body, list), "TSInterfaceBody.body should be a list"
        assert len(interface_body.body) >= 3, (
            f"TSInterfaceBody should have 3 members. Found: {len(interface_body.body)}"
        )


class TestTSEnumMemberInWalk:
    """Tests for TSEnumMember appearing in walk() traversal"""

    def test_ts_enum_member_in_walk(self):
        """RED: TSEnumMember should appear in walk() for enum members"""
        source = "enum Color { Red, Green, Blue }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node_types = [node.type for node, _ in walk(result.program)]

        assert "TSEnumMember" in node_types, (
            f"TSEnumMember should appear in walk() for enum members. Found types: {node_types}"
        )

    def test_ts_enum_member_has_id(self):
        """RED: TSEnumMember should have id field"""
        source = "enum Color { Red, Green, Blue }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        enum_member = find_node(result.program, "TSEnumMember")

        assert enum_member is not None, "Should find TSEnumMember in walk()"
        assert hasattr(enum_member, "id"), "TSEnumMember should have 'id' field"

    def test_ts_enum_member_has_initializer(self):
        """RED: TSEnumMember with value should have initializer field"""
        source = "enum Status { OK = 200, NotFound = 404 }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        enum_member = find_node(result.program, "TSEnumMember")

        assert enum_member is not None, "Should find TSEnumMember in walk()"
        assert hasattr(enum_member, "initializer"), "TSEnumMember should have 'initializer' field"
        assert enum_member.initializer is not None, (
            "TSEnumMember.initializer should be non-None for 'OK = 200'"
        )

    def test_ts_enum_member_count(self):
        """RED: Should have correct number of TSEnumMember nodes"""
        source = "enum Color { Red, Green, Blue }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        enum_members = find_all_nodes(result.program, "TSEnumMember")

        assert len(enum_members) == 3, (
            f"Should have 3 TSEnumMember nodes. Found: {len(enum_members)}"
        )


class TestTSEnumDeclarationDetails:
    """Tests for detailed TSEnumDeclaration node structure"""

    def test_ts_enum_has_members_field(self):
        """RED: TSEnumDeclaration should have members field"""
        source = "enum Color { Red, Green, Blue }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        enum = find_node(result.program, "TSEnumDeclaration")

        assert enum is not None
        assert hasattr(enum, "members"), "TSEnumDeclaration should have 'members' field"
        assert isinstance(enum.members, list), "TSEnumDeclaration.members should be a list"
        assert len(enum.members) == 3, (
            f"TSEnumDeclaration.members should have 3 items. Found: {len(enum.members)}"
        )

    def test_ts_enum_has_const_flag(self):
        """RED: TSEnumDeclaration should have is_const field for const enums"""
        source = "const enum Direction { Up, Down, Left, Right }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        enum = find_node(result.program, "TSEnumDeclaration")

        assert enum is not None
        assert hasattr(enum, "is_const") or hasattr(enum, "const"), (
            "TSEnumDeclaration should have 'is_const' or 'const' field"
        )
        # Check whichever attribute exists
        is_const = getattr(enum, "is_const", None) or getattr(enum, "const", None)
        assert is_const is True, "TSEnumDeclaration should have is_const=True for 'const enum'"


class TestTSTypeParameterDeclarationInWalk:
    """Tests for TSTypeParameterDeclaration appearing in walk() traversal"""

    def test_ts_type_parameter_declaration_in_walk(self):
        """RED: TSTypeParameterDeclaration should appear for generic declarations"""
        source = "function identity<T, U>(a: T, b: U): [T, U] { return [a, b]; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node_types = [node.type for node, _ in walk(result.program)]

        assert "TSTypeParameterDeclaration" in node_types, (
            f"TSTypeParameterDeclaration should appear in walk(). Found types: {node_types}"
        )

    def test_ts_type_parameter_declaration_has_params(self):
        """RED: TSTypeParameterDeclaration should have params list"""
        source = "interface Pair<T, U> { first: T; second: U; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_param_decl = find_node(result.program, "TSTypeParameterDeclaration")

        assert type_param_decl is not None, "Should find TSTypeParameterDeclaration"
        assert hasattr(type_param_decl, "params"), (
            "TSTypeParameterDeclaration should have 'params' field"
        )
        assert isinstance(type_param_decl.params, list), (
            "TSTypeParameterDeclaration.params should be a list"
        )
        assert len(type_param_decl.params) == 2, (
            f"TSTypeParameterDeclaration.params should have 2 items (T, U). "
            f"Found: {len(type_param_decl.params)}"
        )


class TestAllTSNodesHaveSpanAndLineInfo:
    """Tests that all TS intermediate nodes have span and line info"""

    def test_ts_type_annotation_has_span(self):
        """RED: TSTypeAnnotation should have span and line info"""
        source = "const x: number = 1;"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node = find_node(result.program, "TSTypeAnnotation")

        assert node is not None, "Should find TSTypeAnnotation"
        assert hasattr(node, "span"), "TSTypeAnnotation should have 'span'"
        assert hasattr(node, "start_line"), "TSTypeAnnotation should have 'start_line'"
        assert hasattr(node, "end_line"), "TSTypeAnnotation should have 'end_line'"

    def test_ts_type_reference_has_span(self):
        """RED: TSTypeReference should have span and line info"""
        source = "const x: MyType = null;"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node = find_node(result.program, "TSTypeReference")

        assert node is not None, "Should find TSTypeReference"
        assert hasattr(node, "span"), "TSTypeReference should have 'span'"
        assert hasattr(node, "start_line"), "TSTypeReference should have 'start_line'"
        assert hasattr(node, "end_line"), "TSTypeReference should have 'end_line'"

    def test_ts_type_parameter_has_span(self):
        """RED: TSTypeParameter should have span and line info"""
        source = "function foo<T>(): T { return null!; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node = find_node(result.program, "TSTypeParameter")

        assert node is not None, "Should find TSTypeParameter"
        assert hasattr(node, "span"), "TSTypeParameter should have 'span'"
        assert hasattr(node, "start_line"), "TSTypeParameter should have 'start_line'"
        assert hasattr(node, "end_line"), "TSTypeParameter should have 'end_line'"

    def test_ts_property_signature_has_span(self):
        """RED: TSPropertySignature should have span and line info"""
        source = "interface Foo { bar: string; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node = find_node(result.program, "TSPropertySignature")

        assert node is not None, "Should find TSPropertySignature"
        assert hasattr(node, "span"), "TSPropertySignature should have 'span'"
        assert hasattr(node, "start_line"), "TSPropertySignature should have 'start_line'"
        assert hasattr(node, "end_line"), "TSPropertySignature should have 'end_line'"

    def test_ts_method_signature_has_span(self):
        """RED: TSMethodSignature should have span and line info"""
        source = "interface Foo { bar(): void; }"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        node = find_node(result.program, "TSMethodSignature")

        assert node is not None, "Should find TSMethodSignature"
        assert hasattr(node, "span"), "TSMethodSignature should have 'span'"
        assert hasattr(node, "start_line"), "TSMethodSignature should have 'start_line'"
        assert hasattr(node, "end_line"), "TSMethodSignature should have 'end_line'"


# =============================================================================
# NEW TEST CLASSES - Added as per requirements
# =============================================================================


class TestTypeScriptErrorRecovery:
    """Tests for TypeScript error recovery - parser should return partial AST with errors"""

    def test_invalid_interface_extends(self):
        """RED: Invalid interface syntax should return errors"""
        source = "interface Foo extends 123 {}"
        result = parse(source, source_type="tsx")

        assert result.is_valid is False, "Invalid syntax should result in is_valid=False"
        assert len(result.errors) > 0, "Should have at least one error"

    def test_malformed_generics(self):
        """RED: Malformed generics should return errors"""
        source = "function foo<T extends>(): void {}"
        result = parse(source, source_type="tsx")

        assert result.is_valid is False, "Malformed generics should result in is_valid=False"
        assert len(result.errors) > 0, "Should have at least one error"

    def test_invalid_type_annotation(self):
        """RED: Invalid type annotation should return errors"""
        source = "const x: = 1;"
        result = parse(source, source_type="tsx")

        assert result.is_valid is False, "Invalid type annotation should result in is_valid=False"
        assert len(result.errors) > 0, "Should have at least one error"

    def test_incomplete_interface_body(self):
        """RED: Incomplete interface body should return errors"""
        source = "interface Foo { name: }"
        result = parse(source, source_type="tsx")

        assert result.is_valid is False, "Incomplete interface should result in is_valid=False"
        assert len(result.errors) > 0, "Should have at least one error"


class TestTypeScriptAdvancedTypes:
    """Tests for union and intersection types"""

    def test_union_type_parsing(self):
        """RED: Union types should be parsed correctly"""
        source = 'type Status = "pending" | "complete" | "error";'
        result = parse(source, source_type="tsx")

        assert result.is_valid

        # Should find TSTypeAliasDeclaration
        type_alias = find_node(result.program, "TSTypeAliasDeclaration")
        assert type_alias is not None, "Should find TSTypeAliasDeclaration for union type"
        assert type_alias.name == "Status"

        # TSUnionType should appear in walk
        node_types = [node.type for node, _ in walk(result.program)]
        assert "TSUnionType" in node_types, (
            f"TSUnionType should appear in walk() for union type. Found types: {node_types}"
        )

    def test_intersection_type_parsing(self):
        """RED: Intersection types should be parsed correctly"""
        source = "type Combined = TypeA & TypeB;"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        # Should find TSTypeAliasDeclaration
        type_alias = find_node(result.program, "TSTypeAliasDeclaration")
        assert type_alias is not None, "Should find TSTypeAliasDeclaration for intersection type"
        assert type_alias.name == "Combined"

        # TSIntersectionType should appear in walk
        node_types = [node.type for node, _ in walk(result.program)]
        assert "TSIntersectionType" in node_types, (
            f"TSIntersectionType should appear in walk() for intersection type. "
            f"Found types: {node_types}"
        )

    def test_complex_union_intersection(self):
        """RED: Complex union and intersection types should parse"""
        source = "type Complex = (A & B) | (C & D);"
        result = parse(source, source_type="tsx")

        assert result.is_valid

        type_alias = find_node(result.program, "TSTypeAliasDeclaration")
        assert type_alias is not None

        # Both union and intersection should appear
        node_types = [node.type for node, _ in walk(result.program)]
        assert "TSUnionType" in node_types or "TSIntersectionType" in node_types, (
            "Should find union or intersection types in complex type"
        )

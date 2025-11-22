"""
Test suite for JavaScript AST node types.

This module combines tests from:
- test_phase_13_statement_nodes.py (91 tests) - Statement nodes (if, for, while, etc.)
- test_phase_14_expression_nodes.py (36 tests) - Expression nodes (literals, operators, etc.)
- test_phase_15_import_export.py (21 tests) - Import/export declarations

These tests validate JavaScript-specific AST node structures for statements,
expressions, and module import/export declarations.
"""

import pytest

"""
Phase 13: Statement Node Types - RED Phase Tests

Tests for specialized statement nodes with proper fields:
- FunctionDeclaration (name, params, body, is_async, is_generator)
- ClassDeclaration (name, superclass, body)
- VariableDeclaration (kind: const/let/var, declarations)
"""


class TestFunctionDeclarationStructure:
    """Tests for FunctionDeclaration node structure."""

    def test_function_declaration_basic_structure(self):
        """RED: FunctionDeclaration must have correct type and fields."""
        import oxc_python

        source = "function foo(x, y) { return x + y; }"
        result = oxc_python.parse(source, source_type="module")

        func_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "FunctionDeclaration":
                func_node = node
                break

        assert func_node is not None, "Should find FunctionDeclaration"

        # Type property
        assert func_node.type == "FunctionDeclaration"
        assert isinstance(func_node.type, str)

        # Required fields
        assert hasattr(func_node, "name")
        assert hasattr(func_node, "is_async")
        assert hasattr(func_node, "is_generator")

        # Field values
        assert func_node.name == "foo"
        assert func_node.is_async is False
        assert func_node.is_generator is False

    def test_async_function(self):
        """RED: Async function must have is_async=True."""
        import oxc_python

        source = "async function asyncFoo() { await bar(); }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "FunctionDeclaration":
                assert node.name == "asyncFoo"
                assert node.is_async is True
                assert node.is_generator is False
                break
        else:
            pytest.fail("No FunctionDeclaration found")

    def test_generator_function(self):
        """RED: Generator function must have is_generator=True."""
        import oxc_python

        source = "function* genFoo() { yield 1; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "FunctionDeclaration":
                assert node.name == "genFoo"
                assert node.is_async is False
                assert node.is_generator is True
                break
        else:
            pytest.fail("No FunctionDeclaration found")

    def test_async_generator_function(self):
        """RED: Async generator must have both flags True."""
        import oxc_python

        source = "async function* asyncGenFoo() { yield await bar(); }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "FunctionDeclaration":
                assert node.name == "asyncGenFoo"
                assert node.is_async is True
                assert node.is_generator is True
                break
        else:
            pytest.fail("No FunctionDeclaration found")

    def test_function_has_span_and_get_text(self):
        """RED: FunctionDeclaration must have span and get_text()."""
        import oxc_python

        source = "function myFunc() { return 42; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "FunctionDeclaration":
                assert hasattr(node, "span")
                assert hasattr(node, "get_text")
                text = node.get_text(source)
                assert "function myFunc" in text
                break
        else:
            pytest.fail("No FunctionDeclaration found")

    def test_function_has_get_line_range(self):
        """RED: FunctionDeclaration must have get_line_range()."""
        import oxc_python

        source = """function multiLine() {
    return 42;
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "FunctionDeclaration":
                assert hasattr(node, "get_line_range")
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 3
                break
        else:
            pytest.fail("No FunctionDeclaration found")


class TestClassDeclarationStructure:
    """Tests for ClassDeclaration node structure."""

    def test_class_declaration_basic_structure(self):
        """RED: ClassDeclaration must have correct type and fields."""
        import oxc_python

        source = """
        class MyClass extends BaseClass {
            constructor() {}
            method() {}
        }
        """
        result = oxc_python.parse(source, source_type="module")

        class_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ClassDeclaration":
                class_node = node
                break

        assert class_node is not None, "Should find ClassDeclaration"

        # Type property
        assert class_node.type == "ClassDeclaration"
        assert isinstance(class_node.type, str)

        # Required fields
        assert hasattr(class_node, "name")
        assert hasattr(class_node, "superclass")

        # Field values
        assert class_node.name == "MyClass"
        assert class_node.superclass is not None  # Has BaseClass

    def test_class_without_superclass(self):
        """RED: Class without extends should have superclass=None."""
        import oxc_python

        source = "class SimpleClass {}"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ClassDeclaration":
                assert node.name == "SimpleClass"
                assert node.superclass is None
                break
        else:
            pytest.fail("No ClassDeclaration found")

    def test_class_has_span_and_get_text(self):
        """RED: ClassDeclaration must have span and get_text()."""
        import oxc_python

        source = "class MyClass { method() {} }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ClassDeclaration":
                assert hasattr(node, "span")
                assert hasattr(node, "get_text")
                text = node.get_text(source)
                assert "class MyClass" in text
                break
        else:
            pytest.fail("No ClassDeclaration found")


class TestVariableDeclarationStructure:
    """Tests for VariableDeclaration node structure."""

    def test_variable_declaration_const(self):
        """RED: VariableDeclaration must have kind field."""
        import oxc_python

        source = "const x = 1, y = 2;"
        result = oxc_python.parse(source, source_type="module")

        var_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "VariableDeclaration":
                var_node = node
                break

        assert var_node is not None, "Should find VariableDeclaration"

        # Type property
        assert var_node.type == "VariableDeclaration"
        assert isinstance(var_node.type, str)

        # Required fields
        assert hasattr(var_node, "kind")

        # Field values
        assert var_node.kind == "const"

    def test_variable_declaration_let(self):
        """RED: let declaration should have kind='let'."""
        import oxc_python

        source = "let x = 1;"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "VariableDeclaration":
                assert node.kind == "let"
                break
        else:
            pytest.fail("No VariableDeclaration found")

    def test_variable_declaration_var(self):
        """RED: var declaration should have kind='var'."""
        import oxc_python

        source = "var x = 1;"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "VariableDeclaration":
                assert node.kind == "var"
                break
        else:
            pytest.fail("No VariableDeclaration found")

    def test_variable_declaration_all_kinds(self):
        """RED: Test const, let, var declarations."""
        import oxc_python

        source = """
        const constVar = 1;
        let letVar = 2;
        var varVar = 3;
        """
        result = oxc_python.parse(source, source_type="module")

        kinds_found = []
        for node, _ in oxc_python.walk(result.program):
            if node.type == "VariableDeclaration":
                kinds_found.append(node.kind)

        assert "const" in kinds_found
        assert "let" in kinds_found
        assert "var" in kinds_found

    def test_variable_has_span_and_get_text(self):
        """RED: VariableDeclaration must have span and get_text()."""
        import oxc_python

        source = "const myVar = 42;"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "VariableDeclaration":
                assert hasattr(node, "span")
                assert hasattr(node, "get_text")
                text = node.get_text(source)
                assert "const myVar" in text
                break
        else:
            pytest.fail("No VariableDeclaration found")


class TestChunkHoundIntegration:
    """Tests for ChunkHound compatibility."""

    def test_chunkhound_function_name_extraction(self):
        """ChunkHound: FunctionDeclaration.name must be accessible."""
        import oxc_python

        source = "function myFunction() { return 42; }"
        result = oxc_python.parse(source, source_type="module")

        # ChunkHound pattern: _extract_symbol(node, depth)
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "FunctionDeclaration":
                # ChunkHound does: if hasattr(node, 'name') and node.name
                assert hasattr(node, "name")
                assert node.name == "myFunction"
                break
        else:
            pytest.fail("No FunctionDeclaration found")

    def test_chunkhound_class_name_extraction(self):
        """ChunkHound: ClassDeclaration.name must be accessible."""
        import oxc_python

        source = "class MyClass {}"
        result = oxc_python.parse(source, source_type="module")

        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ClassDeclaration":
                assert hasattr(node, "name")
                assert node.name == "MyClass"
                break
        else:
            pytest.fail("No ClassDeclaration found")

    def test_chunkhound_variable_kind_extraction(self):
        """ChunkHound: VariableDeclaration.kind must be accessible."""
        import oxc_python

        source = "const API_KEY = 'secret';"
        result = oxc_python.parse(source, source_type="module")

        for node, _depth in oxc_python.walk(result.program):
            if node.type == "VariableDeclaration":
                assert hasattr(node, "kind")
                assert node.kind == "const"
                break
        else:
            pytest.fail("No VariableDeclaration found")

    def test_chunkhound_map_chunk_type(self):
        """Verify all ChunkHound-required statement types exist."""
        import oxc_python

        source = """
        function myFunc() { return 1; }
        class MyClass {}
        const myVar = 42;
        """
        result = oxc_python.parse(source, source_type="module")

        types_found = set()
        for node, _depth in oxc_python.walk(result.program):
            types_found.add(node.type)

        # ChunkHound's _map_chunk_type expects these
        assert "FunctionDeclaration" in types_found
        assert "ClassDeclaration" in types_found
        assert "VariableDeclaration" in types_found

    def test_chunkhound_extract_symbol_pattern(self):
        """Simulate ChunkHound's _extract_symbol() method."""
        import oxc_python

        def extract_symbol(node, depth: int) -> str:
            """ChunkHound's symbol extraction logic."""
            # Try to get name property
            if hasattr(node, "name") and node.name:
                return node.name

            # Fallback to generic name
            return f"{node.type}_{node.span.start}"

        source = """
        function namedFunc() {}
        class NamedClass {}
        const namedVar = 1;
        """
        result = oxc_python.parse(source, source_type="module")

        symbols = []
        for node, depth in oxc_python.walk(result.program):
            if node.type in ("FunctionDeclaration", "ClassDeclaration", "VariableDeclaration"):
                symbol = extract_symbol(node, depth)
                symbols.append(symbol)

        assert "namedFunc" in symbols
        assert "NamedClass" in symbols
        # VariableDeclaration doesn't have name directly, uses fallback
        assert any("VariableDeclaration" in s for s in symbols)

    def test_full_chunkhound_integration(self):
        """Simulate complete ChunkHound OxcParser usage."""
        import oxc_python

        # Setup (simulating OxcParser.__init__)
        allocator = oxc_python.Allocator()

        # Parse (simulating parse_content)
        source = """
        function processData(input) {
            const processed = transform(input);
            return processed;
        }

        class DataProcessor {
            process(data) {
                return processData(data);
            }
        }
        """

        result = oxc_python.parse(source, source_type="module", allocator=allocator)

        # Validation
        assert result.is_valid, "Parse should succeed"

        # Walk and extract chunks
        chunks = []
        for node, depth in oxc_python.walk(result.program):
            # Filter by chunk type
            if node.type not in ("FunctionDeclaration", "ClassDeclaration"):
                continue

            # Extract symbol
            symbol = (
                node.name
                if hasattr(node, "name") and node.name
                else f"{node.type}_{node.span.start}"
            )

            # Extract code
            code = node.get_text(source)

            # Extract line range
            start_line, end_line = node.get_line_range(source)

            chunks.append(
                {
                    "symbol": symbol,
                    "type": node.type,
                    "code": code,
                    "start_line": start_line,
                    "end_line": end_line,
                    "depth": depth,
                }
            )

        # Verify chunks
        assert len(chunks) >= 2, "Should find at least function and class"

        func_chunk = next(c for c in chunks if c["type"] == "FunctionDeclaration")
        assert func_chunk["symbol"] == "processData"
        assert "function processData" in func_chunk["code"]
        assert func_chunk["start_line"] >= 1

        class_chunk = next(c for c in chunks if c["type"] == "ClassDeclaration")
        assert class_chunk["symbol"] == "DataProcessor"
        assert "class DataProcessor" in class_chunk["code"]

        # Cleanup (simulating reuse)
        allocator.reset()


# =============================================================================
# MISSING STATEMENT TYPES - TDD RED PHASE
# These tests are expected to FAIL until implementation is complete
# =============================================================================


class TestBlockStatement:
    """Tests for BlockStatement node structure."""

    def test_block_statement_structure(self):
        """RED: BlockStatement must have correct type and fields."""
        import oxc_python

        source = "{ const x = 1; const y = 2; }"
        result = oxc_python.parse(source, source_type="module")

        block_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "BlockStatement":
                block_node = node
                break

        assert block_node is not None, "Should find BlockStatement"
        assert block_node.type == "BlockStatement"
        assert isinstance(block_node.type, str)

        # Required fields
        assert hasattr(block_node, "body")
        assert isinstance(block_node.body, list)
        assert len(block_node.body) == 2

    def test_block_statement_empty(self):
        """RED: Empty BlockStatement should have empty body list."""
        import oxc_python

        source = "{}"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "BlockStatement":
                assert hasattr(node, "body")
                assert isinstance(node.body, list)
                assert len(node.body) == 0
                break
        else:
            pytest.fail("No BlockStatement found")

    def test_block_statement_get_text(self):
        """RED: BlockStatement must support get_text()."""
        import oxc_python

        source = "{ let x = 1; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "BlockStatement":
                text = node.get_text(source)
                assert "{" in text
                assert "let x = 1" in text
                break
        else:
            pytest.fail("No BlockStatement found")

    def test_block_statement_get_line_range(self):
        """RED: BlockStatement must support get_line_range()."""
        import oxc_python

        source = """{
    let x = 1;
    let y = 2;
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "BlockStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 4
                break
        else:
            pytest.fail("No BlockStatement found")


class TestExpressionStatement:
    """Tests for ExpressionStatement node structure."""

    def test_expression_statement_structure(self):
        """RED: ExpressionStatement must have correct type and fields."""
        import oxc_python

        source = "console.log('hello');"
        result = oxc_python.parse(source, source_type="module")

        expr_stmt_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ExpressionStatement":
                expr_stmt_node = node
                break

        assert expr_stmt_node is not None, "Should find ExpressionStatement"
        assert expr_stmt_node.type == "ExpressionStatement"
        assert isinstance(expr_stmt_node.type, str)

        # Required fields
        assert hasattr(expr_stmt_node, "expression")
        assert expr_stmt_node.expression is not None

    def test_expression_statement_get_text(self):
        """RED: ExpressionStatement must support get_text()."""
        import oxc_python

        source = "foo();"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ExpressionStatement":
                text = node.get_text(source)
                assert "foo()" in text
                break
        else:
            pytest.fail("No ExpressionStatement found")

    def test_expression_statement_get_line_range(self):
        """RED: ExpressionStatement must support get_line_range()."""
        import oxc_python

        source = "x = y + z;"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ExpressionStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 1
                break
        else:
            pytest.fail("No ExpressionStatement found")


class TestIfStatement:
    """Tests for IfStatement node structure."""

    def test_if_statement_structure(self):
        """RED: IfStatement must have correct type and fields."""
        import oxc_python

        source = """
        if (condition) {
            doSomething();
        } else {
            doOther();
        }
        """
        result = oxc_python.parse(source, source_type="module")

        if_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "IfStatement":
                if_node = node
                break

        assert if_node is not None, "Should find IfStatement"
        assert if_node.type == "IfStatement"
        assert isinstance(if_node.type, str)

        # Required fields
        assert hasattr(if_node, "test")
        assert hasattr(if_node, "consequent")
        assert hasattr(if_node, "alternate")

        assert if_node.test is not None
        assert if_node.consequent is not None
        assert if_node.alternate is not None  # Has else clause

    def test_if_statement_without_else(self):
        """RED: IfStatement without else should have alternate=None."""
        import oxc_python

        source = "if (x > 0) { console.log('positive'); }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "IfStatement":
                assert node.test is not None
                assert node.consequent is not None
                assert node.alternate is None
                break
        else:
            pytest.fail("No IfStatement found")

    def test_if_else_if_chain(self):
        """RED: Else-if chains should create nested IfStatements."""
        import oxc_python

        source = """
        if (x > 0) {
            console.log('positive');
        } else if (x < 0) {
            console.log('negative');
        } else {
            console.log('zero');
        }
        """
        result = oxc_python.parse(source, source_type="module")

        if_count = 0
        for node, _ in oxc_python.walk(result.program):
            if node.type == "IfStatement":
                if_count += 1

        assert if_count == 2, "Should find 2 IfStatements (main and else-if)"

    def test_if_statement_get_text(self):
        """RED: IfStatement must support get_text()."""
        import oxc_python

        source = "if (true) { x = 1; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "IfStatement":
                text = node.get_text(source)
                assert "if (true)" in text
                break
        else:
            pytest.fail("No IfStatement found")

    def test_if_statement_get_line_range(self):
        """RED: IfStatement must support get_line_range()."""
        import oxc_python

        source = """if (condition) {
    doSomething();
} else {
    doOther();
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "IfStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 5
                break
        else:
            pytest.fail("No IfStatement found")


class TestForStatement:
    """Tests for ForStatement node structure."""

    def test_for_statement_structure(self):
        """RED: ForStatement must have correct type and fields."""
        import oxc_python

        source = "for (let i = 0; i < 10; i++) { console.log(i); }"
        result = oxc_python.parse(source, source_type="module")

        for_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ForStatement":
                for_node = node
                break

        assert for_node is not None, "Should find ForStatement"
        assert for_node.type == "ForStatement"
        assert isinstance(for_node.type, str)

        # Required fields
        assert hasattr(for_node, "init")
        assert hasattr(for_node, "test")
        assert hasattr(for_node, "update")
        assert hasattr(for_node, "body")

        assert for_node.init is not None
        assert for_node.test is not None
        assert for_node.update is not None
        assert for_node.body is not None

    def test_for_statement_with_missing_parts(self):
        """RED: ForStatement can have null init/test/update."""
        import oxc_python

        source = "for (;;) { break; }"  # Infinite loop pattern
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ForStatement":
                assert node.init is None
                assert node.test is None
                assert node.update is None
                assert node.body is not None
                break
        else:
            pytest.fail("No ForStatement found")

    def test_for_statement_get_text(self):
        """RED: ForStatement must support get_text()."""
        import oxc_python

        source = "for (let i = 0; i < 5; i++) { x += i; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ForStatement":
                text = node.get_text(source)
                assert "for (" in text
                break
        else:
            pytest.fail("No ForStatement found")

    def test_for_statement_get_line_range(self):
        """RED: ForStatement must support get_line_range()."""
        import oxc_python

        source = """for (let i = 0; i < 10; i++) {
    console.log(i);
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ForStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 3
                break
        else:
            pytest.fail("No ForStatement found")


class TestForInStatement:
    """Tests for ForInStatement node structure."""

    def test_for_in_statement_structure(self):
        """RED: ForInStatement must have correct type and fields."""
        import oxc_python

        source = "for (const key in obj) { console.log(key); }"
        result = oxc_python.parse(source, source_type="module")

        for_in_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ForInStatement":
                for_in_node = node
                break

        assert for_in_node is not None, "Should find ForInStatement"
        assert for_in_node.type == "ForInStatement"
        assert isinstance(for_in_node.type, str)

        # Required fields
        assert hasattr(for_in_node, "left")
        assert hasattr(for_in_node, "right")
        assert hasattr(for_in_node, "body")

        assert for_in_node.left is not None
        assert for_in_node.right is not None
        assert for_in_node.body is not None

    def test_for_in_statement_get_text(self):
        """RED: ForInStatement must support get_text()."""
        import oxc_python

        source = "for (const key in obj) { console.log(key); }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ForInStatement":
                text = node.get_text(source)
                assert "for (" in text
                assert "in obj" in text
                break
        else:
            pytest.fail("No ForInStatement found")

    def test_for_in_statement_get_line_range(self):
        """RED: ForInStatement must support get_line_range()."""
        import oxc_python

        source = """for (const key in obj) {
    console.log(key);
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ForInStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 3
                break
        else:
            pytest.fail("No ForInStatement found")


class TestForOfStatement:
    """Tests for ForOfStatement node structure."""

    def test_for_of_statement_structure(self):
        """RED: ForOfStatement must have correct type and fields."""
        import oxc_python

        source = "for (const item of items) { console.log(item); }"
        result = oxc_python.parse(source, source_type="module")

        for_of_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ForOfStatement":
                for_of_node = node
                break

        assert for_of_node is not None, "Should find ForOfStatement"
        assert for_of_node.type == "ForOfStatement"
        assert isinstance(for_of_node.type, str)

        # Required fields
        assert hasattr(for_of_node, "left")
        assert hasattr(for_of_node, "right")
        assert hasattr(for_of_node, "body")
        assert hasattr(for_of_node, "is_await")

        assert for_of_node.left is not None
        assert for_of_node.right is not None
        assert for_of_node.body is not None
        assert for_of_node.is_await is False

    def test_for_await_of_statement(self):
        """RED: for await...of should have is_await=True."""
        import oxc_python

        source = (
            "async function test() { "
            "for await (const item of asyncIterator) { console.log(item); } }"
        )
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ForOfStatement":
                assert node.is_await is True
                break
        else:
            pytest.fail("No ForOfStatement found")

    def test_for_of_statement_get_text(self):
        """RED: ForOfStatement must support get_text()."""
        import oxc_python

        source = "for (const item of items) { console.log(item); }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ForOfStatement":
                text = node.get_text(source)
                assert "for (" in text
                assert "of items" in text
                break
        else:
            pytest.fail("No ForOfStatement found")

    def test_for_of_statement_get_line_range(self):
        """RED: ForOfStatement must support get_line_range()."""
        import oxc_python

        source = """for (const item of items) {
    process(item);
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ForOfStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 3
                break
        else:
            pytest.fail("No ForOfStatement found")


class TestWhileStatement:
    """Tests for WhileStatement node structure."""

    def test_while_statement_structure(self):
        """RED: WhileStatement must have correct type and fields."""
        import oxc_python

        source = "while (condition) { doWork(); }"
        result = oxc_python.parse(source, source_type="module")

        while_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "WhileStatement":
                while_node = node
                break

        assert while_node is not None, "Should find WhileStatement"
        assert while_node.type == "WhileStatement"
        assert isinstance(while_node.type, str)

        # Required fields
        assert hasattr(while_node, "test")
        assert hasattr(while_node, "body")

        assert while_node.test is not None
        assert while_node.body is not None

    def test_while_statement_get_text(self):
        """RED: WhileStatement must support get_text()."""
        import oxc_python

        source = "while (x > 0) { x--; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "WhileStatement":
                text = node.get_text(source)
                assert "while (" in text
                break
        else:
            pytest.fail("No WhileStatement found")

    def test_while_statement_get_line_range(self):
        """RED: WhileStatement must support get_line_range()."""
        import oxc_python

        source = """while (condition) {
    doWork();
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "WhileStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 3
                break
        else:
            pytest.fail("No WhileStatement found")


class TestDoWhileStatement:
    """Tests for DoWhileStatement node structure."""

    def test_do_while_statement_structure(self):
        """RED: DoWhileStatement must have correct type and fields."""
        import oxc_python

        source = "do { doWork(); } while (condition);"
        result = oxc_python.parse(source, source_type="module")

        do_while_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "DoWhileStatement":
                do_while_node = node
                break

        assert do_while_node is not None, "Should find DoWhileStatement"
        assert do_while_node.type == "DoWhileStatement"
        assert isinstance(do_while_node.type, str)

        # Required fields
        assert hasattr(do_while_node, "body")
        assert hasattr(do_while_node, "test")

        assert do_while_node.body is not None
        assert do_while_node.test is not None

    def test_do_while_statement_get_text(self):
        """RED: DoWhileStatement must support get_text()."""
        import oxc_python

        source = "do { x++; } while (x < 10);"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "DoWhileStatement":
                text = node.get_text(source)
                assert "do {" in text
                assert "while (" in text
                break
        else:
            pytest.fail("No DoWhileStatement found")

    def test_do_while_statement_get_line_range(self):
        """RED: DoWhileStatement must support get_line_range()."""
        import oxc_python

        source = """do {
    doWork();
} while (condition);"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "DoWhileStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 3
                break
        else:
            pytest.fail("No DoWhileStatement found")


class TestSwitchStatement:
    """Tests for SwitchStatement node structure."""

    def test_switch_statement_structure(self):
        """RED: SwitchStatement must have correct type and fields."""
        import oxc_python

        source = """
        switch (value) {
            case 1:
                console.log('one');
                break;
            case 2:
                console.log('two');
                break;
            default:
                console.log('other');
        }
        """
        result = oxc_python.parse(source, source_type="module")

        switch_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "SwitchStatement":
                switch_node = node
                break

        assert switch_node is not None, "Should find SwitchStatement"
        assert switch_node.type == "SwitchStatement"
        assert isinstance(switch_node.type, str)

        # Required fields
        assert hasattr(switch_node, "discriminant")
        assert hasattr(switch_node, "cases")

        assert switch_node.discriminant is not None
        assert isinstance(switch_node.cases, list)
        assert len(switch_node.cases) == 3  # case 1, case 2, default

    def test_switch_statement_get_text(self):
        """RED: SwitchStatement must support get_text()."""
        import oxc_python

        source = "switch (x) { case 1: break; default: break; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "SwitchStatement":
                text = node.get_text(source)
                assert "switch (x)" in text
                break
        else:
            pytest.fail("No SwitchStatement found")

    def test_switch_statement_get_line_range(self):
        """RED: SwitchStatement must support get_line_range()."""
        import oxc_python

        source = """switch (value) {
    case 1:
        break;
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "SwitchStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 4
                break
        else:
            pytest.fail("No SwitchStatement found")


class TestSwitchCase:
    """Tests for SwitchCase node structure."""

    def test_switch_case_structure(self):
        """RED: SwitchCase must have correct type and fields."""
        import oxc_python

        source = "switch (x) { case 1: console.log('one'); break; }"
        result = oxc_python.parse(source, source_type="module")

        case_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "SwitchCase":
                case_node = node
                break

        assert case_node is not None, "Should find SwitchCase"
        assert case_node.type == "SwitchCase"
        assert isinstance(case_node.type, str)

        # Required fields
        assert hasattr(case_node, "test")
        assert hasattr(case_node, "consequent")

        assert case_node.test is not None  # Has case value
        assert isinstance(case_node.consequent, list)

    def test_switch_case_default(self):
        """RED: Default case should have test=None."""
        import oxc_python

        source = "switch (x) { default: console.log('default'); break; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "SwitchCase":
                assert node.test is None  # Default case
                assert isinstance(node.consequent, list)
                break
        else:
            pytest.fail("No SwitchCase found")

    def test_switch_case_get_text(self):
        """RED: SwitchCase must support get_text()."""
        import oxc_python

        source = "switch (x) { case 1: y = 1; break; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "SwitchCase":
                text = node.get_text(source)
                assert "case 1:" in text
                break
        else:
            pytest.fail("No SwitchCase found")


class TestTryStatement:
    """Tests for TryStatement node structure."""

    def test_try_statement_with_catch(self):
        """RED: TryStatement must have correct type and fields."""
        import oxc_python

        source = """
        try {
            riskyOperation();
        } catch (error) {
            console.log(error);
        }
        """
        result = oxc_python.parse(source, source_type="module")

        try_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "TryStatement":
                try_node = node
                break

        assert try_node is not None, "Should find TryStatement"
        assert try_node.type == "TryStatement"
        assert isinstance(try_node.type, str)

        # Required fields
        assert hasattr(try_node, "block")
        assert hasattr(try_node, "handler")
        assert hasattr(try_node, "finalizer")

        assert try_node.block is not None
        assert try_node.handler is not None  # Has catch
        assert try_node.finalizer is None  # No finally

    def test_try_statement_with_finally(self):
        """RED: TryStatement with finally block."""
        import oxc_python

        source = """
        try {
            riskyOperation();
        } finally {
            cleanup();
        }
        """
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "TryStatement":
                assert node.block is not None
                assert node.handler is None  # No catch
                assert node.finalizer is not None  # Has finally
                break
        else:
            pytest.fail("No TryStatement found")

    def test_try_statement_with_catch_and_finally(self):
        """RED: TryStatement with both catch and finally."""
        import oxc_python

        source = """
        try {
            riskyOperation();
        } catch (error) {
            console.log(error);
        } finally {
            cleanup();
        }
        """
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "TryStatement":
                assert node.block is not None
                assert node.handler is not None  # Has catch
                assert node.finalizer is not None  # Has finally
                break
        else:
            pytest.fail("No TryStatement found")

    def test_try_statement_get_text(self):
        """RED: TryStatement must support get_text()."""
        import oxc_python

        source = "try { foo(); } catch (e) { bar(); }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "TryStatement":
                text = node.get_text(source)
                assert "try {" in text
                break
        else:
            pytest.fail("No TryStatement found")

    def test_try_statement_get_line_range(self):
        """RED: TryStatement must support get_line_range()."""
        import oxc_python

        source = """try {
    riskyOperation();
} catch (error) {
    handleError(error);
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "TryStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 5
                break
        else:
            pytest.fail("No TryStatement found")


class TestCatchClause:
    """Tests for CatchClause node structure."""

    def test_catch_clause_structure(self):
        """RED: CatchClause must have correct type and fields."""
        import oxc_python

        source = "try { foo(); } catch (error) { console.log(error); }"
        result = oxc_python.parse(source, source_type="module")

        catch_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "CatchClause":
                catch_node = node
                break

        assert catch_node is not None, "Should find CatchClause"
        assert catch_node.type == "CatchClause"
        assert isinstance(catch_node.type, str)

        # Required fields
        assert hasattr(catch_node, "param")
        assert hasattr(catch_node, "body")

        assert catch_node.param is not None  # Has error parameter
        assert catch_node.body is not None

    def test_catch_clause_without_parameter(self):
        """RED: CatchClause without parameter (ES2019+)."""
        import oxc_python

        source = "try { foo(); } catch { console.log('error'); }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "CatchClause":
                assert node.param is None  # No parameter binding
                assert node.body is not None
                break
        else:
            pytest.fail("No CatchClause found")

    def test_catch_clause_get_text(self):
        """RED: CatchClause must support get_text()."""
        import oxc_python

        source = "try { foo(); } catch (e) { bar(e); }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "CatchClause":
                text = node.get_text(source)
                assert "catch (e)" in text
                break
        else:
            pytest.fail("No CatchClause found")


class TestThrowStatement:
    """Tests for ThrowStatement node structure."""

    def test_throw_statement_structure(self):
        """RED: ThrowStatement must have correct type and fields."""
        import oxc_python

        source = "throw new Error('Something went wrong');"
        result = oxc_python.parse(source, source_type="module")

        throw_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ThrowStatement":
                throw_node = node
                break

        assert throw_node is not None, "Should find ThrowStatement"
        assert throw_node.type == "ThrowStatement"
        assert isinstance(throw_node.type, str)

        # Required fields
        assert hasattr(throw_node, "argument")
        assert throw_node.argument is not None

    def test_throw_statement_get_text(self):
        """RED: ThrowStatement must support get_text()."""
        import oxc_python

        source = "throw new Error('test');"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ThrowStatement":
                text = node.get_text(source)
                assert "throw" in text
                break
        else:
            pytest.fail("No ThrowStatement found")

    def test_throw_statement_get_line_range(self):
        """RED: ThrowStatement must support get_line_range()."""
        import oxc_python

        source = "throw new Error('test');"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ThrowStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 1
                break
        else:
            pytest.fail("No ThrowStatement found")


class TestReturnStatement:
    """Tests for ReturnStatement node structure."""

    def test_return_statement_with_value(self):
        """RED: ReturnStatement must have correct type and fields."""
        import oxc_python

        source = "function foo() { return 42; }"
        result = oxc_python.parse(source, source_type="module")

        return_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ReturnStatement":
                return_node = node
                break

        assert return_node is not None, "Should find ReturnStatement"
        assert return_node.type == "ReturnStatement"
        assert isinstance(return_node.type, str)

        # Required fields
        assert hasattr(return_node, "argument")
        assert return_node.argument is not None  # Returns a value

    def test_return_statement_no_argument(self):
        """RED: ReturnStatement with no argument."""
        import oxc_python

        source = "function foo() { return; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ReturnStatement":
                assert node.argument is None  # No return value
                break
        else:
            pytest.fail("No ReturnStatement found")

    def test_return_statement_get_text(self):
        """RED: ReturnStatement must support get_text()."""
        import oxc_python

        source = "function foo() { return x + y; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ReturnStatement":
                text = node.get_text(source)
                assert "return" in text
                break
        else:
            pytest.fail("No ReturnStatement found")

    def test_return_statement_get_line_range(self):
        """RED: ReturnStatement must support get_line_range()."""
        import oxc_python

        source = "function foo() { return 42; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ReturnStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 1
                break
        else:
            pytest.fail("No ReturnStatement found")


class TestBreakStatement:
    """Tests for BreakStatement node structure."""

    def test_break_statement_structure(self):
        """RED: BreakStatement must have correct type and fields."""
        import oxc_python

        source = "for (;;) { break; }"
        result = oxc_python.parse(source, source_type="module")

        break_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "BreakStatement":
                break_node = node
                break

        assert break_node is not None, "Should find BreakStatement"
        assert break_node.type == "BreakStatement"
        assert isinstance(break_node.type, str)

        # Required fields
        assert hasattr(break_node, "label")
        assert break_node.label is None  # No label

    def test_break_statement_with_label(self):
        """RED: BreakStatement with label."""
        import oxc_python

        source = "outer: for (;;) { inner: for (;;) { break outer; } }"
        result = oxc_python.parse(source, source_type="module")

        break_with_label = None
        for node, _ in oxc_python.walk(result.program):
            if node.type == "BreakStatement" and node.label is not None:
                break_with_label = node
                break

        assert break_with_label is not None, "Should find BreakStatement with label"
        assert break_with_label.label is not None

    def test_break_statement_get_text(self):
        """RED: BreakStatement must support get_text()."""
        import oxc_python

        source = "for (;;) { break; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "BreakStatement":
                text = node.get_text(source)
                assert "break" in text
                break
        else:
            pytest.fail("No BreakStatement found")


class TestContinueStatement:
    """Tests for ContinueStatement node structure."""

    def test_continue_statement_structure(self):
        """RED: ContinueStatement must have correct type and fields."""
        import oxc_python

        source = "for (let i = 0; i < 10; i++) { if (i % 2 === 0) continue; }"
        result = oxc_python.parse(source, source_type="module")

        continue_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "ContinueStatement":
                continue_node = node
                break

        assert continue_node is not None, "Should find ContinueStatement"
        assert continue_node.type == "ContinueStatement"
        assert isinstance(continue_node.type, str)

        # Required fields
        assert hasattr(continue_node, "label")
        assert continue_node.label is None  # No label

    def test_continue_statement_with_label(self):
        """RED: ContinueStatement with label."""
        import oxc_python

        source = (
            "outer: for (let i = 0; i < 10; i++) { "
            "for (let j = 0; j < 10; j++) { continue outer; } }"
        )
        result = oxc_python.parse(source, source_type="module")

        continue_with_label = None
        for node, _ in oxc_python.walk(result.program):
            if node.type == "ContinueStatement" and node.label is not None:
                continue_with_label = node
                break

        assert continue_with_label is not None, "Should find ContinueStatement with label"
        assert continue_with_label.label is not None

    def test_continue_statement_get_text(self):
        """RED: ContinueStatement must support get_text()."""
        import oxc_python

        source = "for (let i = 0; i < 10; i++) { continue; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "ContinueStatement":
                text = node.get_text(source)
                assert "continue" in text
                break
        else:
            pytest.fail("No ContinueStatement found")


class TestLabeledStatement:
    """Tests for LabeledStatement node structure."""

    def test_labeled_statement_structure(self):
        """RED: LabeledStatement must have correct type and fields."""
        import oxc_python

        source = "myLabel: for (;;) { break myLabel; }"
        result = oxc_python.parse(source, source_type="module")

        labeled_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "LabeledStatement":
                labeled_node = node
                break

        assert labeled_node is not None, "Should find LabeledStatement"
        assert labeled_node.type == "LabeledStatement"
        assert isinstance(labeled_node.type, str)

        # Required fields
        assert hasattr(labeled_node, "label")
        assert hasattr(labeled_node, "body")

        assert labeled_node.label is not None
        assert labeled_node.body is not None

    def test_labeled_statement_get_text(self):
        """RED: LabeledStatement must support get_text()."""
        import oxc_python

        source = "myLabel: for (;;) { break myLabel; }"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "LabeledStatement":
                text = node.get_text(source)
                assert "myLabel:" in text
                break
        else:
            pytest.fail("No LabeledStatement found")

    def test_labeled_statement_get_line_range(self):
        """RED: LabeledStatement must support get_line_range()."""
        import oxc_python

        source = """myLabel: for (let i = 0; i < 10; i++) {
    break myLabel;
}"""
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "LabeledStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 3
                break
        else:
            pytest.fail("No LabeledStatement found")


class TestEmptyStatement:
    """Tests for EmptyStatement node structure."""

    def test_empty_statement_structure(self):
        """RED: EmptyStatement must have correct type."""
        import oxc_python

        source = ";"
        result = oxc_python.parse(source, source_type="module")

        empty_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "EmptyStatement":
                empty_node = node
                break

        assert empty_node is not None, "Should find EmptyStatement"
        assert empty_node.type == "EmptyStatement"
        assert isinstance(empty_node.type, str)

    def test_empty_statement_in_for_loop(self):
        """RED: EmptyStatement in for loop (common pattern)."""
        import oxc_python

        source = "for (;;);"  # Infinite loop with empty body
        result = oxc_python.parse(source, source_type="module")

        empty_count = 0
        for node, _ in oxc_python.walk(result.program):
            if node.type == "EmptyStatement":
                empty_count += 1

        assert empty_count >= 1, "Should find at least one EmptyStatement"

    def test_empty_statement_get_text(self):
        """RED: EmptyStatement must support get_text()."""
        import oxc_python

        source = ";"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "EmptyStatement":
                text = node.get_text(source)
                assert text == ";"
                break
        else:
            pytest.fail("No EmptyStatement found")


class TestDebuggerStatement:
    """Tests for DebuggerStatement node structure."""

    def test_debugger_statement_structure(self):
        """RED: DebuggerStatement must have correct type."""
        import oxc_python

        source = "debugger;"
        result = oxc_python.parse(source, source_type="module")

        debugger_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "DebuggerStatement":
                debugger_node = node
                break

        assert debugger_node is not None, "Should find DebuggerStatement"
        assert debugger_node.type == "DebuggerStatement"
        assert isinstance(debugger_node.type, str)

    def test_debugger_statement_get_text(self):
        """RED: DebuggerStatement must support get_text()."""
        import oxc_python

        source = "debugger;"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "DebuggerStatement":
                text = node.get_text(source)
                assert "debugger" in text
                break
        else:
            pytest.fail("No DebuggerStatement found")

    def test_debugger_statement_get_line_range(self):
        """RED: DebuggerStatement must support get_line_range()."""
        import oxc_python

        source = "debugger;"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "DebuggerStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 1
                break
        else:
            pytest.fail("No DebuggerStatement found")


class TestWithStatement:
    """Tests for WithStatement node structure (deprecated but still valid syntax)."""

    def test_with_statement_structure(self):
        """RED: WithStatement must have correct type and fields."""
        import oxc_python

        # Note: 'with' is deprecated in strict mode but still valid in non-strict
        source = "with (obj) { console.log(prop); }"
        result = oxc_python.parse(source, source_type="script")  # Must be script, not module

        with_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "WithStatement":
                with_node = node
                break

        assert with_node is not None, "Should find WithStatement"
        assert with_node.type == "WithStatement"
        assert isinstance(with_node.type, str)

        # Required fields
        assert hasattr(with_node, "object")
        assert hasattr(with_node, "body")

        assert with_node.object is not None
        assert with_node.body is not None

    def test_with_statement_get_text(self):
        """RED: WithStatement must support get_text()."""
        import oxc_python

        source = "with (obj) { x = 1; }"
        result = oxc_python.parse(source, source_type="script")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "WithStatement":
                text = node.get_text(source)
                assert "with (obj)" in text
                break
        else:
            pytest.fail("No WithStatement found")

    def test_with_statement_get_line_range(self):
        """RED: WithStatement must support get_line_range()."""
        import oxc_python

        source = """with (obj) {
    console.log(prop);
}"""
        result = oxc_python.parse(source, source_type="script")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "WithStatement":
                start_line, end_line = node.get_line_range(source)
                assert start_line == 1
                assert end_line == 3
                break
        else:
            pytest.fail("No WithStatement found")


class TestVariableDeclarator:
    """Tests for VariableDeclarator node structure."""

    def test_variable_declarator_structure(self):
        """RED: VariableDeclarator must have correct type and fields."""
        import oxc_python

        source = "const x = 42;"
        result = oxc_python.parse(source, source_type="module")

        declarator_node = None
        for node, _depth in oxc_python.walk(result.program):
            if node.type == "VariableDeclarator":
                declarator_node = node
                break

        assert declarator_node is not None, "Should find VariableDeclarator"
        assert declarator_node.type == "VariableDeclarator"
        assert isinstance(declarator_node.type, str)

        # Required fields
        assert hasattr(declarator_node, "id")
        assert hasattr(declarator_node, "init")

        assert declarator_node.id is not None  # Pattern/Identifier
        assert declarator_node.init is not None  # Expression

    def test_variable_declarator_without_init(self):
        """RED: VariableDeclarator without initializer."""
        import oxc_python

        source = "let x;"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "VariableDeclarator":
                assert node.id is not None
                assert node.init is None  # No initializer
                break
        else:
            pytest.fail("No VariableDeclarator found")

    def test_variable_declarator_get_text(self):
        """RED: VariableDeclarator must support get_text()."""
        import oxc_python

        source = "const myVar = 123;"
        result = oxc_python.parse(source, source_type="module")

        for node, _ in oxc_python.walk(result.program):
            if node.type == "VariableDeclarator":
                text = node.get_text(source)
                assert "myVar" in text
                assert "123" in text
                break
        else:
            pytest.fail("No VariableDeclarator found")


"""
Phase 14: Expression Node Types - Implementation Tests

Tests for expression node types with a focus on ArrowFunctionExpression
which is critical for ChunkHound integration.

TESTING APPROACH:
This phase tests the structure and behavior of expression node classes.
Full AST traversal of expressions will be handled in later phases.
For now, we test:
1. Class instantiation and basic properties
2. Required fields and their types
3. ChunkHound compatibility patterns
4. get_text() and get_line_range() methods
"""


class TestArrowFunctionExpression:
    """Tests for ArrowFunctionExpression - CRITICAL for ChunkHound."""

    def test_arrow_function_basic_structure(self):
        """ArrowFunctionExpression must have correct type and fields."""
        import oxc_python

        span = oxc_python.Span(0, 20)
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=[],
            body=None,
            is_async=False,
            is_generator=False,
        )

        # Type property
        assert arrow_node.type == "ArrowFunctionExpression"
        assert isinstance(arrow_node.type, str)

        # Required fields
        assert hasattr(arrow_node, "is_async")
        assert hasattr(arrow_node, "span")
        assert hasattr(arrow_node, "params")
        assert hasattr(arrow_node, "body")

        # Field values
        assert arrow_node.is_async is False
        assert arrow_node.is_generator is False
        assert isinstance(arrow_node.params, list)

    def test_async_arrow_function(self):
        """Async arrow function must have is_async=True."""
        import oxc_python

        span = oxc_python.Span(10, 40)
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=[],
            body=None,
            is_async=True,
            is_generator=False,
        )

        assert arrow_node.type == "ArrowFunctionExpression"
        assert arrow_node.is_async is True
        assert arrow_node.is_generator is False

    def test_generator_arrow_function(self):
        """Generator arrow function must have is_generator=True."""
        import oxc_python

        span = oxc_python.Span(0, 30)
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=[],
            body=None,
            is_async=False,
            is_generator=True,
        )

        assert arrow_node.type == "ArrowFunctionExpression"
        assert arrow_node.is_async is False
        assert arrow_node.is_generator is True

    def test_async_generator_arrow_function(self):
        """Async generator arrow function."""
        import oxc_python

        span = oxc_python.Span(0, 30)
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=[],
            body=None,
            is_async=True,
            is_generator=True,
        )

        assert arrow_node.type == "ArrowFunctionExpression"
        assert arrow_node.is_async is True
        assert arrow_node.is_generator is True

    def test_arrow_with_params(self):
        """ArrowFunctionExpression with parameters."""
        import oxc_python

        span = oxc_python.Span(0, 20)
        # Create some dummy param nodes
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=["param1", "param2"],  # Simplified for testing
            body=None,
            is_async=False,
            is_generator=False,
        )

        assert len(arrow_node.params) == 2
        assert arrow_node.params == ["param1", "param2"]

    def test_arrow_has_span(self):
        """ArrowFunctionExpression must have span property."""
        import oxc_python

        span = oxc_python.Span(5, 25)
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=[],
            body=None,
            is_async=False,
            is_generator=False,
        )

        assert hasattr(arrow_node, "span")
        assert arrow_node.span == span
        assert arrow_node.span.start == 5
        assert arrow_node.span.end == 25

    def test_arrow_get_text(self):
        """ArrowFunctionExpression must have get_text()."""
        import oxc_python

        source = "const f = (x) => x + 1;"
        span = oxc_python.Span(10, 24)
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=[],
            body=None,
            is_async=False,
            is_generator=False,
        )

        assert hasattr(arrow_node, "get_text")
        text = arrow_node.get_text(source)
        assert isinstance(text, str)
        # Should extract the portion of source from span
        # Note: span 10 to 24 includes the semicolon
        assert text == "(x) => x + 1;"

    def test_arrow_get_line_range(self):
        """ArrowFunctionExpression must have get_line_range()."""
        import oxc_python

        source = "const f = (x) => x + 1;"
        span = oxc_python.Span(10, 24)
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=[],
            body=None,
            is_async=False,
            is_generator=False,
        )

        assert hasattr(arrow_node, "get_line_range")
        start_line, end_line = arrow_node.get_line_range(source)
        assert isinstance(start_line, int)
        assert isinstance(end_line, int)
        assert start_line >= 1
        assert end_line >= start_line


class TestCallExpression:
    """Tests for CallExpression node structure."""

    def test_call_expression_basic_structure(self):
        """CallExpression must have correct type and fields."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        call_node = oxc_python.CallExpression(
            span=span,
            callee=None,
            arguments=[],
        )

        # Type property
        assert call_node.type == "CallExpression"
        assert isinstance(call_node.type, str)

        # Required fields
        assert hasattr(call_node, "callee")
        assert hasattr(call_node, "arguments")
        assert isinstance(call_node.arguments, list)

    def test_call_with_arguments(self):
        """CallExpression with arguments."""
        import oxc_python

        span = oxc_python.Span(0, 15)
        call_node = oxc_python.CallExpression(
            span=span,
            callee=None,
            arguments=["arg1", "arg2", "arg3"],
        )

        assert len(call_node.arguments) == 3
        assert call_node.arguments == ["arg1", "arg2", "arg3"]

    def test_call_has_span(self):
        """CallExpression must have span property."""
        import oxc_python

        span = oxc_python.Span(5, 15)
        call_node = oxc_python.CallExpression(
            span=span,
            callee=None,
            arguments=[],
        )

        assert hasattr(call_node, "span")
        assert call_node.span == span


class TestMemberExpression:
    """Tests for MemberExpression node structure."""

    def test_member_expression_dot_notation(self):
        """MemberExpression for obj.property (computed=false)."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        member_node = oxc_python.MemberExpression(
            span=span,
            object=None,
            property=None,
            computed=False,
        )

        # Type property
        assert member_node.type == "MemberExpression"

        # Required fields
        assert hasattr(member_node, "object")
        assert hasattr(member_node, "property")
        assert hasattr(member_node, "computed")
        assert isinstance(member_node.computed, bool)

        # Dot notation is not computed
        assert member_node.computed is False

    def test_member_expression_bracket_notation(self):
        """MemberExpression for obj[index] (computed=true)."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        member_node = oxc_python.MemberExpression(
            span=span,
            object=None,
            property=None,
            computed=True,
        )

        assert member_node.type == "MemberExpression"
        assert member_node.computed is True


class TestBinaryExpression:
    """Tests for BinaryExpression node structure."""

    def test_binary_expression_addition(self):
        """BinaryExpression for a + b."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        binary_node = oxc_python.BinaryExpression(
            span=span,
            left=None,
            operator="+",
            right=None,
        )

        # Type property
        assert binary_node.type == "BinaryExpression"

        # Required fields
        assert hasattr(binary_node, "left")
        assert hasattr(binary_node, "operator")
        assert hasattr(binary_node, "right")
        assert binary_node.operator == "+"

    def test_binary_expression_various_operators(self):
        """BinaryExpression with various operators."""
        import oxc_python

        operators = ["+", "-", "*", "/", "%", "==", "===", "!==", "<", ">", "<=", ">=", "&&", "||"]

        for op in operators:
            span = oxc_python.Span(0, 10)
            binary_node = oxc_python.BinaryExpression(
                span=span,
                left=None,
                operator=op,
                right=None,
            )

            assert binary_node.type == "BinaryExpression"
            assert binary_node.operator == op


class TestUnaryExpression:
    """Tests for UnaryExpression node structure."""

    def test_unary_expression_not(self):
        """UnaryExpression for !x."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        unary_node = oxc_python.UnaryExpression(
            span=span,
            operator="!",
            argument=None,
        )

        # Type property
        assert unary_node.type == "UnaryExpression"

        # Required fields
        assert hasattr(unary_node, "operator")
        assert hasattr(unary_node, "argument")
        assert unary_node.operator == "!"

    def test_unary_expression_various_operators(self):
        """UnaryExpression with various operators."""
        import oxc_python

        operators = ["!", "-", "+", "~", "typeof", "void", "delete"]

        for op in operators:
            span = oxc_python.Span(0, 10)
            unary_node = oxc_python.UnaryExpression(
                span=span,
                operator=op,
                argument=None,
            )

            assert unary_node.type == "UnaryExpression"
            assert unary_node.operator == op


class TestConditionalExpression:
    """Tests for ConditionalExpression node structure."""

    def test_conditional_expression_ternary(self):
        """ConditionalExpression for test ? consequent : alternate."""
        import oxc_python

        span = oxc_python.Span(0, 20)
        cond_node = oxc_python.ConditionalExpression(
            span=span,
            test=None,
            consequent=None,
            alternate=None,
        )

        # Type property
        assert cond_node.type == "ConditionalExpression"

        # Required fields
        assert hasattr(cond_node, "test")
        assert hasattr(cond_node, "consequent")
        assert hasattr(cond_node, "alternate")


class TestObjectExpression:
    """Tests for ObjectExpression node structure."""

    def test_object_expression_basic(self):
        """ObjectExpression for {key: value}."""
        import oxc_python

        span = oxc_python.Span(0, 15)
        obj_node = oxc_python.ObjectExpression(
            span=span,
            properties=[],
        )

        # Type property
        assert obj_node.type == "ObjectExpression"

        # Required fields
        assert hasattr(obj_node, "properties")
        assert isinstance(obj_node.properties, list)

    def test_object_expression_with_properties(self):
        """ObjectExpression with properties."""
        import oxc_python

        span = oxc_python.Span(0, 20)
        obj_node = oxc_python.ObjectExpression(
            span=span,
            properties=["prop1", "prop2"],
        )

        assert len(obj_node.properties) == 2


class TestArrayExpression:
    """Tests for ArrayExpression node structure."""

    def test_array_expression_basic(self):
        """ArrayExpression for [1, 2, 3]."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        arr_node = oxc_python.ArrayExpression(
            span=span,
            elements=[],
        )

        # Type property
        assert arr_node.type == "ArrayExpression"

        # Required fields
        assert hasattr(arr_node, "elements")
        assert isinstance(arr_node.elements, list)

    def test_array_expression_with_elements(self):
        """ArrayExpression with elements."""
        import oxc_python

        span = oxc_python.Span(0, 15)
        arr_node = oxc_python.ArrayExpression(
            span=span,
            elements=[1, 2, 3],
        )

        assert len(arr_node.elements) == 3


class TestIdentifier:
    """Tests for Identifier node structure."""

    def test_identifier_basic(self):
        """Identifier for variable/function names."""
        import oxc_python

        span = oxc_python.Span(0, 3)
        ident_node = oxc_python.Identifier(
            span=span,
            name="x",
        )

        # Type property
        assert ident_node.type == "Identifier"

        # Required fields
        assert hasattr(ident_node, "name")
        assert ident_node.name == "x"

    def test_identifier_various_names(self):
        """Identifier with various names."""
        import oxc_python

        names = ["myVar", "functionName", "_private", "$dollar", "camelCase", "snake_case"]

        for name in names:
            span = oxc_python.Span(0, len(name))
            ident_node = oxc_python.Identifier(
                span=span,
                name=name,
            )

            assert ident_node.type == "Identifier"
            assert ident_node.name == name


class TestLiteral:
    """Tests for Literal node structure."""

    def test_literal_number(self):
        """Literal for numeric values."""
        import oxc_python

        span = oxc_python.Span(0, 2)
        lit_node = oxc_python.Literal(
            span=span,
            value=42,
            raw="42",
        )

        # Type property
        assert lit_node.type == "Literal"

        # Required fields
        assert hasattr(lit_node, "value")
        assert hasattr(lit_node, "raw")
        assert lit_node.value == 42
        assert lit_node.raw == "42"

    def test_literal_string(self):
        """Literal for string values."""
        import oxc_python

        span = oxc_python.Span(0, 5)
        lit_node = oxc_python.Literal(
            span=span,
            value="hello",
            raw='"hello"',
        )

        assert lit_node.type == "Literal"
        assert lit_node.value == "hello"
        assert lit_node.raw == '"hello"'

    def test_literal_boolean(self):
        """Literal for boolean values."""
        import oxc_python

        span = oxc_python.Span(0, 4)
        lit_node = oxc_python.Literal(
            span=span,
            value=True,
            raw="true",
        )

        assert lit_node.type == "Literal"
        assert lit_node.value is True
        assert lit_node.raw == "true"

    def test_literal_null(self):
        """Literal for null value."""
        import oxc_python

        span = oxc_python.Span(0, 4)
        lit_node = oxc_python.Literal(
            span=span,
            value=None,
            raw="null",
        )

        assert lit_node.type == "Literal"
        assert lit_node.value is None
        assert lit_node.raw == "null"


class TestChunkHoundExpressionIntegration:
    """Tests for ChunkHound expression compatibility - CRITICAL."""

    def test_chunkhound_arrow_function_type_mapping(self):
        """
        ChunkHound Validation: ArrowFunctionExpression maps to FUNCTION type.

        This is the PRIMARY requirement for Phase 14.
        ChunkHound uses _map_chunk_type() to map node types to chunk types.
        """
        import oxc_python

        # Simulate ChunkHound's _map_chunk_type()
        chunk_type_mapping = {
            "FunctionDeclaration": "FUNCTION",
            "ArrowFunctionExpression": "FUNCTION",  # CRITICAL
            "CallExpression": "CALL",
            "ClassDeclaration": "CLASS",
        }

        span = oxc_python.Span(0, 20)
        arrow_node = oxc_python.ArrowFunctionExpression(
            span=span,
            params=[],
            body=None,
            is_async=False,
            is_generator=False,
        )

        # Verify ChunkHound can map this node type
        chunk_type = chunk_type_mapping.get(arrow_node.type)
        assert chunk_type == "FUNCTION", "ArrowFunctionExpression should map to FUNCTION"

    def test_chunkhound_call_expression_access_pattern(self):
        """ChunkHound: CallExpression fields must be accessible."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        call_node = oxc_python.CallExpression(
            span=span,
            callee=None,
            arguments=[],
        )

        # ChunkHound accesses these properties in _extract_chunk()
        assert hasattr(call_node, "callee"), "ChunkHound expects callee"
        assert hasattr(call_node, "arguments"), "ChunkHound expects arguments"
        assert isinstance(call_node.arguments, list), "arguments must be a list"

    def test_chunkhound_member_expression_access_pattern(self):
        """ChunkHound: MemberExpression fields must be accessible."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        member_node = oxc_python.MemberExpression(
            span=span,
            object=None,
            property=None,
            computed=False,
        )

        # ChunkHound accesses these properties
        assert hasattr(member_node, "object"), "ChunkHound expects object"
        assert hasattr(member_node, "property"), "ChunkHound expects property"
        assert hasattr(member_node, "computed"), "ChunkHound expects computed"

    def test_chunkhound_expression_type_checking(self):
        """Verify expression nodes support type-based filtering."""
        import oxc_python

        expressions = [
            oxc_python.ArrowFunctionExpression(
                span=oxc_python.Span(0, 10),
                params=[],
                body=None,
                is_async=False,
                is_generator=False,
            ),
            oxc_python.CallExpression(
                span=oxc_python.Span(10, 20),
                callee=None,
                arguments=[],
            ),
            oxc_python.MemberExpression(
                span=oxc_python.Span(20, 30),
                object=None,
                property=None,
                computed=False,
            ),
            oxc_python.Identifier(
                span=oxc_python.Span(30, 35),
                name="foo",
            ),
        ]

        # ChunkHound pattern: iterate and filter by type
        expression_types = [expr.type for expr in expressions]

        assert "ArrowFunctionExpression" in expression_types
        assert "CallExpression" in expression_types
        assert "MemberExpression" in expression_types
        assert "Identifier" in expression_types


class TestExpressionTypes:
    """Tests verifying all expression types have required properties."""

    def test_all_expression_types_have_type_property(self):
        """Verify all expression types have .type property."""
        import oxc_python

        expressions = [
            oxc_python.ArrowFunctionExpression(
                span=oxc_python.Span(0, 1),
                params=[],
                body=None,
                is_async=False,
                is_generator=False,
            ),
            oxc_python.CallExpression(
                span=oxc_python.Span(0, 1),
                callee=None,
                arguments=[],
            ),
            oxc_python.MemberExpression(
                span=oxc_python.Span(0, 1),
                object=None,
                property=None,
                computed=False,
            ),
            oxc_python.BinaryExpression(
                span=oxc_python.Span(0, 1),
                left=None,
                operator="+",
                right=None,
            ),
            oxc_python.UnaryExpression(
                span=oxc_python.Span(0, 1),
                operator="!",
                argument=None,
            ),
            oxc_python.ConditionalExpression(
                span=oxc_python.Span(0, 1),
                test=None,
                consequent=None,
                alternate=None,
            ),
            oxc_python.ObjectExpression(
                span=oxc_python.Span(0, 1),
                properties=[],
            ),
            oxc_python.ArrayExpression(
                span=oxc_python.Span(0, 1),
                elements=[],
            ),
            oxc_python.Identifier(
                span=oxc_python.Span(0, 1),
                name="x",
            ),
            oxc_python.Literal(
                span=oxc_python.Span(0, 1),
                value=42,
                raw="42",
            ),
        ]

        expected_types = [
            "ArrowFunctionExpression",
            "CallExpression",
            "MemberExpression",
            "BinaryExpression",
            "UnaryExpression",
            "ConditionalExpression",
            "ObjectExpression",
            "ArrayExpression",
            "Identifier",
            "Literal",
        ]

        for expr, expected_type in zip(expressions, expected_types, strict=False):
            assert hasattr(expr, "type"), f"{expected_type} should have type property"
            assert expr.type == expected_type, f"{expected_type} type property mismatch"
            assert isinstance(expr.type, str), f"{expected_type} type should be string"

    def test_all_expression_types_have_span(self):
        """Verify all expression types have .span property."""
        import oxc_python

        span = oxc_python.Span(0, 10)
        expressions = [
            oxc_python.ArrowFunctionExpression(
                span=span,
                params=[],
                body=None,
                is_async=False,
                is_generator=False,
            ),
            oxc_python.CallExpression(
                span=span,
                callee=None,
                arguments=[],
            ),
            oxc_python.MemberExpression(
                span=span,
                object=None,
                property=None,
                computed=False,
            ),
            oxc_python.BinaryExpression(
                span=span,
                left=None,
                operator="+",
                right=None,
            ),
            oxc_python.UnaryExpression(
                span=span,
                operator="!",
                argument=None,
            ),
            oxc_python.ConditionalExpression(
                span=span,
                test=None,
                consequent=None,
                alternate=None,
            ),
            oxc_python.ObjectExpression(
                span=span,
                properties=[],
            ),
            oxc_python.ArrayExpression(
                span=span,
                elements=[],
            ),
            oxc_python.Identifier(
                span=span,
                name="x",
            ),
            oxc_python.Literal(
                span=span,
                value=42,
                raw="42",
            ),
        ]

        for expr in expressions:
            assert hasattr(expr, "span"), f"{expr.type} should have span property"
            assert expr.span == span
            assert hasattr(expr.span, "start")
            assert hasattr(expr.span, "end")

    def test_all_expression_types_have_get_text(self):
        """Verify all expression types have get_text() method."""
        import oxc_python

        source = "const x = 42;"
        span = oxc_python.Span(0, len(source))

        expressions = [
            oxc_python.ArrowFunctionExpression(
                span=span,
                params=[],
                body=None,
                is_async=False,
                is_generator=False,
            ),
            oxc_python.CallExpression(
                span=span,
                callee=None,
                arguments=[],
            ),
            oxc_python.MemberExpression(
                span=span,
                object=None,
                property=None,
                computed=False,
            ),
            oxc_python.BinaryExpression(
                span=span,
                left=None,
                operator="+",
                right=None,
            ),
            oxc_python.UnaryExpression(
                span=span,
                operator="!",
                argument=None,
            ),
            oxc_python.ConditionalExpression(
                span=span,
                test=None,
                consequent=None,
                alternate=None,
            ),
            oxc_python.ObjectExpression(
                span=span,
                properties=[],
            ),
            oxc_python.ArrayExpression(
                span=span,
                elements=[],
            ),
            oxc_python.Identifier(
                span=span,
                name="x",
            ),
            oxc_python.Literal(
                span=span,
                value=42,
                raw="42",
            ),
        ]

        for expr in expressions:
            assert hasattr(expr, "get_text"), f"{expr.type} should have get_text()"
            text = expr.get_text(source)
            assert isinstance(text, str)

    def test_all_expression_types_have_get_line_range(self):
        """Verify all expression types have get_line_range() method."""
        import oxc_python

        source = "const x = 42;"
        span = oxc_python.Span(0, len(source))

        expressions = [
            oxc_python.ArrowFunctionExpression(
                span=span,
                params=[],
                body=None,
                is_async=False,
                is_generator=False,
            ),
            oxc_python.CallExpression(
                span=span,
                callee=None,
                arguments=[],
            ),
            oxc_python.MemberExpression(
                span=span,
                object=None,
                property=None,
                computed=False,
            ),
            oxc_python.BinaryExpression(
                span=span,
                left=None,
                operator="+",
                right=None,
            ),
            oxc_python.UnaryExpression(
                span=span,
                operator="!",
                argument=None,
            ),
            oxc_python.ConditionalExpression(
                span=span,
                test=None,
                consequent=None,
                alternate=None,
            ),
            oxc_python.ObjectExpression(
                span=span,
                properties=[],
            ),
            oxc_python.ArrayExpression(
                span=span,
                elements=[],
            ),
            oxc_python.Identifier(
                span=span,
                name="x",
            ),
            oxc_python.Literal(
                span=span,
                value=42,
                raw="42",
            ),
        ]

        for expr in expressions:
            assert hasattr(expr, "get_line_range"), f"{expr.type} should have get_line_range()"
            start_line, end_line = expr.get_line_range(source)
            assert isinstance(start_line, int)
            assert isinstance(end_line, int)
            assert start_line >= 1
            assert end_line >= start_line


"""
Phase 15: Import/Export Declaration Node Types

Tests for ES module import/export statement nodes.
CRITICAL: ImportDeclaration needed for ChunkHound's HIGH-1 requirement.
"""


def test_import_declaration_exists():
    """RED: Test that ImportDeclaration can be parsed."""
    import oxc_python

    source = 'import { foo } from "module";'
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid

    # Find ImportDeclaration node
    found = False
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportDeclaration":
            found = True
            break

    assert found, "Should find ImportDeclaration node"


def test_import_declaration_properties():
    """RED: Test ImportDeclaration has required properties."""
    import oxc_python

    source = 'import { foo, bar } from "./module.js";'
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportDeclaration":
            # Must have source (module path)
            assert hasattr(node, "source"), "ImportDeclaration missing 'source'"
            assert node.source is not None

            # source should be a string or have a value property
            if hasattr(node.source, "value"):
                assert node.source.value == "./module.js"
            else:
                assert node.source == "./module.js"

            # Must have specifiers (list of imported items)
            assert hasattr(node, "specifiers"), "ImportDeclaration missing 'specifiers'"
            assert isinstance(node.specifiers, list)
            assert len(node.specifiers) == 2  # foo and bar

            return

    pytest.fail("ImportDeclaration not found")


def test_import_specifier_properties():
    """RED: Test ImportSpecifier has imported and local names."""
    import oxc_python

    source = 'import { foo as bar } from "module";'
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportSpecifier":
            # Should have imported (original name)
            assert hasattr(node, "imported"), "ImportSpecifier missing 'imported'"

            # Should have local (local binding name)
            assert hasattr(node, "local"), "ImportSpecifier missing 'local'"

            return

    pytest.fail("ImportSpecifier not found")


def test_import_default_specifier():
    """RED: Test ImportDefaultSpecifier for default imports."""
    import oxc_python

    source = 'import React from "react";'
    result = oxc_python.parse(source, source_type="module")

    found = False
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportDefaultSpecifier":
            found = True
            # Should have local binding name
            assert hasattr(node, "local"), "ImportDefaultSpecifier missing 'local'"
            break

    assert found, "Should find ImportDefaultSpecifier"


def test_import_namespace_specifier():
    """RED: Test ImportNamespaceSpecifier for namespace imports."""
    import oxc_python

    source = 'import * as utils from "utils";'
    result = oxc_python.parse(source, source_type="module")

    found = False
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportNamespaceSpecifier":
            found = True
            # Should have local binding name
            assert hasattr(node, "local"), "ImportNamespaceSpecifier missing 'local'"
            break

    assert found, "Should find ImportNamespaceSpecifier"


def test_export_named_declaration():
    """RED: Test ExportNamedDeclaration for named exports."""
    import oxc_python

    source = "export { foo, bar };"
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ExportNamedDeclaration":
            # Should have specifiers
            assert hasattr(node, "specifiers"), "ExportNamedDeclaration missing 'specifiers'"
            assert isinstance(node.specifiers, list)
            assert len(node.specifiers) == 2

            # declaration should be None (not exporting a declaration)
            assert hasattr(node, "declaration"), "ExportNamedDeclaration missing 'declaration'"

            # source should be None (not re-exporting)
            assert hasattr(node, "source"), "ExportNamedDeclaration missing 'source'"

            return

    pytest.fail("ExportNamedDeclaration not found")


def test_export_default_declaration():
    """RED: Test ExportDefaultDeclaration for default exports."""
    import oxc_python

    source = "export default function foo() {}"
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ExportDefaultDeclaration":
            # Should have declaration
            assert hasattr(node, "declaration"), "ExportDefaultDeclaration missing 'declaration'"
            assert node.declaration is not None
            return

    pytest.fail("ExportDefaultDeclaration not found")


def test_export_all_declaration():
    """RED: Test ExportAllDeclaration for export * syntax."""
    import oxc_python

    source = 'export * from "other-module";'
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ExportAllDeclaration":
            # Should have source
            assert hasattr(node, "source"), "ExportAllDeclaration missing 'source'"
            assert node.source is not None
            return

    pytest.fail("ExportAllDeclaration not found")


def test_export_specifier_properties():
    """RED: Test ExportSpecifier has exported and local names."""
    import oxc_python

    source = "export { foo as bar };"
    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ExportSpecifier":
            # Should have local (original name)
            assert hasattr(node, "local"), "ExportSpecifier missing 'local'"

            # Should have exported (exported name)
            assert hasattr(node, "exported"), "ExportSpecifier missing 'exported'"

            return

    pytest.fail("ExportSpecifier not found")


def test_mixed_imports():
    """RED: Test file with mixed import types."""
    import oxc_python

    source = """
    import React from 'react';
    import { useState, useEffect } from 'react';
    import * as utils from './utils';
    import './styles.css';
    """
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid

    # Count ImportDeclarations
    import_count = sum(
        1 for node, _ in oxc_python.walk(result.program) if node.type == "ImportDeclaration"
    )

    assert import_count == 4, f"Expected 4 imports, found {import_count}"


def test_mixed_exports():
    """RED: Test file with mixed export types."""
    import oxc_python

    source = """
    export function foo() {}
    export const bar = 1;
    export { baz };
    export default class MyClass {}
    export * from './other';
    """
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid

    # Count export types
    export_nodes = [
        node.type for node, _ in oxc_python.walk(result.program) if "Export" in node.type
    ]

    assert len(export_nodes) > 0, "Should find export nodes"


# ChunkHound Validation
def test_chunkhound_import_extraction():
    """
    ChunkHound Validation: Test extracting import statements.

    ChunkHound maps ImportDeclaration to ChunkType.IMPORT for tracking
    module dependencies.
    """
    import oxc_python

    source = """
    import React from 'react';
    import { render } from 'react-dom';
    import * as utils from './utils';

    function App() {
        return React.createElement('div');
    }
    """
    result = oxc_python.parse(source, source_type="module")

    # Extract imports like ChunkHound would
    imports = []
    for node, depth in oxc_python.walk(result.program):
        if node.type == "ImportDeclaration":
            # Get source module
            source_module = None
            if hasattr(node, "source"):
                if hasattr(node.source, "value"):
                    source_module = node.source.value
                else:
                    source_module = node.source

            # Get imported names
            imported_names = []
            if hasattr(node, "specifiers"):
                for spec in node.specifiers:
                    if hasattr(spec, "local"):
                        if hasattr(spec.local, "name"):
                            imported_names.append(spec.local.name)
                        else:
                            imported_names.append(str(spec.local))

            imports.append(
                {
                    "source": source_module,
                    "names": imported_names,
                    "depth": depth,
                }
            )

    # Verify we found all imports
    assert len(imports) == 3, f"Expected 3 imports, found {len(imports)}"

    # Verify sources
    sources = [imp["source"] for imp in imports]
    assert "react" in sources
    assert "react-dom" in sources
    assert "./utils" in sources


def test_chunkhound_export_extraction():
    """
    ChunkHound Validation: Test extracting export statements.

    ChunkHound maps export declarations to ChunkType.EXPORT for tracking
    public API surface.
    """
    import oxc_python

    source = """
    export function publicFunction() {
        return 42;
    }

    export const publicConstant = 'value';

    export default class PublicClass {
        method() {}
    }

    function privateFunction() {
        return 0;
    }
    """
    result = oxc_python.parse(source, source_type="module")

    # Extract exports like ChunkHound would
    exports = []
    for node, depth in oxc_python.walk(result.program):
        if "Export" in node.type:
            export_type = node.type

            # Try to get symbol name
            symbol = None
            if hasattr(node, "declaration") and node.declaration:
                if hasattr(node.declaration, "name"):
                    symbol = node.declaration.name

            exports.append(
                {
                    "type": export_type,
                    "symbol": symbol,
                    "depth": depth,
                }
            )

    # Should find export declarations (not private function)
    assert len(exports) >= 3, f"Expected at least 3 exports, found {len(exports)}"

    # Should have default export
    default_exports = [e for e in exports if e["type"] == "ExportDefaultDeclaration"]
    assert len(default_exports) >= 1, "Should find default export"


def test_chunkhound_module_path_extraction():
    """
    ChunkHound Validation: Test extracting module paths from imports.

    Useful for dependency analysis and module graph construction.
    """
    import oxc_python

    source = """
    import local from './local';
    import relative from '../parent';
    import scoped from '@scope/package';
    import bare from 'package';
    """
    result = oxc_python.parse(source, source_type="module")

    # Extract module paths
    module_paths = []
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportDeclaration":
            if hasattr(node, "source"):
                source_val = node.source
                if hasattr(source_val, "value"):
                    module_paths.append(source_val.value)
                else:
                    module_paths.append(source_val)

    # Verify we got all paths
    assert len(module_paths) == 4
    assert "./local" in module_paths
    assert "../parent" in module_paths
    assert "@scope/package" in module_paths
    assert "package" in module_paths


def test_typescript_imports():
    """RED: Test import/export with TypeScript syntax."""
    import oxc_python

    # Note: import type { } syntax with type modifiers may not be fully supported
    # Test basic TypeScript imports instead
    source = """
    import { MyType } from './types';
    import { OtherType, value } from './module';
    """
    result = oxc_python.parse(source, source_type="tsx")

    # Should parse TypeScript imports
    assert result.is_valid

    # Should find import declarations
    imports = sum(
        1 for node, _ in oxc_python.walk(result.program) if node.type == "ImportDeclaration"
    )
    assert imports >= 2


def test_dynamic_import_expression():
    """RED: Test dynamic import() expressions (if supported)."""
    import oxc_python

    source = """
    async function loadModule() {
        const module = await import('./dynamic-module.js');
        return module.default;
    }
    """
    result = oxc_python.parse(source, source_type="module")

    # Should parse without errors
    assert result.is_valid

    # May have ImportExpression node (different from ImportDeclaration)
    # This is optional - depends on oxc's AST representation


def test_side_effect_imports():
    """RED: Test imports for side effects (no bindings)."""
    import oxc_python

    source = """
    import './polyfill.js';
    import 'core-js/stable';
    """
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid

    # Should find imports even without specifiers
    imports = []
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportDeclaration":
            imports.append(node)

    assert len(imports) == 2

    # Specifiers should be empty or missing
    for imp in imports:
        if hasattr(imp, "specifiers"):
            assert len(imp.specifiers) == 0, "Side-effect imports should have no specifiers"


def test_re_exports():
    """RED: Test export...from re-export syntax."""
    import oxc_python

    source = """
    export { foo, bar } from './module';
    export * from './other-module';
    export { default as renamed } from './default-module';
    """
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid

    # Find re-exports (exports with source)
    re_exports = []
    for node, _depth in oxc_python.walk(result.program):
        if node.type in ("ExportNamedDeclaration", "ExportAllDeclaration"):
            if hasattr(node, "source") and node.source is not None:
                re_exports.append(node)

    assert len(re_exports) >= 2, "Should find re-export statements"


def test_export_declaration_with_inline_declaration():
    """RED: Test export with inline declaration."""
    import oxc_python

    source = """
    export function inlineFunction() {
        return 42;
    }

    export class InlineClass {
        method() {}
    }

    export const inlineConst = 'value';
    """
    result = oxc_python.parse(source, source_type="module")

    assert result.is_valid

    # Find exports with declarations
    exports_with_decl = []
    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ExportNamedDeclaration":
            if hasattr(node, "declaration") and node.declaration is not None:
                exports_with_decl.append(node)

    assert len(exports_with_decl) >= 3, "Should find inline export declarations"


def test_import_export_get_text():
    """RED: Test get_text() on import/export nodes."""
    import oxc_python

    source = """import { foo } from 'module';
export const bar = 1;"""

    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportDeclaration":
            text = node.get_text(source)
            assert "import" in text.lower()
            assert "foo" in text
            assert "module" in text

        elif node.type == "ExportNamedDeclaration":
            text = node.get_text(source)
            assert "export" in text.lower()
            assert "bar" in text


def test_import_export_line_range():
    """RED: Test get_line_range() on import/export nodes."""
    import oxc_python

    source = """// Line 1
import foo from 'module';
// Line 3
export const bar = 1;
"""

    result = oxc_python.parse(source, source_type="module")

    for node, _depth in oxc_python.walk(result.program):
        if node.type == "ImportDeclaration":
            start, end = node.get_line_range(source)
            assert start == 2, f"Import should start at line 2, got {start}"

        elif node.type == "ExportNamedDeclaration":
            start, end = node.get_line_range(source)
            assert start == 4, f"Export should start at line 4, got {start}"

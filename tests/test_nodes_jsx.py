"""
Test suite for JSX and TSX AST node types.

This module combines tests from test_phase_17_jsx_nodes.py (51 tests),
validating JSX/TSX-specific AST nodes including JSX elements, attributes,
fragments, and React component patterns.
"""

"""
Phase 17: JSX Node Types

Tests for JSX AST nodes: JSXElement, JSXFragment, JSXAttribute, etc.
Critical for React codebase support.
"""


def find_node(program, node_type):
    """Helper to find first node of given type in AST."""
    from oxc_python import walk

    for node, _ in walk(program):
        if node.type == node_type:
            return node
    return None


def find_all_nodes(program, node_type):
    """Helper to find all nodes of given type in AST."""
    from oxc_python import walk

    return [node for node, _ in walk(program) if node.type == node_type]


class TestJSXElementBasics:
    """Tests for basic JSX element parsing."""

    def test_jsx_element_basic(self):
        """RED: Test parsing basic JSX element."""
        from oxc_python import parse, walk

        source = "const el = <div>Hello</div>;"
        result = parse(source, source_type="jsx")

        assert result.is_valid, "Should parse valid JSX"

        # Find JSXElement node
        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1, "Should find one JSXElement"

        element = jsx_elements[0]
        assert hasattr(element, "opening_element"), "JSXElement must have opening_element"
        assert hasattr(element, "children"), "JSXElement must have children"
        assert hasattr(element, "closing_element"), "JSXElement must have closing_element"

    def test_jsx_self_closing_element(self):
        """RED: Test self-closing JSX element."""
        from oxc_python import parse, walk

        source = "const img = <img src='pic.jpg' />;"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1
        element = jsx_elements[0]

        # Self-closing elements have no closing_element
        assert element.closing_element is None
        assert element.opening_element is not None
        assert hasattr(element.opening_element, "self_closing")
        assert element.opening_element.self_closing is True

    def test_jsx_nested_elements(self):
        """RED: Test deeply nested JSX structure."""
        from oxc_python import parse, walk

        source = """
        const component = (
            <div className="outer">
                <header>
                    <h1>Title</h1>
                    <nav>
                        <a href="#">Link</a>
                    </nav>
                </header>
                <main>
                    <p>Content</p>
                </main>
            </div>
        );
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find: div, header, h1, nav, a, main, p
        assert len(elements) == 7, f"Should find 7 elements, found {len(elements)}"

    def test_jsx_empty_children(self):
        """RED: Test JSX element with no children."""
        from oxc_python import parse, walk

        source = "<div></div>"
        result = parse(source, source_type="jsx")

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1
        element = jsx_elements[0]

        assert hasattr(element, "children")
        assert isinstance(element.children, list)
        # May be empty or contain only whitespace JSXText
        assert len(element.children) == 0 or all(
            child.type == "JSXText" for child in element.children
        )


class TestJSXOpeningElement:
    """Tests for JSXOpeningElement structure."""

    def test_jsx_opening_element(self):
        """RED: Test JSXOpeningElement structure."""
        from oxc_python import parse, walk

        source = '<div className="container" id="main"></div>'
        result = parse(source, source_type="jsx")

        assert result.is_valid

        opening_elements = [
            node for node, _ in walk(result.program) if node.type == "JSXOpeningElement"
        ]

        assert len(opening_elements) == 1
        opening = opening_elements[0]

        assert hasattr(opening, "name"), "JSXOpeningElement must have name"
        assert hasattr(opening, "attributes"), "JSXOpeningElement must have attributes"
        assert hasattr(opening, "self_closing"), "JSXOpeningElement must have self_closing"

        # Should have 2 attributes: className and id
        assert isinstance(opening.attributes, list)
        assert len(opening.attributes) == 2


class TestJSXClosingElement:
    """Tests for JSXClosingElement structure."""

    def test_jsx_closing_element(self):
        """RED: Test JSXClosingElement structure."""
        from oxc_python import parse, walk

        source = "<div></div>"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        closing_elements = [
            node for node, _ in walk(result.program) if node.type == "JSXClosingElement"
        ]

        assert len(closing_elements) == 1
        closing = closing_elements[0]

        assert hasattr(closing, "name"), "JSXClosingElement must have name"


class TestJSXIdentifier:
    """Tests for JSXIdentifier nodes."""

    def test_jsx_identifier(self):
        """RED: Test JSXIdentifier for element names."""
        from oxc_python import parse, walk

        source = "<button>Click</button>"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        identifiers = [node for node, _ in walk(result.program) if node.type == "JSXIdentifier"]

        # Should find "button" identifier in opening and closing tags
        assert len(identifiers) == 2

        identifier = identifiers[0]
        assert hasattr(identifier, "name"), "JSXIdentifier must have name"
        assert isinstance(identifier.name, str)
        assert identifier.name == "button"


class TestJSXAttributes:
    """Tests for JSX attribute nodes."""

    def test_jsx_attribute(self):
        """RED: Test JSXAttribute structure."""
        from oxc_python import parse, walk

        source = '<div className="container" disabled></div>'
        result = parse(source, source_type="jsx")

        assert result.is_valid

        attributes = [node for node, _ in walk(result.program) if node.type == "JSXAttribute"]

        assert len(attributes) == 2, "Should find className and disabled attributes"

        attr = attributes[0]
        assert hasattr(attr, "name"), "JSXAttribute must have name"
        assert hasattr(attr, "value"), "JSXAttribute must have value"

        # Attribute name should be JSXIdentifier
        assert attr.name.type == "JSXIdentifier"

        # Find disabled attribute (should have no value)
        disabled = next((a for a in attributes if a.name.name == "disabled"), None)
        assert disabled is not None
        assert disabled.value is None, "Boolean attribute should have None value"

    def test_jsx_spread_attribute(self):
        """RED: Test JSXSpreadAttribute for {...props}."""
        from oxc_python import parse, walk

        source = "<Component {...props} />"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        spread_attrs = [
            node for node, _ in walk(result.program) if node.type == "JSXSpreadAttribute"
        ]

        assert len(spread_attrs) == 1, "Should find spread attribute"

        spread = spread_attrs[0]
        assert hasattr(spread, "argument"), "JSXSpreadAttribute must have argument"
        assert spread.argument is not None

    def test_jsx_component_with_props(self):
        """RED: Test React component with multiple prop types."""
        from oxc_python import parse, walk

        source = """
        <Button
            onClick={handleClick}
            disabled
            className="primary"
            style={{ color: 'blue' }}
            {...extraProps}
        >
            Click Me
        </Button>
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        attributes = [
            node
            for node, _ in walk(result.program)
            if node.type in ("JSXAttribute", "JSXSpreadAttribute")
        ]

        # onClick, disabled, className, style, spread
        assert len(attributes) == 5, f"Should find 5 attributes, found {len(attributes)}"

        # Check for spread attribute
        spread_attrs = [a for a in attributes if a.type == "JSXSpreadAttribute"]
        assert len(spread_attrs) == 1, "Should find spread attribute"


class TestJSXText:
    """Tests for JSXText nodes."""

    def test_jsx_text(self):
        """RED: Test JSXText for text content."""
        from oxc_python import parse, walk

        source = "<div>Hello World</div>"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        text_nodes = [node for node, _ in walk(result.program) if node.type == "JSXText"]

        assert len(text_nodes) == 1, "Should find text node"

        text = text_nodes[0]
        assert hasattr(text, "value"), "JSXText must have value"
        assert hasattr(text, "raw"), "JSXText must have raw"

        assert isinstance(text.value, str)
        assert "Hello World" in text.value


class TestJSXFragment:
    """Tests for JSXFragment nodes."""

    def test_jsx_fragment(self):
        """RED: Test JSXFragment for <>...</> syntax."""
        from oxc_python import parse, walk

        source = "const el = <>First<span>Second</span></>;"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        fragments = [node for node, _ in walk(result.program) if node.type == "JSXFragment"]

        assert len(fragments) == 1, "Should find fragment"

        fragment = fragments[0]
        assert hasattr(fragment, "children"), "JSXFragment must have children"
        assert isinstance(fragment.children, list)
        # Fragment has JSXText "First" and JSXElement <span>
        assert len(fragment.children) == 2, "Fragment should have 2 children"


class TestJSXMemberExpression:
    """Tests for JSXMemberExpression nodes."""

    def test_jsx_member_expression(self):
        """RED: Test JSXMemberExpression for <React.Fragment>."""
        from oxc_python import parse, walk

        source = "<React.Fragment><div /></React.Fragment>"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        member_exprs = [
            node for node, _ in walk(result.program) if node.type == "JSXMemberExpression"
        ]

        # Member expression appears in both opening and closing tags
        assert len(member_exprs) == 2, "Should find member expressions in opening/closing"

        member = member_exprs[0]
        assert hasattr(member, "object"), "JSXMemberExpression must have object"
        assert hasattr(member, "property"), "JSXMemberExpression must have property"


class TestJSXExpressionContainer:
    """Tests for JSXExpressionContainer nodes."""

    def test_jsx_with_expressions(self):
        """RED: Test JSX with embedded JavaScript expressions."""
        from oxc_python import parse, walk

        source = """
        const name = "World";
        const el = <div>Hello {name}</div>;
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        # Find JSXExpressionContainer nodes
        expr_containers = [
            node for node, _ in walk(result.program) if node.type == "JSXExpressionContainer"
        ]

        assert len(expr_containers) == 1, "Should find expression container {name}"

        container = expr_containers[0]
        assert hasattr(container, "expression"), "JSXExpressionContainer must have expression"


class TestJSXConditionalRendering:
    """Tests for JSX conditional rendering patterns."""

    def test_jsx_conditional_rendering(self):
        """RED: Test JSX with conditional expressions."""
        from oxc_python import parse, walk

        source = """
        const el = (
            <div>
                {isLoggedIn ? <UserPanel /> : <LoginButton />}
            </div>
        );
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        # Should have conditional expression and multiple JSX elements
        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # div, UserPanel, LoginButton
        assert len(jsx_elements) == 3

    def test_jsx_map_iteration(self):
        """RED: Test JSX with array mapping pattern."""
        from oxc_python import parse, walk

        source = """
        const list = (
            <ul>
                {items.map(item => <li key={item.id}>{item.name}</li>)}
            </ul>
        );
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # ul and li
        assert len(jsx_elements) == 2


class TestTSXComponent:
    """Tests for TypeScript + JSX (TSX) components."""

    def test_tsx_component(self):
        """RED: Test TypeScript + JSX (TSX) component."""
        from oxc_python import parse, walk

        source = """
        interface Props {
            name: string;
            age: number;
        }

        function Greeting({ name, age }: Props): JSX.Element {
            return <div>Hello {name}, age {age}</div>;
        }
        """
        result = parse(source, source_type="tsx")

        assert result.is_valid, "Should parse valid TSX"

        # Should find both TypeScript and JSX nodes
        node_types = set(node.type for node, _ in walk(result.program))

        assert any("TS" in t or "Type" in t for t in node_types), "Should find TypeScript nodes"
        assert "JSXElement" in node_types, "Should find JSX nodes"

    def test_jsx_with_typescript_generics(self):
        """RED: Test JSX with TypeScript generic syntax ambiguity."""
        from oxc_python import parse, walk

        # TypeScript has ambiguity: <T> could be JSX or generic
        # In .tsx files, use trailing comma: <T,> for generics
        source = """
        const generic = <T,>(value: T): T => value;
        const element = <div>Text</div>;
        """
        result = parse(source, source_type="tsx")

        assert result.is_valid, "Should handle TSX generic ambiguity"

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find only the div element, not the generic
        assert len(jsx_elements) == 1
        assert jsx_elements[0].opening_element.name.name == "div"


class TestJSXArrowComponent:
    """Tests for arrow function components returning JSX."""

    def test_jsx_arrow_component(self):
        """RED: Test arrow function returning JSX."""
        from oxc_python import parse, walk

        source = """
        const Component = () => <div>Hello</div>;
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1


class TestJSXGetText:
    """Tests for get_text() on JSX nodes."""

    def test_jsx_get_text(self):
        """RED: Test that JSX nodes work with get_text()."""
        from oxc_python import parse, walk

        source = '<div className="container">Hello</div>'
        result = parse(source, source_type="jsx")

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1
        element = jsx_elements[0]

        # Should be able to get source text
        text = element.get_text(source)
        assert "div" in text
        assert "className" in text
        assert "Hello" in text


class TestJSXGetLineRange:
    """Tests for get_line_range() on JSX nodes."""

    def test_jsx_get_line_range(self):
        """Test that JSX nodes have correct line ranges."""
        from oxc_python import parse, walk

        source = """const x = 1;
const el = <div>
  <span>Text</span>
</div>;
const y = 2;"""

        result = parse(source, source_type="jsx")

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Find the div element (outermost)
        div_element = next(
            (e for e in jsx_elements if hasattr(e, "children") and len(e.children) > 0), None
        )
        assert div_element is not None

        start_line, end_line = div_element.get_line_range(source)

        # div starts on line 2, ends on line 4
        assert start_line == 2
        assert end_line == 4


# ChunkHound Validation
class TestChunkHoundValidation:
    """ChunkHound validation tests for React component extraction."""

    def test_chunkhound_react_component_extraction(self):
        """
        ChunkHound Validation: Extract React components as chunks.

        ChunkHound needs to identify function components by detecting
        functions that return JSX elements.
        """
        from oxc_python import parse, walk

        source = """
        // Function component
        function Header({ title }) {
            return <h1>{title}</h1>;
        }

        // Arrow function component
        const Footer = () => <footer>Copyright 2024</footer>;

        // Class component
        class App extends React.Component {
            render() {
                return (
                    <div>
                        <Header title="My App" />
                        <main>Content</main>
                        <Footer />
                    </div>
                );
            }
        }

        // Non-component function (no JSX)
        function helper(x) {
            return x * 2;
        }
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        # Simulate ChunkHound component detection
        components = []

        for node, depth in walk(result.program):
            if node.type == "FunctionDeclaration":
                # Check if function contains JSX
                function_nodes = list(walk(node))
                has_jsx = any(n.type.startswith("JSX") for n, _ in function_nodes)

                if has_jsx:
                    components.append(
                        {
                            "name": getattr(node, "name", None),
                            "type": "FUNCTION_COMPONENT",
                            "depth": depth,
                        }
                    )

        # Should find Header (not helper)
        assert len(components) == 1
        component_names = [c["name"] for c in components]
        assert "Header" in component_names
        assert "helper" not in component_names, "Non-component functions should be excluded"

    def test_chunkhound_jsx_chunk_extraction(self):
        """
        ChunkHound Validation: Extract JSX elements as chunks.
        """
        from oxc_python import parse, walk

        source = """
        function Dashboard() {
            return (
                <div className="dashboard">
                    <Sidebar>
                        <NavItem icon="home" />
                        <NavItem icon="settings" />
                    </Sidebar>
                    <Content>
                        <Header />
                        <Body />
                    </Content>
                </div>
            );
        }
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        # Count JSX component usages
        jsx_elements = []

        for node, depth in walk(result.program):
            if node.type == "JSXElement":
                # Get component name from opening element
                opening = node.opening_element
                if opening and hasattr(opening, "name"):
                    name = opening.name
                    component_name = getattr(name, "name", None)

                    jsx_elements.append(
                        {
                            "name": component_name,
                            "depth": depth,
                        }
                    )

        # Should find: div, Sidebar, NavItem (x2), Content, Header, Body
        assert len(jsx_elements) == 7

        # Check for custom components (capitalized)
        custom_components = [e for e in jsx_elements if e["name"] and e["name"][0].isupper()]
        assert len(custom_components) == 6, (
            "Should find Sidebar, NavItem (x2), Content, Header, Body"
        )


# =============================================================================
# ADDITIONAL TESTS FOR MISSING/BROKEN JSX FUNCTIONALITY
# These tests target the specific issues identified:
# 1. Self-closing element handling - self_closing not set correctly
# 2. Nested JSX in expressions - JSX inside arrow functions or conditionals
# 3. JSX in iteration - Array.map callbacks with JSX
# =============================================================================


class TestSelfClosingElements:
    """Tests for self_closing property on JSXOpeningElement."""

    def test_br_self_closing_true(self):
        """RED: <br /> should have opening_element.self_closing = True."""
        from oxc_python import parse, walk

        source = "<br />"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1
        element = jsx_elements[0]

        # Critical: self_closing must be True for <br />
        assert element.opening_element.self_closing is True, (
            "self_closing should be True for <br />"
        )
        assert element.closing_element is None, (
            "closing_element should be None for self-closing elements"
        )

    def test_div_pair_self_closing_false(self):
        """RED: <div></div> should have opening_element.self_closing = False."""
        from oxc_python import parse, walk

        source = "<div></div>"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1
        element = jsx_elements[0]

        # Critical: self_closing must be False for <div></div>
        assert element.opening_element.self_closing is False, (
            "self_closing should be False for <div></div>"
        )
        assert element.closing_element is not None, (
            "closing_element should exist for non-self-closing elements"
        )

    def test_input_self_closing_with_attributes(self):
        """RED: <input type="text" /> self-closing with attributes."""
        from oxc_python import parse, walk

        source = '<input type="text" placeholder="Enter text" />'
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1
        element = jsx_elements[0]

        # self_closing should be True even with attributes
        assert element.opening_element.self_closing is True, (
            "self_closing should be True for <input ... />"
        )
        assert element.closing_element is None
        # Should have 2 attributes
        assert len(element.opening_element.attributes) == 2

    def test_component_self_closing_vs_paired(self):
        """RED: Compare self-closing <Component /> vs paired <Component></Component>."""
        from oxc_python import parse, walk

        source = """
        const a = <Component />;
        const b = <Component></Component>;
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 2

        # First should be self-closing
        assert jsx_elements[0].opening_element.self_closing is True, (
            "First Component should be self-closing"
        )
        assert jsx_elements[0].closing_element is None

        # Second should NOT be self-closing
        assert jsx_elements[1].opening_element.self_closing is False, (
            "Second Component should NOT be self-closing"
        )
        assert jsx_elements[1].closing_element is not None


class TestJSXInArrowFunctions:
    """Tests for JSX inside arrow function bodies."""

    def test_arrow_function_returns_jsx_element(self):
        """RED: const Component = () => <div>Hello</div> - JSXElement should appear in walk()."""
        from oxc_python import parse, walk

        source = "const Component = () => <div>Hello</div>;"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1, "Should find JSXElement inside arrow function body"

        # Verify we can get the element's text
        text = jsx_elements[0].get_text(source)
        assert "div" in text
        assert "Hello" in text

    def test_arrow_function_returns_jsx_fragment(self):
        """RED: const render = () => <><span /><span /></> - JSXFragment should appear."""
        from oxc_python import parse, walk

        source = "const render = () => <><span /><span /></>;"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        # Should find the fragment
        fragments = [node for node, _ in walk(result.program) if node.type == "JSXFragment"]

        assert len(fragments) == 1, "Should find JSXFragment inside arrow function body"

        # Should find the span elements inside the fragment
        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 2, "Should find both span elements inside the fragment"

    def test_arrow_function_with_block_body_jsx(self):
        """RED: Arrow function with block body containing JSX."""
        from oxc_python import parse, walk

        source = """
        const Component = () => {
            return <div className="wrapper"><span>Content</span></div>;
        };
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find both div and span
        assert len(jsx_elements) == 2, (
            "Should find all JSX elements inside arrow function block body"
        )

    def test_nested_arrow_function_jsx(self):
        """RED: Nested arrow functions both returning JSX."""
        from oxc_python import parse, walk

        source = """
        const outer = () => {
            const inner = () => <span>Inner</span>;
            return <div>{inner()}</div>;
        };
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find both span and div
        assert len(jsx_elements) == 2, "Should find JSX from both outer and inner arrow functions"


class TestJSXInConditionals:
    """Tests for JSX inside conditional expressions."""

    def test_ternary_with_jsx_both_branches(self):
        """RED: const x = condition ? <div>Yes</div> : <span>No</span>.

        Both JSXElements should appear.
        """
        from oxc_python import parse, walk

        source = "const x = condition ? <div>Yes</div> : <span>No</span>;"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find both div and span
        assert len(jsx_elements) == 2, "Should find JSX elements from both branches of ternary"

        # Check both elements are found
        element_names = [e.opening_element.name.name for e in jsx_elements]
        assert "div" in element_names, "Should find div element"
        assert "span" in element_names, "Should find span element"

    def test_logical_and_with_jsx(self):
        """RED: const x = foo && <div>Shown</div> - JSXElement should appear."""
        from oxc_python import parse, walk

        source = "const x = foo && <div>Shown</div>;"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1, "Should find JSXElement in logical AND expression"

        assert jsx_elements[0].opening_element.name.name == "div"

    def test_logical_or_with_jsx_fallback(self):
        """RED: const x = value || <DefaultComponent /> - JSX as fallback."""
        from oxc_python import parse, walk

        source = "const x = value || <DefaultComponent />;"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1, "Should find JSXElement in logical OR expression"

    def test_nested_conditionals_with_jsx(self):
        """RED: Nested ternary expressions with JSX."""
        from oxc_python import parse, walk

        source = """
        const x = a
            ? <div>A</div>
            : b
                ? <span>B</span>
                : <p>C</p>;
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find all three: div, span, p
        assert len(jsx_elements) == 3, "Should find all JSX elements in nested ternary"

    def test_conditional_jsx_with_expressions_inside(self):
        """RED: Conditional JSX containing expression containers."""
        from oxc_python import parse, walk

        source = """
        const x = show ? <div>{name}</div> : null;
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1

        # Also check for expression container
        expr_containers = [
            node for node, _ in walk(result.program) if node.type == "JSXExpressionContainer"
        ]

        assert len(expr_containers) == 1, "Should find expression container inside conditional JSX"


class TestJSXInArrayMethods:
    """Tests for JSX inside array method callbacks."""

    def test_map_callback_with_jsx(self):
        """RED: items.map(x => <li>{x}</li>) - JSXElement inside map callback should appear."""
        from oxc_python import parse, walk

        source = "items.map(x => <li>{x}</li>);"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1, "Should find JSXElement inside map callback"

        assert jsx_elements[0].opening_element.name.name == "li"

    def test_map_with_key_attribute(self):
        """RED: items.map(item => <Item key={item.id} />) - self-closing with key prop."""
        from oxc_python import parse, walk

        source = "items.map(item => <Item key={item.id} />);"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1
        element = jsx_elements[0]

        # Should be self-closing
        assert element.opening_element.self_closing is True

        # Should have key attribute
        attrs = element.opening_element.attributes
        assert len(attrs) == 1
        assert attrs[0].name.name == "key"

    def test_chained_filter_map_with_jsx(self):
        """RED: items.filter(x => x).map(x => <Item key={x} />) - chained methods."""
        from oxc_python import parse, walk

        source = "items.filter(x => x).map(x => <Item key={x} />);"
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1, "Should find JSXElement in chained method callbacks"

    def test_map_with_nested_jsx(self):
        """RED: map callback returning nested JSX."""
        from oxc_python import parse, walk

        source = """
        items.map(item => (
            <li key={item.id}>
                <span>{item.name}</span>
                <button onClick={item.action}>Click</button>
            </li>
        ));
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find: li, span, button
        assert len(jsx_elements) == 3, "Should find all nested JSX elements in map callback"

    def test_map_inside_jsx_expression_container(self):
        """RED: JSX containing map that returns JSX."""
        from oxc_python import parse, walk

        source = """
        const list = (
            <ul>
                {items.map(item => <li key={item}>{item}</li>)}
            </ul>
        );
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find: ul and li
        assert len(jsx_elements) == 2, "Should find ul and li elements"

        element_names = [e.opening_element.name.name for e in jsx_elements]
        assert "ul" in element_names
        assert "li" in element_names


class TestDeeplyNestedJSX:
    """Tests for deeply nested JSX structures."""

    def test_jsx_inside_function_inside_object_inside_array(self):
        """RED: JSX inside function inside object inside array."""
        from oxc_python import parse, walk

        source = """
        const config = [
            {
                render: () => <div>Item 1</div>
            },
            {
                render: () => <span>Item 2</span>
            }
        ];
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find both div and span
        assert len(jsx_elements) == 2, (
            "Should find JSX elements deeply nested in array > object > function"
        )

    def test_multiple_levels_of_jsx_nesting(self):
        """RED: Multiple levels of JSX nesting."""
        from oxc_python import parse, walk

        source = """
        const app = (
            <div>
                <header>
                    <nav>
                        <ul>
                            <li>
                                <a href="#">
                                    <span>Link Text</span>
                                </a>
                            </li>
                        </ul>
                    </nav>
                </header>
            </div>
        );
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find: div, header, nav, ul, li, a, span = 7 elements
        assert len(jsx_elements) == 7, (
            f"Should find 7 nested JSX elements, found {len(jsx_elements)}"
        )

    def test_jsx_in_callback_in_method_in_class(self):
        """RED: JSX in callback inside method inside class."""
        from oxc_python import parse, walk

        source = """
        class MyComponent {
            render() {
                return (
                    <div>
                        {this.items.map(item => <span key={item}>{item}</span>)}
                    </div>
                );
            }
        }
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find: div, span
        assert len(jsx_elements) == 2, "Should find JSX in deeply nested class method callback"

    def test_jsx_with_multiple_expression_containers(self):
        """RED: JSX with multiple nested expression containers."""
        from oxc_python import parse, walk

        source = """
        const el = (
            <div>
                {items.map(item => (
                    <li key={item.id}>
                        {item.active && <span className="active">{item.name}</span>}
                    </li>
                ))}
            </div>
        );
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Should find: div, li, span
        assert len(jsx_elements) == 3, (
            "Should find all JSX elements through nested expression containers"
        )


class TestReactComponentDetection:
    """Tests for detecting React components via walk()."""

    def test_function_declaration_returning_jsx(self):
        """RED: Function that returns JSX should have the JSX accessible via walk()."""
        from oxc_python import parse, walk

        source = """
        function MyComponent(props) {
            return <div className="component">{props.children}</div>;
        }
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        # Find function declaration
        functions = [node for node, _ in walk(result.program) if node.type == "FunctionDeclaration"]

        assert len(functions) == 1

        # Walk the function to find JSX
        function_node = functions[0]
        jsx_in_function = [node for node, _ in walk(function_node) if node.type == "JSXElement"]

        assert len(jsx_in_function) == 1, "Should find JSX when walking the function node"

    def test_arrow_function_component_jsx_accessible(self):
        """RED: Arrow function components should expose their JSX children."""
        from oxc_python import parse, walk

        source = """
        const MyComponent = ({ name }) => (
            <div>
                <h1>Hello, {name}!</h1>
                <p>Welcome to our site.</p>
            </div>
        );
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        # Find arrow function expression
        arrow_functions = [
            node for node, _ in walk(result.program) if node.type == "ArrowFunctionExpression"
        ]

        assert len(arrow_functions) == 1

        # Walk the arrow function to find all JSX
        arrow_fn = arrow_functions[0]
        jsx_in_arrow = [node for node, _ in walk(arrow_fn) if node.type == "JSXElement"]

        # Should find: div, h1, p
        assert len(jsx_in_arrow) == 3, "Should find all JSX elements when walking arrow function"

    def test_detect_component_vs_non_component(self):
        """RED: Distinguish between component functions (with JSX) and regular functions."""
        from oxc_python import parse, walk

        source = """
        // Component - returns JSX
        function Header() {
            return <header><h1>Title</h1></header>;
        }

        // Not a component - no JSX
        function calculate(x, y) {
            return x + y;
        }

        // Component - arrow function with JSX
        const Footer = () => <footer>Copyright</footer>;

        // Not a component - arrow function without JSX
        const double = x => x * 2;
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        # Find all function-like nodes
        all_functions = [
            node
            for node, _ in walk(result.program)
            if node.type in ("FunctionDeclaration", "ArrowFunctionExpression")
        ]

        # Count components (functions containing JSX)
        components = []
        for fn in all_functions:
            has_jsx = any(n.type.startswith("JSX") for n, _ in walk(fn))
            if has_jsx:
                components.append(fn)

        # Should find Header and Footer as components
        assert len(components) == 2, "Should identify exactly 2 React components"


class TestJSXUtilityMethods:
    """Tests for get_text() and get_line_range() on nested JSX."""

    def test_get_text_on_nested_jsx(self):
        """RED: get_text() should work on nested JSX elements."""
        from oxc_python import parse, walk

        source = """const x = items.map(i => <li key={i}>{i}</li>);"""
        result = parse(source, source_type="jsx")

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        assert len(jsx_elements) == 1

        text = jsx_elements[0].get_text(source)
        assert "<li" in text
        assert "</li>" in text
        assert "key=" in text

    def test_get_line_range_on_multiline_jsx_in_callback(self):
        """RED: get_line_range() on multiline JSX in callback."""
        from oxc_python import parse, walk

        source = """const x = items.map(item => (
    <div>
        <span>{item}</span>
    </div>
));"""
        result = parse(source, source_type="jsx")

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Find the outer div
        div_element = next((e for e in jsx_elements if e.opening_element.name.name == "div"), None)
        assert div_element is not None

        start_line, end_line = div_element.get_line_range(source)

        # div spans lines 2-4
        assert start_line == 2
        assert end_line == 4

    def test_count_jsx_nodes_in_complex_component(self):
        """RED: Count all JSX nodes to verify none are missing."""
        from oxc_python import parse, walk

        source = """
        function ComplexComponent({ items, showHeader }) {
            return (
                <div className="container">
                    {showHeader && <header>Header</header>}
                    <ul>
                        {items.map(item => (
                            <li key={item.id}>
                                {item.active
                                    ? <span className="active">{item.name}</span>
                                    : <span className="inactive">{item.name}</span>
                                }
                            </li>
                        ))}
                    </ul>
                    <footer>Footer</footer>
                </div>
            );
        }
        """
        result = parse(source, source_type="jsx")

        assert result.is_valid

        jsx_elements = [node for node, _ in walk(result.program) if node.type == "JSXElement"]

        # Expected elements:
        # 1. div (container)
        # 2. header (conditional)
        # 3. ul
        # 4. li (in map)
        # 5. span (active, in ternary)
        # 6. span (inactive, in ternary)
        # 7. footer
        expected_count = 7

        assert len(jsx_elements) == expected_count, (
            f"Should find exactly {expected_count} JSX elements, found {len(jsx_elements)}"
        )

        # Verify element names
        element_names = [e.opening_element.name.name for e in jsx_elements]
        assert "div" in element_names
        assert "header" in element_names
        assert "ul" in element_names
        assert "li" in element_names
        assert element_names.count("span") == 2, "Should find 2 span elements"
        assert "footer" in element_names

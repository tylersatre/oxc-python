"""
AST Traversal Tests

Tests for the walk() iterator function with depth tracking.

Combines tests from:
- test_phase_10_walk.py
"""


def test_walk_function_exists():
    """RED: Test that walk() function exists."""
    import oxc_python

    # walk() should be a module-level function
    assert hasattr(oxc_python, "walk")
    assert callable(oxc_python.walk)


def test_walk_returns_iterator():
    """RED: Test that walk() returns an iterable."""
    import oxc_python

    result = oxc_python.parse("const x = 1;")
    walker = oxc_python.walk(result.program)

    # Should be iterable
    assert hasattr(walker, "__iter__")


def test_walk_yields_tuples():
    """RED: Test that walk() yields (node, depth) tuples."""
    import oxc_python

    result = oxc_python.parse("const x = 1;")

    for item in oxc_python.walk(result.program):
        # Each item must be a tuple
        assert isinstance(item, tuple), f"Expected tuple, got {type(item)}"

        # Tuple must have exactly 2 elements
        assert len(item) == 2, f"Expected 2 elements, got {len(item)}"

        node, depth = item

        # Node should have .type property
        assert hasattr(node, "type"), "Node missing .type property"

        # Depth should be an integer
        assert isinstance(depth, int), f"Expected int depth, got {type(depth)}"

        # Depth should be non-negative
        assert depth >= 0, f"Depth should be >= 0, got {depth}"


def test_walk_depth_starts_at_zero():
    """RED: Test that root Program node has depth 0."""
    import oxc_python

    result = oxc_python.parse("const x = 1;")
    items = list(oxc_python.walk(result.program))

    # First node should be Program at depth 0
    assert len(items) > 0, "walk() should yield at least one node"

    first_node, first_depth = items[0]
    assert first_node.type == "Program", f"Expected Program first, got {first_node.type}"
    assert first_depth == 0, f"Program should be at depth 0, got {first_depth}"


def test_walk_depth_increases_for_children():
    """RED: Test that child nodes have depth > parent depth."""
    import oxc_python

    source = "const x = 1;"
    result = oxc_python.parse(source)
    items = list(oxc_python.walk(result.program))

    # Should have Program at depth 0 and statements at depth 1
    assert len(items) >= 2, "Should have at least Program + 1 statement"

    # First item is Program at depth 0
    assert items[0][1] == 0

    # Body statements should be at depth 1
    for node, depth in items[1:]:
        if node.type == "VariableDeclaration":
            assert depth == 1, f"Top-level statement should be at depth 1, got {depth}"


def test_walk_traverses_all_nodes():
    """RED: Test that walk() traverses all top-level nodes."""
    import oxc_python

    source = """
    const x = 1;
    function foo() {}
    class Bar {}
    """
    result = oxc_python.parse(source)
    items = list(oxc_python.walk(result.program))

    # Should have at least Program + 3 statements
    assert len(items) >= 4, f"Should have at least 4 nodes, got {len(items)}"

    # Check we have expected types
    types = [node.type for node, depth in items]
    assert "Program" in types
    assert "VariableDeclaration" in types
    assert "FunctionDeclaration" in types
    assert "ClassDeclaration" in types


def test_walk_empty_program():
    """RED: Test walk() with empty source."""
    import oxc_python

    result = oxc_python.parse("")
    items = list(oxc_python.walk(result.program))

    # Should yield at least the Program node
    assert len(items) >= 1
    assert items[0][0].type == "Program"
    assert items[0][1] == 0


def test_walk_order_deterministic():
    """RED: Test that walk() order is deterministic."""
    import oxc_python

    source = """
    function a() {}
    function b() {}
    function c() {}
    """
    result = oxc_python.parse(source)

    # Walk twice
    items1 = list(oxc_python.walk(result.program))
    items2 = list(oxc_python.walk(result.program))

    # Should yield same order
    assert len(items1) == len(items2)

    for i, ((node1, depth1), (node2, depth2)) in enumerate(zip(items1, items2, strict=False)):
        assert node1.type == node2.type, (
            f"Position {i}: types differ ({node1.type} vs {node2.type})"
        )
        assert depth1 == depth2, f"Position {i}: depths differ ({depth1} vs {depth2})"


# ChunkHound Validation
def test_chunkhound_walk_pattern():
    """
    ChunkHound Validation: Test ChunkHound's exact walk() usage pattern.

    ChunkHound does:
        for node, depth in self._oxc.walk(result.program):
            chunk_type = self._map_chunk_type(node.type)
            if chunk_type is None:
                continue
            symbol = self._extract_symbol(node, depth)
    """
    import oxc_python

    source = """
    function topLevel() {}
    class MyClass {}
    const x = 1;
    """
    result = oxc_python.parse(source)

    # Simulate ChunkHound's _map_chunk_type()
    def map_chunk_type(node_type):
        mapping = {
            "FunctionDeclaration": "FUNCTION",
            "ClassDeclaration": "CLASS",
            "VariableDeclaration": "DEFINITION",
        }
        return mapping.get(node_type)

    # Simulate ChunkHound's _extract_symbol()
    def extract_symbol(node, depth):
        if hasattr(node, "name") and node.name:
            return node.name
        return f"{node.type}_{depth}"

    # Simulate ChunkHound's walk loop
    chunks = []
    for node, depth in oxc_python.walk(result.program):
        chunk_type = map_chunk_type(node.type)
        if chunk_type is None:
            continue

        symbol = extract_symbol(node, depth)
        chunks.append(
            {
                "type": chunk_type,
                "symbol": symbol,
                "depth": depth,
            }
        )

    # Verify we found expected chunks
    assert len(chunks) > 0, "Should find some chunks"

    # All chunks should be at depth 1 (top-level statements)
    for chunk in chunks:
        assert chunk["depth"] == 1, f"Top-level chunk should be at depth 1, got {chunk['depth']}"


def test_chunkhound_hierarchical_filtering():
    """
    ChunkHound Validation: Test using depth for filtering.

    Common pattern: "Show only top-level declarations" (depth = 1)
    """
    import oxc_python

    source = """
    function topLevel1() {}
    function topLevel2() {}
    const x = 1;
    """
    result = oxc_python.parse(source)

    # Get top-level declarations (depth = 1, since Program is depth 0)
    top_level = []
    for node, depth in oxc_python.walk(result.program):
        if depth == 1 and node.type in ("FunctionDeclaration", "VariableDeclaration"):
            top_level.append(node)

    # Should find 3 top-level declarations
    assert len(top_level) >= 2, "Should find top-level declarations"

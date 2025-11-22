"""Type stubs for Node base class."""

from .span import Span

class Node:
    """
    Base AST node with type and location information.

    All AST nodes inherit from or use this base structure.
    The type property returns a string discriminator for runtime type checking.

    Attributes:
        type: Node type as string (e.g., "FunctionDeclaration")
        span: Source location (Span object with start and end byte offsets)
    """

    @property
    def type(self) -> str:
        """
        Get node type as string.

        This is a property, not a method, so accessed as node.type not node.type()
        Essential for ChunkHound's type checking pattern:
            if node.type == "FunctionDeclaration": ...
        """
        ...

    span: Span
    """Source location (Span object with start and end byte offsets)"""

    def __init__(self, type_name: str, span: Span) -> None:
        """
        Create a new Node with type and location.

        Args:
            type_name: Node type as string (e.g., "FunctionDeclaration")
            span: Source location (Span object)
        """
        ...

    def __repr__(self) -> str: ...

"""Type stubs for Span class."""

from typing import TypeAlias

class Span:
    """
    Source code location with byte offsets.

    Represents a range in the source code from `start` to `end` (exclusive).
    Offsets are byte offsets into the UTF-8 source string.

    Attributes:
        start: Start byte offset (inclusive)
        end: End byte offset (exclusive)
    """

    start: int
    """Start byte offset (inclusive)"""

    end: int
    """End byte offset (exclusive)"""

    def __init__(self, start: int, end: int) -> None:
        """Create a new Span with the given byte offsets."""
        ...

    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...

# Type alias for convenience
SpanType: TypeAlias = Span

"""Type stubs for ParseResult class."""

from typing import Any

class ParseResult:
    """
    Result of parsing JavaScript/TypeScript source code.

    Contains the parsed AST (program), any errors encountered, comments,
    and a flag indicating if the parser panicked.

    Attributes:
        program: The root AST node (Program), or None if parsing failed
        errors: List of parse error messages (empty if parsing succeeded)
        comments: List of comments found in the source
        panicked: True if parser hit an unrecoverable error
    """

    program: Any
    """The root AST node (Program), or None if parsing failed"""

    errors: list[str]
    """Parse error messages (empty if parsing succeeded)"""

    comments: list[str]
    """Comments found in the source"""

    panicked: bool
    """True if parser hit an unrecoverable error"""

    @property
    def is_valid(self) -> bool:
        """
        Check if parsing succeeded without errors.

        Returns True only if there are no errors AND parser didn't panic.
        """
        ...

    def __init__(
        self, program: Any, errors: list[str], comments: list[str], panicked: bool
    ) -> None:
        """Create a new ParseResult."""
        ...

    def __repr__(self) -> str: ...

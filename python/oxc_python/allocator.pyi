"""Type stubs for Allocator class."""

class Allocator:
    """
    Reusable memory allocator for efficient parsing.

    Uses arena allocation (bumpalo) internally for O(1) allocation
    and O(1) reset operations.

    This allocator is critical for batch parsing performance. By reusing
    a single allocator across multiple parse operations, you can achieve
    10-100x speedup compared to creating a new allocator for each parse.

    Performance Characteristics:
        - Creation: O(1)
        - reset(): O(1) - constant time
        - Memory: Arena grows as needed, released on reset()

    Safety Notes:
        - Must not be used concurrently from multiple threads
        - AST nodes remain valid until reset() is called
        - In Python, AST nodes are owned by Python after parsing, so reset() is safe
        - GIL ensures single-threaded access

    Example:
        >>> allocator = Allocator()
        >>> for file in files:
        ...     result = parse(file, allocator=allocator)
        ...     process(result)
        ...     allocator.reset()  # Reuse memory for next file

    See Also:
        - Phase 8: parse() function that accepts optional allocator parameter
        - ChunkHound: Main use case for batch parsing
    """

    def __init__(self) -> None:
        """Create a new allocator with arena memory."""
        ...

    def reset(self) -> None:
        """
        Clear allocator for reuse between parse operations.

        MUST be called between parse() calls when reusing an allocator.
        Frees all memory allocated since creation or last reset.

        Complexity: O(1) - Arena reset is constant time.

        Raises:
            No exceptions raised. Poisoned mutex would indicate a bug.

        Example:
            >>> allocator = Allocator()
            >>>
            >>> # Parse first file
            >>> result1 = parse(file1, allocator=allocator)
            >>> process(result1)
            >>>
            >>> # MUST reset before reusing
            >>> allocator.reset()
            >>>
            >>> # Parse second file (reuses arena memory)
            >>> result2 = parse(file2, allocator=allocator)
            >>> process(result2)
        """
        ...

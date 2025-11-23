"""
Performance Benchmark Tests

Benchmarks to verify that parsing scales linearly (O(n)) with file size,
not quadratically (O(n²)) as it did before the line offset table optimization.
"""

import time
import pytest
import oxc_python


def generate_js_file(size_kb: int) -> str:
    """
    Generate a JavaScript file of approximately the specified size.

    Creates realistic JS code with variable declarations, functions, and expressions
    to ensure the AST has a reasonable number of nodes proportional to file size.

    Args:
        size_kb: Target size in kilobytes

    Returns:
        JavaScript source code string
    """
    # Each statement is roughly 30-40 bytes
    # To get size_kb kilobytes, we need approximately (size_kb * 1024) / 35 statements
    num_statements = (size_kb * 1024) // 35

    lines = []
    for i in range(num_statements):
        # Mix of different statement types for realistic AST
        if i % 5 == 0:
            lines.append(f"function func{i}() {{ return {i} * 2; }}")
        elif i % 5 == 1:
            lines.append(f"const obj{i} = {{ a: {i}, b: {i + 1} }};")
        elif i % 5 == 2:
            lines.append(f"let arr{i} = [{i}, {i + 1}, {i + 2}];")
        elif i % 5 == 3:
            lines.append(f"const sum{i} = {i} + {i + 1} + {i + 2};")
        else:
            lines.append(f"var x{i} = Math.sqrt({i});")

    return "\n".join(lines)


def measure_parse_time(source: str, iterations: int = 3, source_type: str = "module") -> float:
    """
    Measure the average parse time for a source file.

    Args:
        source: JavaScript source code
        iterations: Number of iterations to average over
        source_type: Source type for parsing (module, tsx, jsx, etc.)

    Returns:
        Average parse time in seconds
    """
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = oxc_python.parse(source, source_type=source_type)
        end = time.perf_counter()
        times.append(end - start)

        # Verify parse succeeded
        assert result.is_valid, f"Parse failed: {result.errors}"

    return sum(times) / len(times)


@pytest.mark.benchmark
def test_linear_scaling_1kb_to_10kb():
    """Verify parsing scales linearly from 1KB to 10KB files."""
    # Generate test files
    source_1kb = generate_js_file(1)
    source_10kb = generate_js_file(10)

    # Measure parse times
    time_1kb = measure_parse_time(source_1kb)
    time_10kb = measure_parse_time(source_10kb)

    # Calculate scaling factor
    size_ratio = 10  # 10KB / 1KB
    time_ratio = time_10kb / time_1kb if time_1kb > 0 else 0

    # For linear O(n) scaling:
    # - 10x size should be ~10x time (within reasonable overhead)
    # - Allow up to 20x for overhead, but definitely not 100x (which would be quadratic)

    # If it were quadratic O(n²):
    # - 10x size would be 100x time

    assert time_ratio < 20, (
        f"Scaling appears quadratic: 10x size took {time_ratio:.1f}x time "
        f"(1KB: {time_1kb*1000:.2f}ms, 10KB: {time_10kb*1000:.2f}ms). "
        f"Expected <20x for linear scaling, would be ~100x for quadratic."
    )


@pytest.mark.benchmark
def test_linear_scaling_10kb_to_100kb():
    """Verify parsing scales linearly from 10KB to 100KB files."""
    # Generate test files
    source_10kb = generate_js_file(10)
    source_100kb = generate_js_file(100)

    # Measure parse times
    time_10kb = measure_parse_time(source_10kb)
    time_100kb = measure_parse_time(source_100kb)

    # Calculate scaling factor
    size_ratio = 10  # 100KB / 10KB
    time_ratio = time_100kb / time_10kb if time_10kb > 0 else 0

    # Linear: ~10x, Quadratic: ~100x
    assert time_ratio < 20, (
        f"Scaling appears quadratic: 10x size took {time_ratio:.1f}x time "
        f"(10KB: {time_10kb*1000:.2f}ms, 100KB: {time_100kb*1000:.2f}ms). "
        f"Expected <20x for linear scaling."
    )


@pytest.mark.benchmark
@pytest.mark.slow
def test_linear_scaling_100kb_to_1mb():
    """Verify parsing scales linearly from 100KB to 1MB files."""
    # Generate test files
    source_100kb = generate_js_file(100)
    source_1mb = generate_js_file(1000)

    # Measure parse times (fewer iterations for large files)
    time_100kb = measure_parse_time(source_100kb, iterations=2)
    time_1mb = measure_parse_time(source_1mb, iterations=2)

    # Calculate scaling factor
    size_ratio = 10  # 1MB / 100KB
    time_ratio = time_1mb / time_100kb if time_100kb > 0 else 0

    # Linear: ~10x, Quadratic: ~100x
    assert time_ratio < 20, (
        f"Scaling appears quadratic: 10x size took {time_ratio:.1f}x time "
        f"(100KB: {time_100kb*1000:.2f}ms, 1MB: {time_1mb*1000:.2f}ms). "
        f"Expected <20x for linear scaling."
    )


@pytest.mark.benchmark
def test_overall_linear_progression():
    """Verify overall linear scaling across multiple file sizes."""
    sizes = [1, 5, 10, 50]  # KB
    times = []

    for size_kb in sizes:
        source = generate_js_file(size_kb)
        time_taken = measure_parse_time(source, iterations=2)
        times.append((size_kb, time_taken))

    # Check that each doubling of size results in roughly doubling of time
    # (within a factor of 3 to allow for overhead and variance)
    for i in range(len(sizes) - 1):
        size_1, time_1 = times[i]
        size_2, time_2 = times[i + 1]

        size_ratio = size_2 / size_1
        time_ratio = time_2 / time_1 if time_1 > 0 else 0

        # Time ratio should be close to size ratio for linear scaling
        # Allow up to 3x the size ratio (generous bounds for overhead)
        max_expected_ratio = size_ratio * 3

        assert time_ratio < max_expected_ratio, (
            f"Non-linear scaling detected: {size_1}KB to {size_2}KB "
            f"({size_ratio:.1f}x size) took {time_ratio:.1f}x time. "
            f"Expected <{max_expected_ratio:.1f}x for linear scaling."
        )


@pytest.mark.benchmark
def test_small_file_performance():
    """Verify small files (<10KB) parse quickly."""
    source = generate_js_file(5)  # 5KB file

    time_taken = measure_parse_time(source, iterations=5)

    # 5KB file should parse in <50ms (very generous - likely much faster)
    assert time_taken < 0.05, (
        f"Small file (5KB) parsing too slow: {time_taken*1000:.2f}ms. "
        f"Expected <50ms."
    )


@pytest.mark.benchmark
def test_typescript_file_scaling():
    """Verify TypeScript files also scale linearly."""
    # Generate TypeScript code with type annotations
    def generate_ts_file(size_kb: int) -> str:
        num_statements = (size_kb * 1024) // 50  # TS statements are a bit longer
        lines = []
        for i in range(num_statements):
            if i % 3 == 0:
                lines.append(f"function func{i}(x: number): number {{ return x * {i}; }}")
            elif i % 3 == 1:
                lines.append(f"interface Type{i} {{ id: number; name: string; }}")
            else:
                lines.append(f"const val{i}: number = {i} + {i + 1};")
        return "\n".join(lines)

    source_10kb = generate_ts_file(10)
    source_100kb = generate_ts_file(100)

    time_10kb = measure_parse_time(source_10kb, source_type="tsx")
    time_100kb = measure_parse_time(source_100kb, source_type="tsx")

    time_ratio = time_100kb / time_10kb if time_10kb > 0 else 0

    # Should be linear, not quadratic
    assert time_ratio < 20, (
        f"TypeScript scaling appears quadratic: 10x size took {time_ratio:.1f}x time."
    )

#!/usr/bin/env python3
"""
oxc-python Performance Benchmark Suite

Usage:
    python benchmarks/run_benchmarks.py           # Run all benchmarks
    python benchmarks/run_benchmarks.py --json    # Output JSON results
"""

import argparse
import json
import statistics
import time

import oxc_python


def benchmark_function(func, iterations: int = 100):
    """Run function multiple times and return statistics."""
    times = []

    # Warm-up
    warmup = max(5, iterations // 10)
    for _ in range(warmup):
        func()

    # Measure
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # ms

    return {
        "median": statistics.median(times),
        "mean": statistics.mean(times),
        "min": min(times),
        "max": max(times),
        "p95": statistics.quantiles(times, n=20)[18],
        "p99": statistics.quantiles(times, n=100)[98] if len(times) >= 100 else max(times),
    }


def run_parse_benchmarks():
    """Run parsing benchmarks."""
    print("Running parsing benchmarks...")

    small = "const x = 1;\n" * 50
    medium = "const x = 1;\n" * 1000
    large = "const x = 1;\n" * 10000

    results = {
        "small": benchmark_function(
            lambda: oxc_python.parse(small, source_type="module"), iterations=1000
        ),
        "medium": benchmark_function(
            lambda: oxc_python.parse(medium, source_type="module"), iterations=100
        ),
        "large": benchmark_function(
            lambda: oxc_python.parse(large, source_type="module"), iterations=20
        ),
    }

    targets = {"small": 0.5, "medium": 10.0, "large": 1000.0}

    for size in ["small", "medium", "large"]:
        status = "✓" if results[size]["median"] < targets[size] else "✗"
        print(f"  {size:6s}: {results[size]['median']:.3f}ms (target: <{targets[size]}ms) {status}")

    return results


def run_batch_benchmark():
    """Run batch parsing benchmark."""
    print("\nRunning batch benchmark (1000 files)...")

    files = [f"const x{i} = {i}; function f{i}() {{ return {i}; }}" for i in range(1000)]
    allocator = oxc_python.Allocator()

    start = time.perf_counter()
    for source in files:
        oxc_python.parse(source, source_type="module", allocator=allocator)
        allocator.reset()
    elapsed = time.perf_counter() - start

    throughput = len(files) / elapsed
    print(f"  Throughput: {throughput:.0f} files/sec (target: >100)")

    return {"throughput": throughput, "total_time_s": elapsed}


def run_walk_benchmark():
    """Run AST walk benchmark."""
    print("\nRunning walk benchmark...")

    source = (
        """
    class Foo {
        method1() { const x = 1; }
        method2() { const y = 2; }
    }
    """
        * 100
    )

    result = oxc_python.parse(source, source_type="module")

    def walk_ast():
        count = 0
        for _node, _depth in oxc_python.walk(result.program):
            count += 1
        return count

    stats = benchmark_function(walk_ast, iterations=100)
    status = "✓" if stats["median"] < 5.0 else "✗"
    print(f"  Walk median: {stats['median']:.3f}ms (target: <5ms) {status}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Run oxc-python benchmarks")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    print("=" * 50)
    print("oxc-python Performance Benchmarks")
    print("=" * 50)

    results = {
        "parsing": run_parse_benchmarks(),
        "batch": run_batch_benchmark(),
        "walk": run_walk_benchmark(),
    }

    print("\n" + "=" * 50)
    print("Benchmark complete!")

    if args.json:
        print("\nJSON Results:")
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

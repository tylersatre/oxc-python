"""
oxc-py: Python bindings for the oxc JavaScript/TypeScript parser

This package provides high-performance parsing for JavaScript, TypeScript,
JSX, and TSX source code using the oxc Rust parser.
"""

from .oxc_python import *  # noqa: F403  # Import from Rust extension

__all__ = ["__version__"]  # noqa: F405

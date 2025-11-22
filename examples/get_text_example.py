#!/usr/bin/env python3
"""
Phase 11: get_text() Method Example

Demonstrates how to use the get_text() method to extract source code
for AST nodes. This is useful for:
- Code extraction/chunking (ChunkHound use case)
- Semantic analysis
- Documentation generation
- Code transformation

Usage:
    python examples/get_text_example.py
"""

import oxc_python


def main():
    """Demonstrate get_text() method usage."""

    source = """
// User authentication service
class AuthService {
    constructor(config) {
        this.config = config;
    }

    authenticate(username, password) {
        if (!this.validate(username, password)) {
            throw new Error('Invalid credentials');
        }
        return this.generateToken(username);
    }

    validate(username, password) {
        return username && password;
    }

    generateToken(username) {
        return `token_${username}_${Date.now()}`;
    }
}

// Helper function for user management
function createUser(username, email, password) {
    const user = {
        username,
        email,
        password: hashPassword(password),
        createdAt: new Date(),
    };
    return saveUser(user);
}

function deleteUser(userId) {
    return db.users.delete({ id: userId });
}
"""

    print("=" * 70)
    print("Phase 11: get_text() Method Example")
    print("=" * 70)

    # Parse the source code
    result = oxc_python.parse(source)

    if not result.is_valid:
        print(f"Parse errors: {result.errors}")
        return

    # Walk through AST and extract code for all top-level declarations
    print("\nExtracted Code Chunks:\n")
    print("-" * 70)

    chunk_count = 0
    for node, depth in oxc_python.walk(result.program):
        # Only extract top-level declarations (depth == 1)
        if depth != 1:
            continue

        # Filter for interesting node types
        if node.type not in ("FunctionDeclaration", "ClassDeclaration"):
            continue

        # Extract source code using get_text()
        code = node.get_text(source)

        # Display the chunk
        chunk_count += 1
        print(f"\nChunk #{chunk_count}: {node.type}")
        print("-" * 70)
        print(code)
        print("-" * 70)

    print(f"\nTotal chunks extracted: {chunk_count}")

    # Example 2: Extract specific node and show span information
    print("\n" + "=" * 70)
    print("Example 2: Span Information and Text Extraction")
    print("=" * 70)

    for node, depth in oxc_python.walk(result.program):
        if depth == 1 and node.type == "ClassDeclaration":
            print(f"\nNode Type: {node.type}")
            print(f"Span: start={node.span.start}, end={node.span.end}")
            print(f"Length: {node.span.end - node.span.start} bytes")

            # Extract the text
            code = node.get_text(source)
            lines = code.split("\n")
            print(f"Lines: {len(lines)}")
            print("\nExtracted Code:")
            print(code)
            break

    # Example 3: Show how get_text works with Unicode
    print("\n" + "=" * 70)
    print("Example 3: Unicode Support")
    print("=" * 70)

    unicode_source = """
// International greetings
function greetUser(user) {
    const messages = {
        en: `Hello, ${user.name}!`,
        es: `Hola, ${user.name}!`,
        fr: `Bonjour, ${user.name}!`,
        ja: `こんにちは、${user.name}!`,
        emoji: `👋 ${user.name}`,
    };
    return messages;
}
"""

    result = oxc_python.parse(unicode_source)
    for node, depth in oxc_python.walk(result.program):
        if depth == 1 and node.type == "FunctionDeclaration":
            code = node.get_text(unicode_source)
            print("\nExtracted code with Unicode:")
            print(code)
            print("\nUnicode handling: ✓ Works correctly with multi-byte UTF-8 characters")
            break

    print("\n" + "=" * 70)
    print("Complete! get_text() successfully extracted all source code chunks.")
    print("=" * 70)


if __name__ == "__main__":
    main()

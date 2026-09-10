# 🍑 Plum Programming Language

A lightweight interpreted programming language built from scratch for learning compiler and language design.

## Introduction

Plum is a toy programming language created to understand how real programming languages work internally. Instead of relying on parser generators or compiler frameworks, Plum is being implemented from scratch, one feature at a time.

## Current Version

- v0.9 — Logical Operators ✅
- v0.8 — Conditional Statements ✅
- v0.7 — Functions & Returns ✅
- v0.5 — Variables & Types ✅
- v0.4 — Extended Operators & Booleans ✅
- v0.3 — Full Arithmetic Support ✅
- v0.2 — Parser & Interpreter ✅
- v0.1 — Lexer ✅

## Documentation

- [v0.1](docs/v0.1.md) — Lexer
- [v0.2](docs/v0.2.md) — Parser & Interpreter
- [v0.3](docs/v0.3.md) — Full Arithmetic Support
- [v0.4](docs/v0.4.md) — Extended Operators & Booleans
- [v0.5](docs/v0.5.md) — Variables & Types
- [v0.7](docs/v0.7.md) — Functions & Returns
- [v0.8](docs/v0.8.md) — Conditional Statements
- [v0.9](docs/v0.9.md) — Logical Operators
- Roadmap (coming soon)

## Features

### v0.9 — Logical Operators

- 🔗 Logical `and`
- 🔀 Logical `or`
- 🚫 Logical `not`
- 🧩 Combined logical conditions
- 📐 Logical operator precedence
- 🔄 Parenthesized logical expressions

### v0.8 — Conditional Statements

- ❓ `if` statements
- 🔀 `else if` statements
- 🔄 `else` statements
- 📦 Multiple statements inside conditional blocks
- 🌳 Nested conditional statements

### v0.7 — Functions & Returns

- 🌿 `branch` function declarations
- 📞 Function calls
- ↩️ `return` statements
- 🧩 Function parameters
- 📦 Function bodies

### v0.5 — Variables & Types

- 🌱 `plant` for mutable variables
- 🌳 `root` for immutable variables
- 🔢 `int` type
- 🔤 `str` type
- 🟢 `bool` type
- 🌊 `float` type
- 📌 Variable references
- ✏️ Variable assignment

### v0.4 — Extended Operators & Booleans

- ➗ Modulo `%`
- 🔢 Floor division `//`
- ⚡ Power `**`
- ⚖️ Comparison operators: `==`, `!=`, `>`, `<`, `>=`, `<=`
- 🟢 `good` boolean value
- 🔴 `bad` boolean value
- 📐 Extended operator precedence
- 🔄 Parentheses support
- 🛡️ Division-by-zero protection

### v0.3 — Full Arithmetic Support

- ➕ Complete arithmetic operators: `+`, `-`, `*`, `/`
- 📐 Operator precedence (PEMDAS)
- 🔄 Parentheses support
- 🔢 Decimal number support
- 🛡️ Division by zero protection

### v0.2 — Parser & Interpreter

- 🌳 Abstract Syntax Tree (AST)
- 📝 Recursive descent parser
- 🏃 Tree-walking interpreter
- ➕ Addition support
- 📦 `drop` statement for output

### v0.1 — Lexer

- 🔤 Tokenization
- 📝 String literals
- 🗝️ `drop` keyword
- ❌ Error handling

## Quick Start

### Installation

```bash
# Clone the repository

git clone

cd plum

# Activate virtual environment

source .plum/bin/activate

# Run a Plum program

python3 -m plum.main example/main.plum
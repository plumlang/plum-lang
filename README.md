# 🍑 Plum Programming Language

A lightweight interpreted programming language built from scratch for learning compiler and language design.

## Introduction

Plum is a toy programming language created to understand how real programming languages work internally. Instead of relying on parser generators or compiler frameworks, Plum is being implemented from scratch, one feature at a time.

## Current Version

- v0.3 — Full Arithmetic Support ✅
- v0.2 — Parser & Interpreter ✅
- v0.1 — Lexer ✅

## Documentation

- [v0.1](docs/v0.1.md) — Lexer
- [v0.2](docs/v0.2.md) — Parser & Interpreter (Basic)
- [v0.3](docs/v0.3.md) — Full Arithmetic Support
- Roadmap (coming soon)

## Features

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
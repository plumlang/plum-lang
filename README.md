# 🍑 Plum Programming Language

A lightweight interpreted programming language built from scratch in Python to explore compiler design, parsing, and language implementation.

Plum is a learning-focused language developed one feature at a time, without relying on parser generators or compiler frameworks.

## 🚀 Current Version

**v0.10 — Bitwise Operators & Compound Assignment**

Plum currently includes:

- Lexer and recursive-descent parser
- Abstract Syntax Tree (AST)
- Tree-walking interpreter
- Variables, types, constants, and assignment
- Arithmetic, comparison, logical, and bitwise operators
- Compound assignment operators
- Functions and return statements
- Conditional statements
- Loops and loop control flow

## 📚 Documentation

| Version | Features | Documentation |
|---|---|---|
| v0.1 | Lexer | [Read docs](docs/v0.1.md) |
| v0.2 | Parser & Interpreter | [Read docs](docs/v0.2.md) |
| v0.3 | Full Arithmetic Support | [Read docs](docs/v0.3.md) |
| v0.4 | Extended Operators & Booleans | [Read docs](docs/v0.4.md) |
| v0.5 | Variables & Types | [Read docs](docs/v0.5.md) |
| v0.7 | Functions & Returns | [Read docs](docs/v0.7.md) |
| v0.8 | Conditional Statements | [Read docs](docs/v0.8.md) |
| v0.9 | For Loops & Loop Control Flow | [Read docs](docs/v0.9.md) |
| v0.10 | Bitwise Operators & Compound Assignment | [Read docs](docs/v0.10.md) |

## ✨ Features

### v0.10 — Bitwise Operators & Compound Assignment

- 🔢 Bitwise AND: `&`
- 🔢 Bitwise OR: `|`
- ⚡ Bitwise XOR: `^`
- 🔄 Bitwise NOT: `~`
- ⚖️ Integer-valued operand validation for bitwise operations
- 📐 Bitwise operator precedence
- 🔀 Compatibility with logical operators
- ➕ Addition assignment: `+=`
- ➖ Subtraction assignment: `-=`
- ✖️ Multiplication assignment: `*=`
- ➗ Division assignment: `/=`
- 🔢 Modulo assignment: `%=`
- 🧩 Support for expressions on the right-hand side
- 🛡️ Improved compound assignment error messages

### v0.9 — For Loops & Loop Control Flow

- 🔄 `for` loops
- 🌱 Loop variable initialization
- ⚖️ Loop conditions
- ➕ `++` increment operator
- 📦 Multiple statements inside loop bodies
- 🔀 Loops with `if` / `else`
- 🌳 Nested `for` loops

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
- 🌊 `float` type
- 🔤 `str` type
- 🟢 `bool` type
- 📌 Variable references
- ✏️ Variable assignment

### v0.4 — Extended Operators & Booleans

- ➗ Modulo: `%`
- 🔢 Floor division: `//`
- ⚡ Power: `**`
- ⚖️ Comparison operators: `==`, `!=`, `>`, `<`, `>=`, `<=`
- 🟢 `good` boolean value
- 🔴 `bad` boolean value
- 📐 Extended operator precedence
- 🔄 Parentheses support
- 🛡️ Division-by-zero protection

### v0.3 — Full Arithmetic Support

- ➕ Arithmetic operators: `+`, `-`, `*`, `/`
- 📐 Operator precedence
- 🔄 Parentheses support
- 🔢 Decimal number support
- 🛡️ Division-by-zero protection

### v0.2 — Parser & Interpreter

- 🌳 Abstract Syntax Tree (AST)
- 📝 Recursive-descent parser
- 🏃 Tree-walking interpreter
- ➕ Addition support
- 📦 `drop` statement for output

### v0.1 — Lexer

- 🔤 Tokenization
- 📝 String literals
- 🗝️ `drop` keyword
- ❌ Error handling

## 🛠️ Tech Stack

- **Language:** Python
- **Architecture:** Lexer → Parser → AST → Interpreter
- **Parsing:** Recursive-descent parser
- **Execution:** Tree-walking interpreter

## ⚡ Quick Start

### Prerequisites

- Python 3
- Git

### Installation

Clone the repository and enter the project directory:

```bash
git clone <your-repository-url>
cd plum-lang
```

### Run a Plum program

Run the interpreter from the repository root:

```bash
python -m plum.main example/main.plum
```

You can run other example programs the same way:

```bash
python -m plum.main example/v0.10-bitwise.plum
python -m plum.main example/v0.10-compound-assignment.plum
python -m plum.main example/test_logic.plum
```

### Example: Bitwise Operators

```plum
drop(5 & 3)
drop(5 | 3)
drop(5 ^ 3)
drop(~5)
```

Output:

```text
1
7
6
-6
```

### Example: Compound Assignment

```plum
plant int a = 10

a += 5
drop(a)

a *= 2
drop(a)

a %= 6
drop(a)
```

Output:

```text
15
30
0
```

## 🧪 Testing

Plum includes example programs for checking language features and detecting regressions.

Run the logical operator tests:

```bash
python -m plum.main example/test_logic.plum
```

Run the bitwise operator examples:

```bash
python -m plum.main example/v0.10-bitwise.plum
```

Run the compound assignment examples:

```bash
python -m plum.main example/v0.10-compound-assignment.plum
```

Run the extended loop example:

```bash
python -m plum.main example/v0.9-extended.plum
```

## 🧠 How Plum Works

Plum processes source code through three main stages:

1. **Lexer:** Converts source characters into tokens.
2. **Parser:** Converts tokens into an Abstract Syntax Tree (AST).
3. **Interpreter:** Evaluates the AST and executes the program.

This architecture makes Plum a practical project for learning how programming languages process and execute code.

## 🗺️ Roadmap

Potential future improvements:

- Improved runtime error messages without Python tracebacks
- Expanded automated testing
- More language features and standard-library functionality

## 🎯 Project Goal

Plum is an ongoing exploration of programming language design, interpreter implementation, and the fundamentals behind real-world programming languages.

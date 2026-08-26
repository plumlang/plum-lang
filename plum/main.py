import sys

from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter


def run_file(filename: str):
    """Read and run a .plum file"""
    with open(filename, "r") as file:
        content = file.read()

    run(content)


def run(source: str):
    """Lex, parse, and interpret source code"""

    print("--- LEXER OUTPUT ---")

    lexer = Lexer(source=source)
    tokens = lexer.tokenize()

    for token in tokens:
        print(token)

    print("\n--- PARSER OUTPUT ---")

    parser = Parser(tokens)
    program = parser.parse()

    print(program)

    print("\n--- INTERPRETER OUTPUT ---")

    interpreter = Interpreter()
    interpreter.interpret(program)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m plum.main <filename.plum>")
        print("Or: python plum/main.py <filename.plum>")
        sys.exit(1)

    run_file(sys.argv[1])

import sys

from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .interpreter.errors import PlumRuntimeError, PlumNameError


def run_file(filename: str):
    """Read and run a .plum file"""
    try:
        with open(filename, "r") as file:
            content = file.read()

        run(content)

    except FileNotFoundError:
        print(f"Error: File not found: '{filename}'")
        sys.exit(1)

    except OSError as error:
        print(f"Error reading file: {error}")
        sys.exit(1)


def run(source: str):
    """Lex, parse, and interpret source code"""

    try:
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

    except (PlumRuntimeError, PlumNameError) as error:
        print(error)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m plum.main <filename.plum>")
        print("Or: python plum/main.py <filename.plum>")
        sys.exit(1)

    run_file(sys.argv[1])

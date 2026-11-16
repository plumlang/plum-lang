
from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter


def run_source(source: str) -> Interpreter:
    """Tokenize, parse, and execute a Plum source program."""
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    interpreter = Interpreter()
    interpreter.interpret(program)
    return interpreter


def test_recursive_function():
    interpreter = run_source("""
        branch int factorial(int n) {
            if (n <= 1) {
                return 1
            }

            return n * factorial(n - 1)
        }

        plant int result = factorial(5)
    """)

    assert interpreter.global_env["result"] == 120


def test_nested_recursion_preserves_local_state():
    interpreter = run_source("""
        branch int fibonacci(int n) {
            if (n <= 1) {
                return n
            }

            plant int left = fibonacci(n - 1)
            plant int right = fibonacci(n - 2)

            return left + right
        }

        plant int result = fibonacci(7)
    """)

    assert interpreter.global_env["result"] == 13


def test_multiple_parameters_bind_correctly():
    interpreter = run_source("""
        branch int calculate(int a, int b, int c) {
            return a * 100 + b * 10 + c
        }

        plant int result = calculate(3, 5, 7)
    """)

    assert interpreter.global_env["result"] == 357


def test_zero_argument_function():
    interpreter = run_source("""
        branch int getValue() {
            return 42
        }

        plant int result = getValue()
    """)

    assert interpreter.global_env["result"] == 42


def test_nested_function_calls():
    interpreter = run_source("""
        branch int doubleValue(int n) {
            return n * 2
        }

        branch int addFive(int n) {
            return n + 5
        }

        plant int result = addFive(doubleValue(10))
    """)

    assert interpreter.global_env["result"] == 25


def test_function_call_inside_arithmetic_expression():
    interpreter = run_source("""
        branch int square(int n) {
            return n * n
        }

        branch int add(int a, int b) {
            return a + b
        }

        plant int result = square(3) + add(4, 5) * 2
    """)

    assert interpreter.global_env["result"] == 27

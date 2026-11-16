
import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter
from plum.interpreter.errors import PlumNameError

def run_source(source: str) -> Interpreter:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    interpreter = Interpreter()
    interpreter.interpret(program)
    return interpreter


def test_function_rejects_too_few_arguments():
    with pytest.raises(RuntimeError, match="expects 2 arguments"):
        run_source("""
            branch int add(int a, int b) {
                return a + b
            }

            plant int result = add(10)
        """)


def test_function_rejects_too_many_arguments():
    with pytest.raises(RuntimeError, match="expects 2 arguments"):
        run_source("""
            branch int add(int a, int b) {
                return a + b
            }

            plant int result = add(10, 20, 30)
        """)


def test_function_rejects_wrong_argument_type():
    with pytest.raises(RuntimeError, match="Expected int"):
        run_source("""
            branch int doubleValue(int n) {
                return n * 2
            }

            plant int result = doubleValue(good)
        """)


def test_undefined_function_call_raises_error():
    with pytest.raises(PlumNameError, match="Undefined function"):
        run_source("""
            plant int result = unknownFunction()
        """)


def test_function_rejects_wrong_type_in_second_argument():
    with pytest.raises(RuntimeError, match="Expected int"):
        run_source("""
            branch int add(int a, int b) {
                return a + b
            }

            plant int result = add(10, good)
        """)

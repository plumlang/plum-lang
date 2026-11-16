
import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter
from plum.interpreter.errors import PlumRuntimeError


def run_source(source: str) -> Interpreter:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(program)
    return interpreter


def test_function_rejects_wrong_return_type():
    with pytest.raises(PlumRuntimeError, match="Expected int"):
        run_source("""
            branch int getValue() {
                return "hello"
            }

            drop(getValue())
        """)


def test_non_void_function_requires_return_value():
    with pytest.raises(PlumRuntimeError, match="must return a value"):
        run_source("""
            branch int getValue() {
                plant int value = 10
            }

            drop(getValue())
        """)


def test_void_function_cannot_return_value():
    with pytest.raises(PlumRuntimeError, match="cannot return a value"):
        run_source("""
            branch void getValue() {
                return 10
            }

            getValue()
        """)

def test_void_function_can_return_without_value():
    run_source("""
        branch void greet() {
            return
        }

        greet()
    """)


def test_void_function_can_finish_without_explicit_return():
    run_source("""
        branch void greet() {
            plant int value = 10
        }

        greet()
    """)

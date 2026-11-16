
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


def test_function_arguments_are_evaluated_left_to_right():
    interpreter = Interpreter()

    source = """
        plant int counter = 0

        branch int first() {
            counter = counter + 1
            return 10
        }

        branch int second() {
            counter = counter + 1
            return 20
        }

        branch int add(int a, int b) {
            return a + b
        }

        plant int result = add(first(), second())
    """

    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    interpreter.interpret(program)

    assert interpreter.global_env["counter"] == 2
    assert interpreter.global_env["result"] == 30


def test_failed_argument_prevents_function_body_execution():
    interpreter = Interpreter()

    source = """
        plant int counter = 0

        branch int mark() {
            counter = counter + 1
            return 10
        }

        branch int fail() {
            return 1 / 0
        }

        branch int target(int a, int b) {
            counter = counter + 100
            return a + b
        }

        plant int result = target(mark(), fail())
    """

    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    with pytest.raises(PlumRuntimeError, match="Division by zero"):
        interpreter.interpret(program)

    assert interpreter.global_env["counter"] == 1
    assert "result" not in interpreter.global_env
    assert interpreter.scope_stack == []
    assert interpreter.function_depth == 0
    assert interpreter.loop_depth == 0


def test_failed_argument_inside_function_restores_caller_scope():
    interpreter = Interpreter()

    source = """
        branch int fail() {
            return 1 / 0
        }

        branch int target(int value) {
            return value
        }

        branch int outer() {
            plant int local = 50
            return target(fail())
        }

        plant int result = outer()
    """

    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    with pytest.raises(PlumRuntimeError, match="Division by zero"):
        interpreter.interpret(program)

    assert interpreter.scope_stack == []
    assert interpreter.current_env == {}
    assert interpreter.function_depth == 0
    assert interpreter.loop_depth == 0
    assert "local" not in interpreter.global_env

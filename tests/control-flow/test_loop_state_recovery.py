
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


def test_failed_nested_loop_restores_all_loop_scopes():
    interpreter = Interpreter()

    source = """
        plant int outer = 0

        while (outer < 2) {
            plant int inner = 0

            while (inner < 2) {
                plant int broken = 1 / 0
            }
        }
    """

    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    with pytest.raises(PlumRuntimeError, match="Division by zero"):
        interpreter.interpret(program)

    assert interpreter.scope_stack == []
    assert interpreter.loop_depth == 0
    assert interpreter.current_env == {}
    assert interpreter.global_env["outer"] == 0


def test_failed_function_inside_loop_restores_loop_state():
    interpreter = Interpreter()

    source = """
        branch int fail() {
            return 1 / 0
        }

        plant int counter = 0

        while (counter < 3) {
            counter = counter + 1
            fail()
        }
    """

    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    with pytest.raises(PlumRuntimeError, match="Division by zero"):
        interpreter.interpret(program)

    assert interpreter.loop_depth == 0
    assert interpreter.function_depth == 0
    assert interpreter.scope_stack == []
    assert interpreter.global_env["counter"] == 1


def test_continue_in_nested_loop_preserves_outer_loop():
    interpreter = run_source("""
        plant int outer = 0
        plant int total = 0
        plant int inner = 0

        while (outer < 3) {
            outer = outer + 1
            inner = 0

            while (inner < 2) {
                inner = inner + 1
                continue
            }

            total = total + outer
        }
    """)

    assert interpreter.global_env["outer"] == 3
    assert interpreter.global_env["total"] == 6
    assert interpreter.loop_depth == 0
    assert interpreter.scope_stack == []
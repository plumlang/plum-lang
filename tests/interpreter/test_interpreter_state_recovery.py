
import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter
from plum.interpreter.errors import PlumRuntimeError


def parse_source(source: str):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def test_failed_function_call_restores_interpreter_state():
    interpreter = Interpreter()

    program = parse_source("""
        branch int fail() {
            plant int value = 10
            plant int broken = 1 / 0
            return value
        }

        branch int safe() {
            return 42
        }

        plant int result = fail()
    """)

    with pytest.raises(PlumRuntimeError, match="Division by zero"):
        interpreter.interpret(program)

    assert interpreter.scope_stack == []
    assert interpreter.function_depth == 0
    assert interpreter.loop_depth == 0
    assert interpreter.current_env == {}

    recovery_program = parse_source("""
        plant int result = safe()
    """)

    interpreter.interpret(recovery_program)

    assert interpreter.global_env["result"] == 42


def test_failed_nested_block_restores_all_scopes():
    interpreter = Interpreter()

    program = parse_source("""
        branch int calculate() {
            if (true) {
                plant int local = 10
                plant int broken = 1 / 0
            }

            return 100
        }

        plant int result = calculate()
    """)

    with pytest.raises(PlumRuntimeError, match="Division by zero"):
        interpreter.interpret(program)

    assert interpreter.scope_stack == []
    assert interpreter.current_env == {}
    assert interpreter.function_depth == 0
    assert interpreter.loop_depth == 0

    assert "local" not in interpreter.global_env
    assert "broken" not in interpreter.global_env


def test_failed_loop_restores_loop_state():
    interpreter = Interpreter()

    program = parse_source("""
        while (true) {
            plant int broken = 1 / 0
        }
    """)

    with pytest.raises(PlumRuntimeError, match="Division by zero"):
        interpreter.interpret(program)

    assert interpreter.scope_stack == []
    assert interpreter.loop_depth == 0
    assert interpreter.function_depth == 0
    assert interpreter.current_env == {}


def test_failed_loop_inside_function_restores_caller_state():
    interpreter = Interpreter()

    program = parse_source("""
        branch int fail() {
            while (true) {
                plant int broken = 1 / 0
            }

            return 10
        }

        plant int result = fail()
    """)

    with pytest.raises(PlumRuntimeError, match="Division by zero"):
        interpreter.interpret(program)

    assert interpreter.scope_stack == []
    assert interpreter.loop_depth == 0
    assert interpreter.function_depth == 0
    assert interpreter.current_env == {}

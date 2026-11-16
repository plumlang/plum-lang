
import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter
from plum.interpreter.errors import PlumNameError


def run_source(interpreter, source):
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    interpreter.interpret(program)


def test_separate_interpreters_have_isolated_state():
    first = Interpreter()
    second = Interpreter()

    run_source(first, """
        plant int value = 10

        branch int identify() {
            return value
        }
    """)

    run_source(second, """
        plant int value = 20

        branch int identify() {
            return value
        }
    """)

    assert first.global_env["value"] == 10
    assert second.global_env["value"] == 20

    assert first.functions["identify"] != second.functions.get("missing")
    assert first.global_env is not second.global_env


def test_interpreter_preserves_state_across_successful_runs():
    interpreter = Interpreter()

    run_source(interpreter, """
        plant int seed = 40

        branch int increment(int value) {
            return value + 1
        }
    """)

    run_source(interpreter, """
        plant int result = increment(seed)
    """)

    assert interpreter.global_env["seed"] == 40
    assert interpreter.global_env["result"] == 41
    assert "increment" in interpreter.functions
    assert interpreter.scope_stack == []
    assert interpreter.loop_depth == 0
    assert interpreter.function_depth == 0

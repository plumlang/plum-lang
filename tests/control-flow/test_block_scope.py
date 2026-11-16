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


def test_if_block_variable_does_not_leak():
    with pytest.raises(PlumNameError, match="Undefined variable"):
        run_source("""
            if (true) {
                plant int secret = 42
            }

            drop(secret)
        """)


def test_else_block_variable_does_not_leak():
    with pytest.raises(PlumNameError, match="Undefined variable"):
        run_source("""
            if (false) {
                plant int first = 10
            } else {
                plant int second = 20
            }

            drop(second)
        """)


def test_if_block_can_modify_outer_variable():
    interpreter = run_source("""
        plant int score = 10

        if (true) {
            score = 50
        }
    """)

    assert interpreter.global_env["score"] == 50


def test_separate_if_blocks_can_declare_same_variable():
    interpreter = run_source("""
        if (true) {
            plant int value = 10
        }

        if (true) {
            plant int value = 20
        }
    """)

    assert "value" not in interpreter.global_env
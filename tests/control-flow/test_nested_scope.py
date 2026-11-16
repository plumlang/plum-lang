
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


def test_nested_if_block_variable_does_not_leak():
    with pytest.raises(PlumNameError, match="Undefined variable"):
        run_source("""
            if (true) {
                if (true) {
                    plant int secret = 10
                }

                drop(secret)
            }
        """)


def test_inner_if_can_read_outer_block_variable(capsys):
    run_source("""
        if (true) {
            plant int value = 42

            if (true) {
                drop(value)
            }
        }
    """)

    assert capsys.readouterr().out.strip() == "42"


def test_inner_if_can_modify_outer_block_variable():
    interpreter = run_source("""
        if (true) {
            plant int value = 10

            if (true) {
                value = 50
            }

            drop(value)
        }
    """)

    assert "value" not in interpreter.global_env


def test_while_body_variable_does_not_leak():
    with pytest.raises(PlumNameError, match="Undefined variable"):
        run_source("""
            plant int i = 0

            while (i < 1) {
                plant int temporary = 99
                i++
            }

            drop(temporary)
        """)


def test_for_loop_variable_does_not_leak():
    with pytest.raises(PlumNameError, match="Undefined variable"):
        run_source("""
            for (plant int i = 0; i < 1; i++) {
                drop(i)
            }

            drop(i)
        """)


def test_nested_loop_can_read_outer_loop_variable(capsys):
    run_source("""
        for (plant int i = 0; i < 2; i++) {
            for (plant int j = 0; j < 1; j++) {
                drop(i)
            }
        }
    """)

    assert capsys.readouterr().out.strip().splitlines() == ["0", "1"]

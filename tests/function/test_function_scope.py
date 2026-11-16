
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


# ---------------------------------------------------------
# Function and global scope interaction
# ---------------------------------------------------------

def test_function_can_read_global_variable(capsys):
    interpreter = run_source("""
        plant int score = 100

        branch int getScore() {
            return score
        }

        drop(getScore())
    """)

    assert capsys.readouterr().out.strip() == "100"
    assert interpreter.global_env["score"] == 100


def test_function_can_modify_global_variable():
    interpreter = run_source("""
        plant int score = 100

        branch int updateScore() {
            score = score + 50
            return score
        }

        updateScore()
    """)

    assert interpreter.global_env["score"] == 150


# ---------------------------------------------------------
# Function isolation
# ---------------------------------------------------------

def test_callee_cannot_access_callers_local_variable():
    with pytest.raises(PlumNameError, match="Undefined variable"):
        run_source("""
            branch int readSecret() {
                return secret
            }

            branch int caller() {
                plant int secret = 123
                return readSecret()
            }

            drop(caller())
        """)


def test_nested_function_call_preserves_callers_local_variable(capsys):
    run_source("""
        branch int inner() {
            plant int value = 99
            return value
        }

        branch int outer() {
            plant int value = 10

            inner()

            return value
        }

        drop(outer())
    """)

    assert capsys.readouterr().out.strip() == "10"


def test_function_local_variable_does_not_leak_after_return():
    interpreter = run_source("""
        branch int createLocal() {
            plant int temporary = 50
            return temporary
        }

        createLocal()

        plant int temporary = 100
    """)

    assert interpreter.global_env["temporary"] == 100

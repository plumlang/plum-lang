
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


def test_nested_function_call_preserves_caller_local_variables():
    interpreter = run_source("""
        branch int inner(int value) {
            plant int temporary = value * 2
            return temporary
        }

        branch int outer() {
            plant int local = 10
            plant int result = inner(local)
            return local + result
        }

        plant int answer = outer()
    """)

    assert interpreter.global_env["answer"] == 30
    assert "local" not in interpreter.global_env
    assert "temporary" not in interpreter.global_env


def test_nested_function_failure_restores_all_function_scopes():
    interpreter = Interpreter()

    source = """
        branch int fail() {
            plant int inner_local = 1
            return 10 / 0
        }

        branch int middle() {
            plant int middle_local = 2
            return fail()
        }

        branch int outer() {
            plant int outer_local = 3
            return middle()
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

    assert "inner_local" not in interpreter.global_env
    assert "middle_local" not in interpreter.global_env
    assert "outer_local" not in interpreter.global_env


def test_recursive_failure_restores_every_recursion_scope():
    interpreter = Interpreter()

    source = """
        branch int recursive(int n) {
            plant int local = n

            if (n == 0) {
                return 1 / 0
            }

            return recursive(n - 1)
        }

        plant int result = recursive(4)
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
    assert "result" not in interpreter.global_env

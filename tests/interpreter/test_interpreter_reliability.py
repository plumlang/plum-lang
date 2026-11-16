
import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter


def run_source(source: str) -> Interpreter:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(program)
    return interpreter


# ---------------------------------------------------------
# Function execution
# ---------------------------------------------------------

def test_function_with_parameters_and_return(capsys):
    run_source("""
        branch int add(int a, int b) {
            return a + b
        }

        drop(add(10, 20))
    """)

    assert capsys.readouterr().out.strip() == "30"


def test_nested_function_calls(capsys):
    run_source("""
        branch int add(int a, int b) {
            return a + b
        }

        branch int double(int x) {
            return add(x, x)
        }

        drop(double(5))
    """)

    assert capsys.readouterr().out.strip() == "10"


def test_recursive_function(capsys):
    run_source("""
        branch int factorial(int n) {
            if (n <= 1) {
                return 1
            }

            return n * factorial(n - 1)
        }

        drop(factorial(5))
    """)

    assert capsys.readouterr().out.strip() == "120"


def test_function_local_variable_does_not_modify_global(capsys):
    interpreter = run_source("""
        plant int score = 100

        branch int change() {
            plant int score = 50
            return score
        }

        drop(change())
        drop(score)
    """)

    assert capsys.readouterr().out.strip().splitlines() == ["50", "100"]
    assert interpreter.global_env["score"] == 100


def test_function_argument_count_mismatch():
    with pytest.raises(RuntimeError, match="expects 2 arguments"):
        run_source("""
            branch int add(int a, int b) {
                return a + b
            }

            drop(add(10))
        """)


# ---------------------------------------------------------
# Return behaviour
# ---------------------------------------------------------

def test_early_return(capsys):
    run_source("""
        branch int check(int value) {
            if (value > 10) {
                return 1
            }

            return 0
        }

        drop(check(20))
        drop(check(5))
    """)

    assert capsys.readouterr().out.strip().splitlines() == ["1", "0"]


def test_return_inside_loop(capsys):
    run_source("""
        branch int find(int target) {
            plant int i = 0

            while (i < 10) {
                if (i == target) {
                    return i
                }

                i++
            }

            return -1
        }

        drop(find(4))
    """)

    assert capsys.readouterr().out.strip() == "4"


# ---------------------------------------------------------
# Loop behaviour
# ---------------------------------------------------------

def test_nested_loops_break_only_inner_loop(capsys):
    run_source("""
        plant int count = 0

        for (plant int i = 0; i < 3; i++) {
            for (plant int j = 0; j < 5; j++) {
                if (j == 2) {
                    break
                }

                count++
            }
        }

        drop(count)
    """)

    assert capsys.readouterr().out.strip() == "6"


def test_nested_loops_continue_only_inner_loop(capsys):
    run_source("""
        plant int count = 0

        for (plant int i = 0; i < 3; i++) {
            for (plant int j = 0; j < 3; j++) {
                if (j == 1) {
                    continue
                }

                count++
            }
        }

        drop(count)
    """)

    assert capsys.readouterr().out.strip() == "6"


def test_for_loop_without_condition(capsys):
    run_source("""
        plant int i = 0

        for (; ; i++) {
            if (i == 3) {
                break
            }
        }

        drop(i)
    """)

    assert capsys.readouterr().out.strip() == "3"

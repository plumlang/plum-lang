import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter


def run_source(source: str) -> Interpreter:
    """Tokenize, parse, and execute a Plum source program."""
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    interpreter = Interpreter()
    interpreter.interpret(program)
    return interpreter


def test_print_integer(capsys):
    run_source("drop(42)")
    assert capsys.readouterr().out.strip() == "42"


def test_print_boolean(capsys):
    run_source("drop(good)")
    assert capsys.readouterr().out.strip() == "true"


def test_arithmetic_precedence(capsys):
    run_source("drop(2 + 3 * 4)")
    assert capsys.readouterr().out.strip() == "14"


def test_variable_declaration_and_reference(capsys):
    run_source("""
        plant int score = 25
        drop(score)
    """)
    assert capsys.readouterr().out.strip() == "25"


def test_variable_assignment(capsys):
    run_source("""
        plant int score = 10
        score = 20
        drop(score)
    """)
    assert capsys.readouterr().out.strip() == "20"


def test_logical_or_short_circuits(capsys):
    # The right side must not execute because the left side is already true.
    run_source("drop(good || (10 / 0))")
    assert capsys.readouterr().out.strip() == "true"


def test_logical_and_short_circuits(capsys):
    # The right side must not execute because the left side is already false.
    run_source("drop(bad && (10 / 0))")
    assert capsys.readouterr().out.strip() == "false"


def test_logical_or_evaluates_right_side_when_needed(capsys):
    run_source("drop(bad || good)")
    assert capsys.readouterr().out.strip() == "true"


def test_logical_and_evaluates_right_side_when_needed(capsys):
    run_source("drop(good && bad)")
    assert capsys.readouterr().out.strip() == "false"


import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter


def evaluate(source: str):
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(program)
    return interpreter


def test_multiplication_before_addition(capsys):
    evaluate("""
        drop(2 + 3 * 4)
    """)
    assert capsys.readouterr().out.strip() == "14"


def test_parentheses_override_precedence(capsys):
    evaluate("""
        drop((2 + 3) * 4)
    """)
    assert capsys.readouterr().out.strip() == "20"


def test_division_before_addition(capsys):
    evaluate("""
        drop(10 + 20 / 5)
    """)
    assert capsys.readouterr().out.strip() == "14.0"


def test_comparison_after_arithmetic(capsys):
    evaluate("""
        drop(2 + 3 > 4)
    """)
    assert capsys.readouterr().out.strip() == "true"


def test_logical_and_after_comparison(capsys):
    evaluate("""
        drop(2 < 3 && 5 > 4)
    """)
    assert capsys.readouterr().out.strip() == "true"


def test_logical_or_with_and_precedence(capsys):
    evaluate("""
        drop(false || true && false)
    """)
    assert capsys.readouterr().out.strip() == "false"


def test_unary_minus_before_multiplication(capsys):
    evaluate("""
        drop(-2 * 3 + 10)
    """)
    assert capsys.readouterr().out.strip() == "4"


def test_bitwise_and_with_addition(capsys):
    evaluate("""
        drop(1 + 3 & 3)
    """)
    assert capsys.readouterr().out.strip() == "0"

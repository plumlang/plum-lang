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


# ---------------------------------------------------------------------
# Basic execution
# ---------------------------------------------------------------------

def test_print_integer(capsys):
    run_source("drop(42)")
    assert capsys.readouterr().out.strip() == "42"


def test_print_float(capsys):
    run_source("drop(42.5)")
    assert capsys.readouterr().out.strip() == "42.5"


def test_print_boolean(capsys):
    run_source("drop(good)")
    assert capsys.readouterr().out.strip() == "true"


def test_arithmetic_precedence(capsys):
    run_source("drop(2 + 3 * 4)")
    assert capsys.readouterr().out.strip() == "14"


def test_integer_arithmetic_preserves_integer_type():
    interpreter = run_source("""
        plant int result = 2 + 3 * 4
    """)
    assert type(interpreter.global_env["result"]) is int
    assert interpreter.global_env["result"] == 14


def test_decimal_arithmetic_preserves_float_type():
    interpreter = run_source("""
        plant float result = 2.5 + 1.5
    """)
    assert type(interpreter.global_env["result"]) is float
    assert interpreter.global_env["result"] == 4.0


# ---------------------------------------------------------------------
# Strict declaration and assignment typing
# ---------------------------------------------------------------------

def test_int_accepts_integer():
    interpreter = run_source("plant int age = 20")
    assert type(interpreter.global_env["age"]) is int
    assert interpreter.global_env["age"] == 20


def test_int_rejects_float():
    with pytest.raises(RuntimeError, match="Expected int"):
        run_source("plant int age = 20.5")


def test_int_rejects_boolean():
    with pytest.raises(RuntimeError, match="Expected int"):
        run_source("plant int age = good")


def test_float_accepts_integer_implicit_conversion():
    interpreter = run_source("plant float price = 12")

    assert type(interpreter.global_env["price"]) is float
    assert interpreter.global_env["price"] == 12.0

def test_float_accepts_integer_implicit_conversion():
    interpreter = run_source("plant float price = 12")

    assert type(interpreter.global_env["price"]) is float
    assert interpreter.global_env["price"] == 12.0

def test_float_rejects_boolean():
    with pytest.raises(RuntimeError, match="Expected float"):
        run_source("plant float price = good")


def test_bool_rejects_integer_one():
    with pytest.raises(RuntimeError, match="Expected bool"):
        run_source("plant bool enabled = 1")





def test_int_to_float_implicit_conversion():
    interpreter = run_source("""
        plant int age = 20
        plant float price = age
    """)

    assert type(interpreter.global_env["price"]) is float
    assert interpreter.global_env["price"] == 20.0


def test_float_to_int_is_rejected():
    with pytest.raises(RuntimeError, match="Expected int"):
        run_source("plant int age = 20.5")


def test_bool_to_int_is_rejected():
    with pytest.raises(RuntimeError, match="Expected int"):
        run_source("plant int age = good")


def test_int_to_bool_is_rejected():
    with pytest.raises(RuntimeError, match="Expected bool"):
        run_source("plant bool enabled = 1")


def test_bool_to_float_is_rejected():
    with pytest.raises(RuntimeError, match="Expected float"):
        run_source("plant float price = good")
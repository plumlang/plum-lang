
from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter.interpreter import Interpreter


def evaluate(source: str):
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(program)


def test_subtraction_is_left_associative(capsys):
    evaluate("""
        drop(20 - 5 - 3)
    """)
    assert capsys.readouterr().out.strip() == "12"


def test_division_is_left_associative(capsys):
    evaluate("""
        drop(100 / 10 / 2)
    """)
    assert capsys.readouterr().out.strip() == "5.0"


def test_multiplication_and_division_associativity(capsys):
    evaluate("""
        drop(20 / 5 * 2)
    """)
    assert capsys.readouterr().out.strip() == "8.0"


def test_addition_and_subtraction_associativity(capsys):
    evaluate("""
        drop(10 - 3 + 2)
    """)
    assert capsys.readouterr().out.strip() == "9"


def test_exponentiation_is_right_associative(capsys):
    evaluate("""
        drop(2 ** 3 ** 2)
    """)
    assert capsys.readouterr().out.strip() == "512"

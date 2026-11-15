
import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.interpreter import Interpreter


def run_plum(source):
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter()
    return interpreter.interpret(ast)


def test_break_outside_loop_raises_error():
    source = """
    break;
    """

    with pytest.raises(RuntimeError):
        run_plum(source)


def test_continue_outside_loop_raises_error():
    source = """
    continue;
    """

    with pytest.raises(RuntimeError):
        run_plum(source)


def test_return_outside_function_raises_error():
    source = """
    return 10;
    """

    with pytest.raises(RuntimeError):
        run_plum(source)


def test_break_inside_function_cannot_break_caller_loop():
    source = """
    branch drop stopLoop() {
        break;
    }

    plant int i = 0;

    while (i < 3) {
        stopLoop();
        i++;
    }
    """

    with pytest.raises(RuntimeError):
        run_plum(source)


def test_continue_inside_function_cannot_continue_caller_loop():
    source = """
    branch drop skipLoop() {
        continue;
    }

    plant int i = 0;

    while (i < 3) {
        skipLoop();
        i++;
    }
    """

    with pytest.raises(RuntimeError):
        run_plum(source)

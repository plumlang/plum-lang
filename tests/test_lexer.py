
import pytest

from plum.lexer import Lexer, TokenType


def tokenize(source):
    return Lexer(source).tokenize()


def test_empty_source_returns_eof():
    tokens = tokenize("")

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF


def test_arithmetic_operators():
    tokens = tokenize("+ - * / %")

    assert [token.type for token in tokens[:-1]] == [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
    ]


def test_number_token():
    tokens = tokenize("123")

    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == 123
    assert type(tokens[0].value) is int

def test_decimal_number_token():
    tokens = tokenize("3.14")

    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == 3.14
    assert type(tokens[0].value) is float

def test_identifier_token():
    tokens = tokenize("score")

    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "score"


def test_keyword_token():
    tokens = tokenize("plant")

    assert tokens[0].type == TokenType.PLANT
    assert tokens[0].value == "plant"


def test_string_token():
    tokens = tokenize('"hello"')

    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "hello"


def test_eof_is_appended():
    tokens = tokenize("123 + 456")

    assert tokens[-1].type == TokenType.EOF




def test_comparison_operators():
    tokens = tokenize("== != > < >= <=")

    assert [token.type for token in tokens[:-1]] == [
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.GREATER,
        TokenType.LESS,
        TokenType.GREATER_EQUAL,
        TokenType.LESS_EQUAL,
    ]


def test_logical_operators():
    tokens = tokenize("&& || !")

    assert [token.type for token in tokens[:-1]] == [
        TokenType.AND,
        TokenType.OR,
        TokenType.NOT,
    ]





def test_bitwise_operators():
    tokens = tokenize("& | ^ ~ << >>")

    assert [token.type for token in tokens[:-1]] == [
        TokenType.BITWISE_AND,
        TokenType.BITWISE_OR,
        TokenType.BITWISE_XOR,
        TokenType.BITWISE_NOT,
        TokenType.BITWISE_LEFT_SHIFT,
        TokenType.BITWISE_RIGHT_SHIFT,
    ]


def test_compound_assignment_operators():
    tokens = tokenize("+= -= *= /= %=")

    assert [token.type for token in tokens[:-1]] == [
        TokenType.PLUS_EQUALS,
        TokenType.MINUS_EQUALS,
        TokenType.STAR_EQUALS,
        TokenType.SLASH_EQUALS,
        TokenType.PERCENT_EQUALS,
    ]


def test_increment_and_decrement():
    tokens = tokenize("++ --")

    assert [token.type for token in tokens[:-1]] == [
        TokenType.INCREMENT,
        TokenType.DECREMENT,
    ]


def test_floor_division_and_power():
    tokens = tokenize("// **")

    assert [token.type for token in tokens[:-1]] == [
        TokenType.DOUBLE_SLASH,
        TokenType.POWER,
    ]




def test_comment_is_ignored():
    tokens = tokenize("123 # this is a comment\n456")

    assert [token.type for token in tokens] == [
        TokenType.NUMBER,
        TokenType.NUMBER,
        TokenType.EOF,
    ]


def test_line_number_increments():
    tokens = tokenize("123\n456")

    assert tokens[0].line == 1
    assert tokens[1].line == 2
    assert tokens[2].line == 2


def test_unterminated_string_raises_error():
    with pytest.raises(SyntaxError, match="Unterminated String"):
        tokenize('"hello')


def test_invalid_character_raises_error():
    with pytest.raises(SyntaxError, match="Unexpected character"):
        tokenize("123 @ 456")


def test_string_does_not_include_quotes():
    tokens = tokenize('"Plum Language"')

    assert tokens[0].value == "Plum Language"


def test_whitespace_is_ignored():
    tokens = tokenize("   123     +     456   ")

    assert [token.type for token in tokens] == [
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.EOF,
    ]




def test_identifier_starting_with_underscore():
    tokens = tokenize("_score")

    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "_score"


def test_identifier_containing_underscore_and_digits():
    tokens = tokenize("score_123")

    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "score_123"


def test_string_with_newline_updates_line_number():
    tokens = tokenize('"hello\nworld"\n123')

    assert tokens[0].type == TokenType.STRING
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].line == 3




def test_number_with_trailing_decimal_point():
    with pytest.raises(SyntaxError):
        tokenize("123.")


def test_number_with_multiple_decimal_points():
    with pytest.raises(SyntaxError):
        tokenize("12.34.56")


def test_multiple_numbers():
    tokens = tokenize("10 20.5 300")

    assert [token.value for token in tokens[:-1]] == [
        10,
        20.5,
        300,
    ]
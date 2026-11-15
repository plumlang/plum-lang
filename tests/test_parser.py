import pytest

from plum.lexer import Lexer
from plum.parser import Parser
from plum.plum_ast import (
    Program,
    PrintStatement,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    BinaryOperation,
    UnaryOperation,
    VariableDeclaration,
    Assignment,
    CompoundAssignment,
    IfStatement,
    WhileStatement,
    ForStatement,
    FunctionDeclaration,
    FunctionCall,
    ReturnStatement,
    BreakStatement,
    ContinueStatement
)


def parse_source(source):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()

# Test a simple print statement
def test_parse_print_number():
    program = parse_source("drop(10)")

    assert isinstance(program, Program)
    assert len(program.statements) == 1

    statement = program.statements[0]

    assert isinstance(statement, PrintStatement)
    assert isinstance(statement.expression, NumberLiteral)
    assert statement.expression.value == 10


# Test expression parsing
def test_parse_print_string():
    program = parse_source('drop("hello")')

    statement = program.statements[0]

    assert isinstance(statement, PrintStatement)
    assert isinstance(statement.expression, StringLiteral)
    assert statement.expression.value == "hello"


def test_parse_print_boolean():
    program = parse_source("drop(good)")

    statement = program.statements[0]

    assert isinstance(statement.expression, BooleanLiteral)
    assert statement.expression.value is True


def test_parse_addition():
    program = parse_source("drop(5 + 3)")

    expression = program.statements[0].expression

    assert isinstance(expression, BinaryOperation)
    assert expression.operator == "+"
    assert expression.left.value == 5
    assert expression.right.value == 3


# Test operator precedence
def test_multiplication_has_higher_precedence_than_addition():
    program = parse_source("drop(5 + 3 * 2)")

    expression = program.statements[0].expression

    assert expression.operator == "+"
    assert expression.left.value == 5

    assert isinstance(expression.right, BinaryOperation)
    assert expression.right.operator == "*"
    assert expression.right.left.value == 3
    assert expression.right.right.value == 2


def test_parentheses_override_precedence():
    program = parse_source("drop((5 + 3) * 2)")

    expression = program.statements[0].expression

    assert expression.operator == "*"
    assert isinstance(expression.left, BinaryOperation)
    assert expression.left.operator == "+"
    assert expression.right.value == 2

# Test left associativity
def test_subtraction_is_left_associative():
    program = parse_source("drop(10 - 5 - 2)")

    expression = program.statements[0].expression

    assert expression.operator == "-"
    assert isinstance(expression.left, BinaryOperation)
    assert expression.left.operator == "-"
    assert expression.left.left.value == 10
    assert expression.left.right.value == 5
    assert expression.right.value == 2

# Test exponentiation associativity

def test_power_is_right_associative():
    program = parse_source("drop(2 ** 3 ** 2)")

    expression = program.statements[0].expression

    assert expression.operator == "**"
    assert expression.left.value == 2

    assert isinstance(expression.right, BinaryOperation)
    assert expression.right.operator == "**"
    assert expression.right.left.value == 3
    assert expression.right.right.value == 2

# test unary operators
def test_parse_unary_minus():
    program = parse_source("drop(-5)")

    expression = program.statements[0].expression

    assert isinstance(expression, UnaryOperation)
    assert expression.operator == "-"
    assert expression.operand.value == 5


def test_parse_logical_not():
    program = parse_source("drop(!good)")

    expression = program.statements[0].expression

    assert isinstance(expression, UnaryOperation)
    assert expression.operator == "!"
    assert isinstance(expression.operand, BooleanLiteral)
    assert expression.operand.value is True


def test_parse_bitwise_not():
    program = parse_source("drop(~5)")

    expression = program.statements[0].expression

    assert isinstance(expression, UnaryOperation)
    assert expression.operator == "~"
    assert expression.operand.value == 5



# Variable declaration test 
def test_parse_mutable_variable():
    program = parse_source("plant int age = 20")

    declaration = program.statements[0]

    assert isinstance(declaration, VariableDeclaration)
    assert declaration.mutable is True
    assert declaration.var_type == "int"
    assert declaration.name == "age"
    assert declaration.value.value == 20


def test_parse_immutable_variable():
    program = parse_source('root str name = "Plum"')

    declaration = program.statements[0]

    assert isinstance(declaration, VariableDeclaration)
    assert declaration.mutable is False
    assert declaration.var_type == "str"
    assert declaration.name == "name"
    assert declaration.value.value == "Plum"


def test_parse_variable_without_initial_value():
    program = parse_source("plant int score")

    declaration = program.statements[0]

    assert isinstance(declaration, VariableDeclaration)
    assert declaration.name == "score"
    assert declaration.value is None


def test_parse_boolean_variable():
    program = parse_source("plant bool active = good")

    declaration = program.statements[0]

    assert declaration.var_type == "bool"
    assert declaration.value.value is True

# Test Variable assignment

def test_parse_variable_assignment():
    program = parse_source("age = 25")

    assignment = program.statements[0]

    assert isinstance(assignment, Assignment)
    assert assignment.name == "age"
    assert assignment.value.value == 25


def test_parse_addition_assignment():
    program = parse_source("age += 5")

    assignment = program.statements[0]

    assert isinstance(assignment, CompoundAssignment)
    assert assignment.name == "age"
    assert assignment.operator == "+="
    assert assignment.value.value == 5


def test_parse_subtraction_assignment():
    program = parse_source("age -= 2")

    assignment = program.statements[0]

    assert isinstance(assignment, CompoundAssignment)
    assert assignment.name == "age"
    assert assignment.operator == "-="
    assert assignment.value.value == 2

# Test all compound assignment operators
def test_parse_multiplication_assignment():
    program = parse_source("age *= 2")
    assignment = program.statements[0]

    assert isinstance(assignment, CompoundAssignment)
    assert assignment.operator == "*="


def test_parse_division_assignment():
    program = parse_source("age /= 2")
    assignment = program.statements[0]

    assert isinstance(assignment, CompoundAssignment)
    assert assignment.operator == "/="


def test_parse_modulo_assignment():
    program = parse_source("age %= 2")
    assignment = program.statements[0]

    assert isinstance(assignment, CompoundAssignment)
    assert assignment.operator == "%="


# Control flow tests
def test_parse_if_statement():
    program = parse_source("if (age > 18) { drop(age) }")

    statement = program.statements[0]

    assert isinstance(statement, IfStatement)
    assert statement.condition.operator == ">"
    assert len(statement.then_branch) == 1
    assert statement.else_branch is None


def test_parse_if_else_statement():
    program = parse_source(
        "if (age > 18) { drop(age) } else { drop(0) }"
    )

    statement = program.statements[0]

    assert isinstance(statement, IfStatement)
    assert len(statement.then_branch) == 1
    assert len(statement.else_branch) == 1


def test_parse_else_if_statement():
    program = parse_source(
        "if (age > 18) { drop(1) } else if (age > 10) { drop(2) }"
    )

    statement = program.statements[0]

    assert isinstance(statement, IfStatement)
    assert isinstance(statement.else_branch[0], IfStatement)


def test_parse_while_loop():
    program = parse_source(
        "while (age < 10) { age += 1 }"
    )

    statement = program.statements[0]

    assert isinstance(statement, WhileStatement)
    assert statement.condition.operator == "<"
    assert len(statement.body) == 1


def test_parse_for_loop():
    program = parse_source(
        "for (plant int i = 0; i < 10; i++) { drop(i) }"
    )

    statement = program.statements[0]

    assert isinstance(statement, ForStatement)
    assert isinstance(statement.initializer, VariableDeclaration)
    assert statement.condition.operator == "<"
    assert len(statement.body) == 1

# Functions and return statements
def test_parse_function_declaration():
    program = parse_source(
        "branch int add(int a, int b) { return a + b }"
    )

    function = program.statements[0]

    assert isinstance(function, FunctionDeclaration)
    assert function.return_type == "int"
    assert function.name == "add"
    assert function.params == [("int", "a"), ("int", "b")]
    assert len(function.body) == 1
    assert isinstance(function.body[0], ReturnStatement)


def test_parse_function_without_parameters():
    program = parse_source(
        "branch int getAge() { return 20 }"
    )

    function = program.statements[0]

    assert isinstance(function, FunctionDeclaration)
    assert function.name == "getAge"
    assert function.params == []


def test_parse_function_call():
    program = parse_source("drop(add(5, 10))")

    expression = program.statements[0].expression

    assert isinstance(expression, FunctionCall)
    assert expression.name == "add"
    assert len(expression.arguments) == 2


def test_parse_empty_return():
    program = parse_source(
        "branch drop greet() { return }"
    )

    function = program.statements[0]

    assert isinstance(function.body[0], ReturnStatement)
    assert function.body[0].value is None

# Break, continue and syntax error tests
def test_parse_break():
    program = parse_source("while (good) { break }")

    statement = program.statements[0].body[0]

    assert isinstance(statement, BreakStatement)


def test_parse_continue():
    program = parse_source("while (good) { continue }")

    statement = program.statements[0].body[0]

    assert isinstance(statement, ContinueStatement)


def test_invalid_expression_raises_syntax_error():
    with pytest.raises(SyntaxError):
        parse_source("drop(5 + )")


def test_missing_closing_parenthesis_raises_syntax_error():
    with pytest.raises(SyntaxError):
        parse_source("drop(10")


# Custom error testing

def parse_source(source):
    tokens = Lexer(source).tokenize()
    parser = Parser(tokens)
    return parser.parse()


def test_missing_parenthesis_reports_line_and_column():
    source = "drop(10"

    with pytest.raises(
        SyntaxError,
        match=r"line 1, column 8"
    ):
        parse_source(source)


def test_unexpected_token_reports_line_and_column():
    source = "drop(10 + )"

    with pytest.raises(
        SyntaxError,
        match=r"line 1, column 11"
    ):
        parse_source(source)


def test_error_location_after_newline():
    source = "drop(10)\ndrop(20 + )"

    with pytest.raises(
        SyntaxError,
        match=r"line 2, column 11"
    ):
        parse_source(source)


def test_missing_variable_type_reports_location():
    source = "plant age = 20"

    with pytest.raises(
        SyntaxError,
        match=r"line 1, column 7"
    ):
        parse_source(source)


def test_missing_function_return_type_reports_location():
    source = "branch add() {}"

    with pytest.raises(
        SyntaxError,
        match=r"line 1, column 8"
    ):
        parse_source(source)
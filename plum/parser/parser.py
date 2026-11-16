
from typing import List, Optional
from plum.lexer import Token, TokenType
from plum.plum_ast import *


class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()

        raise self._syntax_error(message)

    def _syntax_error(
        self,
        message: str,
        token: Optional[Token] = None
    ) -> SyntaxError:
        token = token or self._peek()

        return SyntaxError(
            f"{message} at line {token.line}, column {token.column}"
        )

    # ---------------------------------------------------------------
    # PRIMARY
    # ---------------------------------------------------------------
    def _primary(self) -> ASTNode:
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(
                TokenType.RIGHT_PAREN,
                "Expected ')' after expression"
            )
            return expr

        if self._match(TokenType.NUMBER):
            return NumberLiteral(self._previous().value)

        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)

        if self._match(TokenType.GOOD):
            return BooleanLiteral(True)

        if self._match(TokenType.BAD):
            return BooleanLiteral(False)

        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value

            if self._check(TokenType.LEFT_PAREN):
                return self._finish_call(name)

            return VariableReference(name)

        token = self._peek()

        raise self._syntax_error(
            f"Unexpected token: {token.value!r}",
            token
        )

    def _finish_call(self, name: str) -> FunctionCall:
        """Finish parsing a function call."""
        arguments = []

        self._consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after function name"
        )

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self._expression())

                if not self._match(TokenType.COMMA):
                    break

        self._consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after arguments"
        )

        return FunctionCall(name, arguments)

    # ---------------------------------------------------------------
    # POSTFIX
    # ---------------------------------------------------------------
    def _postfix(self) -> ASTNode:
        """Parse postfix operators: x++, x--."""
        expr = self._primary()

        while self._match(
            TokenType.INCREMENT,
            TokenType.DECREMENT
        ):
            operator = self._previous().value

            if not isinstance(expr, VariableReference):
                raise self._syntax_error(
                    f"'{operator}' can only be applied to a variable",
                    self._previous()
                )

            expr = IncrementDecrement(
                expr.name,
                operator,
                is_prefix=False
            )

        return expr

    # ---------------------------------------------------------------
    # UNARY
    # ---------------------------------------------------------------
    def _unary(self) -> ASTNode:
        """Parse prefix operators: -x, !x, ~x, ++x, --x."""

        if self._match(TokenType.MINUS):
            operator = self._previous().value
            operand = self._unary()
            return UnaryOperation(operator, operand)

        if self._match(TokenType.NOT):
            operator = self._previous().value
            operand = self._unary()
            return UnaryOperation(operator, operand)

        if self._match(TokenType.BITWISE_NOT):
            operator = self._previous().value
            operand = self._unary()
            return UnaryOperation(operator, operand)

        if self._match(
            TokenType.INCREMENT,
            TokenType.DECREMENT
        ):
            operator = self._previous().value

            name_token = self._consume(
                TokenType.IDENTIFIER,
                f"Expected variable after '{operator}'"
            )

            return IncrementDecrement(
                name_token.value,
                operator,
                is_prefix=True
            )

        return self._postfix()

    # ---------------------------------------------------------------
    # POWER
    # ---------------------------------------------------------------
    def _power(self) -> ASTNode:
        expression = self._unary()

        if self._match(TokenType.POWER):
            operator = self._previous().value
            right = self._power()

            expression = BinaryOperation(
                expression,
                operator,
                right
            )

        return expression

    # ---------------------------------------------------------------
    # MULTIPLICATION
    # ---------------------------------------------------------------
    def _multiplication(self) -> ASTNode:
        left = self._power()

        while self._match(
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT,
            TokenType.DOUBLE_SLASH
        ):
            operator = self._previous().value
            right = self._power()
            left = BinaryOperation(left, operator, right)

        return left

    # ---------------------------------------------------------------
    # ADDITION
    # ---------------------------------------------------------------
    def _addition(self) -> ASTNode:
        left = self._multiplication()

        while self._match(
            TokenType.PLUS,
            TokenType.MINUS
        ):
            operator = self._previous().value
            right = self._multiplication()
            left = BinaryOperation(left, operator, right)

        return left

    # ---------------------------------------------------------------
    # BITWISE SHIFTS
    # ---------------------------------------------------------------
    def _shift(self) -> ASTNode:
        left = self._addition()

        while self._match(
            TokenType.BITWISE_LEFT_SHIFT,
            TokenType.BITWISE_RIGHT_SHIFT
        ):
            operator = self._previous().value
            right = self._addition()
            left = BinaryOperation(left, operator, right)

        return left

    # ---------------------------------------------------------------
    # BITWISE AND
    # ---------------------------------------------------------------
    def _bitwise_and(self) -> ASTNode:
        left = self._shift()

        while self._match(TokenType.BITWISE_AND):
            operator = self._previous().value
            right = self._shift()
            left = BinaryOperation(left, operator, right)

        return left

    # ---------------------------------------------------------------
    # BITWISE XOR
    # ---------------------------------------------------------------
    def _bitwise_xor(self) -> ASTNode:
        left = self._bitwise_and()

        while self._match(TokenType.BITWISE_XOR):
            operator = self._previous().value
            right = self._bitwise_and()
            left = BinaryOperation(left, operator, right)

        return left

    # ---------------------------------------------------------------
    # BITWISE OR
    # ---------------------------------------------------------------
    def _bitwise_or(self) -> ASTNode:
        left = self._bitwise_xor()

        while self._match(TokenType.BITWISE_OR):
            operator = self._previous().value
            right = self._bitwise_xor()
            left = BinaryOperation(left, operator, right)

        return left

    # ---------------------------------------------------------------
    # COMPARISON
    # ---------------------------------------------------------------
    def _comparison(self) -> ASTNode:
        left = self._bitwise_or()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.EQUAL_EQUAL,
            TokenType.NOT_EQUAL
        ):
            operator = self._previous().value
            right = self._bitwise_or()
            left = BinaryOperation(left, operator, right)

        return left

    # ---------------------------------------------------------------
    # EXPRESSIONS
    # ---------------------------------------------------------------
    def _expression(self) -> ASTNode:
        return self._or()

    def _or(self) -> ASTNode:
        left = self._and()

        while self._match(TokenType.OR):
            operator = self._previous().value
            right = self._and()
            left = BinaryOperation(left, operator, right)

        return left

    def _and(self) -> ASTNode:
        left = self._not()

        while self._match(TokenType.AND):
            operator = self._previous().value
            right = self._not()
            left = BinaryOperation(left, operator, right)

        return left

    def _not(self) -> ASTNode:
        if self._match(TokenType.NOT):
            operator = self._previous().value
            return UnaryOperation(operator, self._not())

        return self._comparison()

    # ---------------------------------------------------------------
    # PRINT
    # ---------------------------------------------------------------
    def _print_statement(self) -> PrintStatement:
        self._consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'drop'"
        )

        expr = self._expression()

        self._consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after expression"
        )

        return PrintStatement(expr)

    # ---------------------------------------------------------------
    # VARIABLE DECLARATION
    # ---------------------------------------------------------------
    def _variable_declaration(
        self,
        mutable: bool
    ) -> VariableDeclaration:

        if self._match(TokenType.INT):
            var_type = 'int'
        elif self._match(TokenType.STR):
            var_type = 'str'
        elif self._match(TokenType.BOOL):
            var_type = 'bool'
        elif self._match(TokenType.FLOAT):
            var_type = 'float'
        else:
            raise self._syntax_error(
                "Expected type (int, str, bool, float)"
            )

        name_token = self._consume(
            TokenType.IDENTIFIER,
            "Expected variable name after type"
        )

        name = name_token.value

        value = None

        if self._match(TokenType.EQUALS):
            value = self._expression()

        return VariableDeclaration(
            mutable,
            var_type,
            name,
            value
        )

    # ---------------------------------------------------------------
    # ASSIGNMENT
    # ---------------------------------------------------------------
    def _assignment(self):
        name_token = self._consume(
            TokenType.IDENTIFIER,
            "Expected variable name for assignment"
        )

        name = name_token.value

        operator_tokens = {
            TokenType.EQUALS: "=",
            TokenType.PLUS_EQUALS: "+=",
            TokenType.MINUS_EQUALS: "-=",
            TokenType.STAR_EQUALS: "*=",
            TokenType.SLASH_EQUALS: "/=",
            TokenType.PERCENT_EQUALS: "%=",
        }

        operator_token = self._peek()

        if operator_token.type not in operator_tokens:
            raise self._syntax_error(
                "Expected assignment operator",
                operator_token
            )

        self._advance()

        operator = operator_tokens[operator_token.type]
        value = self._expression()

        if operator == "=":
            return Assignment(name, value)

        return CompoundAssignment(name, operator, value)

    # ---------------------------------------------------------------
    # RETURN
    # ---------------------------------------------------------------
    def _return_statement(self) -> ReturnStatement:
        """Parse return statements, with or without a value."""

        if (
            self._check(TokenType.RIGHT_BRACE)
            or self._check(TokenType.SEMICOLON)
        ):
            return ReturnStatement(None)

        value = self._expression()
        return ReturnStatement(value)

    # ---------------------------------------------------------------
    # FUNCTION PARAMETERS
    # ---------------------------------------------------------------
    def _parse_params(self) -> List[tuple]:
        """Parse function parameters: int a, str b, bool c."""
        params = []

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if self._match(TokenType.INT):
                    param_type = 'int'
                elif self._match(TokenType.STR):
                    param_type = 'str'
                elif self._match(TokenType.BOOL):
                    param_type = 'bool'
                elif self._match(TokenType.FLOAT):
                    param_type = 'float'
                else:
                    raise self._syntax_error(
                        "Expected type in parameter list"
                    )

                name_token = self._consume(
                    TokenType.IDENTIFIER,
                    "Expected parameter name"
                )

                params.append((param_type, name_token.value))

                if not self._match(TokenType.COMMA):
                    break

        return params

    # ---------------------------------------------------------------
    # FUNCTION DECLARATION
    # ---------------------------------------------------------------
    def _function_declaration(self) -> FunctionDeclaration:
        """Parse function declarations."""

        if self._match(TokenType.INT):
            return_type = 'int'
        elif self._match(TokenType.STR):
            return_type = 'str'
        elif self._match(TokenType.BOOL):
            return_type = 'bool'
        elif self._match(TokenType.FLOAT):
            return_type = 'float'
        elif self._match(TokenType.VOID):
            return_type = 'void'
        else:
            raise self._syntax_error("Expected return type")

        name_token = self._consume(
            TokenType.IDENTIFIER,
            "Expected function name"
        )

        name = name_token.value

        self._consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after function name"
        )

        params = self._parse_params()

        self._consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after parameters"
        )

        self._consume(
            TokenType.LEFT_BRACE,
            "Expected '{' for function body"
        )

        body = []

        while (
            not self._check(TokenType.RIGHT_BRACE)
            and not self._is_at_end()
        ):
            body.append(self._statement())

        self._consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' to close function body"
        )

        return FunctionDeclaration(
            return_type,
            name,
            params,
            body
        )

    # ---------------------------------------------------------------
    # IF / ELSE
    # ---------------------------------------------------------------
    def _if_statement(self) -> IfStatement:
        self._consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'if'"
        )

        condition = self._expression()

        self._consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after condition"
        )

        self._consume(
            TokenType.LEFT_BRACE,
            "Expected '{' after condition"
        )

        then_branch = []

        while (
            not self._check(TokenType.RIGHT_BRACE)
            and not self._is_at_end()
        ):
            then_branch.append(self._statement())

        self._consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' after if block"
        )

        else_branch: Optional[List[ASTNode]] = None

        if self._match(TokenType.ELSE):

            if self._match(TokenType.IF):
                else_branch = [self._if_statement()]

            else:
                self._consume(
                    TokenType.LEFT_BRACE,
                    "Expected '{' after 'else'"
                )

                else_branch = []

                while (
                    not self._check(TokenType.RIGHT_BRACE)
                    and not self._is_at_end()
                ):
                    else_branch.append(self._statement())

                self._consume(
                    TokenType.RIGHT_BRACE,
                    "Expected '}' after else block"
                )

        return IfStatement(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch
        )

    # ---------------------------------------------------------------
    # FOR LOOP
    # ---------------------------------------------------------------
    def _for_statement(self) -> ForStatement:
        self._consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'for'"
        )

        # Initializer
        initializer = None

        if not self._check(TokenType.SEMICOLON):

            if self._match(TokenType.PLANT):
                initializer = self._variable_declaration(
                    mutable=True
                )

            elif self._match(TokenType.ROOT):
                initializer = self._variable_declaration(
                    mutable=False
                )

            else:
                # Do not consume the mandatory for-header semicolon.
                initializer = self._statement_core()

        self._consume(
            TokenType.SEMICOLON,
            "Expected ';' after for initializer"
        )

        # Condition
        condition = None

        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()

        self._consume(
            TokenType.SEMICOLON,
            "Expected ';' after for condition"
        )

        # Increment
        increment = None

        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()

        self._consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after for clauses"
        )

        # Body
        self._consume(
            TokenType.LEFT_BRACE,
            "Expected '{' before for body"
        )

        body = []

        while (
            not self._check(TokenType.RIGHT_BRACE)
            and not self._is_at_end()
        ):
            body.append(self._statement())

        self._consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' after for body"
        )

        return ForStatement(
            initializer=initializer,
            condition=condition,
            increment=increment,
            body=body
        )

    # ---------------------------------------------------------------
    # WHILE LOOP
    # ---------------------------------------------------------------
    def _while_statement(self) -> WhileStatement:
        """Parse while loop: while (condition) { body }."""

        self._consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'while'"
        )

        condition = self._expression()

        self._consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after while condition"
        )

        self._consume(
            TokenType.LEFT_BRACE,
            "Expected '{' after while condition"
        )

        body = []

        while (
            not self._check(TokenType.RIGHT_BRACE)
            and not self._is_at_end()
        ):
            body.append(self._statement())

        self._consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' to close while body"
        )

        return WhileStatement(condition, body)

    # ---------------------------------------------------------------
    # STATEMENT DISPATCH
    # ---------------------------------------------------------------
    def _statement(self) -> ASTNode:
        """
        Parse a statement and consume an optional semicolon.

        This allows both:
            plant int age = 20
            plant int age = 20;
        """
        statement = self._statement_core()

        # Semicolon is optional for ordinary statements.
        self._match(TokenType.SEMICOLON)

        return statement

    def _statement_core(self) -> ASTNode:
        """
        Parse the actual statement without consuming a semicolon.

        Used by for-loop initializers because their semicolons
        are mandatory separators in the loop header.
        """

        # Break
        if self._match(TokenType.BREAK):
            return BreakStatement()

        # Continue
        if self._match(TokenType.CONTINUE):
            return ContinueStatement()

        # Function declaration
        if self._match(TokenType.BRANCH):
            return self._function_declaration()

        # Return
        if self._match(TokenType.RETURN):
            return self._return_statement()

        # Variable declaration
        if self._match(TokenType.PLANT):
            return self._variable_declaration(mutable=True)

        if self._match(TokenType.ROOT):
            return self._variable_declaration(mutable=False)

        # Variable assignment
        if self._check(TokenType.IDENTIFIER):
            assignment_operators = {
                TokenType.EQUALS,
                TokenType.PLUS_EQUALS,
                TokenType.MINUS_EQUALS,
                TokenType.STAR_EQUALS,
                TokenType.SLASH_EQUALS,
                TokenType.PERCENT_EQUALS,
            }

            if (
                self.current + 1 < len(self.tokens)
                and self.tokens[self.current + 1].type
                in assignment_operators
            ):
                return self._assignment()

        # Print statement
        if self._match(TokenType.DROP):
            return self._print_statement()

        # If / else
        if self._match(TokenType.IF):
            return self._if_statement()

        # For loop
        if self._match(TokenType.FOR):
            return self._for_statement()

        # While loop
        if self._match(TokenType.WHILE):
            return self._while_statement()

        # Expression
        return self._expression()

    # ---------------------------------------------------------------
    # ENTRY POINT
    # ---------------------------------------------------------------
    def parse(self) -> Program:
        statements = []

        while not self._is_at_end():
            statements.append(self._statement())

        return Program(statements)

    # ---------------------------------------------------------------
    # SOURCE LOCATION
    # ---------------------------------------------------------------
    def _set_location(self, node, token):
        node.line = token.line
        node.column = token.column
        return node

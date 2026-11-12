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
        raise SyntaxError(f"{message} at line {self._peek().line}")

    # ---------------------------------------------------------------
    # PRIMARY
    # ---------------------------------------------------------------
    def _primary(self) -> ASTNode:
        # Handle parentheses
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr

        # Number literal
        if self._match(TokenType.NUMBER):
            return NumberLiteral(float(self._previous().value))

        # String literal
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)

        # Boolean literals
        if self._match(TokenType.GOOD):
            return BooleanLiteral(True)
        if self._match(TokenType.BAD):
            return BooleanLiteral(False)

        # Variable reference or function call
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value

            # Check if it's a function call: identifier(
            if self._check(TokenType.LEFT_PAREN):
                return self._finish_call(name)

            return VariableReference(name)

        raise SyntaxError(
            f"Unexpected token: {self._peek().value} at line {self._peek().line}"
        )

    def _finish_call(self, name: str) -> FunctionCall:
        """Finish parsing a function call after the opening paren"""
        arguments = []

        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")

        # Parse arguments if any
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        return FunctionCall(name, arguments)

    # ---------------------------------------------------------------
    # POSTFIX  (x++ , x--)
    # ---------------------------------------------------------------
    def _postfix(self) -> ASTNode:
        """Parse postfix operators: x++, x--"""
        expr = self._primary()

        while self._match(TokenType.INCREMENT, TokenType.DECREMENT):
            operator = self._previous().value
            if not isinstance(expr, VariableReference):
                raise SyntaxError(
                    f"'{operator}' can only be applied to a variable "
                    f"at line {self._peek().line}"
                )
            expr = IncrementDecrement(expr.name, operator, is_prefix=False)

        return expr

    # ---------------------------------------------------------------
    # UNARY  (-x, !x, ++x, --x)
    # ---------------------------------------------------------------
    def _unary(self) -> ASTNode:
        """Parse prefix operators: -x, !x, ++x, --x"""

        # Unary minus
        if self._match(TokenType.MINUS):
            operator = self._previous().value
            operand = self._unary()
            return UnaryOperation(operator, operand)

        # Logical NOT
        if self._match(TokenType.NOT):
            operator = self._previous().value
            operand = self._unary()
            return UnaryOperation(operator, operand)

        # Pre-increment / pre-decrement
        if self._match(TokenType.INCREMENT, TokenType.DECREMENT):
            operator = self._previous().value
            name_token = self._consume(
                TokenType.IDENTIFIER,
                f"Expected variable after '{operator}'"
            )
            return IncrementDecrement(name_token.value, operator, is_prefix=True)

        return self._postfix()

    # ---------------------------------------------------------------
    # POWER  (**)
    # ---------------------------------------------------------------
    def _power(self) -> ASTNode:
        left = self._unary()
        while self._match(TokenType.POWER):
            operator = self._previous().value
            right = self._unary()
            left = BinaryOperation(left, operator, right)
        return left

    # ---------------------------------------------------------------
    # MULTIPLICATION  (* / % //)
    # ---------------------------------------------------------------
    def _multiplication(self) -> ASTNode:
        left = self._power()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.DOUBLE_SLASH):
            operator = self._previous().value
            right = self._power()
            left = BinaryOperation(left, operator, right)
        return left

    # ---------------------------------------------------------------
    # ADDITION  (+ -)
    # ---------------------------------------------------------------
    def _addition(self) -> ASTNode:
        left = self._multiplication()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().value
            right = self._multiplication()
            left = BinaryOperation(left, operator, right)
        return left

    # ---------------------------------------------------------------
    # COMPARISON  (== != > < >= <=)
    # ---------------------------------------------------------------
    def _comparison(self) -> ASTNode:
        left = self._addition()
        while self._match(
            TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL,
            TokenType.GREATER, TokenType.GREATER_EQUAL,
            TokenType.LESS, TokenType.LESS_EQUAL
        ):
            operator = self._previous().value
            right = self._addition()
            left = BinaryOperation(left, operator, right)
        return left

    def _expression(self) -> ASTNode:
        return self._comparison()

    # ---------------------------------------------------------------
    # PRINT  (drop(...))
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
    # VARIABLE DECLARATION  (plant int x = 5 / root int x = 5)
    # ---------------------------------------------------------------
    def _variable_declaration(self, mutable: bool) -> VariableDeclaration:
        # Parse the type
        if self._match(TokenType.INT):
            var_type = 'int'
        elif self._match(TokenType.STR):
            var_type = 'str'
        elif self._match(TokenType.BOOL):
            var_type = 'bool'
        elif self._match(TokenType.FLOAT):
            var_type = 'float'
        else:
            raise SyntaxError(f"Expected type (int, str, bool, float) at line {self._peek().line}")

        # Parse the variable name
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name after type")
        name = name_token.value

        # Parse the initial value (optional)
        value = None
        if self._match(TokenType.EQUALS):
            value = self._expression()

        return VariableDeclaration(mutable, var_type, name, value)

    # ---------------------------------------------------------------
    # ASSIGNMENT  (x = 5)
    # ---------------------------------------------------------------
    def _assignment(self) -> Assignment:
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name for assignment")
        name = name_token.value

        if self._match(TokenType.EQUALS):
            value = self._expression()
            return Assignment(name, value)

        if self._match(TokenType.PLUS_EQUALS):
            op = '+'
        elif self._match(TokenType.MINUS_EQUALS):
            op = '-'
        elif self._match(TokenType.STAR_EQUALS):
            op = '*'
        elif self._match(TokenType.SLASH_EQUALS):
            op = '/'
        else:
            raise SyntaxError(
            f"Expected assignment operator after '{name}' "
            f"at line {self._peek().line}"
            )

        rhs = self._expression()
        desugared_value = BinaryOperation(
        left=VariableReference(name),
        operator=op,
        right=rhs,
        )
        return Assignment(name, desugared_value)

    # ---------------------------------------------------------------
    # RETURN
    # ---------------------------------------------------------------
    def _return_statement(self) -> ReturnStatement:
        """Parse return statement: return x + 5"""
        # The RETURN token has already been consumed by _match() in _statement()
        # Check if it's an empty return (just 'return' with no value)
        if self._check(TokenType.RIGHT_BRACE):
            return ReturnStatement(None)

        value = self._expression()
        return ReturnStatement(value)

    # ---------------------------------------------------------------
    # FUNCTION PARAMETERS
    # ---------------------------------------------------------------
    def _parse_params(self) -> List[tuple]:
        """Parse function parameters: int a, str b, bool c"""
        params = []

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                # Parse parameter type
                if self._match(TokenType.INT):
                    param_type = 'int'
                elif self._match(TokenType.STR):
                    param_type = 'str'
                elif self._match(TokenType.BOOL):
                    param_type = 'bool'
                elif self._match(TokenType.FLOAT):
                    param_type = 'float'
                else:
                    raise SyntaxError(f"Expected type in parameter list at line {self._peek().line}")

                # Parse parameter name
                name_token = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
                params.append((param_type, name_token.value))

                if not self._match(TokenType.COMMA):
                    break

        return params

    # ---------------------------------------------------------------
    # FUNCTION DECLARATION  (branch int add(int a, int b) { ... })
    # ---------------------------------------------------------------
    def _function_declaration(self) -> FunctionDeclaration:
        """Parse function: branch int add(int a, int b) { ... }"""

        # Parse return type
        if self._match(TokenType.INT):
            return_type = 'int'
        elif self._match(TokenType.STR):
            return_type = 'str'
        elif self._match(TokenType.BOOL):
            return_type = 'bool'
        elif self._match(TokenType.FLOAT):
            return_type = 'float'
        elif self._match(TokenType.DROP):
            return_type = 'void'
        else:
            raise SyntaxError(f"Expected return type at line {self._peek().line}")

        # Parse function name
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.value

        # Parse parameters
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        params = self._parse_params()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")

        # Parse function body
        self._consume(TokenType.LEFT_BRACE, "Expected '{' for function body")
        body = []

        # Parse statements inside the function body
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._statement()
            body.append(stmt)

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' to close function body")

        return FunctionDeclaration(return_type, name, params, body)

    # ---------------------------------------------------------------
    # IF / ELSE
    # ---------------------------------------------------------------
    def _if_statement(self) -> IfStatement:
        # if (condition)
        self._consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'if'"
        )

        condition = self._expression()

        self._consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after condition"
        )

        # if { ... }
        self._consume(
            TokenType.LEFT_BRACE,
            "Expected '{' after condition"
        )

        then_branch = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            then_branch.append(self._statement())

        self._consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' after if block"
        )

        # else / else if
        else_branch: Optional[List[ASTNode]] = None

        if self._match(TokenType.ELSE):

            # else if (...)
            if self._match(TokenType.IF):
                else_branch = [self._if_statement()]

            # else { ... }
            else:
                self._consume(
                    TokenType.LEFT_BRACE,
                    "Expected '{' after 'else'"
                )

                else_branch = []

                while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
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
        # for
        self._consume(
            TokenType.FOR,
            "Expected 'for'"
        )

        # (
        self._consume(
            TokenType.LEFT_PAREN,
            "Expected '(' after 'for'"
        )

        # initializer
        initializer = None
        if not self._check(TokenType.SEMICOLON):
            if self._match(TokenType.PLANT):
                initializer = self._variable_declaration(mutable=True)
            elif self._match(TokenType.ROOT):
                initializer = self._variable_declaration(mutable=False)
            else:
                initializer = self._statement()

        self._consume(
            TokenType.SEMICOLON,
            "Expected ';' after for initializer"
        )

        # condition
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()

        self._consume(
            TokenType.SEMICOLON,
            "Expected ';' after for condition"
        )

        # increment  (now handled by _expression → _unary/_postfix)
        increment = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()

        self._consume(
            TokenType.RIGHT_PAREN,
            "Expected ')' after for clauses"
        )

        # body
        self._consume(
            TokenType.LEFT_BRACE,
            "Expected '{' before for body"
        )

        body = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
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
        """Parse while loop: while (condition) { body }"""

        # consume '('
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")

        # parse the condition
        condition = self._expression()

        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")

        # parse the body
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after while condition")

        body = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._statement()
            body.append(stmt)

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' to close while body")

        return WhileStatement(condition, body)

    # ---------------------------------------------------------------
    # STATEMENT DISPATCH
    # ---------------------------------------------------------------
    def _statement(self) -> ASTNode:
        # Function declaration
        if self._match(TokenType.BRANCH):
            return self._function_declaration()

        # Return statement
        if self._match(TokenType.RETURN):
            return self._return_statement()

        # Variable declaration
        if self._match(TokenType.PLANT):
            return self._variable_declaration(mutable=True)
        if self._match(TokenType.ROOT):
            return self._variable_declaration(mutable=False)

        # Variable assignment
        if self._check(TokenType.IDENTIFIER):
            if (self.current + 1 < len(self.tokens) and
                    self.tokens[self.current + 1].type in (
                        TokenType.EQUALS,
                        TokenType.PLUS_EQUALS,
                        TokenType.MINUS_EQUALS,
                        TokenType.STAR_EQUALS,
                        TokenType.SLASH_EQUALS,
                    )):
                return self._assignment()
            

        # Print statement
        if self._match(TokenType.DROP):
            return self._print_statement()

        # if/else
        if self._match(TokenType.IF):
            return self._if_statement()

        # for loop
        if self._match(TokenType.FOR):
            return self._for_statement()

        # while loop
        if self._match(TokenType.WHILE):
            return self._while_statement()

        # Expression (including function calls, ++, --, etc.)
        return self._expression()

    # ---------------------------------------------------------------
    # ENTRY POINT
    # ---------------------------------------------------------------
    def parse(self) -> Program:
        statements = []
        while not self._is_at_end():
            stmt = self._statement()
            statements.append(stmt)
        return Program(statements)
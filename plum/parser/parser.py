from typing import List
from plum.lexer import Token, TokenType
from plum.plum_ast import *


class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0  # index of current token

    def _previous(self) -> Token:
        """Get the last consumed token"""
        return self.tokens[self.current - 1]

    def _peek(self) -> Token:
        """Look at current token without consuming it"""
        return self.tokens[self.current]

    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        """Consume current token and return it"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    # Helper method for token manipulation
    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any given types.
        If yes, consume it and return True.
        """
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _is_at_end(self) -> bool:
        """Check if we've consumed all tokens"""
        return self._peek().type == TokenType.EOF

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume a token of the expected type or throw an error"""
        if self._check(token_type):
            return self._advance()
        raise SyntaxError(f"{message} at line {self._peek().line}")

    def _primary(self) -> ASTNode:
        """Parse primary expressions (numbers, strings, parentheses)"""

        # Handle Parentheses
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr

        if self._match(TokenType.NUMBER):
            return NumberLiteral(float(self._previous().value))

        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)

        raise SyntaxError(
            f"Unexpected token: {self._peek().value} "
            f"at line {self._peek().line}"
        )

    def _power(self) -> ASTNode:
        """Parse the power operator (**)."""
        left = self._primary()

        while self._match(TokenType.POWER):
            operator = self._previous().value
            right = self._primary()
            left = BinaryOperation(left, operator, right)

        return left

    def _multiplication(self) -> ASTNode:
        """Parse *, /, %, and //"""
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

    def _comparison(self) -> ASTNode:
        """Parse comparison operators."""
        left = self._addition()

        while self._match(
            TokenType.EQUAL_EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.GREATER,
            TokenType.LESS,
            TokenType.GREATER_EQUAL,
            TokenType.LESS_EQUAL
        ):
            operator = self._previous().value
            right = self._addition()
            left = BinaryOperation(left, operator, right)

        return left

    def _addition(self) -> ASTNode:
        """
        Parse + and - (lower precedence)
        Example: 5 + 3 - 2
        """
        left = self._multiplication()  # FIXED: Call _multiplication() not _primary()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().value
            right = self._multiplication()  # FIXED: Call _multiplication() not _primary()
            left = BinaryOperation(left, operator, right)
        
        return left

    def _expression(self) -> ASTNode:
         """Parse an expression"""
         return self._comparison()
   
    def _print_statement(self) -> PrintStatement:
        """Parse 'drop <expression>'"""
        expr = self._expression()
        return PrintStatement(expr)

    def _statement(self) -> ASTNode:
        """Parse a single statement"""

        # Check if it's a 'drop' statement
        if self._match(TokenType.DROP):
            return self._print_statement()

        # Otherwise, it must be an expression
        return self._expression()

    def parse(self) -> Program:
        """Parse all tokens into an AST"""

        statements = []

        # Keep parsing until EOF
        while not self._is_at_end():
            stmt = self._statement()
            statements.append(stmt)

        return Program(statements)
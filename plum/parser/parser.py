from typing import List
from lexer import Token, TokenType
from plum_ast import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0 # index of curr token


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
    def _match(self, *types: TokenType):
        """Check if current token matches any of the given types. If yes, consume it and return True."""

        for token_type in types:
            if self._checek(token_type):
               self._advance()
               return True
        return False

    def _is_at_end(self) -> bool:
        """Check if we've consumed all tokens"""
        return self._peek().type == TokenType.EOF
    
    def _primary(self) -> ASTNode:
        """Parse primary expressions (numbers, strings, etc.)"""
        if self._match(TokenType.NUMBER):
            return NumberLiteral(float(self._previous().value))
        if self._match(TokenType.STRING):
           return StringLiteral(self._previous().value)

        raise SyntaxError(f"Unexpected token: {self._peek().value} at line {self._peek().line}")
    
    
            

    def _addition(self) -> ASTNode:
        """Parse addition: number + number"""
        left = self._primary()
        # if we see a '+', parse the right side
        if self._match(TokenType.PLUS):
            right = self._primary()
            return BinaryOperation(left=left, operator='+', right=right)
        return left

    def _expression(self) -> ASTNode:
        """Parse an expression with + operator"""
        return self._addition()


    def _print_statement(self) -> PrintStatement:
        """Parse 'drop <expression>"""
        expr = self._expression()
        return PrintStatement(expr)


    def _statement(self) -> ASTNode:
        """Parse a single statement"""
        #check if it's a 'drop' statement
        if self.match(TokenType.DROP):
            return self._print_statement()
        # If not 'drop', it must be an expression
        expr = self._expression()
        return expr

    def parse(self) -> Program:
        """Parse all tokens into an AST"""
        statements = []

        # keep parsing util we hit EOF
        while not self._is_at_end():
            stmt = self._statement()
            statements.append(stmt)
        return Program(statements)
    

             
    
        
    
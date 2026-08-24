from typing import List
from lexer import Token, TokenType
from plum_ast import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0 # index of curr token
    def parse(self) -> Program:
        """Parse all tokens into an AST"""
        statements = []

        # keep parsing util we hit EOF
        while not self._is_at_end():
            stmt = self._statement()
            statements.append(stmt)
        return Program(statements)
             

    def _is_at_end(self) -> bool:
        """Check if we've consumed all tokens"""
        return self._peek().type == TokenType.EOF
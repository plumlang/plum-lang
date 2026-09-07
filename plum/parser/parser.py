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
        """Parse primary expressions (numbers, strings, parentheses, variables)"""

        # Handle Parentheses
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        # number literal

        if self._match(TokenType.NUMBER):
            return NumberLiteral(float(self._previous().value))
        # String Literal
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)

        # bool literal
        if self._match(TokenType.GOOD):
          return BooleanLiteral(True)

        if self._match(TokenType.BAD):
            return BooleanLiteral(False)
        # New: v0.5 Variable reference (IDENTIFER)
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value

            # check if it's a func call: identifier
            if self._check(TokenType.LEFT_PAREN):
                return self._finish_call(name);

            return VariableReference(name) 
        raise SyntaxError(
            f"Unexpected token: {self._peek().value} "
            f"at line {self._peek().line}"
        )
    
    def _finish_call(self, name: str) -> FunctionCall:
        """Finish parsing a function call after the opening paren"""
        arguments = []
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")

        # Parse argument if any

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RIGHT_PAREN,"Expected ')' after arguments")
        return FunctionCall(name, arguments)
    
    

    # variable declaration (sk-v0.5)
    def _variable_declaration(self, mutable: bool) -> VariableDeclaration:  
        """
        Parse variable declaration:
        plant int age = 21
        root str name = "Subhro"
        """
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
            raise SyntaxError(
                f"Expected type (int, str, bool, float) at line {self._peek().line}"
            )
        # parse the variable name
        name_token = self._consume(
            TokenType.IDENTIFIER,
            f"Expected variable name after type at line {self._peek().line}" 
        )

        name = name_token.value

        # parse the initial value
        value = None
        if self._match(TokenType.EQUALS):
            value = self._expression()
        return VariableDeclaration(mutable, var_type,name, value)


    def _assignment(self) -> Assignment:
        """Parse variable assignment: x = 10"""
        name_token = self._consume(
            TokenType.IDENTIFIER,
            "Expected variable name for assignment"

        )
        name = name_token.value
        self._consume(TokenType.EQUALS, "Expected '=' after variable name")
        value = self._expression()
        return Assignment(name, value)

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
        # func declare 
        if self._match(TokenType.BRANCH):
            return self._function_declaration()
        
        # return statement
        if self._match(TokenType.RETURN):
            return self._return_statement()

        # New Variable declaration (plant or root)
        if self._match(TokenType.PLANT):
            return self._variable_declaration(mutable=True)
        
        if self._match(TokenType.ROOT):
            return self._variable_declaration(mutable=False)

        # New: variable assignment (check if current token is Identifer follow by = )
        if self._check(TokenType.IDENTIFIER):
            #peeek ahead to see if it's an assignment
            if(self.current +1 < len(self.tokens) and self.tokens[self.current+1].type == TokenType.EQUALS):
                return self._assignment()
        
        


        # Check if it's a 'drop' statement
        if self._match(TokenType.DROP):
            return self._print_statement()

        # Otherwise, it must be an expression
        return self._expression()

    # return statement 
    def _return_statement(self) -> ReturnStatement:
        """Parse return statement: return x + 5"""
        if self._match(TokenType.RETURN):
            if self._check(TokenType.RIGHT_BRACE):
               return ReturnStatement(None)
            value = self._expression()
            return ReturnStatement(value)
        raise SystemError("Expected 'return' keyword")
    
    # parse params 
    def _parse_params(self) -> List[tuple]:
        """Parse function parameters: int a, str b, bool c"""
        params = []

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                # parse parameter type
                if self._match(TokenType.INT):
                   param_type = 'int'
                elif self._match(TokenType.STR):
                   param_type = 'str'
                elif self._match(TokenType.FLOAT):
                    param_type = 'float'
                elif self._match(TokenType.BOOL):
                    param_type = 'bool'
                else:
                    raise SyntaxError(f"Expected type in parameter list at line {self._peek().line}")
                

                name_token = self._consume(TokenType.IDENTIFIER, "Expected parameter name")

                params.append((param_type, name_token.value))

                if not self._match(TokenType.COMMA):
                   break
        return params


    def _function_declaration(self) -> FunctionDeclaration:
        """Parse function: branch int add(int a, int b) { ... }"""

        # parse return type
        if self._match(TokenType.INT):
           return_type = 'int'
        elif self._match(TokenType.STR):
           return_type = 'str'
        elif self._match(TokenType.BOOL):
            return_type = 'bool'
        elif self._match(TokenType.FLOAT):
            return_type = 'float'
        elif self._match(TokenType.DROP):
            return_type = 'void' # special case
        else:
            raise SyntaxError(f"Expected return type at line {self._peek().line}")
        

        #parse func name
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name")

        name = name_token.value

        # parse parameter 
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        params = self._parse_params()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after function name")

        # parse function body
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after function body")

        body = []

        # parse statements inside the func body
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._statement()
            body.append(stmt)
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' to close function body")

        return FunctionDeclaration(return_type, name, params, body)
    


    def parse(self) -> Program:
        """Parse all tokens into an AST"""

        statements = []

        # Keep parsing until EOF
        while not self._is_at_end():
            stmt = self._statement()
            statements.append(stmt)

        return Program(statements)
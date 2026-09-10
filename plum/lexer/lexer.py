from .token import Token
from .token_type import TokenType

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.tokens = []
        
    def tokenize(self) -> list[Token]:
        while self.position < len(self.source):
            current = self.source[self.position]

            # Ignore white spaces
            if current in " \t":
               self.position += 1
               continue
            # new Line 
            if current == "\n":
               self.line += 1
               self.position += 1
               continue
            
            #String Literal
            if current == '"':
                self.tokens.append(self._string())
                continue

            #NUMBER
            if current.isdigit():
                self.tokens.append(self._number())
                continue

            # REMOVED: The old/bad '=' handler that raises an error
            # This was causing the SyntaxError: Unexpected character '='

            # Addition operator (+)
            if current == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', self.line))
                self.position += 1
                continue

            # Comments (--)
            if current == '-' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '-':
                self.position += 2  # skip opening --

                while self.position < len(self.source):
                    if (
                        self.source[self.position] == '-'
                        and self.position + 1 < len(self.source)
                        and self.source[self.position + 1] == '-'
                    ):
                        self.position += 2  # skip closing --
                        break

                    if self.source[self.position] == '\n':
                        self.line += 1

                    self.position += 1
                else:
                    raise SyntaxError(
                        f"Unterminated comment on line {self.line}"
                    )

                continue

            # Subtraction operator (-)
            if current == '-':
               self.tokens.append(Token(TokenType.MINUS, '-', self.line))
               self.position += 1
               continue

            # Multiplication (*) and Power (**)
            if current == '*':
                if self.position + 1 < len(self.source) and self.source[self.position + 1] == '*':
                    self.tokens.append(Token(TokenType.POWER, '**', self.line))
                    self.position += 2
                else:
                    self.tokens.append(Token(TokenType.STAR, '*', self.line))
                    self.position += 1
                continue

            # Division (/) and Floor Division (//)
            if current == '/':
                if self.position + 1 < len(self.source) and self.source[self.position + 1] == '/':
                    self.tokens.append(Token(TokenType.DOUBLE_SLASH, '//', self.line))
                    self.position += 2
                else:
                    self.tokens.append(Token(TokenType.SLASH, '/', self.line))
                    self.position += 1
                continue

            # Modulo operator (%)
            if current == '%':
                self.tokens.append(Token(TokenType.PERCENT, '%', self.line))
                self.position += 1
                continue

            # Not equal operator (!=)
            if current == '!':
                 if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                     self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', self.line))
                     self.position += 2
                     continue
                 else:
                   raise SyntaxError(
                         f"Unexpected character '!' on line {self.line}"
                          )

            # Greater than and greater than or equal
            if current == '>':
                if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', self.line))
                    self.position += 2
                else:
                    self.tokens.append(Token(TokenType.GREATER, '>', self.line))
                    self.position += 1
                continue

            # Less than and less than or equal
            if current == '<':
                 if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                     self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', self.line))
                     self.position += 2
                 else:
                     self.tokens.append(Token(TokenType.LESS, '<', self.line))
                     self.position += 1
                 continue

            # left paren 
            if current == '(':
                self.tokens.append(Token(TokenType.LEFT_PAREN, '(', self.line))
                self.position += 1
                continue

            # right paren 
            if current == ')':
                self.tokens.append(Token(TokenType.RIGHT_PAREN, ')', self.line))
                self.position += 1
                continue

            # New: Left Brace {
            if current == '{':
                self.tokens.append(Token(TokenType.LEFT_BRACE, '{', self.line))
                self.position += 1;
                continue;
            
            # New: Right Brace }
            if current == '}':
                self.tokens.append(Token(TokenType.RIGHT_BRACE, '}', self.line))
                self.position += 1;
                continue

            if current == ',':
               self.tokens.append(Token(TokenType.COMMA, ',', self.line))
               self.position += 1;
               continue

            # v0.5: Equals sign for assignment (=) and comparison (==)
            if current == '=':
                # Check if it's == (comparison) or = (assignment)
                if (self.position + 1 < len(self.source) and self.source[self.position + 1] == '='):
                    # It's == 
                    self.tokens.append(Token(TokenType.EQUAL_EQUAL, '==', self.line))
                    self.position += 2
                else: 
                    # It's = 
                    self.tokens.append(Token(TokenType.EQUALS, '=', self.line))
                    self.position += 1
                continue

            # Identifiers (keywords and variable names)
            if current.isalpha():
               self.tokens.append(self._identifier())
               continue

            raise SyntaxError(
                f"Unexpected character '{current}' on line {self.line}"
            ) 
        self.tokens.append(Token(TokenType.EOF, "", self.line))
        return self.tokens
    

    def _string(self) -> Token:
        self.position += 1 #skip opening quote
        start = self.position
        while (
            self.position < len(self.source)
            and self.source[self.position] != '"'
        ):
            self.position += 1
        if self.position >= len(self.source):
            raise SyntaxError(
                f"Unterminated String on line {self.line}"
            )
        value = self.source[start:self.position]
        self.position += 1 #skip closing quote
        return Token(TokenType.STRING, value, self.line)
    

    def _identifier(self) -> Token:
        start = self.position
        while (
            self.position < len(self.source)
            and (self.source[self.position].isalnum() or self.source[self.position] == '_')
        ):
            self.position += 1

        value = self.source[start: self.position]

        # v0.1 keywords
        if value == 'drop':
            return Token(TokenType.DROP, value, self.line)
        
        # v0.4 boolean keywords (support both 'true'/'false' and 'good'/'bad')
        if value == 'true' or value == 'good':
            return Token(TokenType.GOOD, value, self.line)
        if value == 'false' or value == 'bad':
            return Token(TokenType.BAD, value, self.line)
        
        # v0.5 variable keywords
        if value == 'plant':
            return Token(TokenType.PLANT, value, self.line)
        if value == 'root':
            return Token(TokenType.ROOT, value, self.line)
        
        # v0.5 type keywords
        if value == 'int':
            return Token(TokenType.INT, value, self.line)
        if value == 'str':
            return Token(TokenType.STR, value, self.line)
        if value == 'bool':
            return Token(TokenType.BOOL, value, self.line)
        if value == 'float':
            # FIXED: Was TokenType() incorrectly, now Token()
            return Token(TokenType.FLOAT, value, self.line)
        
        # v0.7 func keyword (NEW)
        if value == 'branch':
           return Token(TokenType.BRANCH, value, self.line)
        
        if value == 'return':
            return Token(TokenType.RETURN, value, self.line)

        # v0.8 conditional keywords
        if value == 'if':
             return Token(TokenType.IF, value, self.line)

        if value == 'else':
           return Token(TokenType.ELSE, value, self.line)
        
        # If not a keyword, it's a variable name (IDENTIFIER)
        return Token(TokenType.IDENTIFIER, value, self.line)


    def _number(self) -> Token:
        start = self.position

        while (
            self.position < len(self.source)
            and self.source[self.position].isdigit()
        ):  
            self.position += 1

        # Handle decimal points (e.g., 3.14)
        if (self.position < len(self.source) 
            and self.source[self.position] == '.' 
            and self.position + 1 < len(self.source)
            and self.source[self.position + 1].isdigit()):
            
            self.position += 1  # skip the '.'
            while (self.position < len(self.source) 
                   and self.source[self.position].isdigit()):
                self.position += 1

        value = self.source[start:self.position]
        return Token(TokenType.NUMBER, value, self.line)
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
            
            #String Litral
            if current == '"':
                self.tokens.append(self._string())
                continue

            #NUMBER
            if current.isdigit():
                self.tokens.append(self._number())
                continue

            # Addition operator (+)
            if current == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', self.line))
                self.position += 1
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
            and self.source[self.position].isalpha()
        ):
            self.position += 1
        value = self.source[start: self.position]
        if value == 'drop':
            return Token(TokenType.DROP,value, self.line)
        raise SyntaxError(
            f"Unknown Keyword '{value}' on line {self.line} "
        )

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

        value = self.source[start:self.position]  # ✅ Fixed: moved outside loop
        return Token(TokenType.NUMBER, value, self.line)
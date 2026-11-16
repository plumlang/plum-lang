from .token import Token
from .token_type import TokenType


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.tokens = []

    def _column(self) -> int:
        """Return the 1-based column at the current source position."""
        last_newline = self.source.rfind("\n", 0, self.position)
        return self.position - last_newline

    def _add_token(self, token_type: TokenType, value) -> None:
        """Add a token using the current line and column."""
        self.tokens.append(
            Token(token_type, value, self.line, self._column())
        )

    def tokenize(self) -> list[Token]:
        while self.position < len(self.source):
            current = self.source[self.position]

            # Ignore whitespace
            if current in " \t":
                self.position += 1
                continue

            # New line
            if current == "\n":
                self.line += 1
                self.position += 1
                continue

            # String literal
            if current == '"':
                self.tokens.append(self._string())
                continue

            # Number
            if current.isdigit():
                self.tokens.append(self._number())
                continue

            # Comments (#)
            if current == "#":
                while (
                    self.position < len(self.source)
                    and self.source[self.position] != "\n"
                ):
                    self.position += 1
                continue

            # Addition (+), increment (++), addition assignment (+=)
            if current == "+":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "+"
                ):
                    self._add_token(TokenType.INCREMENT, "++")
                    self.position += 2

                elif (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "="
                ):
                    self._add_token(TokenType.PLUS_EQUALS, "+=")
                    self.position += 2

                else:
                    self._add_token(TokenType.PLUS, "+")
                    self.position += 1

                continue

            # Subtraction (-), decrement (--), subtraction assignment (-=)
            if current == "-":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "-"
                ):
                    self._add_token(TokenType.DECREMENT, "--")
                    self.position += 2

                elif (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "="
                ):
                    self._add_token(TokenType.MINUS_EQUALS, "-=")
                    self.position += 2

                else:
                    self._add_token(TokenType.MINUS, "-")
                    self.position += 1

                continue

            # Multiplication (*), power (**), multiplication assignment (*=)
            if current == "*":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "*"
                ):
                    self._add_token(TokenType.POWER, "**")
                    self.position += 2

                elif (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "="
                ):
                    self._add_token(TokenType.STAR_EQUALS, "*=")
                    self.position += 2

                else:
                    self._add_token(TokenType.STAR, "*")
                    self.position += 1

                continue

            # Division (/), floor division (//), division assignment (/=)
            if current == "/":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "/"
                ):
                    self._add_token(TokenType.DOUBLE_SLASH, "//")
                    self.position += 2

                elif (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "="
                ):
                    self._add_token(TokenType.SLASH_EQUALS, "/=")
                    self.position += 2

                else:
                    self._add_token(TokenType.SLASH, "/")
                    self.position += 1

                continue

            # Modulo (%) and modulo assignment (%=)
            if current == "%":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "="
                ):
                    self._add_token(TokenType.PERCENT_EQUALS, "%=")
                    self.position += 2

                else:
                    self._add_token(TokenType.PERCENT, "%")
                    self.position += 1

                continue

            # Bitwise AND (&) and logical AND (&&)
            if current == "&":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "&"
                ):
                    self._add_token(TokenType.AND, "&&")
                    self.position += 2

                else:
                    self._add_token(TokenType.BITWISE_AND, "&")
                    self.position += 1

                continue

            # Bitwise OR (|) and logical OR (||)
            if current == "|":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "|"
                ):
                    self._add_token(TokenType.OR, "||")
                    self.position += 2

                else:
                    self._add_token(TokenType.BITWISE_OR, "|")
                    self.position += 1

                continue

            # Bitwise XOR (^)
            if current == "^":
                self._add_token(TokenType.BITWISE_XOR, "^")
                self.position += 1
                continue

            # Bitwise NOT (~)
            if current == "~":
                self._add_token(TokenType.BITWISE_NOT, "~")
                self.position += 1
                continue

            # Not equal (!=) and logical NOT (!)
            if current == "!":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "="
                ):
                    self._add_token(TokenType.NOT_EQUAL, "!=")
                    self.position += 2

                else:
                    self._add_token(TokenType.NOT, "!")
                    self.position += 1

                continue

            # Greater than (>), greater than or equal (>=), right shift (>>)
            if current == ">":
                if self.position + 1 < len(self.source):
                    next_char = self.source[self.position + 1]

                    if next_char == ">":
                        self._add_token(
                            TokenType.BITWISE_RIGHT_SHIFT, ">>"
                        )
                        self.position += 2

                    elif next_char == "=":
                        self._add_token(TokenType.GREATER_EQUAL, ">=")
                        self.position += 2

                    else:
                        self._add_token(TokenType.GREATER, ">")
                        self.position += 1

                else:
                    self._add_token(TokenType.GREATER, ">")
                    self.position += 1

                continue

            # Less than (<), less than or equal (<=), left shift (<<)
            if current == "<":
                if self.position + 1 < len(self.source):
                    next_char = self.source[self.position + 1]

                    if next_char == "<":
                        self._add_token(
                            TokenType.BITWISE_LEFT_SHIFT, "<<"
                        )
                        self.position += 2

                    elif next_char == "=":
                        self._add_token(TokenType.LESS_EQUAL, "<=")
                        self.position += 2

                    else:
                        self._add_token(TokenType.LESS, "<")
                        self.position += 1

                else:
                    self._add_token(TokenType.LESS, "<")
                    self.position += 1

                continue

            # Left parenthesis
            if current == "(":
                self._add_token(TokenType.LEFT_PAREN, "(")
                self.position += 1
                continue

            # Right parenthesis
            if current == ")":
                self._add_token(TokenType.RIGHT_PAREN, ")")
                self.position += 1
                continue

            # Left brace
            if current == "{":
                self._add_token(TokenType.LEFT_BRACE, "{")
                self.position += 1
                continue

            # Right brace
            if current == "}":
                self._add_token(TokenType.RIGHT_BRACE, "}")
                self.position += 1
                continue

            # Semicolon
            if current == ";":
                self._add_token(TokenType.SEMICOLON, ";")
                self.position += 1
                continue

            # Comma
            if current == ",":
                self._add_token(TokenType.COMMA, ",")
                self.position += 1
                continue

            # Equals (=) and equality comparison (==)
            if current == "=":
                if (
                    self.position + 1 < len(self.source)
                    and self.source[self.position + 1] == "="
                ):
                    self._add_token(TokenType.EQUAL_EQUAL, "==")
                    self.position += 2

                else:
                    self._add_token(TokenType.EQUALS, "=")
                    self.position += 1

                continue

            # Identifiers and keywords
            if current.isalpha() or current == "_":
                self.tokens.append(self._identifier())
                continue

            # Invalid character
            raise SyntaxError(
                f"Unexpected character {current!r} "
                f"at line {self.line}, column {self._column()}"
            )

        # EOF token
        self._add_token(TokenType.EOF, "")

        return self.tokens

    def _string(self) -> Token:
        start_line = self.line
        start_column = self._column()

        # Skip opening quote
        self.position += 1
        start = self.position

        while (
            self.position < len(self.source)
            and self.source[self.position] != '"'
        ):
            if self.source[self.position] == "\n":
                self.line += 1

            self.position += 1

        if self.position >= len(self.source):
            raise SyntaxError(
                f"Unterminated String at line {start_line}, "
                f"column {start_column}"
            )

        value = self.source[start:self.position]

        # Skip closing quote
        self.position += 1

        return Token(
            TokenType.STRING,
            value,
            start_line,
            start_column
        )

    def _identifier(self) -> Token:
        start = self.position
        start_line = self.line
        start_column = self._column()

        while (
            self.position < len(self.source)
            and (
                self.source[self.position].isalnum()
                or self.source[self.position] == "_"
            )
        ):
            self.position += 1

        value = self.source[start:self.position]

        # Keywords
        keywords = {
            "drop": TokenType.DROP,
            "true": TokenType.GOOD,
            "good": TokenType.GOOD,
            "false": TokenType.BAD,
            "bad": TokenType.BAD,
            "plant": TokenType.PLANT,
            "root": TokenType.ROOT,
            "int": TokenType.INT,
            "str": TokenType.STR,
            "bool": TokenType.BOOL,
            "float": TokenType.FLOAT,
            "void": TokenType.VOID,
            "branch": TokenType.BRANCH,
            "return": TokenType.RETURN,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "for": TokenType.FOR,
            "while": TokenType.WHILE,
            "break": TokenType.BREAK,
            "continue": TokenType.CONTINUE,
        }

        token_type = keywords.get(value, TokenType.IDENTIFIER)

        return Token(
            token_type,
            value,
            start_line,
            start_column
        )

    def _number(self) -> Token:
        start = self.position
        start_line = self.line
        start_column = self._column()

        # Read integer digits
        while (
            self.position < len(self.source)
            and self.source[self.position].isdigit()
        ):
            self.position += 1

        # Check for decimal point
        is_float = False

        if (
            self.position < len(self.source)
            and self.source[self.position] == "."
            and self.position + 1 < len(self.source)
            and self.source[self.position + 1].isdigit()
        ):
            is_float = True
            self.position += 1

            while (
                self.position < len(self.source)
                and self.source[self.position].isdigit()
            ):
                self.position += 1

        # Convert to correct numeric type
        value = self.source[start:self.position]

        if is_float:
            value = float(value)
        else:
            value = int(value)

        return Token(
            TokenType.NUMBER,
            value,
            start_line,
            start_column
        )
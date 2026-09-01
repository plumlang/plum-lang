from enum import Enum, auto

class TokenType(Enum):
    # v0.1 tokens (already  have)
    DROP = auto()
    STRING = auto()
    EOF = auto()
    # v0.2 - first step: numbers and basic arithmetic 
    NUMBER = auto() # int and float value;
    PLUS = auto() # +
    MINUS = auto() # -
    STAR = auto()
    SLASH = auto()

    #v3  
    PERCENT = auto()       # %
    DOUBLE_SLASH = auto()  # //
    POWER = auto()         # **

    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()

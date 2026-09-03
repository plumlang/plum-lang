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

    # v0.4 - Comparison operators && Boolean values
    EQUAL_EQUAL = auto()    # ==
    NOT_EQUAL = auto()      # !=
    GREATER = auto()        # >
    LESS = auto()           # <
    GREATER_EQUAL = auto()  # >=
    LESS_EQUAL = auto()     # <=
 
    GOOD = auto()   # true
    BAD = auto()    # false

    #v0.5 - keyword variables 
    PLANT = auto(); # mutable variables keyword
    ROOT = auto();  # immutable variable keyword
    INT = auto();
    STR = auto();
    BOOL = auto();
    FLOAT = auto();
    EQUALS = auto(); # = assignment
    IDENTIFIER = auto(); # variable names
    


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
    #v.5
    GOOD = auto()   # true
    BAD = auto()    # false

    #v0.6 - keyword variables 
    PLANT = auto(); # mutable variables keyword
    ROOT = auto();  # immutable variable keyword
    INT = auto();
    STR = auto();
    BOOL = auto();
    FLOAT = auto();
    EQUALS = auto(); # = assignment
    IDENTIFIER = auto(); # variable names

    #v0.7 Functions(NEW)
    BRANCH = auto();
    RETURN = auto();
    LEFT_BRACE = auto();
    RIGHT_BRACE = auto();
    COMMA = auto();
    SEMICOLON =auto()
    
    
    # v0.8 - Conditionals
    IF = auto()
    ELSE = auto()

    #v0.9 - Loops (for loop , while loop )
    FOR = auto()
    WHILE = auto()
    BREAK = auto()
    CONTINUE = auto()
    AND = auto()   # &&
    OR = auto()    # ||
    NOT = auto()   # !


    # v0.10 Increment / Decrement
    INCREMENT = auto()      # ++
    DECREMENT = auto() 
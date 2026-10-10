from dataclasses import dataclass
from typing import List, Optional, Any

class ASTNode:
     """Base class for all AST nodes"""
     pass

@dataclass
class Program(ASTNode):
     """Root node containing all statements"""
     statements: List[ASTNode]

@dataclass
class PrintStatement(ASTNode):
     """Represents 'drop <expression>'"""
     expression: ASTNode

@dataclass
class NumberLiteral(ASTNode):
    """A number like 42 or 3.14"""
    value: float

@dataclass
class BooleanLiteral(ASTNode):
    """A boolean value: good or bad"""
    value: bool
    
@dataclass
class StringLiteral(ASTNode):
     """A string like "hello" """
     value: str

@dataclass 
class BinaryOperation(ASTNode):
    """An operation like 5+3"""
    left: ASTNode 
    operator: str 
    right: ASTNode
    
@dataclass
class VariableDeclaration(ASTNode):
     """Variable declaration: plant int x = 5 or root int x = 5"""
     mutable: bool
     var_type: str
     name: str
     value: Optional[ASTNode] = None

@dataclass
class VariableReference(ASTNode):
     """Reference to a variable: x"""
     name: str

@dataclass
class Assignment(ASTNode):
     """Variable assignment: x = 10 (only for mutable variables)"""
     name: str
     value: ASTNode

# v0.8 - if/else statement
@dataclass
class IfStatement(ASTNode):
    """Represents an if/else statement"""
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None

# NEW: function nodes (v0.7)
@dataclass
class FunctionDeclaration(ASTNode):
     """Function declaration: branch int add(int a, int b) { ... }"""
     return_type: str 
     name: str
     params: List[tuple]
     body: List[ASTNode]

# v0.9 - for loop
@dataclass
class ForStatement(ASTNode):
    """Represents a for loop"""
    initializer: Optional[ASTNode]
    condition: Optional[ASTNode]
    increment: Optional[ASTNode]
    body: List[ASTNode]

# v0.9 extended while loop
@dataclass
class WhileStatement(ASTNode):
     """while loop: while condition {body}"""
     condition: ASTNode
     body: List[ASTNode]

@dataclass
class FunctionCall(ASTNode):
     """Function call: add(5, 3)"""
     name: str
     arguments: List[ASTNode]

@dataclass
class ReturnStatement(ASTNode):
     """Return statement: return x + 5"""
     value: Optional[ASTNode] = None

# v0.9 — Loop control AST nodes (NEW — ADD THESE)
@dataclass
class BreakStatement(ASTNode):
    """Break statement: break"""
    pass

@dataclass
class ContinueStatement(ASTNode):
    """Continue statement: continue"""
    pass

# Python exceptions used at runtime (already in your file)
class BreakException(Exception):
    """Used to break out of loops"""
    pass

class ContinueException(Exception):
    """Used to skip to next iteration"""
    pass
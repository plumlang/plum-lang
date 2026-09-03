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

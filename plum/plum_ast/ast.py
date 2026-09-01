from dataclasses import dataclass
from typing import List

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

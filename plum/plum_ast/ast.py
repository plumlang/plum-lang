from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass(kw_only=True)
class ASTNode:
    """Base class for all AST nodes, including source location."""

    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class Program(ASTNode):
    """Root node containing all statements."""
    statements: List[ASTNode]


@dataclass
class PrintStatement(ASTNode):
    """Represents drop(expression)."""
    expression: ASTNode


@dataclass
class NumberLiteral(ASTNode):
    """A number like 42 or 3.14."""
    value: float


@dataclass
class BooleanLiteral(ASTNode):
    """A boolean value: good or bad."""
    value: bool


@dataclass
class StringLiteral(ASTNode):
    """A string like hello."""
    value: str


@dataclass
class BinaryOperation(ASTNode):
    """An operation like 5 + 3."""
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class VariableDeclaration(ASTNode):
    """Variable declaration: plant int x = 5 or root int x = 5."""
    mutable: bool
    var_type: str
    name: str
    value: Optional[ASTNode] = None


@dataclass
class VariableReference(ASTNode):
    """Reference to a variable: x."""
    name: str


@dataclass
class Assignment(ASTNode):
    """Variable assignment: x = 10."""
    name: str
    value: ASTNode


@dataclass
class CompoundAssignment(ASTNode):
    """Compound assignment: x += 5, x -= 2, etc."""
    name: str
    operator: str
    value: ASTNode


@dataclass
class IfStatement(ASTNode):
    """Represents an if/else statement."""
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None


@dataclass
class FunctionDeclaration(ASTNode):
    """Function declaration: branch int add(int a, int b) { ... }."""
    return_type: str
    name: str
    params: List[tuple]
    body: List[ASTNode]


@dataclass
class ForStatement(ASTNode):
    """Represents a for loop."""
    initializer: Optional[ASTNode]
    condition: Optional[ASTNode]
    increment: Optional[ASTNode]
    body: List[ASTNode]


@dataclass
class WhileStatement(ASTNode):
    """Represents a while loop."""
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class FunctionCall(ASTNode):
    """Function call: add(5, 3)."""
    name: str
    arguments: List[ASTNode]


@dataclass
class ReturnStatement(ASTNode):
    """Return statement: return x + 5."""
    value: Optional[ASTNode] = None


@dataclass
class IncrementDecrement(ASTNode):
    """Pre/post increment or decrement: ++x, x++, --x, x--."""
    name: str
    operator: str
    is_prefix: bool


@dataclass
class UnaryOperation(ASTNode):
    """Unary operation such as -x, !x or ~x."""
    operator: str
    operand: ASTNode


@dataclass
class BreakStatement(ASTNode):
    """Break statement: break."""
    pass


@dataclass
class ContinueStatement(ASTNode):
    """Continue statement: continue."""
    pass


# Python exceptions used at runtime

class BreakException(Exception):
    """Used to break out of loops."""
    pass


class ContinueException(Exception):
    """Used to skip to the next iteration."""
    pass

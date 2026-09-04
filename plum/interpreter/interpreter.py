from plum.plum_ast import *


class Interpreter:

    def __init__(self):
        self.environment = {}  # Store all variables
        self.constants = {}    # Track which variables are constant

    def interpret(self, program: Program):
        """Execute the program"""
        for statement in program.statements:
            self._evaluate(statement)

    def _evaluate(self, node: ASTNode):
        """Evaluate an AST node and return its value"""

        # Program
        if isinstance(node, Program):
            for stmt in node.statements:
                self._evaluate(stmt)
            return None

        # Print statement
        if isinstance(node, PrintStatement):
            value = self._evaluate(node.expression)

            if isinstance(value, bool):
                print("true" if value else "false")
            else:
                print(value)

            return value
        
        # Number literal
        elif isinstance(node, NumberLiteral):
            return node.value

        # Boolean literal
        elif isinstance(node, BooleanLiteral):
            return node.value

        # String literal
        elif isinstance(node, StringLiteral):
            return node.value

        # Variable declaration (plant or root)
        elif isinstance(node, VariableDeclaration):
            value = None
            if node.value is not None:
                value = self._evaluate(node.value)
            
            # Type checking
            if node.var_type == 'int':
                if value is not None and not isinstance(value, (int, float)):
                    raise RuntimeError(
                        f"Type error: Expected int, got {type(value).__name__} "
                        f"for variable '{node.name}'"
                    )
                if value is not None:
                    value = int(value)  # Convert to int if it's a float
            elif node.var_type == 'str':
                if value is not None and not isinstance(value, str):
                    raise RuntimeError(
                        f"Type error: Expected str, got {type(value).__name__} "
                        f"for variable '{node.name}'"
                    )
            elif node.var_type == 'bool':
                if value is not None and not isinstance(value, bool):
                    raise RuntimeError(
                        f"Type error: Expected bool, got {type(value).__name__} "
                        f"for variable '{node.name}'"
                    )
            elif node.var_type == 'float':
                if value is not None and not isinstance(value, (int, float)):
                    raise RuntimeError(
                        f"Type error: Expected float, got {type(value).__name__} "
                        f"for variable '{node.name}'"
                    )
                if value is not None:
                    value = float(value)  # Convert to float
            
            # Store the variable - USE node.name, NOT node.value!
            if node.mutable:
                # plant - mutable
                self.environment[node.name] = value
            else:
                # root - immutable
                if node.name in self.constants:
                    raise RuntimeError(
                        f"Cannot redeclare constant '{node.name}'"
                    )
                self.constants[node.name] = True
                self.environment[node.name] = value
            
            return value

        # Variable reference
        elif isinstance(node, VariableReference):
            if node.name in self.environment:
                return self.environment[node.name]
            raise NameError(f"Undefined variable: '{node.name}'")

        # Variable assignment
        elif isinstance(node, Assignment):
            # Check if variable exists
            if node.name not in self.environment:
                raise NameError(f"Undefined variable: '{node.name}'")
            
            # Check if it's a constant (root)
            if node.name in self.constants:
                raise RuntimeError(
                    f"Cannot reassign constant '{node.name}'"
                )
            
            # Evaluate and assign the new value
            value = self._evaluate(node.value)
            self.environment[node.name] = value
            return value

        # Binary operation
        elif isinstance(node, BinaryOperation):
            left_val = self._evaluate(node.left)
            right_val = self._evaluate(node.right)

            # Handle all arithmetic operators
            if node.operator == '+':
                return left_val + right_val
            elif node.operator == '-':
                return left_val - right_val
            elif node.operator == '*':
                return left_val * right_val
            elif node.operator == '/':
                if right_val == 0:
                    raise RuntimeError("Division by zero!")
                return left_val / right_val
            elif node.operator == '%':
                if right_val == 0:
                    raise RuntimeError("Division by zero!")
                return left_val % right_val
            elif node.operator == '//':
                if right_val == 0:
                    raise RuntimeError("Division by zero!")
                return left_val // right_val
            elif node.operator == '**':
                return left_val ** right_val
            elif node.operator == '==':
                return left_val == right_val
            elif node.operator == '!=':
                return left_val != right_val
            elif node.operator == '>':
                return left_val > right_val
            elif node.operator == '<':
                return left_val < right_val
            elif node.operator == '>=':
                return left_val >= right_val
            elif node.operator == '<=':
                return left_val <= right_val
            else:
                raise RuntimeError(
                    f"Unknown operator: {node.operator}"
                )

        else:
            raise RuntimeError(
                f"Unknown AST node type: {type(node)}"
            )
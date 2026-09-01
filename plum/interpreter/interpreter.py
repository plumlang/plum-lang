from plum.plum_ast import *


class Interpreter:

    def interpret(self, program: Program):
        """Execute the program"""
        for statement in program.statements:
            self._evaluate(statement)

    def _evaluate(self, node: ASTNode):
        """Evaluate an AST node and return its value"""

        # Print statement
        if isinstance(node, PrintStatement):
            value = self._evaluate(node.expression)
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

        # Binary operation
        elif isinstance(node, BinaryOperation):
            left_val = self._evaluate(node.left)
            right_val = self._evaluate(node.right)

            # Handle all arithmetic operators
            if node.operator == '+':
                return left_val + right_val
            elif node.operator == '-':      # NEW: Subtraction
                return left_val - right_val
            elif node.operator == '*':      # NEW: Multiplication
                return left_val * right_val
            elif node.operator == '/':      # NEW: Division
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
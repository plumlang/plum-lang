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

        # String literal
        elif isinstance(node, StringLiteral):
            return node.value

        # Binary operation
        elif isinstance(node, BinaryOperation):
            left_val = self._evaluate(node.left)
            right_val = self._evaluate(node.right)

            if node.operator == '+':
                return left_val + right_val
            else:
                raise RuntimeError(
                    f"Unknown operator: {node.operator}"
                )

        else:
            raise RuntimeError(
                f"Unknown AST node type: {type(node)}"
            )
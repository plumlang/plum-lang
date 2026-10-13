from plum.plum_ast import *
from plum.plum_ast.ast import UnaryOperation


class BreakException(Exception):
    """Used to break out of loops"""
    pass


class ContinueException(Exception):
    """Used to skip to next iteration"""
    pass


class Interpreter:

    def __init__(self):
        self.global_env = {}      # Global variables
        self.constants = {}       # Global constants
        self.functions = {}       # Function definitions
        self.current_env = {}     # Current scope (local variables)
        self.scope_stack = []     # Stack of scopes for function calls
        self.return_value = None  # Return value from function
        self.var_types = {}       # Track declared type per variable

    def interpret(self, program: Program):
        """Execute the program"""
        for statement in program.statements:
            self._evaluate(statement)

    # ---------------------------------------------------------------
    # SCOPE HELPERS
    # ---------------------------------------------------------------
    def _push_scope(self):
        """Create a new local scope"""
        self.scope_stack.append(self.current_env)
        self.current_env = {}

    def _pop_scope(self):
        """Restore the previous scope"""
        self.current_env = self.scope_stack.pop()

    def _get_variable(self, name: str):
        """Get variable from current scope or global scope"""
        if name in self.current_env:
            return self.current_env[name]
        elif name in self.global_env:
            return self.global_env[name]
        raise NameError(f"Undefined variable: '{name}'")

    def _set_variable(self, name: str, value, is_global=True):
        """Set variable in appropriate scope"""
        if is_global:
            self.global_env[name] = value
        else:
            self.current_env[name] = value

    # ---------------------------------------------------------------
    # TYPE COERCION HELPER
    # ---------------------------------------------------------------
    def _coerce_value(self, var_type: str, value, var_name: str):
        """Type check and coerce value to declared type"""
        if value is None:
            return None

        if var_type == 'int':
            if not isinstance(value, (int, float)):
                raise RuntimeError(
                    f"Type error: Expected int, got {type(value).__name__} "
                    f"for variable '{var_name}'"
                )
            return int(value)
        elif var_type == 'str':
            if not isinstance(value, str):
                raise RuntimeError(
                    f"Type error: Expected str, got {type(value).__name__} "
                    f"for variable '{var_name}'"
                )
            return value
        elif var_type == 'bool':
            if not isinstance(value, bool):
                raise RuntimeError(
                    f"Type error: Expected bool, got {type(value).__name__} "
                    f"for variable '{var_name}'"
                )
            return value
        elif var_type == 'float':
            if not isinstance(value, (int, float)):
                raise RuntimeError(
                    f"Type error: Expected float, got {type(value).__name__} "
                    f"for variable '{var_name}'"
                )
            return float(value)
        return value

    # ---------------------------------------------------------------
    # MAIN EVALUATOR
    # ---------------------------------------------------------------
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

            # Type checking + coercion
            value = self._coerce_value(node.var_type, value, node.name)

            # Store the variable in the appropriate scope
            if node.mutable:
                # plant - mutable
                if self.current_env != {}:
                    self.current_env[node.name] = value
                else:
                    self.global_env[node.name] = value
            else:
                # root - immutable
                if node.name in self.constants:
                    raise RuntimeError(f"Cannot redeclare constant '{node.name}'")

                self.constants[node.name] = True
                if self.current_env != {}:
                    self.current_env[node.name] = value
                else:
                    self.global_env[node.name] = value

            # Remember the declared type for future assignments
            self.var_types[node.name] = node.var_type

            return value

        # Variable reference
        elif isinstance(node, VariableReference):
            return self._get_variable(node.name)

        # Variable assignment
        elif isinstance(node, Assignment):
            if node.name in self.current_env:
                if node.name in self.constants:
                    raise RuntimeError(f"Cannot reassign constant '{node.name}'")

                value = self._evaluate(node.value)
                if node.name in self.var_types:
                    value = self._coerce_value(
                        self.var_types[node.name], value, node.name
                    )
                self.current_env[node.name] = value

            elif node.name in self.global_env:
                if node.name in self.constants:
                    raise RuntimeError(f"Cannot reassign constant '{node.name}'")

                value = self._evaluate(node.value)
                if node.name in self.var_types:
                    value = self._coerce_value(
                        self.var_types[node.name], value, node.name
                    )
                self.global_env[node.name] = value
            else:
                raise NameError(f"Undefined variable: '{node.name}'")
            return None

        # Function declaration
        elif isinstance(node, FunctionDeclaration):
            self.functions[node.name] = node
            return None

        # Function call
        elif isinstance(node, FunctionCall):
            if node.name not in self.functions:
                raise NameError(f"Undefined function: '{node.name}'")

            func = self.functions[node.name]

            if len(node.arguments) != len(func.params):
                raise RuntimeError(
                    f"Function '{node.name}' expects {len(func.params)} arguments, "
                    f"got {len(node.arguments)}"
                )

            arg_values = [self._evaluate(arg) for arg in node.arguments]

            self._push_scope()

            for i, (param_type, param_name) in enumerate(func.params):
                if param_type == 'int':
                    arg = arg_values[i]
                    if not isinstance(arg, (int, float)):
                        raise RuntimeError(
                            f"Type error: Expected int for parameter '{param_name}', "
                            f"got {type(arg).__name__}"
                        )
                    self.current_env[param_name] = int(arg)
                elif param_type == 'str':
                    if not isinstance(arg_values[i], str):
                        raise RuntimeError(
                            f"Type error: Expected str for parameter '{param_name}', "
                            f"got {type(arg_values[i]).__name__}"
                        )
                    self.current_env[param_name] = arg_values[i]
                elif param_type == 'bool':
                    if not isinstance(arg_values[i], bool):
                        raise RuntimeError(
                            f"Type error: Expected bool for parameter '{param_name}', "
                            f"got {type(arg_values[i]).__name__}"
                        )
                    self.current_env[param_name] = arg_values[i]
                elif param_type == 'float':
                    arg = arg_values[i]
                    if not isinstance(arg, (int, float)):
                        raise RuntimeError(
                            f"Type error: Expected float for parameter '{param_name}', "
                            f"got {type(arg).__name__}"
                        )
                    self.current_env[param_name] = float(arg)

            # Remember parameter types in the local scope so assignments/incdec
            # inside the function keep the correct type.
            for param_type, param_name in func.params:
                self.var_types[param_name] = param_type

            try:
                for stmt in func.body:
                    self._evaluate(stmt)
                    if self.return_value is not None:
                        break
            finally:
                self._pop_scope()

            if func.return_type != 'void' and self.return_value is None:
                raise RuntimeError(
                    f"Function '{node.name}' must return a value of type '{func.return_type}'"
                )
            result = self.return_value
            self.return_value = None
            return result

        # Return statement
        elif isinstance(node, ReturnStatement):
            if node.value is not None:
                self.return_value = self._evaluate(node.value)
            else:
                self.return_value = None
            return self.return_value

        # if/else statement
        elif isinstance(node, IfStatement):
            condition = self._evaluate(node.condition)

            if condition:
                for statement in node.then_branch:
                    self._evaluate(statement)
            elif node.else_branch is not None:
                for statement in node.else_branch:
                    self._evaluate(statement)

            return None

        # for loop
        elif isinstance(node, ForStatement):
            if node.initializer is not None:
                self._evaluate(node.initializer)

            while node.condition is not None and self._evaluate(node.condition):
                try:
                    for statement in node.body:
                        self._evaluate(statement)
                        if self.return_value is not None:
                            return self.return_value
                except BreakException:
                    break
                except ContinueException:
                    pass  # fall through to the increment

                if node.increment is not None:
                    self._evaluate(node.increment)

            return None

        # while loop
        elif isinstance(node, WhileStatement):
            res = None
            while True:
                condition_value = self._evaluate(node.condition)

                if not isinstance(condition_value, bool):
                    if condition_value == 0 or condition_value == "" or condition_value is None:
                        break
                elif not condition_value:
                    break

                try:
                    for stmt in node.body:
                        self._evaluate(stmt)
                        if self.return_value is not None:
                            return self.return_value
                except BreakException:
                    break
                except ContinueException:
                    continue
            return res

        # break
        elif isinstance(node, BreakStatement):
            raise BreakException()

        # continue
        elif isinstance(node, ContinueStatement):
            raise ContinueException()

        # NEW: Pre/post increment & decrement
        elif isinstance(node, IncrementDecrement):
            # Find scope
            if node.name in self.current_env:
                scope = self.current_env
            elif node.name in self.global_env:
                scope = self.global_env
            else:
                raise NameError(f"Undefined variable: '{node.name}'")

            # Prevent modifying constants
            if node.name in self.constants:
                raise RuntimeError(f"Cannot modify constant '{node.name}'")

            old_value = scope[node.name]

            if node.operator == '++':
                new_value = old_value + 1
            elif node.operator == '--':
                new_value = old_value - 1
            else:
                raise RuntimeError(f"Unknown increment operator: {node.operator}")

            # Re-apply declared type
            if node.name in self.var_types:
                new_value = self._coerce_value(
                    self.var_types[node.name], new_value, node.name
                )

            scope[node.name] = new_value

            # Prefix returns new, postfix returns old
            return new_value if node.is_prefix else old_value

        # Unary operations: arithmetic, logical, and bitwise
        elif isinstance(node, UnaryOperation):
            operand = self._evaluate(node.operand)

            if node.operator == '-':
                return -operand
            elif node.operator == '!':
                return not bool(operand)

            elif node.operator == '~':
                if (
                    isinstance(operand, bool)
                    or not isinstance(operand, (int, float))
                    or int(operand) != operand
                ):
                    raise RuntimeError(
                        "Operator '~' requires an integer operand"
                    )
                return ~int(operand)

            else:
                raise RuntimeError(
                    f"Unknown unary operator: {node.operator}"
                )

        
        # Binary operation
        elif isinstance(node, BinaryOperation):
            left_val = self._evaluate(node.left)
            right_val = self._evaluate(node.right)

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
            

            # Bitwise operators require whole-number operands
            elif node.operator in ('&', '|', '^'):
                if (
                    isinstance(left_val, bool)
                    or isinstance(right_val, bool)
                    or not isinstance(left_val, (int, float))
                    or not isinstance(right_val, (int, float))
                    or int(left_val) != left_val
                    or int(right_val) != right_val
                ):
                    raise RuntimeError(
                        f"Operator '{node.operator}' requires integer operands"
                    )

                left_val = int(left_val)
                right_val = int(right_val)

                if node.operator == '&':
                    return left_val & right_val
                elif node.operator == '|':
                    return left_val | right_val
                else:
                    return left_val ^ right_val

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
            elif node.operator == '&&':
                return bool(left_val) and bool(right_val)
            elif node.operator == '||':
                return bool(left_val) or bool(right_val)
            else:
                raise RuntimeError(f"Unknown operator: {node.operator}")

        else:
            raise RuntimeError(f"Unknown AST node type: {type(node)}")
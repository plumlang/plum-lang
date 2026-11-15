from plum.plum_ast import *
from plum.plum_ast.ast import UnaryOperation


class BreakException(Exception):
    """Used to break out of loops."""


class ContinueException(Exception):
    """Used to skip to the next loop iteration."""


class ReturnException(Exception):
    """Internal control-flow signal for returning from a function."""

    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self):
        self.global_env = {}
        self.global_types = {}
        self.global_constants = set()

        self.functions = {}

        self.current_env = {}
        self.current_types = {}
        self.current_constants = set()
        self.scope_stack = []

        # Kept for compatibility with code that may inspect this attribute.
        self.var_types = self.global_types

    def interpret(self, program: Program):
        """Execute a Plum program."""
        for statement in program.statements:
            self._evaluate(statement)

    # ---------------------------------------------------------------
    # SCOPE HELPERS
    # ---------------------------------------------------------------
    def _push_scope(self):
        self.scope_stack.append(
            (self.current_env, self.current_types, self.current_constants)
        )
        self.current_env = {}
        self.current_types = {}
        self.current_constants = set()

    def _pop_scope(self):
        self.current_env, self.current_types, self.current_constants = (
            self.scope_stack.pop()
        )

    def _find_scope(self, name):
        """Return the environment and type metadata owning a variable."""
        if name in self.current_env:
            return self.current_env, self.current_types, self.current_constants

        if name in self.global_env:
            return self.global_env, self.global_types, self.global_constants

        raise NameError(f"Undefined variable: '{name}'")

    def _get_variable(self, name: str):
        scope, _, _ = self._find_scope(name)
        return scope[name]

    # ---------------------------------------------------------------
    # TYPE CONVERSION
    # ---------------------------------------------------------------
    def _coerce_value(self, var_type: str, value, var_name: str):
        """
        Apply Plum's controlled implicit conversions.

        Allowed:
            int -> float

        Rejected:
            float -> int, bool -> int, int -> bool,
            bool -> float, and string/numeric conversions.
        """
        if value is None:
            return None

        actual_type = type(value)

        if var_type == "int":
            if actual_type is not int:
                raise RuntimeError(
                    f"Type error: Expected int, got {actual_type.__name__} "
                    f"for '{var_name}'"
                )
            return value

        if var_type == "float":
            if actual_type is int:
                return float(value)
            if actual_type is float:
                return value
            raise RuntimeError(
                f"Type error: Expected float, got {actual_type.__name__} "
                f"for '{var_name}'"
            )

        if var_type == "bool":
            if actual_type is not bool:
                raise RuntimeError(
                    f"Type error: Expected bool, got {actual_type.__name__} "
                    f"for '{var_name}'"
                )
            return value

        if var_type == "str":
            if actual_type is not str:
                raise RuntimeError(
                    f"Type error: Expected str, got {actual_type.__name__} "
                    f"for '{var_name}'"
                )
            return value

        # Unknown/user-defined types are left unchanged for now.
        return value

    def _declare_variable(self, node, value):
        """Declare a variable globally or in the active function scope."""
        # An empty local environment is still a local scope. scope_stack tells
        # us whether execution is currently inside a function call.
        if self.scope_stack:
            scope = self.current_env
            types = self.current_types
            constants = self.current_constants
        else:
            scope = self.global_env
            types = self.global_types
            constants = self.global_constants

        # Local variables may shadow globals, but cannot be redeclared in
        # the same scope.
        if node.name in scope:
            raise RuntimeError(f"Variable '{node.name}' is already declared")

        scope[node.name] = value
        types[node.name] = node.var_type

        if not node.mutable:
            constants.add(node.name)

    # ---------------------------------------------------------------
    # EXPRESSION HELPERS
    # ---------------------------------------------------------------
    @staticmethod
    def _is_number(value):
        return type(value) in (int, float)

    @staticmethod
    def _is_integer(value):
        return type(value) is int

    def _binary_type_error(self, operator, left, right):
        raise RuntimeError(
            f"Type error: Operator '{operator}' is not supported for "
            f"{type(left).__name__} and {type(right).__name__}"
        )

    def _apply_binary_operator(self, operator, left, right):
        """Evaluate a non-logical binary operation with Plum errors."""
        try:
            if operator == "+":
                return left + right
            if operator == "-":
                return left - right
            if operator == "*":
                return left * right
            if operator == "/":
                if right == 0:
                    raise RuntimeError("Division by zero!")
                return left / right
            if operator == "%":
                if right == 0:
                    raise RuntimeError("Division by zero!")
                return left % right
            if operator == "//":
                if right == 0:
                    raise RuntimeError("Division by zero!")
                return left // right
            if operator == "**":
                return left ** right

            if operator in ("&", "|", "^", "<<", ">>"):
                if not self._is_integer(left) or not self._is_integer(right):
                    raise RuntimeError(
                        f"Operator '{operator}' requires integer operands"
                    )
                if operator in ("<<", ">>") and right < 0:
                    raise RuntimeError("Shift count cannot be negative")
                if operator == "&":
                    return left & right
                if operator == "|":
                    return left | right
                if operator == "^":
                    return left ^ right
                if operator == "<<":
                    return left << right
                return left >> right

            if operator == "==":
                return left == right
            if operator == "!=":
                return left != right
            if operator == ">":
                return left > right
            if operator == "<":
                return left < right
            if operator == ">=":
                return left >= right
            if operator == "<=":
                return left <= right

        except TypeError as exc:
            self._binary_type_error(operator, left, right)

        raise RuntimeError(f"Unknown operator: {operator}")

    # ---------------------------------------------------------------
    # MAIN EVALUATOR
    # ---------------------------------------------------------------
    def _evaluate(self, node: ASTNode):
        if isinstance(node, Program):
            for statement in node.statements:
                self._evaluate(statement)
            return None

        if isinstance(node, PrintStatement):
            value = self._evaluate(node.expression)
            if type(value) is bool:
                print("true" if value else "false")
            else:
                print(value)
            return value

        if isinstance(node, NumberLiteral):
            return node.value

        if isinstance(node, BooleanLiteral):
            return node.value

        if isinstance(node, StringLiteral):
            return node.value

        # Variable declaration
        if isinstance(node, VariableDeclaration):
            value = None
            if node.value is not None:
                value = self._evaluate(node.value)

            value = self._coerce_value(node.var_type, value, node.name)
            self._declare_variable(node, value)
            return value

        # Variable reference
        if isinstance(node, VariableReference):
            return self._get_variable(node.name)

        # Assignment
        if isinstance(node, Assignment):
            scope, types, constants = self._find_scope(node.name)
            if node.name in constants:
                raise RuntimeError(f"Cannot reassign constant '{node.name}'")

            value = self._evaluate(node.value)
            if node.name in types:
                value = self._coerce_value(types[node.name], value, node.name)
            scope[node.name] = value
            return None

        # Compound assignment
        if isinstance(node, CompoundAssignment):
            scope, types, constants = self._find_scope(node.name)
            if node.name in constants:
                raise RuntimeError(f"Cannot reassign constant '{node.name}'")

            old_value = scope[node.name]
            right_value = self._evaluate(node.value)

            operators = {
                "+=": "+",
                "-=": "-",
                "*=": "*",
                "/=": "/",
                "%=": "%",
            }
            if node.operator not in operators:
                raise RuntimeError(
                    f"Unsupported compound assignment: '{node.operator}'"
                )

            new_value = self._apply_binary_operator(
                operators[node.operator], old_value, right_value
            )
            if node.name in types:
                new_value = self._coerce_value(
                    types[node.name], new_value, node.name
                )
            scope[node.name] = new_value
            return None

        # Function declaration
        if isinstance(node, FunctionDeclaration):
            self.functions[node.name] = node
            return None

        # Function call
        if isinstance(node, FunctionCall):
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
            result = None
            try:
                for (param_type, param_name), arg in zip(func.params, arg_values):
                    self.current_env[param_name] = self._coerce_value(
                        param_type, arg, f"parameter '{param_name}'"
                    )
                    self.current_types[param_name] = param_type

                try:
                    for statement in func.body:
                        self._evaluate(statement)
                except ReturnException as returned:
                    result = returned.value

            finally:
                self._pop_scope()

            if func.return_type == "void":
                if result is not None:
                    raise RuntimeError(
                        f"Void function '{node.name}' cannot return a value"
                    )
                return None

            if result is None:
                raise RuntimeError(
                    f"Function '{node.name}' must return a value of type "
                    f"'{func.return_type}'"
                )

            return self._coerce_value(
                func.return_type, result, f"return value of function '{node.name}'"
            )

        # Return statement
        if isinstance(node, ReturnStatement):
            value = None
            if node.value is not None:
                value = self._evaluate(node.value)
            raise ReturnException(value)

        # If / else
        if isinstance(node, IfStatement):
            condition = self._evaluate(node.condition)
            branch = node.then_branch if condition else node.else_branch
            if branch is not None:
                for statement in branch:
                    self._evaluate(statement)
            return None

        # For loop
        if isinstance(node, ForStatement):
            if node.initializer is not None:
                self._evaluate(node.initializer)

            while (
                node.condition is not None
                and bool(self._evaluate(node.condition))
            ):
                try:
                    for statement in node.body:
                        self._evaluate(statement)
                except BreakException:
                    break
                except ContinueException:
                    pass

                if node.increment is not None:
                    self._evaluate(node.increment)
            return None

        # While loop
        if isinstance(node, WhileStatement):
            while bool(self._evaluate(node.condition)):
                try:
                    for statement in node.body:
                        self._evaluate(statement)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None

        if isinstance(node, BreakStatement):
            raise BreakException()

        if isinstance(node, ContinueStatement):
            raise ContinueException()

        # Increment / decrement
        if isinstance(node, IncrementDecrement):
            scope, types, constants = self._find_scope(node.name)
            if node.name in constants:
                raise RuntimeError(f"Cannot modify constant '{node.name}'")

            old_value = scope[node.name]
            if type(old_value) not in (int, float):
                raise RuntimeError(
                    f"Type error: Operator '{node.operator}' requires a numeric variable"
                )

            if node.operator == "++":
                new_value = old_value + 1
            elif node.operator == "--":
                new_value = old_value - 1
            else:
                raise RuntimeError(
                    f"Unknown increment operator: {node.operator}"
                )

            if node.name in types:
                new_value = self._coerce_value(types[node.name], new_value, node.name)

            scope[node.name] = new_value
            return new_value if node.is_prefix else old_value

        # Unary operations
        if isinstance(node, UnaryOperation):
            operand = self._evaluate(node.operand)

            if node.operator == "-":
                if type(operand) not in (int, float):
                    raise RuntimeError("Unary '-' requires a numeric operand")
                return -operand

            if node.operator == "!":
                return not bool(operand)

            if node.operator == "~":
                if type(operand) is not int:
                    raise RuntimeError(
                        "Operator '~' requires an integer operand"
                    )
                return ~operand

            raise RuntimeError(f"Unknown unary operator: {node.operator}")

        # Binary operations. Logical operators must short-circuit.
        if isinstance(node, BinaryOperation):
            left_val = self._evaluate(node.left)

            if node.operator == "&&":
                if not bool(left_val):
                    return False
                return bool(self._evaluate(node.right))

            if node.operator == "||":
                if bool(left_val):
                    return True
                return bool(self._evaluate(node.right))

            right_val = self._evaluate(node.right)
            return self._apply_binary_operator(
                node.operator, left_val, right_val
            )

        raise RuntimeError(f"Unknown AST node type: {type(node).__name__}")

from plum.plum_ast import *
from plum.plum_ast.ast import UnaryOperation
from plum.interpreter.errors import PlumRuntimeError, PlumNameError


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

        # Control-flow state is isolated at function boundaries.
        self.loop_depth = 0
        self.function_depth = 0

        # Kept for compatibility with code that may inspect this attribute.
        self.var_types = self.global_types

    def interpret(self, program: Program):
        """Execute a Plum program."""
        for statement in program.statements:
            self._evaluate(statement)

    # ---------------------------------------------------------------
    # SCOPE HELPERS
    # ---------------------------------------------------------------

    def _push_scope(self, scope_type="function"):
        self.scope_stack.append(
        (
            self.current_env,
            self.current_types,
            self.current_constants,
            scope_type,
        )
        )

        self.current_env = {}
        self.current_types = {}
        self.current_constants = set()


    def _pop_scope(self):
        (
        self.current_env,
        self.current_types,
        self.current_constants,
        _,
        ) = self.scope_stack.pop()


    def _find_scope(self, name: str, node=None):
        """Find a variable in the current and enclosing scopes."""

        if name in self.current_env:
            return (
            self.current_env,
            self.current_types,
            self.current_constants,
            )

        # Search enclosing loop scopes, but never cross a function boundary.
        for env, types, constants, scope_type in reversed(self.scope_stack):
            if scope_type == "function":
                break

            if name in env:
                return env, types, constants

        if name in self.global_env:
            return (
            self.global_env,
            self.global_types,
            self.global_constants,
            )

        raise PlumNameError(
            f"Undefined variable: '{name}'",
            node,
        )

    def _get_variable(self, name: str, node=None):
        scope, _, _ = self._find_scope(name, node)
        return scope[name]

    # ---------------------------------------------------------------
    # TYPE CONVERSION
    # ---------------------------------------------------------------

    def _coerce_value(self, var_type: str, value, var_name: str, node=None):
        """
        Apply Plum's controlled implicit conversions.

        Allowed:
            int -> float

        Rejected:
            float -> int
            bool -> int
            int -> bool
            bool -> float
            string/numeric conversions
        """

        if value is None:
            return None

        actual_type = type(value)

        if var_type == "int":
            if actual_type is not int:
                raise PlumRuntimeError(
                    f"Type error: Expected int, got {actual_type.__name__} "
                    f"for '{var_name}'",
                    node
                )

            return value

        if var_type == "float":
            if actual_type is int:
                return float(value)

            if actual_type is float:
                return value

            raise PlumRuntimeError(
                f"Type error: Expected float, got {actual_type.__name__} "
                f"for '{var_name}'",
                node
            )

        if var_type == "bool":
            if actual_type is not bool:
                raise PlumRuntimeError(
                    f"Type error: Expected bool, got {actual_type.__name__} "
                    f"for '{var_name}'",
                    node
                )

            return value

        if var_type == "str":
            if actual_type is not str:
                raise PlumRuntimeError(
                    f"Type error: Expected str, got {actual_type.__name__} "
                    f"for '{var_name}'",
                    node
                )

            return value

        # Unknown/user-defined types are left unchanged for now.
        return value

    def _declare_variable(self, node, value):
        """Declare a variable globally or in the active function scope."""

        # An empty local environment is still a local scope.
        # scope_stack tells us whether we are inside a function call.
        if self.scope_stack:
            scope = self.current_env
            types = self.current_types
            constants = self.current_constants
        else:
            scope = self.global_env
            types = self.global_types
            constants = self.global_constants

        # Variables cannot be redeclared in the same scope.
        if node.name in scope:
            raise PlumRuntimeError(
                f"Variable '{node.name}' is already declared",
                node
            )

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

    def _binary_type_error(self, operator, left, right, node=None):
        raise PlumRuntimeError(
            f"Type error: Operator '{operator}' is not supported for "
            f"{type(left).__name__} and {type(right).__name__}",
            node
        )

    def _apply_binary_operator(self, operator, left, right, node=None):
        """Evaluate a non-logical binary operation."""

        try:
            if operator == "+":
                return left + right

            if operator == "-":
                return left - right

            if operator == "*":
                return left * right

            if operator == "/":
                if right == 0:
                    raise PlumRuntimeError("Division by zero", node)

                return left / right

            if operator == "%":
                if right == 0:
                    raise PlumRuntimeError("Division by zero", node)

                return left % right

            if operator == "//":
                if right == 0:
                    raise PlumRuntimeError("Division by zero", node)

                return left // right

            if operator == "**":
                return left ** right

            if operator in ("&", "|", "^", "<<", ">>"):

                if not self._is_integer(left) or not self._is_integer(right):
                    raise PlumRuntimeError(
                        f"Operator '{operator}' requires integer operands",
                        node
                    )

                if operator in ("<<", ">>") and right < 0:
                    raise PlumRuntimeError(
                        "Shift count cannot be negative",
                        node
                    )

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

        except PlumRuntimeError:
            raise

        except TypeError:
            self._binary_type_error(operator, left, right, node)

        raise PlumRuntimeError(
            f"Unknown operator: {operator}",
            node
        )

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

        # Literals
        if isinstance(node, NumberLiteral):
            return node.value

        if isinstance(node, BooleanLiteral):
            return node.value

        if isinstance(node, StringLiteral):
            return node.value

        # -----------------------------------------------------------
        # VARIABLE DECLARATION
        # -----------------------------------------------------------

        if isinstance(node, VariableDeclaration):
            value = None

            if node.value is not None:
                value = self._evaluate(node.value)

            value = self._coerce_value(
                node.var_type,
                value,
                node.name,
                node
            )

            self._declare_variable(node, value)

            return value

        # -----------------------------------------------------------
        # VARIABLE REFERENCE
        # -----------------------------------------------------------

        if isinstance(node, VariableReference):
            return self._get_variable(node.name, node)

        # -----------------------------------------------------------
        # ASSIGNMENT
        # -----------------------------------------------------------

        if isinstance(node, Assignment):
            scope, types, constants = self._find_scope(
                node.name,
                node
            )

            if node.name in constants:
                raise PlumRuntimeError(
                    f"Cannot reassign constant '{node.name}'",
                    node
                )

            value = self._evaluate(node.value)

            if node.name in types:
                value = self._coerce_value(
                    types[node.name],
                    value,
                    node.name,
                    node
                )

            scope[node.name] = value

            return None

        # -----------------------------------------------------------
        # COMPOUND ASSIGNMENT
        # -----------------------------------------------------------

        if isinstance(node, CompoundAssignment):
            scope, types, constants = self._find_scope(
                node.name,
                node
            )

            if node.name in constants:
                raise PlumRuntimeError(
                    f"Cannot reassign constant '{node.name}'",
                    node
                )

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
                raise PlumRuntimeError(
                    f"Unsupported compound assignment: '{node.operator}'",
                    node
                )

            new_value = self._apply_binary_operator(
                operators[node.operator],
                old_value,
                right_value,
                node
            )

            if node.name in types:
                new_value = self._coerce_value(
                    types[node.name],
                    new_value,
                    node.name,
                    node
                )

            scope[node.name] = new_value

            return None

        # -----------------------------------------------------------
        # FUNCTION DECLARATION
        # -----------------------------------------------------------

        if isinstance(node, FunctionDeclaration):
            self.functions[node.name] = node
            return None

        # -----------------------------------------------------------
        # FUNCTION CALL
        # -----------------------------------------------------------

        if isinstance(node, FunctionCall):

            if node.name not in self.functions:
                raise PlumNameError(
                    f"Undefined function: '{node.name}'",
                    node
                )

            func = self.functions[node.name]

            if len(node.arguments) != len(func.params):
                raise PlumRuntimeError(
                    f"Function '{node.name}' expects "
                    f"{len(func.params)} arguments, "
                    f"got {len(node.arguments)}",
                    node
                )

            arg_values = [
                self._evaluate(arg)
                for arg in node.arguments
            ]

            # A function must not inherit the caller's active loops.
            # Its own loops can still use break and continue normally.
            caller_loop_depth = self.loop_depth
            self.loop_depth = 0
            self.function_depth += 1
            self._push_scope()

            result = None

            try:
                for (param_type, param_name), arg in zip(
                    func.params,
                    arg_values
                ):
                    self.current_env[param_name] = self._coerce_value(
                        param_type,
                        arg,
                        f"parameter '{param_name}'",
                        node
                    )

                    self.current_types[param_name] = param_type

                try:
                    for statement in func.body:
                        self._evaluate(statement)

                except ReturnException as returned:
                    result = returned.value

            finally:
                self._pop_scope()
                self.function_depth -= 1
                self.loop_depth = caller_loop_depth

            if func.return_type == "void":

                if result is not None:
                    raise PlumRuntimeError(
                        f"Void function '{node.name}' cannot return a value",
                        node
                    )

                return None

            if result is None:
                raise PlumRuntimeError(
                    f"Function '{node.name}' must return a value of type "
                    f"'{func.return_type}'",
                    node
                )

            return self._coerce_value(
                func.return_type,
                result,
                f"return value of function '{node.name}'",
                node
            )

        # -----------------------------------------------------------
        # RETURN STATEMENT
        # -----------------------------------------------------------

        if isinstance(node, ReturnStatement):
            if self.function_depth == 0:
                raise PlumRuntimeError(
                    "Return statement outside function",
                    node
                )

            value = None

            if node.value is not None:
                value = self._evaluate(node.value)

            raise ReturnException(value)

        # -----------------------------------------------------------
        # IF / ELSE
        # -----------------------------------------------------------

        if isinstance(node, IfStatement):
            condition = self._evaluate(node.condition)

            branch = (
                node.then_branch
                if condition
                else node.else_branch
            )

            if branch is not None:
                # Each executed branch gets its own lexical block scope.
                # Outer variables remain visible through _find_scope().
                self._push_scope("block")
                try:
                    for statement in branch:
                        self._evaluate(statement)
                finally:
                    self._pop_scope()

            return None

        # -----------------------------------------------------------
        # FOR LOOP
        # -----------------------------------------------------------

        if isinstance(node, ForStatement):
            self._push_scope("loop")
            self.loop_depth += 1

            try:
                if node.initializer is not None:
                    self._evaluate(node.initializer)

                while (
                    node.condition is None
                    or bool(self._evaluate(node.condition))
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

            finally:
                self.loop_depth -= 1
                self._pop_scope()

        # -----------------------------------------------------------
        # WHILE LOOP
        # -----------------------------------------------------------

        if isinstance(node, WhileStatement):
            self._push_scope("loop")
            self.loop_depth += 1

            try:
                while bool(self._evaluate(node.condition)):
                    try:
                        for statement in node.body:
                            self._evaluate(statement)

                    except BreakException:
                        break

                    except ContinueException:
                        continue

                return None

            finally:
                self.loop_depth -= 1
                self._pop_scope()

        # -----------------------------------------------------------
        # BREAK / CONTINUE
        # -----------------------------------------------------------

        if isinstance(node, BreakStatement):
            if self.loop_depth == 0:
                raise PlumRuntimeError(
                    "Break statement outside loop",
                    node
                )

            raise BreakException()

        if isinstance(node, ContinueStatement):
            if self.loop_depth == 0:
                raise PlumRuntimeError(
                    "Continue statement outside loop",
                    node
                )

            raise ContinueException()

        # -----------------------------------------------------------
        # INCREMENT / DECREMENT
        # -----------------------------------------------------------

        if isinstance(node, IncrementDecrement):
            scope, types, constants = self._find_scope(
                node.name,
                node
            )

            if node.name in constants:
                raise PlumRuntimeError(
                    f"Cannot modify constant '{node.name}'",
                    node
                )

            old_value = scope[node.name]

            if type(old_value) not in (int, float):
                raise PlumRuntimeError(
                    f"Type error: Operator '{node.operator}' "
                    f"requires a numeric variable",
                    node
                )

            if node.operator == "++":
                new_value = old_value + 1

            elif node.operator == "--":
                new_value = old_value - 1

            else:
                raise PlumRuntimeError(
                    f"Unknown increment operator: {node.operator}",
                    node
                )

            if node.name in types:
                new_value = self._coerce_value(
                    types[node.name],
                    new_value,
                    node.name,
                    node
                )

            scope[node.name] = new_value

            return new_value if node.is_prefix else old_value

        # -----------------------------------------------------------
        # UNARY OPERATIONS
        # -----------------------------------------------------------

        if isinstance(node, UnaryOperation):
            operand = self._evaluate(node.operand)

            if node.operator == "-":

                if type(operand) not in (int, float):
                    raise PlumRuntimeError(
                        "Unary '-' requires a numeric operand",
                        node
                    )

                return -operand

            if node.operator == "!":
                return not bool(operand)

            if node.operator == "~":

                if type(operand) is not int:
                    raise PlumRuntimeError(
                        "Operator '~' requires an integer operand",
                        node
                    )

                return ~operand

            raise PlumRuntimeError(
                f"Unknown unary operator: {node.operator}",
                node
            )

        # -----------------------------------------------------------
        # BINARY OPERATIONS
        # -----------------------------------------------------------

        if isinstance(node, BinaryOperation):
            left_val = self._evaluate(node.left)

            # Logical operators must short-circuit.
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
                node.operator,
                left_val,
                right_val,
                node
            )

        # -----------------------------------------------------------
        # UNKNOWN AST NODE
        # -----------------------------------------------------------

        raise PlumRuntimeError(
            f"Unknown AST node type: {type(node).__name__}",
            node
        )
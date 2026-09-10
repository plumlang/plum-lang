from plum.plum_ast import *


class Interpreter:

    def __init__(self):
        self.global_env = {}      # Global variables
        self.constants = {}       # Global constants
        self.functions = {}       # Function definitions
        self.current_env = {}     # Current scope (local variables)
        self.scope_stack = []     # Stack of scopes for function calls
        self.return_value = None  # Return value from function

    def interpret(self, program: Program):
        """Execute the program"""
        for statement in program.statements:
            self._evaluate(statement)

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
    
    def _set_varibale(self, name: str, value, is_global=True):
        """Set variable in appropriate scope"""
        if is_global:
            self.global_env[name] = value
        else:
            self.current_env[name] = value



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
            
            # Store the variable in the appropriate scope
            if node.mutable:
                # plant - mutable
                if self.current_env != {}:
                   #Inside a func - local
                   self.current_env[node.name] = value
                else:
                    #globsl scope
                    self.global_env[node.name] = value
            else:
                # root - immutable
                if node.name in self.constants:
                    raise RuntimeError(f"Cannot redeclare constant '{node.name}'")
                
                self.constants[node.name] = True
                if self.current_env != {}:
                    #inside a func - local constant
                   self.current_env[node.name] = value
                else:
                    self.global_env[node.name] = value
            
            return value

        # Variable reference
        elif isinstance(node, VariableReference):
           return self._get_variable(node.name)

        # Variable assignment
        elif isinstance(node, Assignment):
            # Check if variable exists in current scope or global
            if node.name in self.current_env:
                # Check if it's a constant in current scope
                # Constants are tracked in self.constants globally
                if node.name in self.constants:
                   raise RuntimeError(f"Cannot reassign constant '{node.name}'")
                self.current_env[node.name] = self._evaluate(node.value)
            elif node.name in self.global_env:
                # check if it's a constant
                if node.name in self.constants:
                    raise RuntimeError(f"Cannot reassign constant '{node.name}'")
                self.global_env[node.name] = self._evaluate(node.value)
            else:
                raise NameError(f"Undefined variable: '{node.name}'")
            return None
        
        # new v0.7 func declaration
        elif isinstance(node, FunctionDeclaration):
            self.functions[node.name] = node
            return None

        elif isinstance(node, FunctionCall):
            if node.name not in self.functions:
                raise NameError(f"Undefined function: '{node.name}'")
            
            func = self.functions[node.name]

            # eval args 
            if len(node.arguments) != len(func.params):
                raise RuntimeError(
                    f"Function '{node.name}' expects {len(func.params)} arguments, "
                    f"got {len(node.arguments)}"
                )

            arg_values = [self._evaluate(arg) for arg in node.arguments]

            # push new scope for func
            self._push_scope()

            # Bind parameters to local variable
            for i, (param_type, param_name) in enumerate(func.params):
                # Type check args
                if param_type == 'int':
                    if not isinstance(arg_values[i], (int, float)):
                        raise RuntimeError(
                            f"Type error: Expected int for parameter '{param_name}', "
                            f"got {type(arg_values[i]).__name__}"
                        )
                    self.current_env[param_name] = int(arg_values[i])
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
                    if not isinstance(arg_values[i], (int, float)):
                        raise RuntimeError(
                            f"Type error: Expected float for parameter '{param_name}', "
                            f"got {type(arg_values[i]).__name__}"
                        )
                    self.current_env[param_name] = float(arg_values[i])
                
                self.return_value = None
            try:
                for stmt in func.body:
                    self._evaluate(stmt)
                    if self.return_value is not None:
                        break
            finally:
                    # pop scopesel
                    self._pop_scope()
                
            # Check return type
            if func.return_type != 'void' and self.return_value is None:
                raise RuntimeError(
                f"Function '{node.name}' must return a value of type '{func.return_type}'"
                )
            result = self.return_value
            self.return_value = None
            return result
        

        # New Return statement
        elif isinstance(node, ReturnStatement):
            if node.value is not None:
               self.return_value = self._evaluate(node.value)
            else:
                self.return_value = None
            return self.return_value
    
                # v0.8 - if/else statement
        elif isinstance(node, IfStatement):
            condition = self._evaluate(node.condition)

            if condition:
                for statement in node.then_branch:
                    self._evaluate(statement)
            elif node.else_branch is not None:
                for statement in node.else_branch:
                    self._evaluate(statement)

            return None
        
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

            # v0.9 - Logical operators
            elif node.operator == 'and':
                return left_val and right_val
            elif node.operator == 'or':
                return left_val or right_val

            else:
                raise RuntimeError(
                    f"Unknown operator: {node.operator}"
                )

                # v0.9 - Logical NOT
        elif isinstance(node, UnaryOperation):
            operand = self._evaluate(node.operand)

            if node.operator == "not":
                return not operand

            raise RuntimeError(
                f"Unknown unary operator: {node.operator}"
            )
        
        else:
            raise RuntimeError(
                f"Unknown AST node type: {type(node)}"
            )
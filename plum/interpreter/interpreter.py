from plum.plum_ast import *




class Interpreter:

    def __init__(self):
        self.global_env = {}      # Global variables
        self.constants = {}       # Global constants
        self.functions = {}       # Function definitions
        self.current_env = {}     # Current scope (local variables)
        self.scope_stack = []     # Stack of scopes for function calls
        self.return_value = None  # Return value from function
        self.var_types = {}       # Track declared type per variable (NEW)

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

    def _coerce_value(self, var_type: str, value, var_name: str):
        """Type check and coerce value to declared type (NEW helper)"""
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
                    # Inside a func - local
                    self.current_env[node.name] = value
                else:
                    # global scope
                    self.global_env[node.name] = value
            else:
                # root - immutable
                if node.name in self.constants:
                    raise RuntimeError(f"Cannot redeclare constant '{node.name}'")
                
                self.constants[node.name] = True
                if self.current_env != {}:
                    # inside a func - local constant
                    self.current_env[node.name] = value
                else:
                    self.global_env[node.name] = value
            
            # NEW: Remember the declared type for future assignments
            self.var_types[node.name] = node.var_type
            
            return value

        # Variable reference
        elif isinstance(node, VariableReference):
           return self._get_variable(node.name)

        # Variable assignment
        elif isinstance(node, Assignment):
            # Check if variable exists in current scope or global
            if node.name in self.current_env:
                # Check if it's a constant
                if node.name in self.constants:
                    raise RuntimeError(f"Cannot reassign constant '{node.name}'")
                
                # Evaluate and re-apply type
                value = self._evaluate(node.value)
                if node.name in self.var_types:
                    value = self._coerce_value(
                        self.var_types[node.name], value, node.name
                    )
                self.current_env[node.name] = value
                
            elif node.name in self.global_env:
                # Check if it's a constant
                if node.name in self.constants:
                    raise RuntimeError(f"Cannot reassign constant '{node.name}'")
                
                # Evaluate and re-apply type
                value = self._evaluate(node.value)
                if node.name in self.var_types:
                    value = self._coerce_value(
                        self.var_types[node.name], value, node.name
                    )
                self.global_env[node.name] = value
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
            try:
                for stmt in func.body:
                    self._evaluate(stmt)
                    if self.return_value is not None:
                        break
            finally:
                    # pop scope
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

        # v0.9 - for loop
        elif isinstance(node, ForStatement):
            # Initialize loop variable
            if node.initializer is not None:
                self._evaluate(node.initializer)

            # Run while condition is true
            while node.condition is not None and self._evaluate(node.condition):
                for statement in node.body:
                    self._evaluate(statement)

                # Increment loop variable
                if node.increment is not None:
                    self._evaluate(node.increment)

            return None
        
        # v0.9 extended
        elif isinstance(node, WhileStatement):
            """Execute a while loop"""
            res = None
            while True:
                # eval condition 
                condition_value = self._evaluate(node.condition)

                # Convert to boolean if needed 
                if not isinstance(condition_value, bool):
                   # For non-boolean values, check truthiness
                    if condition_value == 0 or condition_value == "" or condition_value is None:
                        break
                elif not condition_value:
                    break

                # execute body 
                try:
                    for stmt in node.body:
                        self._evaluate(stmt)
                        # check for return value (inside func)
                        if self.return_value is not None:
                            return self.return_value
                except BreakException:
                    break
                except ContinueException:
                    continue
            return res
                
        elif isinstance(node, BreakStatement):
            raise BreakException()

        elif isinstance(node, ContinueStatement):
            raise ContinueException()       

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
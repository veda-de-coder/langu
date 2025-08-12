from nodes import *
from environment import Environment

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class RuntimeError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ObjectInstance:
    def __init__(self, class_name, class_def=None):
        self.class_name = class_name
        self.properties = {}
        self.methods = {}
        self.class_def = class_def
    
    def get_property(self, name):
        if name in self.properties:
            return self.properties[name]
        if name in self.methods:
            return self.methods[name]
        return None
    
    def set_property(self, name, value):
        self.properties[name] = value
    
    def add_method(self, name, method):
        self.methods[name] = method
    
    def has_method(self, name):
        return name in self.methods

class Method:
    def __init__(self, name, parameters, body, closure_env):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure_env = closure_env
    
    def call(self, interpreter, arguments, instance=None):
        if len(arguments) != len(self.parameters):
            raise RuntimeError(f"Method {self.name} expects {len(self.parameters)} arguments, got {len(arguments)}")
        
        method_env = Environment(self.closure_env)
        
        if instance:
            method_env.set("this", instance)
        
        for i, param in enumerate(self.parameters):
            method_env.set(param, arguments[i])
        
        previous_env = interpreter.current_env
        interpreter.current_env = method_env
        
        try:
            for stmt in self.body:
                interpreter.visit(stmt)
            return None
        except ReturnException as ret:
            return ret.value
        finally:
            interpreter.current_env = previous_env

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.classes = {}
    
    def interpret(self, nodes):
        result = None
        try:
            for node in nodes:
                result = self.visit(node)
        except RuntimeError as e:
            print(f"Runtime Error: {e.message}")
        return result
    
    def visit(self, node):
        if node is None:
            return None
        
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise RuntimeError(f"No visit method for {type(node).__name__}")
        return method(node)
        
    def visit_ClassNode(self, node):
        # Store class with its parent reference
        self.classes[node.name] = node
        
        class_env = Environment(self.current_env)
        previous_env = self.current_env
        self.current_env = class_env
        
        try:
            # If there's a parent class, inherit its properties/methods
            if node.parent_class:
                if node.parent_class not in self.classes:
                    raise RuntimeError(f"Parent class not found: {node.parent_class}")
                
                parent_class = self.classes[node.parent_class]
                # Create a temporary instance to copy properties
                temp_parent = ObjectInstance(node.parent_class, parent_class)
                self.visit_ClassNode(parent_class)  # Ensure parent is processed
                
                # Copy parent properties to current class
                for prop, value in temp_parent.properties.items():
                    class_env.set(prop, value)
                for method_name, method in temp_parent.methods.items():
                    class_env.set(method_name, method)
            
            # Process current class body
            for stmt in node.body:
                self.visit(stmt)
        finally:
            self.current_env = previous_env
        
        return node
    
    def visit_ObjectCreateNode(self, node):
        if node.class_name not in self.classes:
            raise RuntimeError(f"Undefined class: {node.class_name}")
        
        class_def = self.classes[node.class_name]
        obj = ObjectInstance(node.class_name, class_def)
        
        obj_env = Environment(self.current_env)
        obj_env.set("this", obj)
        previous_env = self.current_env
        self.current_env = obj_env
        
        try:
            for stmt in class_def.body:
                if isinstance(stmt, AssignmentNode) and isinstance(stmt.target, VariableNode):
                    value = self.visit(stmt.value)
                    obj.set_property(stmt.target.name, value)
                elif isinstance(stmt, MethodNode):
                    method = Method(stmt.name, stmt.parameters, stmt.body, self.current_env)
                    obj.add_method(stmt.name, method)
        finally:
            self.current_env = previous_env
        
        return obj
    
    def visit_MethodNode(self, node):
        method = Method(node.name, node.parameters, node.body, self.current_env)
        return method
    
    def visit_MethodCallNode(self, node):
        obj = self.visit(node.object)
        if not isinstance(obj, ObjectInstance):
            raise RuntimeError("Cannot call method on non-object")
        
        if not obj.has_method(node.method_name):
            raise RuntimeError(f"Method '{node.method_name}' not found on object of type {obj.class_name}")
        
        method = obj.get_property(node.method_name)
        arguments = [self.visit(arg) for arg in node.arguments]
        
        return method.call(self, arguments, obj)
    
    def visit_PropertyAccessNode(self, node):
        obj = self.visit(node.object)
        if isinstance(obj, ObjectInstance):
            value = obj.get_property(node.property)
            if value is None:
                raise RuntimeError(f"Property '{node.property}' not found on object of type {obj.class_name}")
            return value
        else:
            raise RuntimeError("Cannot access property on non-object")
    
    def visit_AssignmentNode(self, node):
        value = self.visit(node.value)
        
        if isinstance(node.target, VariableNode):
            self.current_env.set(node.target.name, value)
        elif isinstance(node.target, PropertyAccessNode):
            obj = self.visit(node.target.object)
            if isinstance(obj, ObjectInstance):
                obj.set_property(node.target.property, value)
            else:
                raise RuntimeError("Cannot set property on non-object")
        else:
            raise RuntimeError("Invalid assignment target")
        
        return value
    
    def visit_BinOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        op = node.operator
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right
        elif op == 'and':
            return self.is_truthy(left) and self.is_truthy(right)
        elif op == 'or':
            return left if self.is_truthy(left) else right
        else:
            raise RuntimeError(f"Unknown binary operator: {op}")
    
    def visit_UnaryOpNode(self, node):
        operand = self.visit(node.operand)
        
        if node.operator == '-':
            return -operand
        elif node.operator == 'not' or node.operator == '!':
            return not self.is_truthy(operand)
        else:
            raise RuntimeError(f"Unknown unary operator: {node.operator}")
    
    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        
        if self.is_truthy(condition):
            result = None
            for stmt in node.then_body:
                result = self.visit(stmt)
            return result
        elif node.else_body:
            result = None
            for stmt in node.else_body:
                result = self.visit(stmt)
            return result
        
        return None
    
    def visit_WhileNode(self, node):
        result = None
        while self.is_truthy(self.visit(node.condition)):
            for stmt in node.body:
                result = self.visit(stmt)
        return result
    
    def visit_ReturnNode(self, node):
        value = None
        if node.expression:
            value = self.visit(node.expression)
        raise ReturnException(value)
    
    def visit_PrintNode(self, node):
        value = self.visit(node.expression)
        print(self.stringify(value))
        return value
    
    def visit_VariableNode(self, node):
        try:
            return self.current_env.get(node.name)
        except Exception:
            raise RuntimeError(f"Undefined variable: {node.name}")
    
    def visit_StringNode(self, node):
        return node.value
    
    def visit_NumberNode(self, node):
        return node.value
    
    def visit_BooleanNode(self, node):
        return node.value
    
    def visit_NullNode(self, node):
        return None
    
    def is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True
    
    def stringify(self, value):
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, ObjectInstance):
            return f"<{value.class_name} instance>"
        return str(value)
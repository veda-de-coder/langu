class ClassNode:
    def __init__(self, name, body, parent_class=None):
        self.name = name
        self.body = body
        self.parent_class = parent_class

class MethodNode:
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

class MethodCallNode:
    def __init__(self, object_expr, method_name, arguments):
        self.object = object_expr
        self.method_name = method_name
        self.arguments = arguments

class ObjectCreateNode:
    def __init__(self, class_name):
        self.class_name = class_name

class PropertyAccessNode:
    def __init__(self, object_expr, property_name):
        self.object = object_expr
        self.property = property_name

class AssignmentNode:
    def __init__(self, target, value):
        self.target = target
        self.value = value

class BinOpNode:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOpNode:
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class IfNode:
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ReturnNode:
    def __init__(self, expression=None):
        self.expression = expression

class PrintNode:
    def __init__(self, expression):
        self.expression = expression

class VariableNode:
    def __init__(self, name):
        self.name = name

class StringNode:
    def __init__(self, value):
        self.value = value

class NumberNode:
    def __init__(self, value):
        self.value = value

class BooleanNode:
    def __init__(self, value):
        self.value = value

class NullNode:
    def __init__(self):
        self.value = None

class ExtendsNode:
    def __init__(self, parent_class):
        self.parent_class = parent_class

class SuperNode:
    def __init__(self):
        pass
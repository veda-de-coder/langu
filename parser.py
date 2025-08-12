from Tokeniser import *
from nodes import *

class ParseError(Exception):
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        super().__init__(self.message)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self, message="Invalid syntax"):
        raise ParseError(f"{message} at token {self.current_token}", self.current_token)
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")
    
    def parse(self):
        nodes = []
        while self.current_token.type != EOF:
            try:
                node = self.parse_statement()
                if node:
                    nodes.append(node)
            except ParseError as e:
                print(f"Parse error: {e}")
                self.synchronize()
        return nodes
    
    def synchronize(self):
        while self.current_token.type not in [SEMI, CLASS, PRINT, IF, WHILE, EOF]:
            self.current_token = self.lexer.get_next_token()
        if self.current_token.type == SEMI:
            self.current_token = self.lexer.get_next_token()
    
    def parse_statement(self):
        if self.current_token.type == CLASS:
            return self.parse_class()
        elif self.current_token.type == IF:
            return self.parse_if()
        elif self.current_token.type == WHILE:
            return self.parse_while()
        elif self.current_token.type == RETURN:
            return self.parse_return()
        elif self.current_token.type == PRINT:
            return self.parse_print()
        elif self.current_token.type == IDENTIFIER:
            return self.parse_assignment_or_expression()
        else:
            expr = self.parse_expression()
            self.eat(SEMI)
            return expr
        
    def parse_class(self):
        self.eat(CLASS)
        name = self.current_token.value
        self.eat(IDENTIFIER)
        
        # Add inheritance support
        parent_class = None
        if self.current_token.type == EXTENDS:  # Need to add EXTENDS to Tokeniser
            self.eat(EXTENDS)
            parent_class = self.current_token.value
            self.eat(IDENTIFIER)
        
        self.eat(LBRACE)
        body = []
        while self.current_token.type != RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.eat(RBRACE)
        return ClassNode(name, body, parent_class)
    
    def parse_if(self):
        self.eat(IF)
        self.eat(LPAREN)
        condition = self.parse_expression()
        self.eat(RPAREN)
        self.eat(LBRACE)
        
        then_body = []
        while self.current_token.type != RBRACE:
            stmt = self.parse_statement()
            if stmt:
                then_body.append(stmt)
        
        self.eat(RBRACE)
        return IfNode(condition, then_body)
    
    def parse_while(self):
        self.eat(WHILE)
        self.eat(LPAREN)
        condition = self.parse_expression()
        self.eat(RPAREN)
        self.eat(LBRACE)
        
        body = []
        while self.current_token.type != RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.eat(RBRACE)
        return WhileNode(condition, body)
    
    def parse_return(self):
        self.eat(RETURN)
        expr = None
        if self.current_token.type != SEMI:
            expr = self.parse_expression()
        self.eat(SEMI)
        return ReturnNode(expr)
    
    def parse_assignment_or_expression(self):
        expr = self.parse_expression()
        
        if self.current_token.type == EQUALS:
            self.eat(EQUALS)
            value = self.parse_expression()
            self.eat(SEMI)
            return AssignmentNode(expr, value)
        else:
            self.eat(SEMI)
            return expr
    
    def parse_print(self):
        self.eat(PRINT)
        expr = self.parse_expression()
        self.eat(SEMI)
        return PrintNode(expr)
    
    def parse_expression(self):
        return self.parse_logical_or()
    
    def parse_logical_or(self):
        expr = self.parse_logical_and()
        
        while self.current_token.type == OR:
            op = self.current_token.value
            self.eat(OR)
            right = self.parse_logical_and()
            expr = BinOpNode(expr, op, right)
        
        return expr
    
    def parse_logical_and(self):
        expr = self.parse_equality()
        
        while self.current_token.type == AND:
            op = self.current_token.value
            self.eat(AND)
            right = self.parse_equality()
            expr = BinOpNode(expr, op, right)
        
        return expr
    
    def parse_equality(self):
        expr = self.parse_comparison()
        
        while self.current_token.type in [EQ, NE]:
            op = self.current_token.value
            self.eat(self.current_token.type)
            right = self.parse_comparison()
            expr = BinOpNode(expr, op, right)
        
        return expr
    
    def parse_comparison(self):
        expr = self.parse_addition()
        
        while self.current_token.type in [LT, GT, LE, GE]:
            op = self.current_token.value
            self.eat(self.current_token.type)
            right = self.parse_addition()
            expr = BinOpNode(expr, op, right)
        
        return expr
    
    def parse_addition(self):
        expr = self.parse_multiplication()
        
        while self.current_token.type in [PLUS, MINUS]:
            op = self.current_token.value
            self.eat(self.current_token.type)
            right = self.parse_multiplication()
            expr = BinOpNode(expr, op, right)
        
        return expr
    
    def parse_multiplication(self):
        expr = self.parse_unary()
        
        while self.current_token.type in [MULTIPLY, DIVIDE]:
            op = self.current_token.value
            self.eat(self.current_token.type)
            right = self.parse_unary()
            expr = BinOpNode(expr, op, right)
        
        return expr
    
    def parse_unary(self):
        if self.current_token.type in [MINUS, NOT]:
            op = self.current_token.value
            self.eat(self.current_token.type)
            expr = self.parse_unary()
            return UnaryOpNode(op, expr)
        
        return self.parse_postfix()
    
    def parse_postfix(self):
        expr = self.parse_primary()
        
        while True:
            if self.current_token.type == DOT:
                self.eat(DOT)
                prop_name = self.current_token.value
                self.eat(IDENTIFIER)
                
                if self.current_token.type == LPAREN:
                    self.eat(LPAREN)
                    args = []
                    while self.current_token.type != RPAREN:
                        args.append(self.parse_expression())
                        if self.current_token.type == COMMA:
                            self.eat(COMMA)
                    self.eat(RPAREN)
                    expr = MethodCallNode(expr, prop_name, args)
                else:
                    expr = PropertyAccessNode(expr, prop_name)
            else:
                break
        
        return expr
    
    def parse_primary(self):
        if self.current_token.type == NEW:
            self.eat(NEW)
            class_name = self.current_token.value
            self.eat(IDENTIFIER)
            return ObjectCreateNode(class_name)
        
        elif self.current_token.type == NUMBER:
            value = self.current_token.value
            self.eat(NUMBER)
            return NumberNode(value)
        
        elif self.current_token.type == STRING:
            value = self.current_token.value
            self.eat(STRING)
            return StringNode(value)
        
        elif self.current_token.type == TRUE:
            self.eat(TRUE)
            return BooleanNode(True)
        
        elif self.current_token.type == FALSE:
            self.eat(FALSE)
            return BooleanNode(False)
        
        elif self.current_token.type == NULL:
            self.eat(NULL)
            return NullNode()
        
        elif self.current_token.type == IDENTIFIER:
            name = self.current_token.value
            self.eat(IDENTIFIER)
            return VariableNode(name)
        
        elif self.current_token.type == LPAREN:
            self.eat(LPAREN)
            expr = self.parse_expression()
            self.eat(RPAREN)
            return expr
        
        else:
            self.error(f"Unexpected token in expression: {self.current_token.type}")
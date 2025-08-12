from Tokeniser import *

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
    
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            self.advance()
            self.advance()
            while self.current_char is not None:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    break
                self.advance()
    
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def read_number(self):
        num_str = ""
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        return float(num_str) if '.' in num_str else int(num_str)
    
    def read_string(self):
        value = ""
        self.advance()
        while self.current_char is not None and self.current_char != '"':
            value += self.current_char
            self.advance()
        self.advance()
        return value
    
    def read_identifier(self):
        value = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            value += self.current_char
            self.advance()
        return value
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue
            
            if self.current_char.isdigit():
                return Token(NUMBER, self.read_number())
            
            if self.current_char == '"':
                return Token(STRING, self.read_string())
            
            if self.current_char.isalpha() or self.current_char == '_':
                value = self.read_identifier()
                keywords = {
                    "class": CLASS, "new": NEW, "print": PRINT, "if": IF,
                    "while": WHILE, "return": RETURN, "function": FUNCTION,
                    "true": TRUE, "false": FALSE, "null": NULL, "and": AND, "or": OR, "not": NOT
                }
                return Token(keywords.get(value, IDENTIFIER), value)
            
            if self.current_char == '{':
                self.advance()
                return Token(LBRACE, '{')
            
            if self.current_char == '}':
                self.advance()
                return Token(RBRACE, '}')
            
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(EQ, '==')
                else:
                    self.advance()
                    return Token(EQUALS, '=')
            
            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(NE, '!=')
                else:
                    self.advance()
                    return Token(NOT, '!')
            
            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(LE, '<=')
                else:
                    self.advance()
                    return Token(LT, '<')
            
            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(GE, '>=')
                else:
                    self.advance()
                    return Token(GT, '>')
            
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            
            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')
            
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            
            if self.current_char == '*':
                self.advance()
                return Token(MULTIPLY, '*')
            
            if self.current_char == '/':
                self.advance()
                return Token(DIVIDE, '/')
            
            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')
            
            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')
            
            raise Exception(f"Invalid character: {self.current_char}")
        
        return Token(EOF, None)
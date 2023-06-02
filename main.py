import string

ALPHABETS = string.ascii_letters
NUMBERS = string.digits + "."
IGNORE = [" ", "\t"]
OPERANDS = ["+", "-", "/", "*", "(", ")", "="]
KEYWORDS = ["var"]

class NumberType:
    def __init__(self, text, value):
        self.text = text
        self.value = value

    def __repr__(self):
        return f"Number '{self.text}'"

class Context:
    def __init__(self):
        self.symbol_table = SymbolTable()

class Keyword:
    def __init__(self, name):
        self.name = name
        self.kind = "KeywordKind"
        self.value = "KeywordKind"

    def __repr__(self):
        return f"'{self.name}'"

class Identifier:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"({self.name})"



class SymbolTable:
    def __init__(self):
        self.table = {}
        self.parent = None

    def set(self, name, value):
        print(f"Setting {name} to {value}")
        self.table[name] = value
        print(self.table)

    def get(self, name):
        res = self.table.get(name, None)
        if res:
            return res
        else:
            self.parent.get(name)

class Operand:
    def __init__(self, text):
        self.text = text
        if self.text == "+":
            self.kind = "PlusOperator"
        if self.text == "-":
            self.kind = "MinusOperator"
        if self.text == "*":
            self.kind = "MultiplyOperator"
        if self.text == "/":
            self.kind = "DivideOperator"
        if self.text == "(":
            self.kind = "ParenOpenOperator"
        if self.text == ")":
            self.kind = "ParenCloseOperator"
        if self.text == "=":
            self.kind = "AssignmentOperator"
    
    def __repr__(self):
        return f"Kind: {self.kind}"

class Lexer:
    def __init__(self, text):
        self.text = text + " "
        self.idx = 0
        self.current = self.text[self.idx]
        self.tokens = []

    def generate_tokens(self):
        tok = ""
        while self.should_step():

            if tok in KEYWORDS:
                tok = Keyword(tok)
                self.tokens.append(tok)
                tok = ""

            if self.current in OPERANDS not in IGNORE:
                tok = Operand(self.current)
                self.tokens.append(tok)
                tok = ""
            elif self.current in ALPHABETS:
                tok += self.current
            elif self.current in NUMBERS:
                tok += self.current
            
            elif self.current in IGNORE:
                try:
                    if isinstance(tok, str):
                        if "." in tok:
                            tok = NumberType(tok, float(tok))
                        else:
                            tok = NumberType(tok, int(tok))
                except ValueError as e:
                    if tok:
                        tok = Identifier(tok)

                if tok:
                    self.tokens.append(tok)
                tok = ""

            self.step()

    def should_step(self):    
        return self.idx < len(self.text) and self.current != "\0"

    def step(self):
        if self.should_step():
            self.idx += 1
            if(self.idx == len(self.text)):
                self.current = self.text[len(self.text) - 1]
            else:
                self.current = self.text[self.idx]
        else:
            self.current = "\0"

class BinaryExpression:
    def __init__(self, operand, left, right):
        self.operand = operand
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.operand} {self.right})"

class Parser:
    def __init__(self, text, ctx = None):
        self.text = text
        self.lexer = Lexer(text)
        if ctx:
            self.ctx = ctx
        else:
            self.ctx = Context()
        self.lexer.generate_tokens()
        self.tokens = self.lexer.tokens
        print(self.tokens)
        self.idx = 0
        self.current = self.tokens[self.idx]

    def generate_tree(self):
        """
            1 + 2 + 3
                +
               / \
              1   +
                 / \
                2   3

            1 + 2 * 3 / 4
                +
               / \
              1   *
                 / \
                2   /
                   / \
                  3   4

            (1 + 2) * 4
                  *
                 / \
                +   4
               / \   
              1   2   
                    
            Expression:
                TYPE IDENTIFIER = expression
                term PLUS|MINUS term
            term:
                factor MULTIPLY|DIVIDE factor
            factor:
                expression POW expression
            atom:
                IDENTIFIER
                INT|FLOAT
                Lparen EXPR Rparen
        """
        return self.parse_expr()

    def parse_expr(self):
        if isinstance(self.current, Keyword):
            kw = self.current.value
            self.step()
            if isinstance(self.current, Identifier):
                var_name = self.current.name
                self.step()
                if isinstance(self.current, Operand) and self.current.kind == "AssignmentOperator":
                    self.step()
                    var_value = self.parse_expr()
                    self.step()
                    self.ctx.symbol_table.set(var_name, var_value)

        left = self.parse_term()
        while isinstance(self.current, Operand) and self.current.kind in ("PlusOperator", "MinusOperator"):
            operand = self.current
            self.step()
            right = self.parse_term()
            left = BinaryExpression(operand, left, right)

        return left

    def parse_term(self):
        left = self.parse_factor()
        while isinstance(self.current, Operand) and self.current.kind in ("MultiplyOperator", "DivideOperator"):
            operand = self.current
            self.step()
            right = self.parse_factor()
            left = BinaryExpression(operand, left, right)
            
        return left


    def parse_factor(self):
        if (isinstance(self.current, NumberType)):
            curr = self.current
            self.step()
            return curr

        if (isinstance(self.current, Identifier)):
            curr = self.current
            self.step()
            return self.ctx.symbol_table.get(curr.name)

        if (isinstance(self.current, Operand) and (self.current.kind == "ParenOpenOperator")):
            self.step()
            res = self.parse_expr()
            self.step()
            return res
        
        if (isinstance(self.current, Operand) and (self.current.kind == "ParenCloseOperator")):
             pass

    def step(self):
        self.idx += 1
        if self.idx < len(self.tokens):
            self.current = self.tokens[self.idx]
    
    def peek(self, idx):
        return self.tokens[idx]




if __name__ == "__main__":
    ctx = Context()
    while True:
        p = Parser(input("> "), ctx=ctx)
        x = p.generate_tree()
        print(x)

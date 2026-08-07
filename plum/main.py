from lexer.lexer import Lexer
with open("example/hello.plum", "r") as file:
     source = file.read()
lexer = Lexer(source=source)
tokens = lexer.tokenize()
for token in tokens:
    print(token)
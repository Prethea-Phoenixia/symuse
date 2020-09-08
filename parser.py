from primitives import *

inputstring = "(2+(5*(4+3)*2)^2)"
s = Session()
a = s.parseNewLine(inputstring)
a.collapseStack()
print(a)
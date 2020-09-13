from primitives import *

inputstring = "(x+1+y)*y*x"
s = Session()
a = s.parseNewLine(inputstring)
a.stack.collapseStack()
a.prettyPrint()
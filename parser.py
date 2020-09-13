from primitives import *

inputstring = "(x+1+y)*y"
s = Session()
a = s.parseNewLine(inputstring)
a.stack.collapseStack()
a.prettyPrint()
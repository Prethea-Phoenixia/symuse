from primitives import *

inputstring = "(x+1)*(y+1)"
s = Session()
a = s.parseNewLine(inputstring)
a.stack.collapseStack()
a.prettyPrint()

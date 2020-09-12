from primitives import *

inputstring = "(x+1)/(x+1)"
s = Session()
a = s.parseNewLine(inputstring)
a.stack.collapseStack()
a.prettyPrint()

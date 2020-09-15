from primitives import *

inputstring = "(1/2)-1"
s = Session()
a = s.parseNewLine(inputstring)
a.stack.collapseStack()
a.prettyPrint()

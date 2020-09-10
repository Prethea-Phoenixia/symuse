from primitives import *

inputstring = "(1+1/1.5*14)^2"
s = Session()
a = s.parseNewLine(inputstring)
a.stack.collapseStack()
a.prettyPrint()

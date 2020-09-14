from primitives import *

inputstring = "(5/x+x/5)/x"
s = Session()
a = s.parseNewLine(inputstring)
a.stack.collapseStack()
a.prettyPrint()
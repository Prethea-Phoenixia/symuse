class Session:
    def __init__(self):
        self.funcs = []
        self.vars = []

    def newVar(self, name, val=None):
        newvar = Variable()
        newvar.name = name
        newvar.val = val

        self.vars.append(newvar)
        return newvar

    def checkVar(self, string):
        """
        lookup our register of variables and see if
        the variable is defined within this session

        if not: create a variable. returns the cre-
        ated variable.
        """
        print(string)
        for var in self.vars:
            if var.name == string:
                return var
        newvar = self.newVar(string)
        return newvar

    def parseNewLine(self, string):
        return Stacks().parse(string)


class Function(Session):
    def __init__(self):
        super().__init__()
        self.name = None
        self.stack = None
        self.range = None

    def noConsFunc(self, stack):
        self.stack = stack


class Stacks(Session):
    def __init__(self):
        super().__init__()
        self.numStack = []
        self.opStack = []
        self.priority = []
        self.bracket = []

    def parse(self, inputString):
        h = 0
        isfirstpass = True
        bracketLVL = 0  # modifies priority (order of evaluation) e.g. brackets.

        all_operand_str = [x.str_rp for x in all_operands]
        for i in range(0, len(inputString)):

            if inputString[i] not in ["(", ")"] and isfirstpass:
                h = i  # remember where the start of numeric value is
                isfirstpass = False

            if inputString[i] == "(":
                bracketLVL += 1
            elif inputString[i] == ")":
                bracketLVL -= 1

            for operand in all_operands:
                if inputString[i] == operand.str_rp:
                    self.numStack.append(inputString[h:i].strip("()"))
                    self.opStack.append(operand)
                    self.priority.append(operand.priority)
                    self.bracket.append(bracketLVL)
                    h = i + len(operand.str_rp)

            if all(x not in inputString[i:] for x in all_operand_str):
                try:
                    self.numStack.append(
                        inputString[i : inputString[i:].index(")") + i]
                    )
                except:
                    self.numStack.append(inputString[i:])
                break

        """
        fold up numstack into object, create new variable as necessary.
        """
        newStack = []
        for obj in self.numStack:
            if obj.isnumeric():
                newStack.append(float(obj))

            else:
                newStack.append(super().checkVar(obj))

        self.numStack = newStack

        return self

    def collapseStack(self):
        """expand numStack to produce a collapsed result"""

        for layer in reversed(range(min(self.bracket), max(self.bracket) + 1)):

            bracket_l = self.bracket.index(layer)
            bracket_r = len(self.bracket) - self.bracket[::-1].index(layer)

            for num in range(bracket_l, bracket_r + 1):

                i = (
                    self.priority[bracket_l:bracket_r].index(
                        max(self.priority[bracket_l:bracket_r])
                    )
                    + bracket_l
                )
                print("i = {}".format(i + bracket_l))

                left = self.numStack[i]
                right = self.numStack[i + 1]
                o = self.opStack[i]

                if isinstance(left, float) and isinstance(right, float):
                    self.numStack.pop(i)
                    self.numStack.pop(i)  # pop twice: x, and x+1
                    self.bracket.pop(i)
                    self.opStack.pop(i)
                    self.priority.pop(i)

                    if o == _plus:
                        self.numStack.insert(i, left + right)
                    elif o == _minus:
                        self.numStack.insert(i, left - right)
                    elif o == _product:
                        self.numStack.insert(i, left * right)
                    elif o == _divide:
                        self.numStack.insert(i, left / right)
                    elif o == _exponent:
                        self.numStack.insert(i, left ** right)

                if len(self.opStack) == 0:
                    return self

                print(self.numStack)
                print(self.priority)
                print(self.bracket)
                print()


class Variable(Session):
    def __init__(self):
        super().__init__()
        self.name = None
        self.val = []


class Operand:
    """
    priorities:
        0   "="
        1   "+" "-"
        2   "*" "/"
        3   "^" 
        4   "(" ")"
    """

    def __init__(self, str_rp, prior):
        self.str_rp = str_rp
        self.priority = prior
        pass


class Range:
    def __init__(self):
        self.low
        self.high
        self.closed_low
        self.closed_high


_plus = Operand("+", 1)
_minus = Operand("-", 1)
_product = Operand("*", 2)
_divide = Operand("/", 2)
_equal = Operand("=", 0)
_exponent = Operand("^", 3)

basic_operands = [_plus, _minus, _product, _divide, _equal, _exponent]

all_operands = basic_operands

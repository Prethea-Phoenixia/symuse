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
        for var in self.vars:
            if var.name == string:
                return var
        newvar = self.newVar(string)
        return newvar

    def parseNewLine(self, string):
        func = Function()
        func.stack = Stacks().parse(string)
        return func


class Function(Session):
    def __init__(self):
        super().__init__()
        self.name = None
        self.stack = None
        self.range = None

    def prettyPrint(self):
        print(self.stack.numStack[0])


class Fraction(Session):
    """Functions to handle exact fractions,
        for example 1/3"""

    def __init__(self, up, down):
        super().__init__()
        self.top, self.bottom = self.gcd(up, down)
        print(self.top, self.bottom)

    def gcd(self, a, b):
        _, amod = str(float(a)).split(".")
        _, bmod = str(float(b)).split(".")

        from math import gcd as mgcd

        div = mgcd(int(abs(a) * 10 ** len(amod)), int(abs(b) * 10 ** len(bmod)))
        return (a / div * 10 ** len(amod), b / div * 10 ** len(amod))

    def __add__(self, other):
        ans = Fraction(other * self.bottom + self.top, self.bottom)
        return ans

    def __sub__(self, other):
        ans = Fraction(-other * self.bottom + self.top, self.bottom)
        return ans

    def __mul__(self, other):
        if not isinstance(other, Fraction):
            ans = Fraction(self.top * other, self.bottom)
            return ans
        else:
            ans = Fraction(self.top * other.top, self.bottom * other.bottom)
            return ans

    def __truediv__(self, other):
        ans = Fraction(self.top, self.bottom * other)
        return ans

    """defining reverse operations of the commutative operators"""

    __rmul__ = __mul__
    __radd__ = __add__

    """non-commutative"""

    def __rsub__(self, other):
        ans = Fraction(other * self.bottom - self.top, self.bottom)
        return ans

    def __rtruediv__(self, other):
        ans = Fraction(self.bottom * other, self.top)
        return ans

    def __str__(self):
        return "{}/{}".format(int(self.top), int(self.bottom))


class Polynomial(Session):
    def __init__(self):
        super().__init__()
        self.var = None


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

            if inputString[i] in (str(x) for x in range(0, 10)) and isfirstpass:
                h = i  # remember where the start of numeric value is
                isfirstpass = False

            if inputString[i] == "(":
                bracketLVL += 1
            elif inputString[i] == ")":
                bracketLVL -= 1

            for operand in all_operands:
                if inputString[i] == operand.str_rp:

                    """handling lone - used as a minus sign.
                        e.g. "-1"
                    """

                    if inputString[h - 1] == _minus.str_rp:
                        self.numStack.append("0")

                    """ add values to stack
                    """

                    if h == i:
                        """prevent empty variables in case of "-sinX" or stuff like that
                        """

                        pass
                    else:
                        self.numStack.append(inputString[h:i])

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
        print(self.numStack)
        newStack = []
        for obj in self.numStack:
            if obj.replace(".","").isnumeric():
                newStack.append(float(obj))

            else:
                newStack.append(super().checkVar(obj))

        self.numStack = newStack
        print(self.numStack)
        return self

    def collapseStack(self):
        """expand numStack to produce a collapsed result"""

        for layer in reversed(range(min(self.bracket), max(self.bracket) + 1)):

            bracket_l = self.bracket.index(layer)
            bracket_r = len(self.bracket) - self.bracket[::-1].index(layer)

            for num in range(0, bracket_r + 1 - bracket_l):

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
                    if isinstance(left, Fraction) or isinstance(right, Fraction):
                        self.numStack.insert(i, left / right)
                    else:
                        self.numStack.insert(i, Fraction(left, right))
                elif o == _exponent:
                    self.numStack.insert(i, left ** right)

                if len(self.opStack) == 0:
                    break

                print(self.numStack)
                print(self.priority)
                print(self.bracket)
                print()

        print("collapsed:")
        print(self.numStack)

    def interactiveEval(self):
        pass


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
_sin = Operand("SIN", 4)
_cos = Operand("COS", 4)
_tan = Operand("TAN", 4)

basic_operands = [_plus, _minus, _product, _divide, _equal, _exponent]
trigonometry = [_sin, _cos, _tan]

all_operands = basic_operands + trigonometry

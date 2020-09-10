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

    def __pow__(self, exponent):
        ans = Fraction(self.top ** exponent, self.bottom ** exponent)
        return ans


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

    def prettyPrint(self):
        for i in range(0, len(self.numStack)):
            print("{:_^10}".format(i), end="")
        print()
        for x in self.numStack:
            print("{:^10}".format(str(x)), end="")
        print()
        for x in self.opStack:
            print("{:>10}".format(x.str_rp), end="")
        print()
        evaled = False
        print("     ", end="")
        for x, y in zip(self.priority, self.bracket):

            def next_bracket_layer(n):
                indices = [
                    i for i, x in enumerate(self.bracket) if x == max(self.bracket) - n
                ]

                if len(indices) == 0:
                    next_bracket_layer(n + 1)
                else:
                    return indices[0], indices[-1] + 1

            l, r = next_bracket_layer(0)

            if x == max(self.priority[l:r]) and not evaled:
                print("{:^10}".format("NEXT^EVAL"), end="")
                evaled = True
            else:
                print("{:^10}".format(""), end="")
        print()

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
            if obj.replace(".", "").isnumeric():
                newStack.append(float(obj))

            else:
                newStack.append(super().checkVar(obj))

        self.numStack = newStack
        return self

    def collapseStack(self):
        """expand numStack to produce a collapsed result"""

        """example:
            number stack: 1,2,3,4
            operand stack: + / *
            bracket stack: 1 1 0

        a.k.a (1+2/3)*4
        """

        self.prettyPrint()

        for layer in reversed(range(min(self.bracket), max(self.bracket) + 1)):

            bracket_l = self.bracket.index(layer)  # 0
            bracket_r = len(self.bracket) - self.bracket[::-1].index(layer)  # 3-1=2

            for num in range(0, bracket_r - bracket_l):  # range(0,2),two executions.
                i = (
                    self.priority[bracket_l:bracket_r].index(
                        max(self.priority[bracket_l:bracket_r])
                    )
                    + bracket_l
                )
                """
                    self.priority[0:2]-> (1,2)
                    (1,2).index(max(1,2)) = 1
                    1+bracket_l = 1+0 =1

                """

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

                self.prettyPrint()

                if len(self.opStack) == 0:
                    break

                # bracket_r = len(self.bracket) - self.bracket[::-1].index(layer)
                bracket_r -= 1  # equivalent expression

                """updates the bracket information:
                    number stack: 1,2/3,4
                    operand stack: +   x
                    bracket stack  1   0

                    bracket_l is constant as stack evaluation only pops from the right
                    bracket_r is shrunk one to account for popped info: 2-1=1 
                """

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

basic_operands = [_plus, _minus, _product, _divide, _equal, _exponent]

all_operands = basic_operands

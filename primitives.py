import string


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


class Stacks(Session):
    def __init__(self):
        super().__init__()
        self.numStack = []
        self.opStack = []
        self.priority = []
        self.bracket = []

    def prettyPrint(self):

        width = 20
        for i in range(0, len(self.numStack)):
            print("{:_^{}}".format(i, width), end="")
        print()
        for x in self.numStack:
            print("{:^{}}".format(str(x), width), end="")
        print()
        for x in self.opStack:
            print("{:>{}}".format(x.str_rp, width), end="")
        print()
        evaled = False
        print("{}".format(" " * int(width / 2)), end="")
        for x, y in zip(self.priority, self.bracket):

            def next_bracket_layer(n):
                indices = [
                    i for i, x in enumerate(self.bracket) if x == max(self.bracket) - n
                ]
                not_indices = [
                    i for i in range(0, len(self.bracket)) if i not in indices
                ]
                if len(indices) == 0:
                    next_bracket_layer(n + 1)
                else:
                    if len(not_indices) == 0:
                        return indices[0], indices[-1] + 1
                    else:
                        """for example 1+(2+3)*(1/4)
                        """
                        next_non_index = [i for i in not_indices if i > indices[0]]
                        if len(next_non_index) > 0:
                            return indices[0], min(next_non_index)
                        else:
                            return indices[0], indices[-1] + 1

            l, r = next_bracket_layer(0)

            if x == max(self.priority[l:r]) and not evaled:
                print("{:^{}}".format("NEXT^EVAL", width), end="")
                evaled = True
            else:
                print("{:^{}}".format("", width), end="")
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

            indices = [i for i, x in enumerate(self.bracket) if x == layer]
            # in this case: 0,1
            not_indices = [i for i in range(0, len(self.bracket)) if i not in indices]
            # in this case: 2

            bracket_l = indices[0]
            if len(not_indices) > 0:
                next_non_index = [i for i in not_indices if i > indices[0]]
                if len(next_non_index) > 0:
                    bracket_r = min(next_non_index)
                else:
                    bracket_r = indices[-1] + 1
            else:
                bracket_r = indices[-1] + 1

            for num in range(0, len(indices)):  # range(0,2),two executions.
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
                    if isinstance(left, float) and isinstance(right, float):
                        self.numStack.insert(i, Fraction(left, right))
                    else:
                        self.numStack.insert(i, left / right)

                elif o == _exponent:
                    self.numStack.insert(i, left ** right)

                self.prettyPrint()

                if len(self.opStack) == 0:
                    break

                """updates the bracket information:
                    number stack: 1,2/3,4
                    operand stack: +   x
                    bracket stack  1   0

                    bracket_l is constant as stack evaluation only pops from the right
                    bracket_r is shrunk one to account for popped info: 2-1=1 
                """

                indices = [i for i, x in enumerate(self.bracket) if x == layer]
                # in this case: 0,1
                not_indices = [
                    i for i in range(0, len(self.bracket)) if i not in indices
                ]
                # in this case: 2

                if len(indices) == 0:
                    break

                bracket_l = indices[0]
                if len(not_indices) > 0:
                    next_non_index = [i for i in not_indices if i > indices[0]]
                    if len(next_non_index) > 0:
                        bracket_r = min(next_non_index)
                    else:
                        bracket_r = indices[-1] + 1
                else:
                    bracket_r = indices[-1] + 1

    def interactiveEval(self):
        pass


class Variable(Session):
    def __init__(self):
        super().__init__()
        self.name = None
        self.val = None

    def __str__(self):
        return self.name

    def __add__(self, other):
        ans = Polynomial([self], [1], [[1]])
        if isinstance(other, Variable):
            # x + y
            ans.newLeaf(other, 1, 1)
        elif isinstance(other, Fraction) or isinstance(other, float):
            # x + 1/2
            ans.newLeaf(self, other, 0)  # x+ 1/2*x^0

        return ans

    __radd__ = __add__

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, Fraction):
            return Polynomial([self], [other], [[1]])

    __rmul__ = __mul__


# fmt:off
superscript_map = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
    "7": "⁷", "8": "⁸", "9": "⁹", "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ",
    "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ᶦ", "j": "ʲ", "k": "ᵏ",
    "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "۹", "r": "ʳ",
    "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ",
    "z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ᶜ", "D": "ᴰ", "E": "ᴱ", "F": "ᶠ",
    "G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ",
    "N": "ᴺ", "O": "ᴼ", "P": "ᴾ", "Q": "Q", "R": "ᴿ", "S": "ˢ", "T": "ᵀ",
    "U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "X": "ˣ", "Y": "ʸ", "Z": "ᶻ", "+": "⁺",
    "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾", ".": "\u00b7"}

subscript_map = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆",
    "7": "₇", "8": "₈", "9": "₉", "a": "ₐ", "b": "♭", "c": "꜀", "d": "ᑯ",
    "e": "ₑ", "f": "բ", "g": "₉", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
    "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "q": "૧", "r": "ᵣ",
    "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "w": "w", "x": "ₓ", "y": "ᵧ",
    "z": "₂", "A": "ₐ", "B": "₈", "C": "C", "D": "D", "E": "ₑ", "F": "բ",
    "G": "G", "H": "ₕ", "I": "ᵢ", "J": "ⱼ", "K": "ₖ", "L": "ₗ", "M": "ₘ",
    "N": "ₙ", "O": "ₒ", "P": "ₚ", "Q": "Q", "R": "ᵣ", "S": "ₛ", "T": "ₜ",
    "U": "ᵤ", "V": "ᵥ", "W": "w", "X": "ₓ", "Y": "ᵧ", "Z": "Z", "+": "₊",
    "-": "₋", "=": "₌", "(": "₍", ")": "₎"}

# fmt:on

super_trans = str.maketrans(
    "".join(superscript_map.keys()), "".join(superscript_map.values())
)

sub_trans = str.maketrans(
    "".join(subscript_map.keys()), "".join(subscript_map.values())
)


class Polynomial(Session):
    """polynomial data structure:
    example:2a+3b+5ab

    self.var:           list,           e.g. [a,b]
    self.coefficient:   list,           e.g. [2,3,5]
    self.exponent:      nested list,    e.g. [[1,0],[0,1],[1,1]]



    """

    def __init__(self, v, coe, exp):
        super().__init__()
        self.variable = v
        self.coefficient = coe
        self.exponent = exp
        self.comb()

    def extendVars(self, vars):
        for var in vars:
            if var not in self.variable:
                self.variable.append(var)
                self.exponent = [i + [0] for i in self.exponent]

    def comb(self):
        """merge similiar terms """
        i = 0
        while i < len(self.coefficient) - 1:
            j = i + 1
            while j < len(self.coefficient):
                if self.exponent[i] == self.exponent[j]:
                    new_coe = self.coefficient[i] + self.coefficient[j]
                    self.coefficient.pop(i)
                    self.coefficient.pop(j - 1)
                    self.exponent.pop(j)
                    self.coefficient.insert(i, new_coe)
                j += 1
            i += 1

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, Fraction):
            newPoly = Polynomial(
                self.variable, [x * other for x in self.coefficient], self.exponent
            )
        elif isinstance(other, Variable):
            if other in self.variable:
                allVars = self.variable
                newExp = self.exponent
                for i in newExp:
                    i[self.variable.index(other)] += 1
            else:
                allVars = self.variable + [other]
                newExp = [i + [1] for i in self.exponent]

            newPoly = Polynomial(allVars, self.coefficient, newExp)
        elif isinstance(other, Polynomial):
            """Polynomial Multiplication
            example:(2a^2-b)(a+b) = 2a^3-ab+2a^2b-b^2

            var stack:      a,b              a,b            a,b
            coefficient:    2,-1             1,1            2,-1,2,-1
            exponent:       2,1              1,1            (3,0),(1,1),(2,1),(1,2)
            """
            all_vars = self.variable + [
                i for i in other.variable if i not in self.variable
            ]
            newCoe = [
                self.coefficient[i] * other.coefficient[g]
                for g in range(0, len(other.coefficient))
                for i in range(0, len(self.coefficient))
            ]

            self.extendVars(all_vars)
            other.extendVars(all_vars)

            newExp = []
            for v in all_vars:

                vExp = [
                    self.exponent[i][self.variable.index(v)]
                    + other.exponent[g][other.variable.index(v)]
                    for g in range(0, len(other.exponent))
                    for i in range(0, len(self.exponent))
                ]
                if newExp == []:
                    newExp = [[i] for i in vExp]
                else:
                    newExp = [newExp[i] + [vExp[i]] for i in range(0, len(vExp))]

            newPoly = Polynomial(all_vars, newCoe, newExp)
        return newPoly

    __rmul__ = __mul__

    def __add__(self, other):
        if isinstance(other, float) or isinstance(other, Fraction):
            ans = Polynomial(
                self.variable,
                self.coefficient + [other],
                self.exponent + [[0] * len(self.variable)],
            )

        elif isinstance(other, Polynomial):
            allVar = self.variable
            for oVar in other.variable:
                if oVar in allVar:
                    pass
                else:
                    allVar.append(oVar)

            nVars = len(allVar)

            selfAllExp = [[0] * nVars] * len(self.exponent)
            for var in self.variable:
                for i in len(self.exponent):
                    selfAllExp[i][allVar.index(var)] = self.exponent[i][
                        self.variable.index(var)
                    ]

            otherAllExp = [[0] * nVars] * len(other.exponent)
            for var in other.variable:
                for i in len(other.exponent):
                    otherAllExp[i][allVar.index(var)] = other.exponent[i][
                        other.variable.index(var)
                    ]

            ans = Polynomial(
                allVar,
                self.coefficient.extend(other.coefficient),
                selfAllExp.extend(otherAllExp),
            )
            ans.comb()

        elif isinstance(other, Variable):
            ans = Polynomial(self.variable, self.coefficient, self.exponent)
            ans.newLeaf(other, 1, 1)
        return ans

    __radd__ = __add__

    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, Fraction):
            newPoly = Polynomial(
                self.variable, [x / other for x in self.coefficient], self.exponent
            )
            return newPoly
        elif isinstance(other, Variable):
            newPoly = Polynomial(
                self.variable + [other],
                self.coefficient,
                [i + [-1] for i in self.exponent],
            )
            return newPoly

        elif isinstance(other, Polynomial):
            """polynomial division, returns a fraction object"""
            newFract = Fraction(self, other)
            return newFract

    def __str__(self):
        string = ""
        for i in range(0, len(self.coefficient)):
            if self.coefficient[i] > 0:
                if self.coefficient[i] == 1 and max(self.exponent[i]) > 0:
                    string += "+"
                else:
                    string += "+{}".format(self.coefficient[i])
            else:
                if self.coefficient[i] == -1 and max(self.exponent[i]) > 0:
                    string += "+"
                else:
                    string += "-{}".format(self.coefficient[i])

            for v in range(0, len(self.variable)):
                if self.exponent[i][v] == 0:
                    pass
                elif self.exponent[i][v] == 1:
                    string += "{}".format(self.variable[v])
                elif self.exponent[i][v] == -1:
                    string += "/{}".format(self.variable[v])
                else:
                    string += "{}{}".format(
                        self.variable[v], str(self.exponent[i][v]).translate(super_trans)
                    )

        if string[0] == "-":
            return string
        else:
            return string[1:]

    def newLeaf(self, var, coe, exp):
        if var in self.variable:
            pass
        else:
            self.variable.append(var)
            self.exponent = [i + [0] for i in self.exponent]

        self.coefficient.append(coe)
        self.exponent.append([0] * len(self.variable))
        self.exponent[-1][self.variable.index(var)] = exp


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

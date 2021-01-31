import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        self.rank = float('inf')

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'

    def deriv(self, var):
        return Num(1) if self.name == var else Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        val = mapping.get(self.name, 'F in the chat lol')
        return KeyError if val == 'F in the chat lol' else val


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        self.rank = float('inf')

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'

    def __eq__(self, other):
        if not isinstance(other, Num):
            return False
        return self.n == other.n

    def deriv(self, var):
        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        return self.n


class BinOp(Symbol):
    def __init__(self, left, right):
        # Convert inputs to proper types if necessary
        inputs = [left, right]
        for i, inp in enumerate(inputs):
            if isinstance(inp, int) or isinstance(inp, int):
                inputs[i] = Num(inp)
            elif isinstance(inp, str):
                inputs[i] = Var(inp)
        self.left, self.right = inputs

    def __repr__(self):
        return self.type + '(' + repr(self.left) + ', ' + repr(self.right) + ')'

    def __str__(self):
        # Add parentheses around expressions if necessary
        return self.left_str() + ' ' + self.symbol + ' ' + self.right_str()

    def left_str(self):
        return '(' + str(self.left) + ')' if self.rank > self.left.rank else str(self.left)

    def right_str(self):
        return '(' + str(self.right) + ')' if self.rank > self.right.rank else str(self.right)


class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol = '+'
        self.type = 'Add'
        self.rank = 1

    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)

    def simplify(self):
        simple = self.left.simplify() + self.right.simplify()
        l = simple.left
        r = simple.right
        if not (isinstance(l, Num) and isinstance(r, Num)):
            if l == Num(0):
                return r
            elif r == Num(0):
                return l
            return simple  # At least one of either left or right is a BinOp or Var, so we can't simplify any further
        return Num(l.n + r.n)  # Left and right are both Num objects

    def eval(self, mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)


class Sub(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol = '-'
        self.type = 'Sub'
        self.rank = 1

    def deriv(self, var):
        return self.left.deriv(var) - self.right.deriv(var)

    def simplify(self):
        simple = self.left.simplify() - self.right.simplify()
        l = simple.left
        r = simple.right
        if not (isinstance(l, Num) and isinstance(r, Num)):
            if r == Num(0):  # We only look at x - 0, because 0 - x isn't simplified in our SymAlg model
                return l
            return simple  # At least one of either left or right is a BinOp or Var, so we can't simplify any further
        return Num(l.n - r.n)  # Left and right are both Num objects

    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)

    def right_str(self):
        return '(' + str(self.right) + ')' if self.rank >= self.right.rank else str(self.right)


class Mul(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol = '*'
        self.type = 'Mul'
        self.rank = 2

    def deriv(self, var):
        # Product Rule
        l = self.left
        r = self.right
        return l * r.deriv(var) + r * l.deriv(var)

    def simplify(self):
        simple = self.left.simplify() * self.right.simplify()
        l = simple.left
        r = simple.right
        if not (isinstance(l, Num) and isinstance(r, Num)):
            if l == Num(1):
                return r
            elif r == Num(1):
                return l
            elif l == Num(0) or r == Num(0):
                return Num(0)
            return simple  # At least one of either left or right is a BinOp or Var, so we can't simplify any further
        return Num(l.n * r.n)  # Left and right are both Num objects

    def eval(self, mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)


class Div(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.symbol = '/'
        self.type = 'Div'
        self.rank = 2

    def deriv(self, var):
        # Quotient Rule
        num = self.left
        den = self.right
        (den * num.deriv(var) - num * den.deriv(var)) / (den * den)

    def simplify(self):
        simple = self.left.simplify() / self.right.simplify()
        l = simple.left
        r = simple.right
        if not (isinstance(l, Num) and isinstance(r, Num)):
            if r == Num(1):  # We only look at x / 1, because 1 / x can't be simplified
                return l
            elif l == Num(0):
                return Num(0)
            return simple  # At least one of either left or right is a BinOp or Var, so we can't simplify any further
        return Num(l.n / r.n)  # Left and right are both Num objects

    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)

    def right_str(self):
        return '(' + str(self.right) + ')' if self.rank >= self.right.rank else str(self.right)


def sym(expr):
    def parse(exp):
        if exp[0] == '(' and exp[-1] == ')':
            exp = exp[1:-1]  # Remove bounding parentheses
            left_end = 0
            if exp[0] == '(':
                # If the left term is a parenthesized expression, determine where it ends
                left_end = match_parentheses(exp, 0)
            operator = exp[left_end + 1]  # operator will be located directly after our left-hand expression
            # By similar logic, right hand-expression will be everything directly after the operator:
            right_start = left_end + 2
            left = parse(exp[:left_end + 1])
            right = parse(exp[right_start:])
            operator = {'+': Add, '-': Sub, '*': Mul, '/': Div}[operator]
            return operator(left, right)
        else:  # If we don't have a parenthesized expression, i.e. a lone number or variable
            val = exp[0]
            if 65 <= ord(val[0]) <= 90 or 97 <= ord(val[0]) <= 122:
                # Val is a single lowercase or uppercase letter, and thus a variable
                return Var(val)
            else:
                # We don't have a parenthesized expression, and our expression isn't a variable, thus, it's a number
                return Num(int(val))
    return parse(tokenize(expr))


def tokenize(exp):
    tokens = []
    current_num = ''
    for c in exp + ' ':  # We add a space so that if the last value in an expression is a number, we still tokenize it
        if 48 <= ord(c) <= 57 or c == '-':
            # If c is an integer or negative sign, we can build up to form a number
            current_num += c
        else:
            if not current_num == '':
                # If we hit anything that can't be used to build on current_num, we're done building
                tokens.append(current_num)
                current_num = ''
            if c != ' ':
                tokens.append(c)  # If we hit anything that can't be used to build on current_num,
                # and it's not a space, we add it to tokens as well
    return tokens


def match_parentheses(exp, start):
    # Given a tokenized expression and a starting index corresponding to an
    # opening parenthesis, find the corresponding closing parenthesis
    count = 0  # Add one for '(', subtract one for ')'
    for i, c in enumerate(exp[start:]):
        if c == '(':
            count += 1
        elif c == ')':
            count -= 1
        if count == 0:
            return i + start
    return None


if __name__ == '__main__':
    a = sym('(x + (2 * y))')
    print(a)
    print(a.deriv('x'))
    print(a.deriv('x').simplify())

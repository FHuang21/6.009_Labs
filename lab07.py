import doctest
from turtle import right
from xmlrpc.client import boolean

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.

class Symbol:
    def simplify(self):
        return self

    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mul(self, other)

    def __truediv__(self, other):
        return Div(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __rsub__(self, other):
        return Sub(other, self)

    def __rmul__(self, other):
        return Mul(other, self)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

class Var(Symbol):
    precedence = float('inf')
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"

    def deriv(self, var):
        if var == self.name: #constants = 0 after deriving
            return Num(1)
        else:
            return Num(0)

    def eval(self, env):
        try:
            return env[self.name]
        except KeyError:
            raise KeyError

class Num(Symbol):
    precedence = float('inf')
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"
    
    def deriv(self, var):
        return Num(0) #constants = 0 after deriving

    def eval(self, env):
        return self.n

#helper function
def type_cast(operand):
    '''
    returns operand cast as the proper type based on the lab's parameters
    '''
    if isinstance(operand, int):
        return Num(operand)
    elif isinstance(operand, str):
        return Var(operand)
    elif isinstance(operand, Symbol):
        return operand
    else:
        raise TypeError

class BinOp(Symbol):
    '''
    Representation of a combination of primitive symbols
    Each instance of any of these classes should have two instance variables:
        left: a Symbol instance representing the left-hand operand
        right: a Symbol instance representing the right-hand operand
    Subclasses:
        Add, to represent an addition
        Sub, to represent a subtraction
        Mul, to represent a multiplication
        Div, to represent a division
    '''

    def __init__(self, left, right):
        '''
        Initializes BinOp with a left operand, right operand, and it's operator
        '''
        self.left = type_cast(left)
        self.right = type_cast(right)

    def __str__(self):
        '''
        Returns readable string format of the BinOp.
        Accounts for PEMDAS precedence rules and implements parentheses where necessary
        to follow standard math ordering precedures.
        '''
        left_op = self.left
        right_op = self.right

        #checks and adds parantheses if needed for left_op based on PEMDAS operations
        if (self.paren_left_order is True and self.left.precedence <= self.precedence):
            left_op = '(' + str(left_op) + ')'
        if (self.paren_left_order is False and self.left.precedence < self.precedence):
            left_op = '(' + str(left_op) + ')'
        #checks and adds parantheses if needed for right_op based on PEMDAS operations
        if (self.paren_right_order is True and self.right.precedence <= self.precedence):
            right_op = '(' + str(right_op) + ')'
        if (self.paren_right_order is False and self.right.precedence < self.precedence):
            right_op = '(' + str(right_op) + ')'

        out_str = str(left_op) + ' ' + self.operation + ' ' + str(right_op)
        return out_str

    def __repr__(self):
        out_repr = self.__class__.__name__ + '(' + repr(self.left) + ', ' + repr(self.right) + ')'
        return out_repr

    def eval(self, env):
        '''
        Input: dictionary mapping variables to numbers
        Output: returns the evaluated expression substituting 
        in the numbers to the given mapped variables
        '''
        left_eval = self.left.eval(env)
        right_eval = self.right.eval(env)
        return (self.combination(left_eval, right_eval))

class Add(BinOp):
    operation = '+'
    precedence = -1
    paren_left_order = False
    paren_right_order = False
    

    #takes the derivative of two operands separately
    def deriv(self, var):
        '''
        Input: the expression is taken the derivative of in respect to the 
        input, var, 
        Output: Returns the derivative of the expression in respect to var
        '''
        left_deriv = self.left.deriv(var)
        right_deriv = self.right.deriv(var)
        return Add(left_deriv, right_deriv)

    def simplify(self):
        '''
        Input: Symbol representing the full expression 
        Output: Returns a simplified Symbol representing the full expression
        that accounts for redundency in the expresssion
        '''
        left_simplify = self.left.simplify()
        right_simplify = self.right.simplify()
        if isinstance(left_simplify, Num) and isinstance(right_simplify, Num):
            return Num(left_simplify.n + right_simplify.n)
        else:
            if isinstance(left_simplify, Num) and left_simplify.n == 0:
                return right_simplify
            elif isinstance(right_simplify, Num) and right_simplify.n == 0:
                return left_simplify
            return Add(left_simplify, right_simplify)

    def combination(self, left, right):
        '''
        Input: left operand, right operand
        Output: Evaluation of left and right operand based on operator
        '''
        return(left + right)


class Sub(BinOp):
    operation = '-'
    precedence = -1
    paren_left_order = False
    paren_right_order = True #order matters for right side of binOp

    #takes the derivative of two operands separately
    def deriv(self, var):
        left_deriv = self.left.deriv(var)
        right_deriv = self.right.deriv(var)
        return Sub(left_deriv, right_deriv)

    def simplify(self):
        left_simplify = self.left.simplify()
        right_simplify = self.right.simplify()
        if isinstance(left_simplify, Num) and isinstance(right_simplify, Num):
            return Num(left_simplify.n - right_simplify.n)
        else:
            if isinstance(right_simplify, Num) and right_simplify.n == 0:
                return left_simplify
            return Sub(left_simplify, right_simplify)

    def combination(self, left, right):
        return(left - right)

class Mul(BinOp):
    operation = '*'
    precedence = 0
    paren_left_order = False
    paren_right_order = False

    #follows multiplication derivative rule
    def deriv(self, var):
        left_deriv = self.left.deriv(var)
        right_deriv = self.right.deriv(var)
        left_add = self.left * right_deriv
        right_add = self.right * left_deriv
        return left_add + right_add

    def simplify(self):
        left_simplify = self.left.simplify()
        right_simplify = self.right.simplify()
        if isinstance(left_simplify, Num) and isinstance(right_simplify, Num):
            return Num(left_simplify.n * right_simplify.n)
        else:
            if (isinstance(right_simplify, Num) and right_simplify.n == 0) or (isinstance(left_simplify, Num) and left_simplify.n == 0):
                return Num(0)
            elif isinstance(right_simplify, Num) and right_simplify.n == 1:
                return left_simplify
            elif isinstance(left_simplify, Num) and left_simplify.n == 1:
                return right_simplify
            return Mul(left_simplify, right_simplify)

    def combination(self, left, right):
        return(left * right)


class Div(BinOp):
    operation = '/'
    precedence = 0
    paren_left_order = False
    paren_right_order = True #order matters for right side of binOp

    #follows division derivative rule
    def deriv(self, var):
        left_deriv = self.left.deriv(var)
        right_deriv = self.right.deriv(var)
        numerator = (self.right * left_deriv) - (self.left * right_deriv)
        denominator = (self.right * self.right)
        return Div(numerator, denominator)

    def simplify(self):
        left_simplify = self.left.simplify()
        right_simplify = self.right.simplify()
        if isinstance(left_simplify, Num) and isinstance(right_simplify, Num):
            return Num(left_simplify.n / right_simplify.n)
        else:
            if isinstance(right_simplify, Num) and right_simplify.n == 1:
                return left_simplify
            elif isinstance(left_simplify, Num) and left_simplify.n == 0:
                return Num(0)
            return Div(left_simplify, right_simplify)

    def combination(self, left, right):
        return(left / right)


class Pow(BinOp):
    operation = '**'
    precedence = 1
    paren_left_order = True #order matters for left side of the binOp
    paren_right_order = False

    #handles derivatives with power
    def deriv(self, var):
        if not isinstance(self.right, Num):
            raise TypeError
        n = self.right
        u = self.left
        left_mult = (n * u**(n-1))
        right_mult = u.deriv(var)
        return left_mult * right_mult
    
    def simplify(self):
        left_simplify = self.left.simplify()
        right_simplify = self.right.simplify()
        #Any expression raised to the power 0 should simplify to 1.
        if isinstance(right_simplify, Num) and right_simplify.n == 0: 
            return Num(1)
        #Any expression raised to the power 1 should simplify to itself.
        if isinstance(right_simplify, Num) and right_simplify.n == 1:
            return left_simplify
        #0 raised to any positive power (or to any other symbolic expression that is not a single number) should simplify to 0
        if isinstance(left_simplify, Num) and left_simplify.n == 0:
            if isinstance(right_simplify, Num) and right_simplify.n < 0:
                return Pow(left_simplify, right_simplify)
            return Num(0)
        if isinstance(left_simplify, Num) and isinstance(right_simplify, Num):
            return Num(left_simplify.n ** right_simplify.n)
        return Pow(left_simplify, right_simplify)
    
    def combination(self, left, right):
        return(left ** right)


operations = {'+': Add, '-': Sub, '*': Mul, '/': Div, '**': Pow, }

#helper function
def tokenize(x):
    '''
    Input: string of expression
    Output: returns a list of meaningful tokens 
    (parentheses, variable names, numbers, or operands)
    '''
    return x.replace('(', ' ( ').replace(')', ' ) ').split()

#helper function
def parse(tokens):
    '''
    Input: Token list
    Output: Returns the appropriate instance of Symbol 
    (or some subclass thereof)
    '''
    def parse_expression(index):
        '''
        Input: Integer indexing into the tokens list
        Output: Returns a pair of values:
        1) the expression found starting at the location given 
        by index (an instance of one of the Symbol subclasses)
        2) the index beyond where this expression ends 
        (e.g., if the expression ends at the token with index 6 
        in the tokens list, then the returned value should be 7).
        '''
        #test number case
        try:
            return Num(int(tokens[index])), index + 1
        except ValueError:
            pass

        #test variable case
        if tokens[index] is not '(' and tokens[index] is not ')' and tokens[index] not in operations:
            return Var(str(tokens[index])), index + 1

        #test operation case
        if tokens[index] is '(':
            first = parse_expression(index + 1)
            second = parse_expression(first[1] + 1)
            left = first[0]
            right = second[0]
            operator = tokens[first[1]]
            return operations[operator](left, right), second[1] + 1
                   
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def expression(str):
    '''
    Input: String expression
    Output: Returns the parsed expression after 
    tokenizing the string
    '''
    tokened = tokenize(str)
    return parse(tokened)
                   
if __name__ == "__main__":
    doctest.testmod()
    x = Var('x')
    y = Var('y')
    z= Add(Var('x'), Sub(Var('y'), Num(2)))
    print(z)
    print(z.deriv('x'))
    print(repr(parse(['(', 'x','+', '5', ')'])))
    w = Mul(Var('x'), Add(Var('y'), Var('z')))
    print(w)
    #expression('(x * (2 + 3))')
    ppow =  Pow(Mul(Var('x'), Add(Num(2), Num(3))), Num(2))
    print(ppow)
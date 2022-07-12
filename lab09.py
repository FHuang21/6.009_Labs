"""6.009 Lab 9: Carlae Interpreter Part 2"""

from argparse import ArgumentDefaultsHelpFormatter
from distutils.command.build import build
import sys
sys.setrecursionlimit(10_000)
#!/usr/bin/env python3
"""6.009 Lab 8: Carlae (LISP) Interpreter"""

import doctest

from pyparsing import empty

# NO ADDITIONAL IMPORTS!

###########################
# Carlae-related Exceptions #
###########################

class CarlaeError(Exception):

    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('2')
    2
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x

def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
   
    """
    final = ''
    length = len(source)
    i = 0
    while i < length:
        if source[i] == '#':
            #move index to end of comment
            while i != '\n':
                #if # is the last item in the string, or we have reached last element in string
                if i == length - 1:
                    i = i + 1
                    break
                elif source[i] == '\n':   
                    break
                else:
                    i = i + 1
        if i < length:
            final = final + source[i]
            i = i + 1
        else:
           break
    return final.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(tokens, bool = True):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    >>> parse(["(", "cat", "(", "dog", "(", "tomato", ")", ")", ")"])
    ['cat', ['dog', ['tomato']]]
    """

    front_count = 0
    back_count = 0

    if len(tokens) == 0:
            raise CarlaeSyntaxError
    else:
        for token in tokens:
            if token == "(":
                front_count += 1
            elif token == ")":
                back_count += 1
            else:
                pass
        if (front_count != back_count and bool == True):
            raise CarlaeSyntaxError

    current = tokens.pop(0)
    lst = [] #creates a list for every pair of parenthesis

    #recursive step
    if current == '(':
        
        while tokens[0] != ')':
            recurse_out = parse(tokens, False) #calls parse recursively
            lst.append(recurse_out) 

        tokens.pop(0) #deletes first element in token
        return lst
    
    #error conditions
    elif (current == ":=" and bool == True) or (front_count != back_count and bool == True) or (current == ')'):
        raise CarlaeSyntaxError
    else:
        return number_or_symbol(current)
    

######################
# Built-in Functions #
######################

operators = {
    '==': lambda x, y: x == y,
    '>': lambda x, y: x > y,
    '>=': lambda x, y: x>= y,
    '<': lambda x, y: x < y,
    '<=': lambda x, y: x <= y
}

#helper function
def compare(argument, op):
    '''
    checks if all elements in argument satisfy the operator
    Returns '@t' if True, '@f' if False
    '''
    index = 1
    for i in range(len(argument)-1):
        x = argument[i]
        y = argument[i+1]
        if operators[op](x, y) == True:
            index += 1
        else:
            break
    if index == len(argument):
        return '@t'
    else:
        return '@f'

#helper function
def not_function(args):
    if len(args) != 1:
        raise CarlaeEvaluationError
    elif args[0] == '@t':
        return '@f'
    else:
        return '@t'

def head(pair):
    '''
    returns head
    '''
    if isinstance(pair, Pair):
        return pair.get_head()
    else:
        raise CarlaeEvaluationError

#helper
def if_head(args):
    if len(args) == 1:
        return head(args[0])
    else:
        raise CarlaeEvaluationError 

def tail(pair):
    '''
    return tail
    '''
    if isinstance(pair, Pair):
        return pair.get_tail()
    else:
        raise CarlaeEvaluationError

#helper
def if_tail(args):
    if len(args) == 1:
        return tail(args[0])
    else:
        raise CarlaeEvaluationError 

def build_list(args):
    '''
    builds and returns a Pair linked-list
    '''
    
    if len(args) != 0:
        return Pair(args[0], build_list(args[1:]))
    else:
        return 'nil'

def build_pair(args):
    '''
    builds and returns a Pair
    '''
    if len(args) == 2:
        return Pair(args[0], args[1])
    else:
        raise CarlaeEvaluationError

def is_linked_list(args):
    '''
    returns true is args is a linked-list, false otherwise
    '''
    if args[0] == 'nil':
        return '@t'
    my_list = args[0]
    while isinstance(my_list, Pair):
        my_list = my_list.get_tail()
    if my_list == 'nil':
        return '@t'
    return '@f'


def len_list(args):
    '''
    returns length of input list
    '''
    if args == 'nil': #base case
        return 0
    elif isinstance(args, Pair):
        return 1 + len_list(args.get_tail())
    else:
        raise CarlaeEvaluationError
#helper
def if_length(args):
    if len(args) == 1:
        return len_list(args[0])
    else:
        raise CarlaeEvaluationError 

def nth_element(args, index):
    '''
    returns element at index in args
    '''
    if isinstance(args, Pair):
        if index == 0: #base case
            return args.get_head()
        else:
            return nth_element(args.get_tail(), index - 1)
    else:
        raise CarlaeEvaluationError
#helper
def if_nth(args):
    if len(args) == 2:
        return nth_element(args[0], args[1])
    else:
        raise CarlaeEvaluationError

def concat(args):
    '''
    concatenate lists in args
    '''
    if len(args) == 0:
        return 'nil'

    first = args[0]
    if first == 'nil':
        return concat(args[1:])    
    elif not isinstance(first, Pair):
        raise CarlaeEvaluationError
    elif len(args) == 1:
        return first.copy()
    elif first.get_tail() == 'nil':
        return Pair(first.get_head(), concat(args[1:]))
    else:
        a_list = [first.get_tail()]
        for i in range(1, len(args)):
            a_list.append(args[i])
        return Pair(first.get_head(), concat(a_list))

def map(funct, lis):
    '''
    returns a list that has been applied by a function
    '''
    a_list = []
    for i in range(len_list(lis)):
        a_list.append(funct([nth_element(lis, i)]))
    return build_list(a_list)

#helper
def if_map(args):
    if len(args) == 2:
        return map(args[0], args[1])
    else:
        raise CarlaeEvaluationError

def filter(funct, lis):
    '''
    return new list where the applied function on elements
    is true for all elements
    '''
    a_list = []
    for i in range(len_list(lis)):
        if funct([nth_element(lis, i)]) == '@t':
            a_list.append(nth_element(lis, i))
    return build_list(a_list)
    
#helper function
def if_filter(args):
    if len(args) == 2:
        return filter(args[0], args[1])
    else:
        raise CarlaeEvaluationError    

def reduce(funct, lis, initial):
    '''
    returns a list by applying a function successively to each element
    '''
    current = initial
    for i in range(len_list(lis)):
        current = funct([current, nth_element(lis, i)])
    return current

#helper function
def if_reduce(args):
    if len(args) == 3:
        return reduce(args[0], args[1], args[2])
    else:
        raise CarlaeEvaluationError   

def begin(args):
    return args[-1]

carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": lambda args: args[0] if len(args) == 1 else args[0] * carlae_builtins["*"](args[1:]),
    "/": lambda args:  1 / args[0] if len(args) == 1 else args[0] / carlae_builtins["*"](args[1:]), 
    "@t": '@t',
    "@f": '@f',
    "=?": lambda args: '@t' if len(args) == 1 else compare(args, '=='), 
    ">": lambda args: '@t' if len(args) == 1 else compare(args, '>'),
    ">=": lambda args: '@t' if len(args) == 1 else compare(args, '>='),
    "<": lambda args: '@t' if len(args) == 1 else compare(args, '<'),
    "<=": lambda args: '@t' if len(args) == 1 else compare(args, '<='),
    "not": not_function,
    "nil": 'nil',
    "list": lambda args: 'nil' if len(args) == 0 else build_list(args),
    "list?": is_linked_list,
    "pair": build_pair,
    "head": if_head,
    "tail": if_tail,
    "length": if_length,
    "nth": if_nth,
    "concat": concat,
    "map": if_map,
    "filter": if_filter,
    "reduce": if_reduce,
    "begin": begin 


}

##############
# Evaluation #
##############

#Environment Class
class Environment():
    def __init__(self, parent = None, variable = None):
        #parent environment (enclosed inside) and variable dictionary
        self.parent = parent
        if variable == None:
            self.variables = dict()
        else:
            self.variables = variable

    def set_item(self, name, expr): #binds variable to value
        self.variables[name] = expr
    
    def get_item(self, var): #searches for the variable
        if var in self.variables: #binding in the environment
            return self.variables[var] 
        if self.parent: #if environment has a parent, check parent environment
            return self.parent.get_item(var)
        else: #no binding in environment and no parent environment
            raise CarlaeNameError

    def get_evmt_item(self, var):
        if var in self.variables: #binding in the environment
            return self
        if self.parent: #if environment has a parent, check parent environment
            return self.parent.get_evmt_item(var)
        else: #no binding in environment and no parent environment
            raise CarlaeNameError

    def delete(self, var):
        '''
        Removes variable binding in current environment
        '''
        if var in self.variables:
            temp = self.variables[var]
            del self.variables[var]
            return temp
        else:
            raise CarlaeNameError

#Function Class 
class Function:
    def __init__(self, param, expr, environment):
        self.param = param #parameters
        self.expr = expr #expression
        self.environment = environment 

    def __call__(self, argument):
        a_dict = {}
        if len(self.param) != len(argument):
            raise CarlaeEvaluationError
        else:
            for i in range(len(self.param)):
                a_dict[self.param[i]] = argument[i] #sets params to arguments passed n
        child = Environment(parent = self.environment, variable = a_dict) #creates a new evmt who has a parent evmt
        return evaluate(self.expr, child) #evaluate the function

#Pair Class
class Pair():
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def get_head(self):
        '''
        returns head
        '''
        return self.head 
    
    def get_tail(self):
        '''
        returns tail'''
        return self.tail 

    def copy(self):
        '''
        Creates copy of self Pair
        '''
        head = self.head if isinstance(self.head, str) or is_num(self.head) else self.head.copy()
        tail = self.tail if isinstance(self.tail, str) or is_num(self.tail) else self.tail.copy()
        return Pair(head, tail)

    def __str__(self):
        '''
        return string representation of Pair
        '''
        return(f'Pair ({str(self.head)} , {str(self.tail)})')


#helper function
def is_symbol(tree):
    """
    returns true if string

    """
    if type(tree) is str:
        return True
    else:
        return False

#helper function
def is_num(tree):
    """
    returns true if number

    """
    if type(tree) is int or type(tree) is float:
        return True
    else:
        return False

#helper function
def is_pair(tree):
    if isinstance(tree, Pair):
        return True
    else:
        return False

def evaluate(tree, environment=None):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if environment == None: #environment has no parent
        environment = Environment(parent = Environment(variable= carlae_builtins)) #builtin parent Carlae dictionary 
        
    if is_symbol(tree):
        return environment.get_item(tree)
        
    elif is_num(tree):
        return tree
    
    elif isinstance(tree, Pair):
        return tree
    
    #Needs further evaluation
    elif type(tree) == list:
        if tree == []:
            raise CarlaeEvaluationError
        key = tree[0]
        if key == "function":
            length = len(tree)
            param = tree[1]
            expr = tree[2]
            if length == 3 or type(param) == list:
                return Function(param, expr, environment) #parameter, expression, environment
            else:
                raise CarlaeEvaluationError

        elif key == ":=":
            expr = tree[1]
            if type(expr) != list:
                val = evaluate(tree[2], environment)
                environment.set_item(tree[1], val) #binds variable to value 
                return val
            else:
                # define functions 
                return evaluate([':=', expr[0], ["function", expr[1:], tree[2]]], environment)
        
        #evaluate for if conditional        
        elif key == 'if':
            length = len(tree)
            condition = tree[1]
            if evaluate(condition, environment) == '@t':
                return evaluate(tree[2], environment)
            else:
                return evaluate(tree[3], environment)
        
        #short-circuit case for and & or
        elif key == 'and':
            index = 1
            while index < len(tree) and evaluate(tree[index], environment) == '@t':
                index += 1
            if index == len(tree):
                return '@t'
            else:
                return '@f'
        elif key == 'or':
            index = 1
            while index < len(tree) and evaluate(tree[index], environment) != '@t':
                index += 1
            if index < len(tree):
                return '@t' 
            else:
                return '@f'


        #special case: del , let, and set!
        elif key == 'del':
            if len(tree) == 2:
                return environment.delete(tree[1])
            else:
                raise CarlaeEvaluationError

        elif key == 'let':
            evmt = Environment(parent=environment, variable = None)
            if len(tree) == 3:
                for i in tree[1]:
                    evmt.set_item(i[0], evaluate(i[1], environment))
                return evaluate(tree[2], evmt)
            else:
                raise CarlaeEvaluationError

        elif key == 'set!':
            if len(tree) == 3:
                evmt = environment.get_evmt_item(tree[1])
                eval = evaluate(tree[2], environment)
                evmt.set_item(tree[1], eval)
                return eval
            else:
                raise CarlaeEvaluationError

        else:
            try:
                a_list = [] 
                i = 1
                while i < len(tree):
                    a_list.append(evaluate(tree[i], environment)) #recurses and evaluates each item in tree from 1 to end
                    i+=1
                return evaluate(key, environment)(a_list)
            except TypeError:
                raise CarlaeEvaluationError
    else:
        raise CarlaeEvaluationError

def repl():
    '''
    for testing
    '''
    environment = Environment(parent = Environment(variable= carlae_builtins))
    for file_name in sys.argv[1:]:
        evaluate_file(file_name, environment)
    while True:
        inp = input("in>")
        if inp == "STOP":
            break
        else:
            parsed = parse(tokenize(inp))
            eval =  evaluate(parsed,environment)
            print("out>", eval)

def result_and_env(tree, environment = None):
    if environment == None:
        environment = Environment(parent = Environment(variable= carlae_builtins))
    return evaluate(tree, environment), environment

def evaluate_file(file_name, env = None):
    '''
    evaluates the file
    '''
    file = open(file_name)
    file = file.read()
    return evaluate(parse(tokenize(file)), env)

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    doctest.testmod()

    repl()



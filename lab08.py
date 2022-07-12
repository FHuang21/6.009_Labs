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
    ["cat", ["dog", ["tomato"]]]
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


carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": lambda args: args[0] if len(args) == 1 else args[0] * carlae_builtins["*"](args[1:]),
    "/": lambda args:  1 / args[0] if len(args) == 1 else args[0] / carlae_builtins["*"](args[1:]), 
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

#Function Class 
class Function:
    def __init__(self, param, expr, environment):
        self.param = param #parameters
        self.expr = expr #expression
        self.environment = environment #pointer to environment in which the function was defined (function's enclosing frame)4

    def __call__(self, argument):
        a_dict = {}
        if len(self.param) != len(argument):
            raise CarlaeEvaluationError
        else:
            for i in range(len(self.param)):
                a_dict[self.param[i]] = argument[i] #sets params to arguments passed n
        child = Environment(parent = self.environment, variable = a_dict) #creates a new evmt who has a parent evmt
        return evaluate(self.expr, child) #evaluate the function

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
    
    #Needs further evaluation
    elif type(tree) == list:
        if tree == []:
            raise CarlaeEvaluationError
        if tree[0] == "function":
            length = len(tree)
            param = tree[1]
            expr = tree[2]
            if length == 3 or type(param) == list:
                return Function(param, expr, environment) #parameter, expression, environment
            else:
                raise CarlaeEvaluationError

        elif tree[0] == ":=":
            expr = tree[1]
            if type(expr) != list:
                val = evaluate(tree[2], environment)
                environment.set_item(tree[1], val) #binds variable to value 
                return val
            else:
                # define functions 
                return evaluate([':=', expr[0], ["function", expr[1:], tree[2]]], environment)
        else:
            try:
                a_list = [] 
                i = 1
                while i < len(tree):
                    a_list.append(evaluate(tree[i], environment)) #recursively evaluates each item in tree[1:]
                    i+=1
                return evaluate(tree[0], environment)(a_list) #performs function on the list created
            except TypeError:
                raise CarlaeEvaluationError
    else:
        raise CarlaeEvaluationError

def repl():
    environment = Environment(parent = Environment(variable= carlae_builtins))
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

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    doctest.testmod()
    repl()
    

#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""
     
import sys
import typing
import doctest
from xmlrpc.client import boolean
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

'''
When we commit to representing problems in CNF, we can represent:

a variable as a Python string
a literal as a pair (a tuple), containing a variable and a Boolean value (False if not appears in this literal, True otherwise)
a clause as a list of literals
a formula as a list of clauses
'''
#helper functions
def shorten(formula, literal):
    '''
    returns the shortened formula by setting a literal to a boolean
    (literal is a pair(tuple), containing a variable and a Boolean value)
    '''  
    not_literal = (literal[0], not literal[1])
    shortened = []
    for index in range(len(formula)): #iterate through clauses in formula
        if literal not in formula[index]: #check if given literal is not in clause
            new_list = formula[index].copy()
            shortened.append(new_list) #append clause to new shortened formula
            for i in shortened[len(shortened)-1]:
                if not_literal in shortened[len(shortened)-1]: #if literal with not Boolean is in clause
                    shortened[len(shortened)-1].remove(not_literal) #remove literal with not Boolean
    return shortened

def merge_dict(dict1, dict2):
    '''
    Combines two dictionaries with their keys and values
    into one single dictionary
    '''
    a_dict = dict1.copy()
    a_dict.update(dict2)
    return a_dict

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.
    Returns a dictionary mapping every assignment to a boolean that satisfies the formula

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    #print(formula)
    #base case: if formula is empty list
    if formula == []:
        return {}
    
    else:
        initial_val = min(formula, key = lambda x: len(x))[0][0]
        #initial_val = formula[0][0][0]    #formula --> clause  --> literal --> first index: assignment
        lits = [True,False]
        for lit in lits:
            new_form = shorten(formula,(initial_val,lit))
            #print(new_form)
            #if new_form is satisfied with initial value's boolean assignment
            if new_form == []:
                return {initial_val: lit}
            #If there's an empty list in new formula, then that means all literals in a clause have been removed due to assigned boolean not matching constraints
            elif [] in new_form:
                continue
            #recursive step
            else:
                new_dict = satisfying_assignment(new_form)
                
                #if boolean assignment is False
                if lit == False:
                    if new_dict != None:
                        return merge_dict(new_dict, {initial_val: lit})             
                    else:
                        return None
                #if boolean assignment is True
                else:
                    if new_dict != None:
                        return merge_dict(new_dict, {initial_val: lit})
    
                
#helper functions
def combinations(a_list, length):
    '''
    return list of lists containing all combinations of length n of elements in a list
    '''
    combo_list = []
    #base case
    if length == 0:
        return [[]]
    
    for i in range(len(a_list)):
        current = a_list[i]
        remaining_list = a_list[i+1:]
        #recursive function
        for pos in combinations(remaining_list, length - 1):
            combo_list.append([current] + pos)
    return combo_list

# Students are only assigned to rooms included in their preferences.
def assign_preferences(student_preferences):
    formula = []
    #loops through every student
    for student in student_preferences:
        preference = []
        #loops through each students' preference
        for room in student_preferences[student]:
            #adds to list if preference is True
            preference.append((student + '_' + room, True))
        formula.append(preference)
    return formula
# Each student is assigned to exactly one room.
def assign_one_student(student_preferences,room_capacities):
    formula = []
    rooms = []
    #for each room in all rooms
    for room in room_capacities:
        rooms.append(room)
    #for each student in all students
    for student in student_preferences:
        combo_list = []
        for room in rooms: #makes list of literals
            combo_list.append((student + '_' + room, False))
        new_combo_list = combinations(combo_list, 2) #uses combinations helper function to find new list of combinations of literals
        formula.extend(new_combo_list)
    return formula

# No room has more assigned students than it can fit.
def assign_room_limit(student_preferences,room_capacities):
    formula = []
    students = []
    #for each student in all students
    for student in student_preferences:
        students.append(student)
    #for each room in all rooms
    for room in room_capacities:
        students_preferred = []
        #for each student
        for i in students:
            #if student has room in their preferences, add to preferred students list
            if room in student_preferences[i]:
                students_preferred.append(i)
        #check if room capacity is less than students who prefer said room
        if room_capacities[room] < len(students_preferred):
            combo_list = []
            for student in students:
                combo_list.append((student + '_' + room, False))
            new_combo_list = combinations(combo_list, room_capacities[room]+1)
            formula.extend(new_combo_list)
    return formula
    

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    #return fun1 + func2 + func3
    formula = []
    formula.extend(assign_preferences(student_preferences))
    formula.extend(assign_one_student(student_preferences, room_capacities))
    formula.extend(assign_room_limit(student_preferences, room_capacities))
    return formula

if __name__ == '__main__':
    import doctest
    # _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)


    saman = False
    mike = False
    charles = False
    jonathan = False
    tim = True

    pickles = False
    vanilla = True
    chocolate = False
    rule1 = (saman or mike or charles or jonathan or tim)
    # At least one of them must have committed the crime!  Here, one of these
    # variables being True represents that person having committed the crime.



    rule2 = ((not saman or not mike)
        and (not saman or not charles)
        and (not saman or not jonathan)
        and (not saman or not tim)
        and (not mike or not charles)
        and (not mike or not jonathan)
        and (not mike or not tim)
        and (not charles or not jonathan)
        and (not charles or not tim)
        and (not jonathan or not tim))
    # At most one of the suspects is guilty.  In other words, for any pair of
    # suspects, at least one must be NOT guilty (so that we cannot possibly find
    # two or more people guilty).

    # Together, rule2 and rule1 guarantee that exactly one suspect is guilty.


    rule3 = ((not chocolate or not vanilla or not pickles)
        and (chocolate or vanilla)
        and (chocolate or pickles)
        and (vanilla or pickles))
    # Here is our rule that the cupcakes included exactly two of the flavors.  Put
    # another way: we can't have all flavors present; and, additionally, among
    # any pair of flavors, at least one was present.


    rule4 = ((not saman or pickles)
        and (not saman or not chocolate)
        and (not saman or not vanilla))
    # If Saman is guilty, this will evaluate to True only if only pickles-flavored
    # cupcakes were present.  If Saman is not guilty, this will always evaluate to
    # True.  This is our way of encoding the fact that, if Saman is guilty, only
    # pickles-flavored cupcakes must have been present.


    rule5 = (not charles or jonathan) and (not jonathan or charles)
    # If Charles ate cupcakes without sharing with Jonathan, the first case will fail
    # to hold.  Likewise for Jonathan eating without sharing.  Since Charles and Jonathan
    # only eat cupcakes together, this rule excludes the possibility that only one
    # of them ate cupcakes.


    rule6 = ((not mike or chocolate)
        and (not mike or vanilla)
        and (not mike or pickles))
    # If Mike is the culprit and we left out a flavor, the corresponding case here
    # will fail to hold.  So this rule encodes the restriction that Mike can only
    # be guilty if all three types of cupcakes are present.


    satisfied = rule1 and rule2 and rule3 and rule4 and rule5 and rule6

    #print(satisfied)
    rule3 = [[('chocolate', True), ('vanilla', False), ('pickles', True)],
         [('chocolate', True), ('vanilla', True)],
         [('chocolate', True), ('pickles', True)],
         [('vanilla', True), ('pickles', True)]]
    cnf = [[("a",True),("b",True)], [("a",False),("b",False),("c",True)], [("b",True),("c",True)], [("b",True),("c",False)], [("a",False),("b",False),("c",False)]]
    # test = [
    # [('a', True), ('b', True), ('c', True)],
    # [('a', False), ('f', True)],
    # [('d', False), ('e', True), ('a', True), ('g', True)],
    # [('h', False), ('c', True), ('a', False), ('f', True)],
    # ]
    test = [[("d",True),("b",True)],[("a",True),("b",True)], [("a",False),("b",False),("c",True)],
     [("b",True),("c",True)], [("b",True),("c",False)], [("a",False),("b",False),("c",False)]]
    test2 = cnf = [[('a', True), ('a', False)], 
    [('b', True), ('a', True)], 
    [('b', True)], 
    [('b', False), ('b', False), ('a', False)], 
    [('c', True), ('d', True)], 
    [('c', True), ('d', True)]]
    print(satisfying_assignment(test2))
    #print(satisfying_assignment(cnf))
    #print(shorten(test,('a', True )))
    #print(assign_one_student({'Alice': {'basement', 'penthouse'},
                        #     'Bob': {'kitchen'},
                        #     'Charles': {'basement', 'kitchen'},
                        #     'Dana': {'kitchen', 'penthouse', 'basement'}},
                        #    {'basement': 1,
                        #     'kitchen': 2,
                        #     'penthouse': 4}))
    #print(satisfying_assignment(test))

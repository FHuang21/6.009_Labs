# 6.009 Lab 2: Snekoban

import json
from tkinter import Y
import typing

from pyparsing import empty

# NO ADDITIONAL IMPORTS!

#x --> rows, y --> columns
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    #makes the game state as a dictionary with each object type as a list
    #each list corresponding to an object contains tuples of each object's (y,x) components
    game = {
        'rows': len(level_description),
        'columns': len(level_description[0]),
        'player': [],
        'wall': [],
        'target': [],
        'computer': [],
    }
    #Loops through entire level description and appends each object's position to the corresponding list value in the game dictionary
    #x --> rows, y --> columns
    for x in range(len(level_description)):
        for y in range(len(level_description[x])):
            for z in level_description[x][y]:
                if z == 'player': 
                    game['player'].append((x,y)) #appends player position to game['player']
                elif z == 'wall':
                    game['wall'].append((x,y))  #appends wall position to game['wall']
                elif z == 'target':
                    game['target'].append((x,y)) #appends target position to game['target']
                elif z == 'computer':
                    game['computer'].append((x,y)) #appends computer position to game['computer']
    return game
     

def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    if not game['computer'] or not game['target']:
        return False        
    for pos in game['target']:
        if pos not in game['computer']:
            return False
    return True
        

def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    current_pos = game['player'][0]
    new_pos = (current_pos[0] + direction_vector[direction][0], current_pos[1] + direction_vector[direction][1])
    new_game = {
             'rows': game['rows'],
        'columns': game['columns'],
        'player': game['player'].copy(),
        'wall': game['wall'].copy(),
        'target': game['target'].copy(),
        'computer': game['computer'].copy(),
    }
    #new_pos contains a wall
    if new_pos in game['wall']: #returns unchanged game because player cannot move in this direction
        return new_game 
    #new_pos contains a computer
    elif new_pos in game['computer']:
        computer_blocker = (new_pos[0] + direction_vector[direction][0], new_pos[1] + direction_vector[direction][1]) #blocker position for a computer
        if computer_blocker in game['wall'] or computer_blocker in game['computer']: #returns unchanged game if computer_blocker is a wall or a computer
            return new_game
        else: #returns new_game with computer moved to computer_blocker position and player moved to original computer position
            new_game['computer'].append(computer_blocker)
            new_game['computer'].remove(new_pos)
            new_game['player'].append(new_pos)
            new_game['player'].remove(current_pos)
            return new_game
    else: #returns new_game with player movement
        new_game['player'].append(new_pos)
        new_game['player'].remove(current_pos)
        return new_game  

def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    level = []
    for row in range(game['rows']):
        level.append([])
        for column in range(game['columns']):
            level[row].append([])
            if (row, column) in game['player']:
                level[row][column].append('player')
            if (row, column) in game['wall']:
                level[row][column].append('wall')
            if (row, column) in game['computer']:
                level[row][column].append('computer')
            if (row, column) in game['target']:
                level[row][column].append('target')  
    return level          


            

            

def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    shortest_path = []
    agenda_path = [shortest_path] #initialize agenda for paths
    agenda_game = [game] # initialize agenda for games
    visited = set() #initialize visited set
    directions = ['up', 'down', 'left', 'right']
    while agenda_game: #satisfy condition of having games still in agenda to check through
        game = agenda_game.pop(0) #deletes game from agenda
        shortest_path = agenda_path.pop(0) #deletes path from agenda
        for i in directions: # looks through all four directions
            new_game = step_game(game, i) #initialize new game state
            coordinates = tuple(new_game['player'] + sorted(new_game['computer'])) #sets unique player & computer locations on game to coordinates to be added to visited game states
            if victory_check(game): #checks if player won
                return shortest_path
            if coordinates not in visited: #if a new unique coordinate, adds to visited
                agenda_game.append(new_game)
                agenda_path.append(shortest_path+[i])
                visited.add(coordinates)
    return None
    




if __name__ == "__main__":
    level_description =  [
        [['wall'], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target', 'computer']],
       # [['wall'], ['computer'], ['target']],
    ]
    game = new_game(level_description)
    print(game)
    #print(dump_game(game))
    print(step_game(game, 'down'))
    print(victory_check(game))
    

#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

from dataclasses import replace
from socket import if_indextoname
import typing
import doctest
from venv import create

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    # board = []
    # for r in range(num_rows):
    #     row = []
    #     for c in range(num_cols):
    #         if [r, c] in bombs or (r, c) in bombs:
    #             row.append('.')
    #         else:
    #             row.append(0)
    #     board.append(row)
    # visible = []
    # for r in range(num_rows):
    #     row = []
    #     for c in range(num_cols):
    #         row.append(False)
    #     visible.append(row)
    # for r in range(num_rows):
    #     for c in range(num_cols):
    #         if board[r][c] == 0:
    #             neighbor_bombs = 0
    #             if 0 <= r-1 < num_rows:
    #                 if 0 <= c-1 < num_cols:
    #                     if board[r-1][c-1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r < num_rows:
    #                 if 0 <= c-1 < num_cols:
    #                     if board[r][c-1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r+1 < num_rows:
    #                 if 0 <= c-1 < num_cols:
    #                     if board[r+1][c-1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r-1 < num_rows:
    #                 if 0 <= c < num_cols:
    #                     if board[r-1][c] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r < num_rows:
    #                 if 0 <= c < num_cols:
    #                     if board[r][c] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r+1 < num_rows:
    #                 if 0 <= c < num_cols:
    #                     if board[r+1][c] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r-1 < num_rows:
    #                 if 0 <= c+1 < num_cols:
    #                     if board[r-1][c+1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r < num_rows:
    #                 if 0 <= c+1 < num_cols:
    #                     if board[r][c+1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r+1 < num_rows:
    #                 if 0 <= c+1 < num_cols:
    #                     if board[r+1][c+1] == '.':
    #                         neighbor_bombs += 1
    #             board[r][c] = neighbor_bombs
    # return {
    #     'dimensions': (num_rows, num_cols),
    #     'board': board,
    #     'visible': visible,
    #     'state': 'ongoing'}
    return new_game_nd((num_rows, num_cols), bombs)

def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    # if game['state'] == 'defeat' or game['state'] == 'victory':
    #     game['state'] = game['state']  # keep the state the same
    #     return 0

    # if game['board'][row][col] == '.':
    #     game['visible'][row][col] = True
    #     game['state'] = 'defeat'
    #     return 1

    # bombs = 0
    # covered_squares = 0
    # for r in range(game['dimensions'][0]):
    #     for c in range(game['dimensions'][1]):
    #         if game['board'][r][c] == '.':
    #             if game['visible'][r][c] == True:
    #                 bombs += 1
    #         elif game['visible'][r][c] == False:
    #             covered_squares += 1
    # if bombs != 0:
    #     # if bombs is not equal to zero, set the game state to defeat and
    #     # return 0
    #     game['state'] = 'defeat'
    #     return 0
    # if covered_squares == 0:
    #     game['state'] = 'victory'
    #     return 0

    # if game['visible'][row][col] != True:
    #     game['visible'][row][col] = True
    #     revealed = 1
    # else:
    #     return 0

    # if game['board'][row][col] == 0:
    #     num_rows, num_cols = game['dimensions']
    #     if 0 <= row-1 < num_rows:
    #         if 0 <= col-1 < num_cols:
    #             if game['board'][row-1][col-1] != '.':
    #                 if game['visible'][row-1][col-1] == False:
    #                     revealed += dig_2d(game, row-1, col-1)
    #     if 0 <= row < num_rows:
    #         if 0 <= col-1 < num_cols:
    #             if game['board'][row][col-1] != '.':
    #                 if game['visible'][row][col-1] == False:
    #                     revealed += dig_2d(game, row, col-1)
    #     if 0 <= row+1 < num_rows:
    #         if 0 <= col-1 < num_cols:
    #             if game['board'][row+1][col-1] != '.':
    #                 if game['visible'][row+1][col-1] == False:
    #                     revealed += dig_2d(game, row+1, col-1)
    #     if 0 <= row-1 < num_rows:
    #         if 0 <= col < num_cols:
    #             if game['board'][row-1][col] != '.':
    #                 if game['visible'][row-1][col] == False:
    #                     revealed += dig_2d(game, row-1, col)
    #     if 0 <= row < num_rows:
    #         if 0 <= col < num_cols:
    #             if game['board'][row][col] != '.':
    #                 if game['visible'][row][col] == False:
    #                     revealed += dig_2d(game, row, col)
    #     if 0 <= row+1 < num_rows:
    #         if 0 <= col < num_cols:
    #             if game['board'][row+1][col] != '.':
    #                 if game['visible'][row+1][col] == False:
    #                     revealed += dig_2d(game, row+1, col)
    #     if 0 <= row-1 < num_rows:
    #         if 0 <= col+1 < num_cols:
    #             if game['board'][row-1][col+1] != '.':
    #                 if game['visible'][row-1][col+1] == False:
    #                     revealed += dig_2d(game, row-1, col+1)
    #     if 0 <= row < num_rows:
    #         if 0 <= col+1 < num_cols:
    #             if game['board'][row][col+1] != '.':
    #                 if game['visible'][row][col+1] == False:
    #                     revealed += dig_2d(game, row, col+1)
    #     if 0 <= row+1 < num_rows:
    #         if 0 <= col+1 < num_cols:
    #             if game['board'][row+1][col+1] != '.':
    #                 if game['visible'][row+1][col+1] == False:
    #                     revealed += dig_2d(game, row+1, col+1)

    # bombs = 0  # set number of bombs to 0
    # covered_squares = 0
    # for r in range(game['dimensions'][0]):
    #     # for each r,
    #     for c in range(game['dimensions'][1]):
    #         # for each c,
    #         if game['board'][r][c] == '.':
    #             if game['visible'][r][c] == True:
    #                 # if the game visible is True, and the board is '.', add 1 to
    #                 # bombs
    #                 bombs += 1
    #         elif game['visible'][r][c] == False:
    #             covered_squares += 1
    # bad_squares = bombs + covered_squares
    # if bad_squares > 0:
    #     game['state'] = 'ongoing'
    #     return revealed
    # else:
    #     game['state'] = 'victory'
    #     return revealed
    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    # output = [[[0] for _ in range(game['dimensions'][1]) ] for _ in range(game['dimensions'][0])]
    # for row in range(game['dimensions'][0]):
    #     for column in range(game['dimensions'][1]):
            
    #         if xray == False:
    #             if game['visible'][row][column] == False:
    #                 output[row][column] = '_'
    #             else:
    #                 output[row][column] = str(game['board'][row][column])

    #         else: #xray is True
    #             if game['board'][row][column] == 0:
    #                 output[row][column] = ' '
    #             else:
    #                 output[row][column] = str(game['board'][row][column])
    # return output
    return render_nd(game, xray)

def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    ASCII = ""
    locations = render_2d_locations(game, xray)
    for row in range(game['dimensions'][0]):
        for column in range(game['dimensions'][1]):
            if xray == True:
                ASCII += locations[row][column]
            else: #xray == False
                if game['visible'][row][column] == False:
                    ASCII += '_'
                else:
                    ASCII += locations[row][column]
        if row != game['dimensions'][0] - 1:
            ASCII += "\n"
    return ASCII           


#helper functions
def get_coordinate_value(game_board, coord_lists):
    '''A function that, given an N-d array and a tuple/list of coordinates,
        returns the value at those coordinates in the array.

    >>> get_coordinate_value([['_', '3', '1', '_'], 
    ...                ['_', '_', '1', '_']], (1, 2))
    '1'
    >>> get_coordinate_value([['_', '3', '1', '_'], 
    ...                ['_', '_', '1', '_']], (0, 0))
    '_'
    '''
    #base case
    if len(coord_lists) == 1:
        return game_board[coord_lists[0]]
    #recursive step
    else:
        return get_coordinate_value(game_board[coord_lists[0]], coord_lists[1:])
        
def replace_value(game_board, coord_lists, value):
    '''A function that, given an N-d array, a tuple/list of coordinates, and a value, 
    replaces the value at those coordinates in the array with the given value.
    >>> a = [[[0, 0], [1, 1], [1, 1]], [[0, 0], [1, 1], ['.', 1]], [[0, 0], [1, 1], [1, 1]]]
    >>> replace_value(a ,(2,1,0), value = 'w')
    >>> a
    [[[0, 0], [1, 1], [1, 1]], [[0, 0], [1, 1], ['.', 1]], [[0, 0], ['w', 1], [1, 1]]]

    '''
    #base case    
    if len(coord_lists) == 1:
        game_board[coord_lists[0]] = value
        #print(game_board)
    #recursive step
    else:
        replace_value(game_board[coord_lists[0]], coord_lists[1:], value)
    
def create_array(dimensions, value):
    '''A function that, given a list of dimensions and a value, creates a new N-d array 
    with those dimensions, where each value in the array is the given value. 
    >>> create_array([2, 2, 2], 2)
    [[[2, 2], [2, 2]], [[2, 2], [2, 2]]]
    
    >>> create_array([2, 4, 3], 2)
    [[[2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2]], [[2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2]]]
    '''
    dim = dimensions[0]
    if len(dimensions) == 1:
        return [value] * dim
    else:
        return [create_array(dimensions[1:], value) for var in range(dim)]

def game_state(game):
    '''A function that, given a game, returns the state of that game 
    ('ongoing', 'defeat', or 'victory').
    >>> game_state({
    ... 'dimensions': [4, 3],
    ... 'board': [[1,  '.',  2], [1,   2,  '.'], [1,   2,   1], ['.', 1,   0]],
    ... 'visible': [[True, False, False], [False, True, False], [False, True, True], [False, True, True]],
    ... 'state': 'ongoing',
    ...            })
    'ongoing'  
    >>> game_state({
    ... 'dimensions': [4, 3],
    ... 'board': [[1,  '.',  2], [1,   2,  '.'], [1,   2,   1], ['.', 1,   0]],
    ... 'visible': [[True, False, True], [True, True, False], [True, True, True], [False, True, True]],
    ... 'state': 'victory',
    ...            })
    'victory'  
    >>> game_state({
    ... 'dimensions': [4, 3],
    ... 'board': [[1,  '.',  2], [1,   2,  '.'], [1,   2,   1], ['.', 1,   0]],
    ... 'visible': [[True, True, True], [True, True, False], [True, True, True], [False, True, True]],
    ... 'state': 'defeat',
    ...            })
    'defeat'  
    '''
    coord_list = get_possible_coordinates(game['dimensions'])
    for coordinate in coord_list:
        #print('coordinate: ', coordinate)
        if get_coordinate_value(game['board'] , coordinate) == "." and get_coordinate_value(game['visible'], coordinate) == True:
            game['state'] = 'defeat'
            return game['state']
    
    for coordinate in coord_list:
            if get_coordinate_value(game['board'] , coordinate) != "." and get_coordinate_value(game['visible'], coordinate) == False:
                game['state'] = 'ongoing'
                return game['state']
    game['state'] = 'victory'
    return game['state']

def get_neighbors(coordinates, dimensions):
    '''
    A function that returns all the neighbors of a given set of coordinates in a given game.
    >>> get_neighbors([1, 1], [3, 3])
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]    
    >>> get_neighbors([5, 13, 0], [10, 20, 3])
    [(4, 12, 0), (4, 12, 1), (4, 13, 0), (4, 13, 1), (4, 14, 0), (4, 14, 1), (5, 12, 0), (5, 12, 1), (5, 13, 0), (5, 13, 1), (5, 14, 0), (5, 14, 1), (6, 12, 0), (6, 12, 1), (6, 13, 0), (6, 13, 1), (6, 14, 0), (6, 14, 1)]
    '''
    neighbors_list = []
    #base case
    if len(coordinates) == 1:
        for i in range(-1, 2):
            coord_neighbor = coordinates[0] + i
            if coord_neighbor >=0 and coord_neighbor < dimensions[0]:
                neighbors_list.append((coord_neighbor,))
    #recursive step
    else:
        for i in range(-1, 2):
            coord_neighbor = coordinates[0] + i
            if coord_neighbor >=0 and coord_neighbor < dimensions[0]:
                for j in get_neighbors(coordinates[1:], dimensions[1:]):
                    neighbors_list.append((coord_neighbor,)+(j))
    return neighbors_list

def get_possible_coordinates(dimensions):
    '''A function that returns all possible coordinates in a given board based
    on its dimensions.
        'board': [[1,  '.',  2], [1,   2,  '.'], [1,   2,   1], ['.', 1,   0]],
    >>> get_possible_coordinates([4, 3])
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 2)]
    '''
    coord_list = []
    if len(dimensions) == 1:
        for i in range(dimensions[0]):
            coord_list.append((i,))
    else:
        for i in range(dimensions[0]):
            for j in get_possible_coordinates(dimensions[1:]):
                coord_list.append((i,)+(j))
    return coord_list

# N-D IMPLEMENTATION

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    game_array = create_array(dimensions, 0)
    game = {
        'board': [],
        'dimensions': dimensions,
        'state': 'ongoing',
        'visible': create_array(dimensions, False)
    }
    for bomb in bombs: #loc is a tuple coordinate of bomb location: Ex) (0, 0, 1)
        replace_value(game_array, bomb, '.')
        for neighbor in get_neighbors(bomb, list(dimensions)): #neighbor is list coordinate of bomb neighbor: Ex) (0, 0, 1)
            if get_coordinate_value(game_array, neighbor) != '.': 
                value = get_coordinate_value(game_array, neighbor)
                replace_value(game_array, neighbor, value + 1)
    game['board'] = game_array
    return game


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    if game['state'] != 'ongoing':
        return 0

    not_bomb_squares = 0
    visible_squares = 0

    possible_coords = get_possible_coordinates(game['dimensions']) #list of all possible coordinates
    for coord in possible_coords: #coord is a coord location
        #print ('coord, ', coord)
        if get_coordinate_value(game['board'], coord) != '.':
            not_bomb_squares+=1
        if get_coordinate_value(game['visible'], coord) == True:
            visible_squares +=1
    
    to_check = [coordinates]
    squares_searched = 0

    # do fill when get_coordinate_value(game['board'], coordinates) == '0'
    while visible_squares <= not_bomb_squares and to_check:
        this_square = to_check.pop(0)
        #check if coord is already visible before
        if get_coordinate_value(game['visible'], this_square) == False:
            replace_value(game['visible'], this_square, True)
            visible_squares +=1
            squares_searched += 1

            if get_coordinate_value(game['board'], this_square) == '.':
                game['state'] = 'defeat'
                return squares_searched
            elif get_coordinate_value(game['board'], this_square) != 0:
                continue
            else: #square value is 0: no bombs in neighbors
                for neighbor in get_neighbors(this_square, game['dimensions']):
                    to_check.append(neighbor)
    
    if visible_squares == not_bomb_squares:
        game['state'] = 'victory'
    return squares_searched

        

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    nd_array = create_array(game['dimensions'], ' ')
    for coords in get_possible_coordinates(game['dimensions']):
        value = get_coordinate_value(game['board'], coords)
        if xray == False:
            if get_coordinate_value(game['visible'], coords) == False:
                replace_value(nd_array, coords, '_')
            else: #coord value is visible 
                if value != 0:
                    replace_value(nd_array, coords, str(value))
        else: #xray == True
            if value != 0:
                replace_value(nd_array, coords, str(value))
    return nd_array


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    dig_nd,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=True)
    # # 
    #new_game = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    # print(new_game)

    # a = [[[0, 0], [1, 1], [1, 1]], [[0, 0], [1, 1], ['.', 1]], [[0, 0], [1, 1], [1, 1]]]
    # # >>> replace_value(a ,(2,1,0), value = 'w')
    # # >>> a

    # g = {'dimensions': (2, 4, 2),
    #      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    #                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    #      'visible': [[[False, False], [False, True], [False, False],
    #                 [False, False]],
    #               [[False, False], [False, False], [False, False],
    #                 [False, False]]],
    #       'state': 'ongoing'}
    # dig_nd(g, (0, 3, 0))
    # dump(g)
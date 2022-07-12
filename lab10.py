"""6.009 Lab 10: Snek Is You Video Game"""

import doctest
from operator import truediv
from types import GenericAlias

from pytest import Instance

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

class General():
    '''
    Object on the game board
    -superclass for text and graphic
    '''
    def __init__(self, name, location):
        '''
        Inputs: Name is either all caps or all lowercase, location is a tuple
        '''
        self.name = name
        self.loc = location
        self.property = {}
        #default rules
        for prop in PROPERTIES:
            self.property[prop] = False
        if self.name in WORDS: #default
            self.property['PUSH'] = True

    def set_property(self, property, bool):
        '''
        sets property of obj
        '''
        self.property[property] = bool
    
    def change_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_location(self):
        return self.loc

    def is_you(self):
        return self.property['YOU']

    def update_location(self, location):
        self.loc = location
    
    def is_property(self, prop):
        if prop == 'PUSH':
            return self.property['PUSH']
        elif prop == 'PULL':
            return self.property['PULL']    
        elif prop == 'STOP':
            return self.property['STOP']    
        elif prop == 'WIN':
            return self.property['WIN']   
        elif prop == 'DEFEAT': 
            return self.property['DEFEAT']
        else:
            raise TypeError

    def move(self, location, direction, objects, game, previous = None):
        '''
        Inputs: location self wants to move to, direction, other objects at that location, 
        game board
        Output: Returns a dictionary of the self object and the new location that self has moved to,
        also includes the other objects and their new locations. Returns empty dictionary {} if move
        is blocked off
        '''
        output = {self: location}
        previous = {self} if previous == None else previous

       #contains STOP text object
        for obj in objects:
            if isinstance(obj, general):
                if obj.is_property('STOP'):  #checks if an object at the coord obj wants to move to is STOP
                    if not obj.is_property('PUSH'): #PUSH takes priority over STOP so pushable even if STOP
                        return {}

        #contains DEFEAT text object
        for obj in objects:
            if isinstance(obj, general):
                if obj.is_property('DEFEAT'): #checks for defeat text object
                    return {self: 'defeated'}



        for obj in objects: #moving every object located at said coordinate
            if obj not in previous and isinstance(obj, general):

                #PUSH property
                if obj.is_property('PUSH'):
                    if isinstance(game, Board):
                    #try moving object to new coordinate
                        new_location = game.apply_direction(location, direction)
                        if location != game.apply_direction(location, direction): #object did not move
                            #recursive step
                            new_loc_objs = game.get_objects_at(new_location) #set
                            new_object_moves = obj.move(new_location, direction, new_loc_objs, game, previous) #checks objects in same direction as current object being pushed
                            out = {} if new_object_moves == {} else new_object_moves
                            if out == {}:
                                return {}
                            else:
                                previous.add(obj) #adds obj to previous counter
                                output.update(new_object_moves) #updates output dictionary to include new object moves 
                        else:
                            return {}
                #WIN Condition
                if obj.is_property('WIN'):
                    if not obj.is_property('PUSH'):
                        game.set_state('Game won!')
        #PULL property
        negative_direction = get_opposite_vector(direction)
        if isinstance(game, Board):    
            original_location = game.apply_direction(location, negative_direction) #retrieves original location
            pulled_object_location = game.apply_direction(original_location, negative_direction) #retrieves location of pulled objects

        if original_location == pulled_object_location:
            objects_pulled = {}
        elif original_location != pulled_object_location:
            objects_pulled = game.get_objects_at(pulled_object_location) #creates set of pulled objects at given location
        else:
            pass
        
        for obj in objects_pulled:
            if isinstance(obj, general):
                if obj not in previous and obj.is_property('PULL'):
                    previous.add(obj) 
                    #recursive step
                    new_object_moves = obj.move(original_location, direction, game.get_objects_at(original_location), game, previous) #similar format to PUSH
                    output.update(new_object_moves)

        return output        
                
class text(general):
    '''
    Represented by an uppercase string and rendered as all-caps text.
    '''
    def __init__(self, name, location):
        '''
        Inputs: Name is all caps, location is a tuple
        '''
        super().__init__(self, name, location)
        if self.name in WORDS:
            self.property['PUSH'] = True

class graphic(general):
    '''
    Represented by a lowercase string and rendered with an image that represents that string.
    '''
    def __init__(self, name, location):
        '''
        Inputs: Name is all lower case, location is a tuple
        '''
        super().__init__(self, name, location)
    
    def is_YOU(self):
        '''
        checks if player is you
        '''
        return self.property['YOU']

#helper function
def get_opposite_vector(direction):
    '''
    Returns the opposite direction
    '''
    if direction == 'up':
        return 'down'
    elif direction == 'down':
        return 'up'
    elif direction == 'left':
        return 'right'
    elif direction == 'right':
        return 'left'

#helper function
def round_edges(val, vmin, vmax):
    '''
    Returns rounded value of coordinate
    Makes sure no objects go out of bounds
    '''
    output = min(max(vmin,val), vmax)
    return output

#helper function
def noun_replacer(rule, objects):
    '''
    inputs: a rule, and iteratable objects
    output: returns a dictionary with nouns mapped to their name based on rule applied
    '''
    replace_dict = {}
    first_word = rule[0]
    third_word = rule[2]
    if third_word in NOUNS: #both first and third word are nouns; setting first noun to third noun
        for obj in objects: #change all first nouns to second nouns objects
            if isinstance(obj, general): #if obj is a graphic object
                if obj.get_name() == first_word.lower(): #check if object name is the same as first word
                    replace_dict[obj] = third_word.lower() #adds obj as key and new object name as value
    return replace_dict

#helper function
def property_setter(rule, objects):
    '''
    inputs: a rule, and iterable objects
    output: returns a dictionary with properties mapped to their names
    '''
    third_word = rule[2]
    first_word = rule[0]
    if third_word in PROPERTIES: 
        for obj in objects:
            if isinstance(obj, general):
                if obj.get_name() == first_word.lower():
                    obj.set_property(third_word, True)

class Board(object):

    def __init__(self, level_description):
        '''
        Initializes the Board object
        sets rows, columns, game state, objects set, and map coordinates of objects
        '''
        self.rows = len(level_description)
        self.col = len(level_description[0])
        self.dimensions = (self.rows, self.col)
        self.state = 'ongoing'
        
          #set of objects in game board
        objects = set()
        for r in range(self.rows):
            for c in range(self.col):
                for item in level_description[r][c]:
                    objects.add(general(item, (r,c)))

        #coordinates dictionary for locations of objs             
        mapping = {}
        for obj in objects:
            coords = obj.get_location()
            if coords in mapping:
                mapping[coords].add(obj)
            else:
                mapping[coords] = {obj}   
            
        self.objects = objects
        self.map = mapping
        self.rules = self.get_rules() #list of rules
        
        self.implement_rules(bool = True)
    
    def get_rows(self):
        return self.rows #returns an int
    
    def get_columns(self):
        return self.col #returns an int

    def get_dims(self):
        return (self.rows, self.col)

    def get_objects(self):
        return self.objects #returns a set

    def get_objects_at(self, location):
        '''
        location is a coordinate tuple
        returns set of objects if objects exist at location; None otherwise
        '''
        empty = set()
        if location in self.map:
            return self.map[location]
        elif location not in self.map:
            return empty
        else:
            return empty
    
    def set_state(self, update):
        self.state = update
        
    def is_won(self):
        return self.state == 'won'

    def has_lost(self):
        return self.state == 'lost'
        
    def get_YOU_objects(self):
        '''
        returns a list of Obj instances with you prop
        '''
        YOU_list = []
        for obj in self.objects:
            if isinstance(obj, general):
                if obj.is_you():
                    YOU_list.append(obj)
        return YOU_list    

    def update_locations(self, objects, loc):
        '''
        Shifts all objects on game board to new location
        '''
        for i in range(len(objects)):
            obj = objects[i]
            new_location = loc[i]
            if isinstance(obj, general):
                obj.update_location(new_location)
            
    def apply_direction(self, loc, direction):
        '''
        Takes input current location and a direction vector.
        Returns a tuple of new location after applying vector. 
        '''
        rows = self.rows
        col = self.col
        current_r = loc[0]
        current_c = loc[1]
        delta_r = direction_vector[direction][0]
        delta_c = direction_vector[direction][1]
        applied_r = round_edges(current_r + delta_r, 0, rows - 1)
        applied_c = round_edges(current_c + delta_c, 0, col -1)
        return (applied_r, applied_c)

    def check_word(self, loc, w_type = None):
        '''
        Inputs: location on game board and wordtype ie. (NOUN, PROPERTY, WORDS)
        Output: returns the object at loc if it of said wordtype, returns None if multiple objects
        at that location or no objects of said wordtype are at that location
        '''
        if w_type is None:
            w_type = WORDS
        obs = set()
        try:
            obs = self.map[loc] #obs is a set
        except:
            return None
        if len(obs) == 1:
            item = obs.pop() #removes last item in list
            if isinstance(item, general):
                obs.add(item)
                if item.get_name() in w_type:
                    return item

    def get_board(self):
        '''
        dump board function
        '''
        rows = self.rows
        columns = self.col
        objects = self.objects
        dump = []

        for r in range(rows):
            dump.append([])
            for c in range(columns):
                dump[r].append([])

        for obj in objects:
            if isinstance(obj, general):
                name = obj.get_name()
                loc =  obj.get_location()
                row = loc[0]
                col = loc[1]
                dump[row][col].append(name)
        return dump

    def get_neighbors(self, location):
        '''
        inputs: location of current object
        outputs: return set of all neighbors location
        '''
        neighbors = set()
        rows = self.rows
        col = self.col

        obj_r = location[0]
        obj_c = location[1]
        for dir in direction_vector:
            delta_r = direction_vector[dir][0]
            delta_c = direction_vector[dir][1]
            #account for out-of-bounds error
            neighbor_r = round_edges(obj_r + delta_r ,0 ,rows -1)
            neighbor_c = round_edges(obj_c + delta_c, 0, col - 1)
            neighbors.add((neighbor_r, neighbor_c)) #adds all neighbors to set

        neighbors.remove(location) #removes any neighbors that were rounded and stayed the same
        return neighbors        

    def get_rules(self):
        '''
        finds all the rules on a given game board
        Returns a list of rules
        Rules are of format NOUN IS NOUN | PROPERTY
        '''
        rules = []
        #find all objects
        text_objects = set()
        for obj in self.objects:
            if isinstance(obj, general):
                if obj.get_name() in WORDS: #checks if object is a text object
                    text_objects.add(obj)

        IS_objects = set()
        for obj in text_objects:
            if obj.get_name() == 'IS': #finds all 'IS' objects
                IS_objects.add(obj)
        
        #creates NOUN -IS- PROP rules
        for obj in IS_objects:
            if isinstance(obj, general):
                IS_loc = obj.get_location()

                #rule moves horizontally and vertically
                for dir in ['left', 'up']:
                    nouns = []
                    properties = [] #just right side of IS, can be noun or properties
                    #sets opposite direction
                    if dir == 'left':
                        opp_direction = 'right'
                    else:
                        opp_direction = 'down'
                    
                    noun_location = self.apply_direction(IS_loc, dir)
                    noun = self.check_word(self.apply_direction(IS_loc, dir), w_type=NOUNS) #check if NOUN is a NOUN
                    if noun: #is noun
                        property_location = self.apply_direction(IS_loc, opp_direction)   #property location should be to the right or down of IS_object
                        prop = self.check_word(property_location, w_type=PROPERTIES | NOUNS) #appends nouns or properties
                        if prop: #is prop
                            nouns.append(noun)
                            properties.append(prop)
                            

                            #check for ANDs
                            directions = [dir, opp_direction] #list of directions
                            current_location = [noun_location, property_location]
                            word_types = [NOUNS] + [NOUNS | PROPERTIES]
                            np_list = [nouns, properties] #list of noun and property location


                            for i in range(len(directions)): #checks dir for nouns, opp for properties --> limits to changing nouns once
                                direction = directions[i]
                                and_coord = self.apply_direction(current_location[i], direction) #coordinates for AND object
                                #checks if there is an AND word
                                and_obj = self.check_word(and_coord, w_type={'AND'})  #either an obj or none
                                while and_obj != None: #loops until there are no more ANDs
                                    word_coord = self.apply_direction(and_coord, direction) #first iteration direction is back, second iteration direciton is forward
                                    word_obj = self.check_word(word_coord, w_type=word_types[i]) #wordtype must be noun for back, then either noun or prop for forward
                                    if word_obj != None: #proper grammar of noun first, then noun or prop second
                                        np_list[i].append(word_obj) #appends to nouns or properties list
                                        and_coord = self.apply_direction(word_coord, direction) #continues to progress forward in grammar direction
                                        and_obj = self.check_word(and_coord, w_type={'AND'}) #check if and is an AND object
                                    else:
                                        and_obj = None

                    #add rules to rules list
                    for noun in nouns:
                        if isinstance(noun, general):
                            for prop in properties:
                                if isinstance(prop, general):
                                    rule = [noun.get_name(), 'IS', prop.get_name()] #adds rule to rules list
                                    rules.append(rule)
        return rules
    
    def implement_rules(self, bool = False):
        '''
        Implements the rules set in place by the text game
        Returns nothing but updates objects on the game board
        '''       
        #set default properties for each object
        for obj in self.objects:
            for prop in PROPERTIES:
                if isinstance(obj, general): 
                    if obj.get_name() in WORDS and prop == 'PUSH':
                        obj.set_property(prop, True)
                    else:
                        obj.set_property(prop, False)

        #replace noun with another noun
        if bool != True:  #implement rules only applies first time so only updates objects one object at a time
            obj_replacement = dict()
            for rule in self.rules:
                replace_dict = noun_replacer(rule, self.objects) #dict with objects with new object names

                #prevents multiple rule changes, update
                obj_replacement.update(replace_dict) #updates obj_replacement dict with dictionary replace_dict
            for obj in obj_replacement:
                if isinstance(obj, general):
                    obj.change_name(obj_replacement[obj]) #changes name of every obj to new object name

        #property with noun
        for rule in self.rules:
            property_setter(rule, self.objects) 
        return None

    def defeat_checker(self):
        '''
        defeat checker
        '''
        for obj in self.get_YOU_objects():
            if isinstance(obj, general):
                if obj.is_property('DEFEAT'):
                    self.map[obj.get_location()].remove(obj)
                    self.objects.remove(obj)
                    self.state = 'has lost'
                    return None

    def victory_checker(self):
        '''
        victory checker
        '''
        for you in self.get_YOU_objects(): #for every you object
            if isinstance(you, general): 
                try:
                    others = self.map[you.get_location()] #gets every other object at you location
                except: 
                    continue 
                for other in others: 
                    if isinstance(other, general): 
                        if other.is_property('WIN'): 
                            self.state = 'won' 
                            return None

    def update_game(self, updates):
        '''
        inputs: a dictionary of updates
        output: return None
        keys in updates are objects on game board
        values in updates are new location coordinates
        updates the game board/objects so objects are in new locations
        '''
        for obj in updates:
            if isinstance(obj, general):
                old_location = obj.get_location()
                new_location = updates[obj]
                
                #update self.mapping
                self.map[old_location].remove(obj)
                
                if new_location != 'defeated':#not defeated
                    if new_location in self.map:
                        self.map[new_location].add(obj)
                    elif new_location not in self.map:
                        self.map[new_location] = {obj}
                                        
                    #update object attribute
                    obj.update_location(new_location)
                else:
                    self.objects.remove(obj)
        self.rules = self.get_rules()
        self.implement_rules()
        self.defeat_checker()
        self.victory_checker()

def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    return Board(level_description)

def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    if isinstance(game, Board):
        row = game.get_rows
        col = game.get_columns
        
        #list of all YOU objects
        YOU_list = game.get_YOU_objects()
        
        #dict of keys = Object, value is new location coords
        moves = {}
        for u in (YOU_list):
            #check if valid move
            #check in bounds, STOP
            you = u
            if isinstance(you, general):
                new_loc = game.apply_direction(you.get_location(), direction)
                #don't move because of edge case
                if you.get_location() == new_loc:
                    continue
                #get the dictionary corresponding to new moves
                new_moves = you.move(new_loc, direction, game.get_objects_at(new_loc), game)
                moves.update(new_moves)

        game.update_game(moves) #updates game
        return game.is_won() #checks condition

def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    if isinstance(game, Board):
        return game.get_board()
    

if __name__ == "__main__":
    output = []
    rows = 5
    columns = 7
    for r in range(rows):
        output.append([])
        for c in range(columns):
            output[r].append([])
    outpat = [[[] for c in range(columns)] for r in range(rows)]

    # print('output', output)
    # print('outpat,', outpat)
    boolean = False

    a_dict = {

        'a': 1,
        'b': 2,
        'c': 3
    }

    b_dict = {

        'a': 3,
        'e': 3,
        'f': 3
    }
    a_dict.update(b_dict)
    print(a_dict)



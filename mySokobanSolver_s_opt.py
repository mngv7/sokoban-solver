'''

    Sokoban assignment


The functions and classes defined in this module will be called by a marker script. 
You should complete the functions and classes according to their specified interfaces.

No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.

You are NOT allowed to change the defined interfaces.
In other words, you must fully adhere to the specifications of the 
functions, their arguments and returned values.
Changing the interfacce of a function will likely result in a fail 
for the test of your code. This is not negotiable! 

You have to make sure that your code works with the files provided 
(search.py and sokoban.py) as your code will be tested 
with the original copies of these files. 

Last modified by 2022-03-27  by f.maire@qut.edu.au
- clarifiy some comments, rename some functions
  (and hopefully didn't introduce any bug!)

'''

# You have to make sure that your code works with 
# the files provided (search.py and sokoban.py) as your code will be tested 
# with these files
import search 
import sokoban
from sokoban import find_2D_iterator
from collections import deque
from search import Node
import time

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)
    
    '''
    return [ "trial"]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




def taboo_cells(warehouse):
    '''  
    Identify the taboo cells of a warehouse. A "taboo cell" is by definition
    a cell inside a warehouse such that whenever a box get pushed on such 
    a cell then the puzzle becomes unsolvable. 
    
    Cells outside the warehouse are not taboo. It is a fail to tag an 
    outside cell as taboo.
    
    When determining the taboo cells, you must ignore all the existing boxes, 
    only consider the walls and the target cells.  
    Use only the following rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of 
             these cells is a target.
    
    @param warehouse: 
        a Warehouse object with the worker inside the warehouse

    @return
       A string representing the warehouse with only the wall cells marked with 
       a '#' and the taboo cells marked with a 'X'.  
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.  
    '''
    squares_to_remove = ['@', '$']
    target_squares = ['!', '.', '*']
    wall_square = '#'
    taboo_square = 'X'

    def is_corner(warehouse, x, y, wall=None):
        '''
        

        Parameters
        ----------
        warehouse : warehouse object
        x : x coordinate
        y : y coordinate
        wall : ensure that a wall coordinate isn't being passed

        Returns
        -------
        Boolean indicating if the given cell is a corner

        '''
        num_ud_walls = 0
        num_lr_walls = 0
        # check for walls above and below
        for (dx, dy) in [(0, 1), (0, -1)]:
            if warehouse[y + dy][x + dx] == wall_square:
                num_ud_walls += 1
        # check for walls left and right
        for (dx, dy) in [(1, 0), (-1, 0)]:
            if warehouse[y + dy][x + dx] == wall_square:
                num_lr_walls += 1
        if wall:
            return (num_ud_walls >= 1) or (num_lr_walls >= 1)
        else:
            return (num_ud_walls >= 1) and (num_lr_walls >= 1)

    # string representation
    warehouse_str = str(warehouse)

    # remove anything that isn't a wall or a target
    for char in squares_to_remove:
        warehouse_str = warehouse_str.replace(char, ' ')

    # convert warehouse string into 2D array
    warehouse_2d = [list(line) for line in warehouse_str.split('\n')]

    # apply rule 1
    for y in range(len(warehouse_2d) - 1):
        inside = False
        for x in range(len(warehouse_2d[0]) - 1):
            # iterate until the first wall is found, indicating inside the warehouse
            if not inside:
                if warehouse_2d[y][x] == wall_square:
                    inside = True
            else:
                # check if all cells to the right of current cell are empty, indicating outside the warehouse
                if all([cell == ' ' for cell in warehouse_2d[y][x:]]):
                    break
                if warehouse_2d[y][x] not in target_squares:
                    if warehouse_2d[y][x] != wall_square:
                        if is_corner(warehouse_2d, x, y):
                            warehouse_2d[y][x] = taboo_square

    # apply rule 2
    for y in range(1, len(warehouse_2d) - 1):
        for x in range(1, len(warehouse_2d[0]) - 1):
            if warehouse_2d[y][x] == taboo_square \
                    and is_corner(warehouse_2d, x, y):
                row = warehouse_2d[y][x + 1:]
                col = [row[x] for row in warehouse_2d[y + 1:][:]]
                # fill in taboo cells in the row to the right of the current cell
                for x2 in range(len(row)):
                    if row[x2] in target_squares or row[x2] == wall_square:
                        break
                    if row[x2] == taboo_square \
                            and is_corner(warehouse_2d, x2 + x + 1, y):
                        if all([is_corner(warehouse_2d, x3, y, 1)
                                for x3 in range(x + 1, x2 + x + 1)]):
                            for x4 in range(x + 1, x2 + x + 1):
                                warehouse_2d[y][x4] = 'X'
                # fill in taboo cells underneath the column of the current cell
                for y2 in range(len(col)):
                    if col[y2] in target_squares or col[y2] == wall_square:
                        break
                    if col[y2] == taboo_square \
                            and is_corner(warehouse_2d, x, y2 + y + 1):
                        if all([is_corner(warehouse_2d, x, y3, 1)
                                for y3 in range(y + 1, y2 + y + 1)]):
                            for y4 in range(y + 1, y2 + y + 1):
                                warehouse_2d[y4][x] = 'X'

    # convert 2D array back into string
    warehouse_str = '\n'.join([''.join(line) for line in warehouse_2d])

    # remove the remaining target_squares
    for char in target_squares:
        warehouse_str = warehouse_str.replace(char, ' ')
    return warehouse_str











# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -



def manhattanDistance(p1, p2):
    '''
    

    Parameters
    ----------
    p1 : point 1
    p2 : point 2

    Returns
    -------
    the manhattan distance between points 1 and 2

    '''
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def offsetToDirection(offset):
    '''
    

    Parameters
    ----------
    offset : Offset of the occupant's current location to their target location

    Raises
    ------
    ValueError
        Raises if the offset isn't in a valid direction

    Returns
    -------
    str
        The direction from the occupan's location to their target location

    '''
    if offset == (1,0):
        return 'Right'
    elif offset == (0,1):
        return 'Down'
    elif offset == (-1,0):
        return 'Left'
    elif offset == (0,-1):
        return 'Up'
    else:
        raise ValueError("Invalid offset")
        
def directionToOffset(direction):
    '''
    

    Parameters
    ----------
    direction : string
        String representation of direction

    Raises
    ------
    ValueError
        Raises if an invalid direction is passed

    Returns
    -------
    tuple
       Offset relative to the direction

    '''
    if direction == 'Right':
        return (1,0)
    elif direction == 'Down':
        return (0,1)
    elif direction == 'Left':
        return (-1,0)
    elif direction == 'Up':
        return (0,-1)
    else:
        raise ValueError("Invalid direction")
        

def canMove(state, offset):
    '''
    

    Parameters
    ----------
    state : list
        list of strings representing the warehouse map
    offset : tuple
        offset for the worker to be moved by

    Raises
    ------
    ValueError
        Raises if no worker is found in the given warehouse state

    Returns
    -------
    Boolean
        Indicates if the worker can move in that direction

    '''
    try:
        worker_position = next(find_2D_iterator(state, '@'))
    except StopIteration:
        try:
            worker_position = next(find_2D_iterator(state, '!'))
        except:
            raise ValueError("No worker found in the given state.")
        

    new_x = worker_position[0] + offset[0]
    new_y = worker_position[1] + offset[1]

    # Check if new worker position is out of bounds
    if new_y < 0 or new_y >= len(state) or new_x < 0 or new_x >= len(state[new_y]):
        return False

    occupant = state[new_y][new_x]

    if occupant in ' .':  # Worker can move to an empty space or target
        return True
    elif occupant == '$':  # There's a box in the worker's way
        push_x = new_x + offset[0]
        push_y = new_y + offset[1]

        # Check if the new box position is out of bounds
        if push_y < 0 or push_y >= len(state) or push_x < 0 or push_x >= len(state[push_y]):
            return False

        next_occupant = state[push_y][push_x]
        # Box can be pushed if the next cell is empty or a target, and it's not a taboo cell
        return next_occupant in ' .' and (push_x, push_y) not in tabooCells

    return False

def findOccupant(state, coords):
    '''
    

    Parameters
    ----------
    state : list
        List of strings representing the warehouse map state
    coords : tuple
        Coordinates of the cell to check

    Raises
    ------
    ValueError
        Raises if invalid coordinates are passed

    Returns
    -------
    char
        Character designation for the occupant of the cell

    '''
    x,y = coords
    if (0 <= x < len(state[y])) and (0 <= y < len(state)):
        return state[y][x]
    else:
        raise ValueError("Incorrect coordinates passed")
        
def parseState(state):
    '''
    

    Parameters
    ----------
    state : list
        List of strings representing the warehouse map state

    Returns
    -------
    boxes : list
        A list of the coordinates with boxes found in the state sorted by said coordinates

    '''
    boxes = list(find_2D_iterator(state, '$'))
    boxes.sort(key=lambda x: (x[1], x[0]))
    
    return boxes
    
    
offsets = [(1,0),(0,1),(-1,0),(0,-1)]

class HashableState:
    '''
    This class defines a hashable and immutable state that can be passed to a Node
    without raising any errors about data types. It takes a string representation of the warehouse and a
    list of dictionaries for each box in said warehouse, and then converts this data into a workable type
    for the given search algorithms. Getter methods have been included to then receive this data back from instances of 
    this object, along with methods for comparison and equivalence checks
    '''
    def __init__(self, state):
        self.map = state[0]
        self.box_weights_dict = tuple(frozenset(d.items()) for d in state[1])

    def __hash__(self):
        return hash((self.map, self.box_weights_dict))

    def __eq__(self, other):
        return (self.map, self.box_weights_dict) == (other.map, other.box_weights_dict)

    def __lt__(self, other):
        # Perform 'comparison' (stop Node class from trying to compare two HashableState instances)
        return self.map < other.map

    def get_dict(self):
        return [dict(d) for d in self.box_weights_dict]

    def get_map(self):
        return self.map

    # for debugging purposes
    def __str__(self):
        return f"The map is {self.map}\nthe dictionary is {list(self.box_weights_dict)}"


class SokobanPuzzle(search.Problem):
    '''
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of 
    the provided module 'search.py'. 
    
    '''
    
    def __init__(self, warehouse):
        if warehouse is None:
            raise FileNotFoundError
        elif warehouse:
            global tabooCells
            tabooCells = set(find_2D_iterator(taboo_cells(warehouse).split("\n"), "X"))
            warehouse_str = str(warehouse)

            dynamicBoxes = [{'id': index, 'coord': box, 'weight': weight}
                for index, (box, weight) in enumerate(zip(warehouse.boxes, warehouse.weights))] # list of dictionaries for each box with a unique identifier

    
            self.initial = HashableState((warehouse_str, dynamicBoxes)) # create hashable and immutable datatype to be passed as the state
            self.goal = sorted(warehouse.targets, key=lambda x: (x[1], x[0]))
            self.walls = warehouse.walls
            self.targets = warehouse.targets
        

    def actions(self, state):
        """
        Return the list of actions that can be executed in the given state.
        
        """
        state = state.get_map().splitlines()
        possibleActions = []
        for offset in offsets:
            if canMove(state, offset):
                possibleActions.append(offsetToDirection(offset))
        return possibleActions
    
    def result(self, state, action):
        assert action in self.actions(state)
        workingState = state.get_map().splitlines() # use getter methods to receive data
        dynamicBoxes = state.get_dict()
        newState = [list(line) for line in workingState]
        boxesCurrent = list(find_2D_iterator(workingState, '$'))
        try:
            workerCurrent = next(find_2D_iterator(workingState, '@'))
        except StopIteration:
            try:
                workerCurrent = next(find_2D_iterator(workingState, '!'))
            except:
                raise ValueError("No worker found in the given state.")
        offset = directionToOffset(action)
        newCoord = tuple(a + b for a, b in zip(workerCurrent, offset))
        occupant = findOccupant(newState, newCoord)
    
        if occupant == '$':
            boxIndex = boxesCurrent.index(newCoord)
            newBoxPosition = tuple(a + b for a, b in zip(newCoord, offset))
            for box in dynamicBoxes:
                if box['coord'] == newCoord:
                    box['coord'] = newBoxPosition
            # Clear the original box position
            newState[boxesCurrent[boxIndex][1]][boxesCurrent[boxIndex][0]] = ' ' if newState[boxesCurrent[boxIndex][1]][boxesCurrent[boxIndex][0]] == '$' else newState[boxesCurrent[boxIndex][1]][boxesCurrent[boxIndex][0]]
            # Place box at new position
            newState[newBoxPosition[1]][newBoxPosition[0]] = '$'
        
        # Case for when a worker moves off a target
        if newState[workerCurrent[1]][workerCurrent[0]] == '!':
            newState[workerCurrent[1]][workerCurrent[0]] = '.'
        else:
            newState[workerCurrent[1]][workerCurrent[0]] = ' '
        
        # Place worker at new position
        if newState[newCoord[1]][newCoord[0]] == '.':
            newState[newCoord[1]][newCoord[0]] = '!'
        else:
            newState[newCoord[1]][newCoord[0]] = '@'
    
        newState = [''.join(line) for line in newState]
        return HashableState(("\n".join(newState), dynamicBoxes)) # return state as HashableState


            
    def goal_test(self, state):
        # Extract and sort the boxes positions from the state
        state = state.get_map().splitlines()
        boxes = parseState(state)
        
    
        # Check if sorted boxes match the sorted goal
        return sorted(boxes, key=lambda x: (x[1], x[0])) == self.goal
    
    def path_cost(self, c, state1, action, state2, moves_by_worker = None):
        # Retrieve box positions and weights from both states
        box_map1 = {box['id']: box for box in state1.get_dict()}
        box_map2 = {box['id']: box for box in state2.get_dict()}
    
        # Every action has at least a cost of 1
        c += 1
    
        # Find how far each box moved
        for id, box1 in box_map1.items():
            box2 = box_map2[id]
            if box1['coord'] != box2['coord']:
                # Calculate the Manhattan distance the box moved
                distance = manhattanDistance(box1['coord'], box2['coord'])
                # Compute the cost of moving this box based on its weight
                move_cost = distance * box1['weight']
                c += move_cost
        if moves_by_worker: 
            c += moves_by_worker-1 # - 1 to not count the last move twice
    
        return c



    
    def h(self, state):
        boxes = parseState(state.state.get_map().splitlines())
        dynamicBoxes = state.state.get_dict()
        total_cost = 0
        for box in boxes:
            closest_target_distance = float('inf')
            for target in self.targets:
                distance = manhattanDistance(box, target)
                if distance < closest_target_distance:
                    closest_target_distance = distance
            # find weight of given box
            for checkBox in dynamicBoxes:
                if checkBox['coord'] == box:
                    weight = checkBox['weight']
                    
            total_cost += closest_target_distance * weight
        return total_cost

        
            
            
            
        
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    '''
    Determine if the sequence of actions listed in 'action_seq' is legal or not.
    
    @param warehouse: a valid Warehouse object
    @param action_seq: a sequence of legal actions.
    
    @return:
        The string 'Impossible', if one of the action was not valid.
        Otherwise, a string representing the state of the puzzle after applying the sequence of actions.
    '''
    # create a copy of the warehouse to ensure no changes happen to the original
    warehouse = warehouse.copy()
    x, y = warehouse.worker
    
    for move in action_seq:
        # movement directions
        dx, dy = 0, 0
        if move == 'Up': dy = -1
        elif move == 'Down': dy = 1
        elif move == 'Left': dx = -1
        elif move == 'Right': dx = 1
        else: raise ValueError('Invalid move:', move)
        
        # Calculate new positions
        x_move = x + dx
        y_move = y + dy
        
        # Check if the new worker position is a wall
        if (x_move, y_move) in warehouse.walls:
            return 'Impossible'
        
        # Check if the new position has a box
        if (x_move, y_move) in warehouse.boxes:
            new_box_x = x_move + dx
            new_box_y = y_move + dy
            # Check if the new box position is valid
            if (new_box_x, new_box_y) in warehouse.walls or (new_box_x, new_box_y) in warehouse.boxes:
                return 'Impossible'
            # Move the box
            warehouse.boxes.remove((x_move, y_move))
            warehouse.boxes.append((new_box_x, new_box_y))
        
        # Update the worker position
        x, y = x_move, y_move
    
    # Update the worker position in the warehouse
    warehouse.worker = (x, y)
    # Return the new warehouse state as a string
    return str(warehouse)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_weighted_sokoban(warehouse):
    '''
    This function analyses the given warehouse.
    It returns the two items. The first item is an action sequence solution. 
    The second item is the total cost of this action sequence.
    
    @param 
     warehouse: a valid Warehouse object

    @return
    
        If puzzle cannot be solved 
            return 'Impossible', None
        
        If a solution was found, 
            return S, C 
            where S is a list of actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
            C is the total cost of the action sequence C

    '''
    t0 = time.time()
    problem = SokobanPuzzle(warehouse)
    solution = search.astar_graph_search(problem)
    
    if solution is None:
        return 'Impossible', None
    
    actions = [node.action for node in solution.path()[1:]]  # Extract actions
    if check_elem_action_seq(warehouse, actions) == 'Impossible':
        return 'Impossible', None

    # Ensure to extract the state properly to pass to path_cost if needed
    final_state = solution.state  # Make sure this extracts the string representation
    moves_by_worker = len(actions)
    cost = problem.path_cost(0, problem.initial, None, final_state, moves_by_worker)
    t1 = time.time()
    print("Solver took ",t1-t0, ' seconds')
    
    return actions, cost


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

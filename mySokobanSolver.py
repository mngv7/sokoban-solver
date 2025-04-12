
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

Last modified by 2021-08-17  by f.maire@qut.edu.au
- clarifiy some comments, rename some functions
  (and hopefully didn't introduce any bug!)

'''

# You have to make sure that your code works with 
# the files provided (search.py and sokoban.py) as your code will be tested 
# with these files
import search 
import sokoban
from collections import defaultdict

# Predefined moves dictionary for consistency and speed.
MOVES = {
    "Left":  (-1, 0),
    "Right": (1, 0),
    "Up":    (0, -1),
    "Down":  (0, 1)
}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)
    
    '''
    return [ (11592931, 'Zackariya', 'Taylor'), (11220139, 'Isobel', 'Jones'), (1124744, 'Sophia', 'Sweet') ]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from sokoban import find_2D_iterator

def find_1D_iterator_exclude(line, *exclude_chars):
    for pos, char in enumerate(line):
        if char not in exclude_chars:
            yield pos

def find_2D_iterator_exclude(lines, *exclude_chars):
    for y, line in enumerate(lines):
        for x in find_1D_iterator_exclude(line, *exclude_chars):
            yield (x, y)

def get_corner_taboo_cells(candidate_taboo_cells, wall_cells):
    corner_taboo_cells = set()
    for (x, y) in candidate_taboo_cells:
        north = (x, y - 1)
        east  = (x + 1, y)
        south = (x, y + 1)
        west  = (x - 1, y)
        if ((north in wall_cells and east in wall_cells) or
            (east in wall_cells and south in wall_cells) or
            (south in wall_cells and west in wall_cells) or
            (west in wall_cells and north in wall_cells)):
            corner_taboo_cells.add((x, y))
    return corner_taboo_cells

def get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells):
    wall_taboo_cells = set()
    # Group corners by column for vertical segments.
    corners_by_col = defaultdict(list)
    for (x, y) in corner_taboo_cells:
        corners_by_col[x].append(y)
    for x, ys in corners_by_col.items():
        ys.sort()
        for i in range(len(ys) - 1):
            y1, y2 = ys[i], ys[i+1]
            if (x, y1 - 1) in wall_cells and (x, y2 + 1) in wall_cells:
                gap_count = 0
                last_was_gap = False
                is_valid = True
                for y in range(y1 + 1, y2):
                    if (x, y) in taboo_row_nullifier:
                        is_valid = False
                        break
                    if ((x - 1, y) not in wall_cells and (x + 1, y) not in wall_cells):
                        if last_was_gap:
                            is_valid = False
                            break
                        gap_count += 1
                        last_was_gap = True
                    else:
                        last_was_gap = False
                if is_valid and gap_count <= 1:
                    for y in range(y1 + 1, y2):
                        wall_taboo_cells.add((x, y))
    # Group corners by row for horizontal segments.
    corners_by_row = defaultdict(list)
    for (x, y) in corner_taboo_cells:
        corners_by_row[y].append(x)
    for y, xs in corners_by_row.items():
        xs.sort()
        for i in range(len(xs) - 1):
            x1, x2 = xs[i], xs[i+1]
            if (x1 - 1, y) in wall_cells and (x2 + 1, y) in wall_cells:
                gap_count = 0
                last_was_gap = False
                is_valid = True
                for x in range(x1 + 1, x2):
                    if (x, y) in taboo_row_nullifier:
                        is_valid = False
                        break
                    if ((x, y - 1) not in wall_cells and (x, y + 1) not in wall_cells):
                        if last_was_gap:
                            is_valid = False
                            break
                        gap_count += 1
                        last_was_gap = True
                    else:
                        last_was_gap = False
                if is_valid and gap_count <= 1:
                    for x in range(x1 + 1, x2):
                        wall_taboo_cells.add((x, y))
    return wall_taboo_cells

def get_taboo_cell_map(warehouse, taboo_cells):
    lines = [list(line) for line in str(warehouse).split('\n')]
    for i, line in enumerate(lines):
        for j in range(len(line)):
            if (j, i) in taboo_cells:
                line[j] = 'X'
            elif line[j] not in {'#', ' '}:
                line[j] = ' '

    taboo_cell_map_r = "\n".join("".join(line) for line in lines)
    return taboo_cell_map_r

def mark_outside_walls(s):
    first = s.find('#')
    last = s.rfind('#')
    if first == -1 or last == -1:
        return s  
    return '?' * first + s[first:last + 1] + '?' * (len(s) - last - 1)

def taboo_cells(warehouse):
    '''  
    Identify the taboo cells of a warehouse. A "taboo cell" is by definition
    a cell inside a warehouse such that whenever a box get pushed on such 
    a cell then the puzzle becomes unsolvable. 
    
    Cells outside the warehouse are not taboo. It is a fail to tag one as taboo.
    
    When determining the taboo cells, you must ignore all the existing boxes, 
    only consider the walls and the target  cells.  
    Use only the following rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of 
             these cells is a target.
    
    @param warehouse: 
        a Warehouse object with a worker inside the warehouse

    @return
       A string representing the warehouse with only the wall cells marked with 
       a '#' and the taboo cells marked with a 'X'.  
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.  
    '''
    lines = str(warehouse).split('\n')
    wall_cells = set(warehouse.walls)
    # Combine targets with positions from '*' and '#' to "nullify" rows.
    taboo_row_nullifier = set(warehouse.targets) | set(find_2D_iterator(lines, '*')) | set(find_2D_iterator(lines, '#'))
    lines = [mark_outside_walls(line) for line in lines]

    candidate_taboo_cells = set(find_2D_iterator_exclude(lines, '.', '#', '*', '?'))
    corner_taboo_cells = get_corner_taboo_cells(candidate_taboo_cells, wall_cells)
    wall_taboo_cells = get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells)
    computed_taboo_set = corner_taboo_cells | wall_taboo_cells
    taboo_cell_map = get_taboo_cell_map(warehouse, computed_taboo_set)
    return taboo_cell_map

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class SokobanPuzzle(search.Problem):
    '''
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of 
    the provided module 'search.py'. 
    
    '''
    
    #
    #         "INSERT YOUR CODE HERE"
    #
    #     Revisit the sliding puzzle and the pancake puzzle for inspiration!
    #
    #     Note that you will need to add several functions to 
    #     complete this class. For example, a 'result' method is needed
    #     to satisfy the interface of 'search.Problem'.
    #
    #     You are allowed (and encouraged) to use auxiliary functions and classes

    
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.walls = set(warehouse.walls)
        self.targets = set(warehouse.targets)
        # Each box is represented as a (x, y, weight) tuple.
        boxes_with_weights = [(box[0], box[1], weight)
                              for box, weight in zip(warehouse.boxes, warehouse.weights)]
        boxes_with_weights.sort(key=lambda b: (b[1], b[0]))
        self.initial = (warehouse.worker, tuple(boxes_with_weights))
        # Compute taboo cells from the warehouse drawing.
        taboo_map = taboo_cells(warehouse)
        self.taboo_set = {(j, i)
                          for i, line in enumerate(taboo_map.splitlines())
                          for j, ch in enumerate(line) if ch == 'X'}
        # Pre-cache moves.
        self._moves = MOVES

    def is_deadlock(self, state): #(unsolvable)
        # Use set intersection: if any box (not on a target) lies in a taboo cell, it's a deadlock.
        _, boxes = state
        box_positions = {(bx, by) for bx, by, _ in boxes}
        return bool(box_positions & (self.taboo_set - self.targets))
    
    
    def actions(self, state):
        (wx, wy), boxes = state
        boxes_xy = {(b[0], b[1]) for b in boxes}
        available_actions = []
        for action, (dx, dy) in self._moves.items():
            nx, ny = wx + dx, wy + dy
            if (nx, ny) in self.walls:
                continue
            if (nx, ny) in boxes_xy:
                bnx, bny = nx + dx, ny + dy
                if (bnx, bny) in boxes_xy or (bnx, bny) in self.walls:
                    continue
                available_actions.append(action)
            else:
                available_actions.append(action)
        return available_actions
    

    def result(self, state, action):
        (wx, wy), boxes = state
        dx, dy = self._moves[action]
        new_worker = (wx + dx, wy + dy)
        new_boxes = list(boxes)
        for i, (bx, by, w) in enumerate(new_boxes):
            if (bx, by) == new_worker:
                new_boxes[i] = (bx + dx, by + dy, w)
                break
        return (new_worker, tuple(sorted(new_boxes, key=lambda b: (b[1], b[0]))))
        
    def goal_test(self, state):
        _, boxes = state
        return all((bx, by) in self.targets for bx, by, _ in boxes)

    def path_cost(self, c, state1, action, state2):
        _, boxes1 = state1
        _, boxes2 = state2
        b1_dict = {(bx, by): (bx, by, w) for bx, by, w in boxes1}
        for (bx, by, w) in boxes2:
            if (bx, by) not in b1_dict:
                return c + 1 + w
        return c + 1
  
    def h(self, node):
        if self.is_deadlock(node.state):
            return 10**6  # A high cost to discourage deadlocks.
        _, boxes = node.state
        return sum(min(abs(bx - tx) + abs(by - ty) for (tx, ty) in self.targets)
                   for bx, by, _ in boxes)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    '''
    
    Determine if the sequence of actions listed in 'action_seq' is legal or not.
    
    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.
        
    @param warehouse: a valid Warehouse object

    @param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
           
    @return
        The string 'Impossible', if one of the action was not valid.
           For example, if the agent tries to push two boxes at the same time,
                        or push a box into a wall.
        Otherwise, if all actions were successful, return                 
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    '''
    
    warehouse_copy = warehouse.copy()
    worker_x, worker_y = warehouse_copy.worker
    boxes = set(warehouse_copy.boxes)
    walls = set(warehouse_copy.walls)

    for action in action_seq:
        if action not in MOVES:
            return "Impossible"
        dx, dy = MOVES[action]
        new_worker_x, new_worker_y = worker_x + dx, worker_y + dy

        if (new_worker_x, new_worker_y) in walls:
            return "Impossible"

        if (new_worker_x, new_worker_y) in boxes:
            new_box_x, new_box_y = new_worker_x + dx, new_worker_y + dy
            if (new_box_x, new_box_y) in walls or (new_box_x, new_box_y) in boxes:
                return "Impossible"
            boxes.remove((new_worker_x, new_worker_y))
            boxes.add((new_box_x, new_box_y))

        worker_x, worker_y = new_worker_x, new_worker_y

    warehouse_copy.worker = (worker_x, worker_y)
    warehouse_copy.boxes = tuple(boxes)
    return str(warehouse_copy)
    


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

    problem = SokobanPuzzle(warehouse)
    result = search.astar_graph_search(problem)
    
    if result is None:
        return "Impossible", 0
    
    return result.solution(), result.path_cost
    
    


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


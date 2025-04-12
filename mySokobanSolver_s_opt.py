
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
    corner_taboo_cells: set[tuple] = set()
    for candidate_taboo_cell in candidate_taboo_cells:
        x, y = candidate_taboo_cell
        north = x, y - 1
        east = x + 1, y
        south = x, y + 1
        west = x - 1, y

        if (north in wall_cells and east in wall_cells) or \
        (east in wall_cells and south in wall_cells) or \
        (south in wall_cells and west in wall_cells) or \
        (west in wall_cells and north in wall_cells):
            corner_taboo_cells.add((x, y))
    return corner_taboo_cells

def get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells):
    wall_taboo_cells: set[tuple] = set()

    for corner1 in corner_taboo_cells:
        for corner2 in corner_taboo_cells:
            if corner1 == corner2:
                continue

            x1, y1 = corner1
            x2, y2 = corner2

            if x1 == x2:  # Same column (vertical check)
                if (x1, y1 - 1) in wall_cells and (x1, y2 + 1) in wall_cells:
                    min_y, max_y = min(y1, y2), max(y1, y2)
                    is_valid = True
                    for y in range(min_y + 1, max_y):
                        if (x1, y) in taboo_row_nullifier:
                            is_valid = False
                            break
                        if (x1 - 1, y) not in wall_cells and (x1 + 1, y) not in wall_cells:
                            # If no walls on either side, gap detected
                            is_valid = False
                            break
                    if is_valid:
                        for y in range(min_y + 1, max_y):
                            wall_taboo_cells.add((x1, y))

            elif y1 == y2:  # Same row (horizontal check)
                if (x1 - 1, y1) in wall_cells and (x2 + 1, y1) in wall_cells:
                    min_x, max_x = min(x1, x2), max(x1, x2)
                    is_valid = True
                    for x in range(min_x + 1, max_x):
                        if (x, y1) in taboo_row_nullifier:
                            is_valid = False
                            break
                        if (x, y1 - 1) not in wall_cells and (x, y1 + 1) not in wall_cells:
                            # If no walls above or below, gap detected
                            is_valid = False
                            break
                    if is_valid:
                        for x in range(min_x + 1, max_x):
                            wall_taboo_cells.add((x, y1))

    return wall_taboo_cells


def get_taboo_cell_map(warehouse, taboo_cells):
    lines = [list(line) for line in str(warehouse).split('\n')]
    for i, line in enumerate(lines):
        for j in range(len(line)):
            if (j, i) in taboo_cells:
                line[j] = 'X'
            elif line[j] not in {'#', ' '}:
                line[j] = ' '

    taboo_cell_map = "\n".join("".join(line) for line in lines)
    return taboo_cell_map

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
    taboo_row_nullifier = set(warehouse.targets) | set(find_2D_iterator(lines, '*')) | set(find_2D_iterator(lines, '#'))
    lines = [mark_outside_walls(line) for line in lines]

    candidate_taboo_cells = set(find_2D_iterator_exclude(lines, '.', '#', '*', '?'))
    
    corner_taboo_cells = get_corner_taboo_cells(candidate_taboo_cells, wall_cells)
    wall_taboo_cells = get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells)
    taboo_cells = corner_taboo_cells | wall_taboo_cells

    taboo_cell_map = get_taboo_cell_map(warehouse, taboo_cells)

    return taboo_cell_map

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def get_reachable_positions(worker_pos, walls, boxes):
        from collections import deque
        visited = set()
        frontier = deque([worker_pos])
        while frontier:
            x, y = frontier.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in walls and (nx, ny) not in boxes and (nx, ny) not in visited:
                    frontier.append((nx, ny))
        return visited



from itertools import combinations
# from search import FIFOQueue

# def get_reachable_positions(worker_pos, walls, boxes):
#     frontier = FIFOQueue()         # Using FIFOQueue from the search module
#     frontier.append(worker_pos)
#     reached = set()

#     while frontier:
#         current = frontier.pop()
#         if current in reached:
#             continue
#         reached.add(current)
#         for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#             neighbor = (current[0] + dx, current[1] + dy)
#             if neighbor not in walls and neighbor not in boxes and neighbor not in reached:
#                 frontier.append(neighbor)
#     return reached


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
        self.visited_box_states = set()
        self.deadlock_cache = {}
        
        # each box represented as (x, y, weight) tuple
        boxes_with_weights = [(box[0], box[1], weight) for box, weight in zip(warehouse.boxes, warehouse.weights)]
        boxes_with_weights.sort(key=lambda b: (b[1], b[0]))
        self.initial = (warehouse.worker, tuple(boxes_with_weights))

        if not hasattr(self, '_seen_box_configs'):
            self._seen_box_configs = set()

        #get tabboo cells
        taboo_map = taboo_cells(warehouse)
        self.taboo_set = {
            (j, i)
            for i, line in enumerate(taboo_map.splitlines())
            for j, ch in enumerate(line)
            if ch == 'X'
        }

        

    def __eq__(self, other):
        return isinstance(other, SokobanPuzzle) and self.initial == other.initial

    def __hash__(self):
        return hash(self.initial)  # only hash box positions


    def is_box_blocked(self, box_positions, box):
            x, y = box
            walls = self.walls
            boxes = set(box_positions) - {(x, y)}
            obstacles = walls.union(boxes)

            if ((x - 1, y) in obstacles and (x, y - 1) in obstacles): return True
            if ((x + 1, y) in obstacles and (x, y - 1) in obstacles): return True
            if ((x - 1, y) in obstacles and (x, y + 1) in obstacles): return True
            if ((x + 1, y) in obstacles and (x, y + 1) in obstacles): return True

            return False
    

    def has_frozen_clusters(self, box_positions):
        for b1, b2 in combinations(box_positions, 2):
            if abs(b1[0] - b2[0]) + abs(b1[1] - b2[1]) == 1:
                if self.is_box_blocked(box_positions, b1) and self.is_box_blocked(box_positions, b2):
                    return True
        return False

    def is_taboo_deadlock(self, state):
        _, boxes = state
        for bx, by, _ in boxes:
            if (bx, by) in self.taboo_set and (bx, by) not in self.targets:
                return True
        return False
    
    def is_deadlock(self, state):
        _, boxes = state
        box_positions = frozenset((b[0], b[1]) for b in boxes)

        if box_positions in self.deadlock_cache:
            return self.deadlock_cache[box_positions]

        # Check for taboo deadlock (fatal)
        if any((bx, by) in self.taboo_set and (bx, by) not in self.targets for bx, by, _ in boxes):
            self.deadlock_cache[box_positions] = True
            return True

        # Don't cache soft deadlocks (they might get out of deadlock)
        if any(self.is_box_blocked(box_positions, (bx, by)) for bx, by, _ in boxes):
            return True

        if self.has_frozen_clusters(box_positions):
            return True

        return False


    def actions(self, state):
        if self.is_taboo_deadlock(state) and state != self.initial:
            return []
        
        directions = ['Up', 'Down', 'Left', 'Right']
        (wx, wy), boxes = state
        boxes_xy = {(b[0], b[1]) for b in boxes}
        reachable = get_reachable_positions((wx, wy), self.walls, boxes_xy)
        self.last_reachable_cache = reachable 
        moves = {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1)}
        actions = []

        for action in directions:
            
            
            dx, dy = moves[action]
            nx, ny = wx + dx, wy + dy
            if (nx, ny) in self.walls:
                continue
            if (nx, ny) in boxes_xy:
                bnx, bny = nx + dx, ny + dy
                if (bnx, bny) in self.walls or (bnx, bny) in boxes_xy:
                    continue
                if (wx, wy) in reachable:  # the worker must be able to reach the pushing position
                    actions.append(action)
            else:
                if (nx, ny) in reachable:
                    actions.append(action)
        return actions



    def result(self, state, action):
        (wx, wy), boxes = state
        boxes = list(boxes)
        dx, dy = {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1)}[action]
        new_worker = (wx + dx, wy + dy)
        for i, (bx, by, w) in enumerate(boxes):
            if (bx, by) == new_worker:
                new_box = (bx + dx, by + dy, w)
                boxes[i] = new_box
                break
        return (new_worker, tuple(sorted(boxes, key=lambda b: (b[1], b[0]))))


        
    def goal_test(self, state):
        _, boxes = state
        return all((b[0], b[1]) in self.targets for b in boxes)

    def path_cost(self, c, state1, action, state2):
        _, b1 = state1
        _, b2 = state2
        
        moved_box = None
        b1_xy = {(b[0], b[1]): b for b in b1}
        b2_xy = {(b[0], b[1]): b for b in b2}
        # identify  box that moved by comparing positions:
        for pos, box in b2_xy.items():
            if pos not in b1_xy:
                moved_box = box
                break
        if moved_box:
            return c + 1 + moved_box[2]
        return c + 1
  

    def h(self, node):
        state = node.state
        box_pos = frozenset((b[0], b[1]) for b in state[1])

        # penalty for repeated box positions with no new pushes
        if box_pos in self._seen_box_configs:
            penalty = 100  
        else:
            penalty = 0
            self._seen_box_configs.add(box_pos)

        if self.is_deadlock(node.state):
            return 10**6

        worker, boxes = node.state
        box_cost = 0

        for bx, by, weight in boxes:
            # Reward being on target by reducing cost
            if (bx, by) in self.targets:
                continue
            d = min(abs(bx - tx) + abs(by - ty) for (tx, ty) in self.targets)
            box_cost += d * (1 + weight * 0.5)

        # Find boxes that can be pushed (reachable by worker)
        # boxes_xy = {(b[0], b[1]) for b in boxes}
        # # reachable = get_reachable_positions(worker, self.walls, boxes_xy)
        # reachable = getattr(self, '_cached_reachable', get_reachable_positions(worker, self.walls, boxes_xy))

        # reachable_boxes = [box for box in boxes if (box[0], box[1]) in reachable]
        # if reachable_boxes:
        #     nearest_push_dist = min(abs(worker[0] - bx) + abs(worker[1] - by)
        #                             for bx, by, _ in reachable_boxes)
        # else:
        #     nearest_push_dist = 10  # punish being far from any box

        return box_cost + penalty #+ nearest_push_dist * 2  # boost penalty for idling



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

    #vectors for moving
    moves = {
        "Left": (-1, 0),
        "Right": (1, 0),
        "Up": (0, -1),
        "Down": (0, 1)
    }

    worker_x, worker_y = warehouse_copy.worker
    boxes = set(warehouse_copy.boxes)  
    walls = set(warehouse_copy.walls)

    for action in action_seq:
        if action not in moves:
            return "Impossible" 
        
        #calc new worker position:
        dx, dy = moves[action]
        new_worker_x, new_worker_y = worker_x + dx, worker_y + dy

        if (new_worker_x, new_worker_y) in walls:
            return "Impossible"

        if (new_worker_x, new_worker_y) in boxes:
            new_box_x, new_box_y = new_worker_x + dx, new_worker_y + dy

            # if theres a wall or another box:
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

    # develop this initial check??:
    # if is_initial_state_deadlocked(warehouse):
    #     return ['Impossible']
    
    problem = SokobanPuzzle(warehouse)
    
    if all((b[0], b[1]) in warehouse.targets for b in warehouse.boxes):
        return [], 0
    
    result = search.astar_graph_search(problem)
    
    
    if result is None:
        return ['Impossible'], None
    
    return result.solution(), result.path_cost
    
    


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


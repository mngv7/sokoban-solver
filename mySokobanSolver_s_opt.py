"""
    Sokoban assignment

The functions and classes defined in this module will be called by a marker script. 
You should complete the functions and classes according to their specified interfaces.

No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.

You are NOT allowed to change the defined interfaces.
In other words, you must fully adhere to the specifications of the 
functions, their arguments and returned values.
Changing the interface of a function will likely result in a fail 
for the test of your code. This is not negotiable! 

You have to make sure that your code works with the files provided 
(search.py and sokoban.py) as your code will be tested 
with the original copies of these files. 

Last modified by 2021-08-17  by f.maire@qut.edu.au
- clarifiy some comments, rename some functions
  (and hopefully didn't introduce any bug!)
"""

import search
import sokoban

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def my_team():
    '''
    Return the list of team members as a list of triplets (student_number, first_name, last_name).
    '''
    return [ (11592931, 'Zackariya', 'Taylor'),
             (11220139, 'Isobel', 'Jones'),
             (1124744, 'Sophia', 'Sweet') ]

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
        east  = x + 1, y
        south = x, y + 1
        west  = x - 1, y

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
            if x1 == x2:  # vertical wall
                if (x1, y1 - 1) in wall_cells and (x1, y2 + 1) in wall_cells:
                    min_y, max_y = min(y1, y2), max(y1, y2)
                    is_valid = True
                    for y in range(min_y + 1, max_y):
                        if (x1, y) in taboo_row_nullifier:
                            is_valid = False
                            break
                        if (x1 - 1, y) not in wall_cells and (x1 + 1, y) not in wall_cells:
                            is_valid = False
                            break
                    if is_valid:
                        for y in range(min_y + 1, max_y):
                            wall_taboo_cells.add((x1, y))
            elif y1 == y2:  # horizontal wall
                if (x1 - 1, y1) in wall_cells and (x2 + 1, y1) in wall_cells:
                    min_x, max_x = min(x1, x2), max(x1, x2)
                    is_valid = True
                    for x in range(min_x + 1, max_x):
                        if (x, y1) in taboo_row_nullifier:
                            is_valid = False
                            break
                        if (x, y1 - 1) not in wall_cells and (x, y1 + 1) not in wall_cells:
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
    Identify taboo cells in the warehouse (cells that if occupied by a box
    make the puzzle unsolvable).
    '''
    lines = str(warehouse).split('\n')
    wall_cells = set(warehouse.walls)
    taboo_row_nullifier = set(warehouse.targets) | set(find_2D_iterator(lines, '*')) | set(find_2D_iterator(lines, '#'))
    lines = [mark_outside_walls(line) for line in lines]
    candidate_taboo_cells = set(find_2D_iterator_exclude(lines, '.', '#', '*', '?'))
    corner_taboo_cells = get_corner_taboo_cells(candidate_taboo_cells, wall_cells)
    wall_taboo_cells = get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells)
    taboo_cells_set = corner_taboo_cells | wall_taboo_cells
    taboo_cell_map = get_taboo_cell_map(warehouse, taboo_cells_set)
    return taboo_cell_map

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# ------------------------------------------------------
# Macro-Move Helper functions for SokobanPuzzle
# ------------------------------------------------------
# In this approach the worker’s walking steps are aggregated
# into a single “macro” action that moves the worker to the
# necessary pushing position, then performs the push.
#
# We perform a BFS that, for each reachable cell,
# returns (distance, path) where path is a list of elementary moves.
# ------------------------------------------------------

def compute_reachable_and_paths(worker_pos, walls, boxes):
    """
    Compute reachable positions from worker_pos in the grid,
    while avoiding walls and boxes.
    Returns a dictionary: position -> (distance, path)
    where path is a list of elementary moves (strings).
    """
    from collections import deque
    moves = {
        "Left": (-1, 0),
        "Right": (1, 0),
        "Up": (0, -1),
        "Down": (0, 1)
    }
    frontier = deque()
    frontier.append(worker_pos)
    # Distance and path: position -> (distance, path)
    dist = {worker_pos: (0, [])}
    while frontier:
        pos = frontier.popleft()
        (x, y) = pos
        d, path = dist[pos]
        for move, (dx, dy) in moves.items():
            nx, ny = x + dx, y + dy
            newpos = (nx, ny)
            if newpos in walls or newpos in boxes:
                continue
            if newpos not in dist:
                new_path = path + [move]
                dist[newpos] = (d + 1, new_path)
                frontier.append(newpos)
    return dist  # contains all reachable positions with their walk cost and path

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SokobanPuzzle class using macro moves
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from itertools import combinations

class SokobanPuzzle(search.Problem):
    '''
    An instance of SokobanPuzzle represents a weighted Sokoban problem.
    In this macro-moves version, the worker’s movement (without pushes) is handled
    via a BFS that provides a full elementary path. Only moves that push a box generate
    a state change.
    '''
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.walls = set(warehouse.walls)
        self.targets = set(warehouse.targets)
        self.visited_box_states = set()
        self.deadlock_cache = {}
        # Caches:
        self.reachable_cache = {}  # key: (worker, frozenset(boxes)); value: dict of pos->(distance, path)
        self.h_cache = {}
        
        # Each box: (x, y, weight)
        boxes_with_weights = [(box[0], box[1], weight)
                              for box, weight in zip(warehouse.boxes, warehouse.weights)]
        boxes_with_weights.sort(key=lambda b: (b[1], b[0]))
        self.initial = (warehouse.worker, tuple(boxes_with_weights))
        
        if not hasattr(self, '_seen_box_configs'):
            self._seen_box_configs = set()

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
        return hash(self.initial)

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
        if any((bx, by) in self.taboo_set and (bx, by) not in self.targets for bx, by, _ in boxes):
            self.deadlock_cache[box_positions] = True
            return True
        if any(self.is_box_blocked(box_positions, (bx, by)) for bx, by, _ in boxes):
            return True
        if self.has_frozen_clusters(box_positions):
            return True
        return False

    # -------------------------------
    # Macro-move version of actions()
    # -------------------------------
    def actions(self, state):
        # Early prune: if state is taboo deadlock, do not expand further.
        if self.is_taboo_deadlock(state) and state != self.initial:
            return []
        (worker_x, worker_y), boxes = state
        boxes_set = {(b[0], b[1]) for b in boxes}

        # Build a key for caching BFS from worker position.
        key = (worker_x, worker_y, frozenset(boxes_set))
        if key in self.reachable_cache:
            reachable_dict = self.reachable_cache[key]
        else:
            reachable_dict = compute_reachable_and_paths((worker_x, worker_y), self.walls, boxes_set)
            self.reachable_cache[key] = reachable_dict

        moves = {
            "Left": (-1, 0),
            "Right": (1, 0),
            "Up": (0, -1),
            "Down": (0, 1)
        }
        macro_actions = []
        # For each box, see if we can push it in any direction.
        for i, (bx, by, weight) in enumerate(boxes):
            for move, (dx, dy) in moves.items():
                push_from = (bx + dx, by + dy)   # where the worker must stand
                target = (bx - dx, by - dy)        # where the box would be pushed to
                if push_from not in reachable_dict:
                    continue  # worker cannot get to the push position
                # Check that the target cell is free (i.e. not a wall or another box)
                if target in self.walls or target in boxes_set:
                    continue
                # Retrieve the path (list of elementary moves) to get to push_from.
                walk_distance, walk_path = reachable_dict[push_from]
                # Create a composite (macro) action:
                #   composite_action = (elementary_move_sequence, box_index, (dx, dy), total_cost)
                # where elementary_move_sequence = walk_path + [move] (the final move pushes the box)
                elementary_moves = walk_path + [move]
                total_cost = walk_distance + (1 + weight)
                macro_actions.append( (elementary_moves, i, (dx, dy), total_cost) )
        return macro_actions

    # ---------------------------------
    # Macro-move result: apply a push action.
    # ---------------------------------
    def result(self, state, action):
        # action is a tuple: (elementary_moves, box_index, (dx, dy), cost)
        _, box_index, (dx, dy), _ = action
        (worker, boxes) = state
        boxes = list(boxes)
        bx, by, weight = boxes[box_index]
        # The worker must be in position push_from (but for state update we ignore the walking path)
        # When a box is pushed, it moves to (bx - dx, by - dy) and the worker takes the box's original cell.
        new_box_pos = (bx - dx, by - dy, weight)
        boxes[box_index] = new_box_pos
        new_worker = (bx, by)   # worker ends where the pushed box originally was
        return (new_worker, tuple(sorted(boxes, key=lambda b: (b[1], b[0]))))

    def goal_test(self, state):
        _, boxes = state
        return all((b[0], b[1]) in self.targets for b in boxes)

    # -------------------------------
    # Macro-move path_cost: use the cost computed in the action.
    # -------------------------------
    def path_cost(self, c, state1, action, state2):
        # action is (elementary_moves, box_index, (dx, dy), cost)
        return c + action[3]

    def h(self, node):
        state = node.state
        if state in self.h_cache:
            return self.h_cache[state]
        box_pos = frozenset((b[0], b[1]) for b in state[1])
        if box_pos in self._seen_box_configs:
            penalty = 100
        else:
            penalty = 0
            self._seen_box_configs.add(box_pos)
        if self.is_deadlock(node.state):
            self.h_cache[state] = 10**6
            return 10**6
        worker, boxes = node.state
        box_cost = 0
        for bx, by, weight in boxes:
            if (bx, by) in self.targets:
                continue
            d = min(abs(bx - tx) + abs(by - ty) for (tx, ty) in self.targets)
            box_cost += d * (1 + weight * 0.5)
        computed_heuristic = box_cost + penalty
        self.h_cache[state] = computed_heuristic
        return computed_heuristic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# The check_elem_action_seq function remains unchanged.
# It expects a sequence of elementary moves.
# -------------------------------

def check_elem_action_seq(warehouse, action_seq):
    '''
    Check if the sequence of actions is legal.
    Returns the final state as a string if legal; otherwise, "Impossible".
    '''
    warehouse_copy = warehouse.copy()
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
        dx, dy = moves[action]
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

# --------------------------------------------------
# A helper to flatten composite (macro) actions into a list
# of elementary moves.
# --------------------------------------------------
def flatten_composite_actions(composite_actions):
    """Given a list of composite actions (each a tuple where the first element 
    is a list of elementary moves), return a single flattened list of moves."""
    flattened = []
    for comp in composite_actions:
        elementary_moves = comp[0]
        flattened.extend(elementary_moves)
    return flattened

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# solve_weighted_sokoban remains the same except that we flatten the solution.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_weighted_sokoban(warehouse):
    '''
    Analyse the given warehouse and return a solution action sequence and its cost.
    
    @param warehouse: a valid Warehouse object
    @return:
       If the puzzle is unsolvable: ('Impossible', None)
       Otherwise, (S, C) where S is a list of elementary moves (each a string) 
       and C is the total cost.
    '''
    problem = SokobanPuzzle(warehouse)
    # If puzzle is already solved.
    if all((b[0], b[1]) in warehouse.targets for b in warehouse.boxes):
        return [], 0
    result = search.astar_graph_search(problem)
    if result is None:
        return ['Impossible'], None
    # result.solution() is a list of composite actions.
    composite_solution = result.solution()
    elementary_solution = flatten_composite_actions(composite_solution)
    return elementary_solution, result.path_cost

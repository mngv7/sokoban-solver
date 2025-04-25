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

import search 
import sokoban
from collections import deque
from itertools import combinations

# -----------------------------------------------------------------------------
def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplets of the form (student_number, first_name, last_name)
    '''
    return [
        (11592931, 'Zackariya', 'Taylor'),
        (11220139, 'Isobel', 'Jones'),
        (1124744, 'Sophia', 'Sweet')
    ]

# -----------------------------------------------------------------------------
from sokoban import find_2D_iterator

def find_1D_iterator_exclude(line, *exclude_chars):
    '''
    Returns positions in a string that don't match excluded characters
    '''    
    for pos, char in enumerate(line):
        if char not in exclude_chars:
            yield pos

def find_2D_iterator_exclude(lines, *exclude_chars):
    '''
    Returns (x, y) positions in a grid that don't match excluded characters.
    '''
    for y, line in enumerate(lines):
        for x in find_1D_iterator_exclude(line, *exclude_chars):
            yield (x, y)

def get_corner_taboo_cells(candidate_taboo_cells, wall_cells):
    '''
    Returns corner cells that are taboo based on adjacent walls
    '''
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
    '''
    Returns additional taboo cells along walls between taboo corners
    '''
    wall_taboo_cells = set()
    for corner1, corner2 in combinations(corner_taboo_cells, 2):
        x1, y1 = corner1
        x2, y2 = corner2
        if x1 == x2:  # Vertical alignment.
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
        elif y1 == y2:  # Horizontal alignment.
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
    '''
    Returns a string-based map marking taboo cells with 'X'
    '''
    lines = [list(line) for line in str(warehouse).split('\n')]
    for i, line in enumerate(lines):
        for j in range(len(line)):
            if (j, i) in taboo_cells:
                line[j] = 'X'
            elif line[j] not in {'#', ' '}:
                line[j] = ' '

    taboo_cell_map = "\n".join("".join(line) for line in lines)
    return taboo_cell_map

def get_interior_cells(warehouse):
    ''' 
    Use BFS from the worker to identify cells inside the warehouse.
    '''
    lines = [list(line) for line in str(warehouse).split('\n')]
    height = len(lines)

    walls = set(warehouse.walls)
    visited = set()
    queue = deque()
    
    # Start BFS from the worker position
    start = warehouse.worker
    if start in walls:
        return set()  # Fail-safe: worker embedded in a wall?

    queue.append(start)
    visited.add(start)

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        x, y = queue.popleft()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= ny < height and 0 <= nx < len(lines[ny]):
                if (nx, ny) not in walls and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    return visited

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
    interior_cells = get_interior_cells(warehouse)

    taboo_row_nullifier = set(warehouse.targets) | set(find_2D_iterator(lines, '*')) | set(find_2D_iterator(lines, '#'))
    candidate_taboo_cells = set(find_2D_iterator_exclude(lines, '.', '#', '*', '?'))

    candidate_taboo_cells &= interior_cells

    corner_taboo_cells = get_corner_taboo_cells(candidate_taboo_cells, wall_cells)
    wall_taboo_cells = get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells)
    taboo_cells = (corner_taboo_cells | wall_taboo_cells) & interior_cells

    taboo_cell_map = get_taboo_cell_map(warehouse, taboo_cells)

    return taboo_cell_map

# -----------------------------------------------------------------------------
def get_reachable_positions(worker_pos, walls, boxes):
    '''
    Compute and return all positions that the worker can reach from worker_pos
    without moving any box. A standard BFS is used for performance.
    '''
    visited = {worker_pos}
    frontier = deque([worker_pos])
    while frontier:
        x, y = frontier.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in walls and (nx, ny) not in boxes and (nx, ny) not in visited:
                visited.add((nx, ny))
                frontier.append((nx, ny))
    return visited

# -----------------------------------------------------------------------------

class SokobanPuzzle(search.Problem):
    '''
    An instance of SokobanPuzzle represents a weighted Sokoban puzzle.
    It holds the walls, targets, weighted boxes, worker position, taboo cells, and
    precomputed data to accelerate the solver.
    '''
    
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.walls = set(warehouse.walls)
        self.targets = set(warehouse.targets)
        self.deadlock_cache = {}

        boxes_with_weights = [(box[0], box[1], weight)
                              for box, weight in zip(warehouse.boxes, warehouse.weights)]
        boxes_with_weights.sort(key=lambda b: (b[1], b[0]))
        self.initial = (warehouse.worker, tuple(boxes_with_weights))

        taboo_map = taboo_cells(warehouse)
        self.taboo_set = {(j, i)
                          for i, line in enumerate(taboo_map.splitlines())
                          for j, ch in enumerate(line)
                          if ch == 'X'}

        # Memoized function to compute minimum target distance for any cell
        self.compute_min_target_distance = search.memoize(
            lambda bx, by: min(abs(bx - tx) + abs(by - ty) for (tx, ty) in self.targets)
        )

    def __eq__(self, other):
        return isinstance(other, SokobanPuzzle) and self.initial == other.initial

    def __hash__(self):
        return hash(self.initial)

    def actions(self, state):
        directions = ['Up', 'Down', 'Left', 'Right']
        (wx, wy), boxes = state
        boxes_xy = {(b[0], b[1]) for b in boxes}
        reachable = get_reachable_positions((wx, wy), self.walls, boxes_xy)
        moves = {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1)}
        legal_actions = []
        for action in directions:
            dx, dy = moves[action]
            nx, ny = wx + dx, wy + dy
            if (nx, ny) in self.walls:
                continue
            if (nx, ny) in boxes_xy:
                bnx, bny = nx + dx, ny + dy
                if (bnx, bny) in self.walls or (bnx, bny) in boxes_xy or (bnx, bny) in self.taboo_set:
                    continue
                if (wx, wy) in reachable:
                    legal_actions.append(action)
            else:
                if (nx, ny) in reachable:
                    legal_actions.append(action)
        return legal_actions

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
        for pos, box in b2_xy.items():
            if pos not in b1_xy:
                moved_box = box
                break
        if moved_box:
            return c + 1 + moved_box[2]
        return c + 1

    def h(self, node):
        _, boxes = node.state
        box_cost = 0
        for bx, by, weight in boxes:
            if (bx, by) in self.targets:
                continue
            d = self.compute_min_target_distance(bx, by)
            box_cost += d * (1 + weight)
        return box_cost


# -----------------------------------------------------------------------------
def check_elem_action_seq(warehouse, action_seq):
    '''
    Verify if a sequence of actions is legal in a warehouse.
    Returns the resulting state as a string if legal; otherwise, returns "Impossible".
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

# -----------------------------------------------------------------------------
def solve_weighted_sokoban(warehouse):
    '''
    Solve the weighted Sokoban puzzle for the given warehouse.
    
    Returns:
      If unsolvable: ('Impossible', None)
      Otherwise: (solution_action_sequence, total_cost)
    '''
    if all((b[0], b[1]) in warehouse.targets for b in warehouse.boxes):
        return [], 0
    
    problem = SokobanPuzzle(warehouse)
    result = search.astar_graph_search(problem)
    
    if result is None:
        return ['Impossible'], None
    return result.solution(), result.path_cost

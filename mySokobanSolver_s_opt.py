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
from collections import defaultdict, deque
from itertools import combinations
from functools import lru_cache

# Predefined moves dictionary for consistency and speed.
MOVES = {
    "Left":  (-1, 0),
    "Right": (1, 0),
    "Up":    (0, -1),
    "Down":  (0, 1)
}

# ---------------------------------------------------------------------
def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplets of the form (student_number, first_name, last_name)
    '''
    return [(11592931, 'Zackariya', 'Taylor'),
            (11220139, 'Isobel', 'Jones'),
            (1124744, 'Sophia', 'Sweet')]

# ---------------------------------------------------------------------
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
    # Vertical segments: group corners by column.
    corners_by_col = defaultdict(list)
    for (x, y) in corner_taboo_cells:
        corners_by_col[x].append(y)
    for x, ys in corners_by_col.items():
        ys.sort()
        for i in range(len(ys) - 1):
            y1, y2 = ys[i], ys[i+1]
            if (x, y1 - 1) in wall_cells and (x, y2 + 1) in wall_cells:
                is_valid = True
                for y in range(y1 + 1, y2):
                    if (x, y) in taboo_row_nullifier:
                        is_valid = False
                        break
                    if ((x - 1, y) not in wall_cells and (x + 1, y) not in wall_cells):
                        is_valid = False
                        break
                if is_valid:
                    for y in range(y1 + 1, y2):
                        wall_taboo_cells.add((x, y))
    # Horizontal segments: group corners by row.
    corners_by_row = defaultdict(list)
    for (x, y) in corner_taboo_cells:
        corners_by_row[y].append(x)
    for y, xs in corners_by_row.items():
        xs.sort()
        for i in range(len(xs) - 1):
            x1, x2 = xs[i], xs[i+1]
            if (x1 - 1, y) in wall_cells and (x2 + 1, y) in wall_cells:
                is_valid = True
                for x in range(x1 + 1, x2):
                    if (x, y) in taboo_row_nullifier:
                        is_valid = False
                        break
                    if ((x, y - 1) not in wall_cells and (x, y + 1) not in wall_cells):
                        is_valid = False
                        break
                if is_valid:
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
    return "\n".join("".join(line) for line in lines)

def mark_outside_walls(s):
    first = s.find('#')
    last = s.rfind('#')
    if first == -1 or last == -1:
        return s  
    return '?' * first + s[first:last + 1] + '?' * (len(s) - last - 1)

def taboo_cells(warehouse):
    '''  
    Identify the taboo cells of a warehouse.
    
    A "taboo cell" is a cell inside the warehouse such that whenever a box is pushed
    onto it, the puzzle becomes unsolvable.
    
    Rules:
      Rule 1: A cell is taboo if it is a corner (adjacent to two walls) and not a target.
      Rule 2: All cells between two corners along a wall are taboo if none is a target.
    
    @param warehouse: a Warehouse object with a worker.
    @return: A string representation of the warehouse with walls marked as '#' and taboo cells as 'X'.
             (No worker, target, or box marks are included.)
    '''
    lines = str(warehouse).split('\n')
    wall_cells = set(warehouse.walls)
    taboo_row_nullifier = set(warehouse.targets) | set(find_2D_iterator(lines, '*')) | set(find_2D_iterator(lines, '#'))
    lines = [mark_outside_walls(line) for line in lines]
    candidate_taboo_cells = set(find_2D_iterator_exclude(lines, '.', '#', '*', '?'))
    corner_taboo_cells = get_corner_taboo_cells(candidate_taboo_cells, wall_cells)
    wall_taboo_cells = get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells)
    computed_taboo_set = corner_taboo_cells | wall_taboo_cells
    taboo_cell_map = get_taboo_cell_map(warehouse, computed_taboo_set)
    return taboo_cell_map

# ---------------------------------------------------------------------
# Optimize reachable positions with caching.
@lru_cache(maxsize=10000)
def _cached_reachable(worker, boxes, walls):
    # worker: a tuple (x, y)
    # boxes: a frozenset of box positions
    # walls: a frozenset of wall positions (constant per warehouse)
    frontier = deque([worker])
    visited = set()
    while frontier:
        pos = frontier.popleft()
        if pos in visited:
            continue
        visited.add(pos)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            newpos = (pos[0] + dx, pos[1] + dy)
            if newpos not in walls and newpos not in boxes and newpos not in visited:
                frontier.append(newpos)
    return frozenset(visited)

def get_reachable_positions(worker_pos, walls, boxes):
    # This fallback function (used by check_elem_action_seq) runs a basic BFS.
    visited = set()
    frontier = deque([worker_pos])
    while frontier:
        pos = frontier.popleft()
        if pos in visited:
            continue
        visited.add(pos)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            newpos = (pos[0] + dx, pos[1] + dy)
            if newpos not in walls and newpos not in boxes and newpos not in visited:
                frontier.append(newpos)
    return visited

# ---------------------------------------------------------------------
class SokobanPuzzle(search.Problem):
    '''
    An instance of 'SokobanPuzzle' represents a Sokoban puzzle.
    It contains the walls, targets, boxes (with weights), and the worker.
    This implementation is fully compatible with the search functions in search.py.
    '''
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.walls = set(warehouse.walls)
        self.walls_frozenset = frozenset(warehouse.walls)  # For fast lookup in cached reachability.
        self.targets = set(warehouse.targets)
        self.visited_box_states = set()
        self.deadlock_cache = {}
        # Each box is represented as (x, y, weight)
        boxes_with_weights = [(box[0], box[1], weight)
                              for box, weight in zip(warehouse.boxes, warehouse.weights)]
        boxes_with_weights.sort(key=lambda b: (b[1], b[0]))
        self.initial = (warehouse.worker, tuple(boxes_with_weights))
        self._seen_box_configs = set()
        # Compute taboo cells.
        taboo_map = taboo_cells(warehouse)
        self.taboo_set = {(j, i)
                          for i, line in enumerate(taboo_map.splitlines())
                          for j, ch in enumerate(line) if ch == 'X'}
        self._moves = MOVES

    def __eq__(self, other):
        return isinstance(other, SokobanPuzzle) and self.initial == other.initial

    def __hash__(self):
        return hash(self.initial)

    def is_box_blocked(self, box_positions, box):
        x, y = box
        obstacles = self.walls.union(box_positions - {(x, y)})
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

    def actions(self, state):
        # If a state is clearly deadlocked via taboo configuration, do not generate actions.
        if self.is_taboo_deadlock(state) and state != self.initial:
            return []
        (wx, wy), boxes = state
        boxes_xy = {(b[0], b[1]) for b in boxes}
        # Use the cached reachability function.
        worker = (wx, wy)
        boxes_fro = frozenset(boxes_xy)
        reachable = _cached_reachable(worker, boxes_fro, self.walls_frozenset)
        moves = self._moves
        available_actions = []
        for action, (dx, dy) in moves.items():
            nx, ny = wx + dx, wy + dy
            if (nx, ny) in self.walls:
                continue
            if (nx, ny) in boxes_xy:
                bnx, bny = nx + dx, ny + dy
                if (bnx, bny) in self.walls or (bnx, bny) in boxes_xy:
                    continue
                # Check that the worker can reach the pushing position.
                if worker in reachable:
                    available_actions.append(action)
            else:
                if (nx, ny) in reachable:
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
        return all((b[0], b[1]) in self.targets for b in boxes)

    def path_cost(self, c, state1, action, state2):
        _, b1 = state1
        _, b2 = state2
        b1_dict = {(b[0], b[1]): (b[0], b[1], b[2]) for b in b1}
        for (bx, by, w) in b2:
            if (bx, by) not in b1_dict:
                return c + 1 + w
        return c + 1

    def h(self, node):
        state = node.state
        box_pos = frozenset((b[0], b[1]) for b in state[1])
        penalty = 100 if box_pos in self._seen_box_configs else 0
        if not penalty:
            self._seen_box_configs.add(box_pos)
        if self.is_deadlock(node.state):
            return 10**6
        worker, boxes = node.state
        box_cost = 0
        for bx, by, weight in boxes:
            if (bx, by) in self.targets:
                continue
            d = min(abs(bx - tx) + abs(by - ty) for (tx, ty) in self.targets)
            box_cost += d * (1 + weight * 0.5)
        return box_cost + penalty

# ---------------------------------------------------------------------
def check_elem_action_seq(warehouse, action_seq):
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

# ---------------------------------------------------------------------
def solve_weighted_sokoban(warehouse):
    if all((b[0], b[1]) in warehouse.targets for b in warehouse.boxes):
        return [], 0
    problem = SokobanPuzzle(warehouse)
    result = search.astar_graph_search(problem)
    if result is None:
        return ['Impossible'], None
    return result.solution(), result.path_cost

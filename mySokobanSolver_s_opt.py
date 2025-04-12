"""
    Sokoban assignment

The functions and classes defined in this module will be called by a marker script. 
You should complete the functions and classes according to their specified interfaces.

No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.

You are NOT allowed to change the defined interfaces.
In other words, you must fully adhere to the specifications of the 
functions, their arguments and returned values.

You have to make sure that your code works with the provided 
search.py and sokoban.py files as your code will be tested 
with these files.

Last modified by 2025-04-17 
"""

import search
import sokoban

# ------------------------------------------------------------------
# Provide your team info
# ------------------------------------------------------------------
def my_team():
    '''
    Return the list of team members of this assignment submission as a list
    of triplets of the form (student_number, first_name, last_name)
    '''
    return [
        (11592931, 'Zackariya', 'Taylor'),
        (11220139, 'Isobel', 'Jones'),
        (1124744,  'Sophia', 'Sweet')
    ]

# ------------------------------------------------------------------
# Helper iterators for taboo cells
# ------------------------------------------------------------------
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
    for c1 in corner_taboo_cells:
        for c2 in corner_taboo_cells:
            if c1 == c2:
                continue
            x1, y1 = c1
            x2, y2 = c2
            # vertical
            if x1 == x2:
                if (x1, y1 - 1) in wall_cells and (x1, y2 + 1) in wall_cells:
                    min_y, max_y = min(y1, y2), max(y1, y2)
                    valid = True
                    for yy in range(min_y + 1, max_y):
                        if (x1, yy) in taboo_row_nullifier:
                            valid = False
                            break
                        if (x1 - 1, yy) not in wall_cells and (x1 + 1, yy) not in wall_cells:
                            valid = False
                            break
                    if valid:
                        for yy in range(min_y + 1, max_y):
                            wall_taboo_cells.add((x1, yy))
            # horizontal
            elif y1 == y2:
                if (x1 - 1, y1) in wall_cells and (x2 + 1, y1) in wall_cells:
                    min_x, max_x = min(x1, x2), max(x1, x2)
                    valid = True
                    for xx in range(min_x + 1, max_x):
                        if (xx, y1) in taboo_row_nullifier:
                            valid = False
                            break
                        if (xx, y1 - 1) not in wall_cells and (xx, y1 + 1) not in wall_cells:
                            valid = False
                            break
                    if valid:
                        for xx in range(min_x + 1, max_x):
                            wall_taboo_cells.add((xx, y1))
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
    last  = s.rfind('#')
    if first == -1 or last == -1:
        return s
    return ('?' * first) + s[first:last + 1] + ('?' * (len(s) - last - 1))

def taboo_cells(warehouse):
    """
    Identify the taboo cells of a warehouse.
    """
    lines = str(warehouse).split('\n')
    wall_cells = set(warehouse.walls)
    taboo_row_nullifier = (set(warehouse.targets) |
                           set(find_2D_iterator(lines, '*')) |
                           set(find_2D_iterator(lines, '#')))
    lines = [mark_outside_walls(line) for line in lines]
    candidate_taboo = set(find_2D_iterator_exclude(lines, '.', '#', '*', '?'))
    corners = get_corner_taboo_cells(candidate_taboo, wall_cells)
    wall_tabs = get_wall_taboo_cells(corners, taboo_row_nullifier, wall_cells)
    taboo_cells_set = corners | wall_tabs
    return get_taboo_cell_map(warehouse, taboo_cells_set)

# ------------------------------------------------------------------
# BFS to determine worker reachable squares (single-step approach).
# We use caching to avoid recomputing for the same arrangement.
# ------------------------------------------------------------------
def get_reachable_positions(worker_pos, walls, boxes):
    from collections import deque
    visited = set()
    queue = deque([worker_pos])
    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if (nx, ny) not in walls and (nx, ny) not in boxes and (nx, ny) not in visited:
                queue.append((nx, ny))
    return visited

# ------------------------------------------------------------------
# Minimal assignment cost function using bitmask DP.
# ------------------------------------------------------------------
def dp_assignment(cost_matrix):
    """
    cost_matrix[i][j]: cost of assigning box i to target j.
    Returns minimal sum of assignment cost.
    """
    n = len(cost_matrix)
    dp = {0: 0}  # key: bitmask of which boxes have been assigned, value: minimal cost so far
    for mask in range(1 << n):
        # j = number of bits set in mask => which target index to assign next
        j = bin(mask).count('1')
        if j >= n:
            continue
        for i in range(n):
            if not (mask & (1 << i)):  # if box i not assigned yet
                new_mask = mask | (1 << i)
                cost = dp[mask] + cost_matrix[i][j]
                if new_mask not in dp or cost < dp[new_mask]:
                    dp[new_mask] = cost
    return dp[(1 << n) - 1]

# ------------------------------------------------------------------
# SokobanPuzzle: single-step expansions, with advanced caching & heuristic
# ------------------------------------------------------------------
from itertools import combinations

class SokobanPuzzle(search.Problem):
    """
    A single-step (OG) Sokoban puzzle class with optimizations:
      - BFS caching
      - advanced deadlock checks
      - minimal assignment heuristic
      - repeated-state penalty
    """
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.walls     = set(warehouse.walls)
        self.targets   = set(warehouse.targets)
        self.deadlock_cache = {}
        self.reachable_cache = {}
        self.h_cache = {}

        # For repeated-state penalty
        if not hasattr(self, "_seen_box_configs"):
            self._seen_box_configs = set()

        # Gather boxes + weights
        boxes_with_weights = [(b[0], b[1], w) 
                              for b, w in zip(warehouse.boxes, warehouse.weights)]
        # Sort them for consistent state ordering
        boxes_with_weights.sort(key=lambda x: (x[1], x[0]))
        self.initial = (warehouse.worker, tuple(boxes_with_weights))

        # Precompute taboo set
        taboo_map = taboo_cells(warehouse)
        self.taboo_set = set()
        for i, row in enumerate(taboo_map.splitlines()):
            for j, ch in enumerate(row):
                if ch == 'X':
                    self.taboo_set.add((j, i))

    def __eq__(self, other):
        return isinstance(other, SokobanPuzzle) and self.initial == other.initial

    def __hash__(self):
        return hash(self.initial)

    def is_box_blocked(self, box_positions, box):
        x, y = box
        obstacles = set(box_positions) | self.walls
        # Check corner block
        if ((x-1,y) in obstacles and (x,y-1) in obstacles): return True
        if ((x+1,y) in obstacles and (x,y-1) in obstacles): return True
        if ((x-1,y) in obstacles and (x,y+1) in obstacles): return True
        if ((x+1,y) in obstacles and (x,y+1) in obstacles): return True
        return False

    def has_frozen_clusters(self, box_positions):
        # If 2 adjacent boxes are both blocked, that's a cluster deadlock
        for b1, b2 in combinations(box_positions, 2):
            if abs(b1[0] - b2[0]) + abs(b1[1] - b2[1]) == 1:
                if self.is_box_blocked(box_positions, b1) and \
                   self.is_box_blocked(box_positions, b2):
                    return True
        return False

    def is_taboo_deadlock(self, state):
        # If any box is on a taboo cell (and not on a target), it's a deadlock
        _, boxes = state
        for bx, by, _ in boxes:
            if (bx, by) in self.taboo_set and (bx, by) not in self.targets:
                return True
        return False

    def is_deadlock(self, state):
        """
        Check various deadlocks: taboo, corner blocks, cluster.
        Cache results by box positions.
        """
        _, boxes = state
        box_positions = frozenset((b[0], b[1]) for b in boxes)
        if box_positions in self.deadlock_cache:
            return self.deadlock_cache[box_positions]

        # 1) taboo cells
        if any(((bx, by) in self.taboo_set and (bx, by) not in self.targets)
               for bx, by, _ in boxes):
            self.deadlock_cache[box_positions] = True
            return True

        # 2) corner block
        if any(self.is_box_blocked(box_positions, (bx, by)) for bx, by, _ in boxes):
            self.deadlock_cache[box_positions] = True
            return True

        # 3) cluster freeze
        if self.has_frozen_clusters(box_positions):
            self.deadlock_cache[box_positions] = True
            return True

        self.deadlock_cache[box_positions] = False
        return False

    # ------------------------------------------------------------------
    # actions() for single-step expansions
    # ------------------------------------------------------------------
    def actions(self, state):
        if self.is_taboo_deadlock(state) and state != self.initial:
            return []
        directions = ['Left','Right','Up','Down']
        (wx, wy), boxes = state
        boxes_xy = {(b[0], b[1]) for b in boxes}

        # BFS caching
        key = (wx, wy, frozenset(boxes_xy))
        if key in self.reachable_cache:
            reachable = self.reachable_cache[key]
        else:
            reachable = get_reachable_positions((wx, wy), self.walls, boxes_xy)
            self.reachable_cache[key] = reachable

        moves = {
            'Left':  (-1, 0),
            'Right': (1, 0),
            'Up':    (0, -1),
            'Down':  (0, 1)
        }
        valid_actions = []
        for d in directions:
            dx, dy = moves[d]
            nx, ny = wx + dx, wy + dy
            if (nx, ny) in self.walls:
                continue
            if (nx, ny) in boxes_xy:
                # Potential push
                bnx, bny = nx + dx, ny + dy
                if (bnx, bny) in self.walls or (bnx, bny) in boxes_xy:
                    continue
                # Worker must be able to get behind that box
                if (wx, wy) in reachable:
                    valid_actions.append(d)
            else:
                # Simple move
                if (nx, ny) in reachable:
                    valid_actions.append(d)
        return valid_actions

    # ------------------------------------------------------------------
    # result() applies a single-step action
    # ------------------------------------------------------------------
    def result(self, state, action):
        (wx, wy), boxes = state
        boxes = list(boxes)
        moves = {
            'Left':  (-1, 0),
            'Right': (1, 0),
            'Up':    (0, -1),
            'Down':  (0, 1)
        }
        dx, dy = moves[action]
        new_worker = (wx + dx, wy + dy)
        for i, (bx, by, w) in enumerate(boxes):
            if (bx, by) == new_worker:
                # push
                new_box = (bx + dx, by + dy, w)
                boxes[i] = new_box
                break
        boxes.sort(key=lambda b: (b[1], b[0]))
        return (new_worker, tuple(boxes))

    def goal_test(self, state):
        _, boxes = state
        return all((b[0], b[1]) in self.targets for b in boxes)

    # ------------------------------------------------------------------
    # path_cost with box weight
    # ------------------------------------------------------------------
    def path_cost(self, c, s1, action, s2):
        (_, boxes1) = s1
        (_, boxes2) = s2
        # Identify which box moved
        boxes1_set = {(b[0], b[1]): b for b in boxes1}
        boxes2_set = {(b[0], b[1]): b for b in boxes2}
        moved_box = None
        for pos, b in boxes2_set.items():
            if pos not in boxes1_set:
                moved_box = b
                break
        if moved_box:
            return c + 1 + moved_box[2]
        return c + 1

    # ------------------------------------------------------------------
    # Improved heuristic: Minimal assignment (bitmask DP) + penalty for repeats
    # ------------------------------------------------------------------
    def h(self, node):
        state = node.state
        if state in self.h_cache:
            return self.h_cache[state]

        if self.is_deadlock(state):
            self.h_cache[state] = 10**6
            return 10**6

        # repeated-state penalty
        box_positions = frozenset((b[0], b[1]) for b in state[1])
        if box_positions in self._seen_box_configs:
            penalty = 100
        else:
            penalty = 0
            self._seen_box_configs.add(box_positions)

        # build cost matrix (ManhattanDist * (1 + weight*0.5))
        boxes = state[1]
        cost_matrix = []
        for (bx, by, w) in boxes:
            row = []
            for (tx, ty) in self.targets:
                dist = abs(bx - tx) + abs(by - ty)
                row.append(dist * (1 + 0.5 * w))
            cost_matrix.append(row)

        assignment_cost = dp_assignment(cost_matrix)
        val = assignment_cost + penalty
        self.h_cache[state] = val
        return val

# ------------------------------------------------------------------
# check_elem_action_seq: unchanged.
# ------------------------------------------------------------------
def check_elem_action_seq(warehouse, action_seq):
    """
    Check if the sequence of actions is legal, returning "Impossible" or final layout as a string.
    """
    warehouse_copy = warehouse.copy()
    moves = {
        "Left":  (-1, 0),
        "Right": (1, 0),
        "Up":    (0, -1),
        "Down":  (0, 1)
    }
    worker_x, worker_y = warehouse_copy.worker
    boxes = set(warehouse_copy.boxes)
    walls = set(warehouse_copy.walls)
    for action in action_seq:
        if action not in moves:
            return "Impossible"
        dx, dy = moves[action]
        nx, ny = worker_x + dx, worker_y + dy
        # check walls
        if (nx, ny) in walls:
            return "Impossible"
        # check boxes
        if (nx, ny) in boxes:
            n2x, n2y = nx + dx, ny + dy
            if (n2x, n2y) in walls or (n2x, n2y) in boxes:
                return "Impossible"
            boxes.remove((nx, ny))
            boxes.add((n2x, n2y))
        worker_x, worker_y = nx, ny
    warehouse_copy.worker = (worker_x, worker_y)
    warehouse_copy.boxes = tuple(sorted(boxes, key=lambda b: (b[1], b[0])))
    return str(warehouse_copy)

# ------------------------------------------------------------------
# solve_weighted_sokoban: run A* with the above puzzle definition
# ------------------------------------------------------------------
def solve_weighted_sokoban(warehouse):
    """
    Solve the puzzle with single-step expansions and advanced heuristic.
    Return (action_list, cost) or (['Impossible'], None) if unsolvable.
    """
    problem = SokobanPuzzle(warehouse)
    # quick check if already solved
    if all((b[0], b[1]) in warehouse.targets for b in warehouse.boxes):
        return [], 0

    result = search.astar_graph_search(problem)
    if result is None:
        return ['Impossible'], None

    return result.solution(), result.path_cost

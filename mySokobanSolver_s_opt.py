"""
    Sokoban assignment

    [Original assignment header comments remain unchanged]
"""

import search 
import sokoban
from collections import deque
from itertools import combinations

# Predefined constant for moves (used by several methods)
MOVES = {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1)}


def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)
    '''
    return [(11592931, 'Zackariya', 'Taylor'),
            (11220139, 'Isobel', 'Jones'),
            (1124744, 'Sophia', 'Sweet')]

# -----------------------------------------------------------------------------

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
    for candidate in candidate_taboo_cells:
        x, y = candidate
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
    for corner1 in corner_taboo_cells:
        for corner2 in corner_taboo_cells:
            if corner1 == corner2:
                continue
            x1, y1 = corner1
            x2, y2 = corner2

            if x1 == x2:  # vertical check
                if (x1, y1 - 1) in wall_cells and (x1, y2 + 1) in wall_cells:
                    min_y, max_y = min(y1, y2), max(y1, y2)
                    valid = True
                    for y in range(min_y + 1, max_y):
                        if (x1, y) in taboo_row_nullifier:
                            valid = False
                            break
                        if (x1 - 1, y) not in wall_cells and (x1 + 1, y) not in wall_cells:
                            valid = False
                            break
                    if valid:
                        for y in range(min_y + 1, max_y):
                            wall_taboo_cells.add((x1, y))

            elif y1 == y2:  # horizontal check
                if (x1 - 1, y1) in wall_cells and (x2 + 1, y1) in wall_cells:
                    min_x, max_x = min(x1, x2), max(x1, x2)
                    valid = True
                    for x in range(min_x + 1, max_x):
                        if (x, y1) in taboo_row_nullifier:
                            valid = False
                            break
                        if (x, y1 - 1) not in wall_cells and (x, y1 + 1) not in wall_cells:
                            valid = False
                            break
                    if valid:
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
    return "\n".join("".join(line) for line in lines)

def mark_outside_walls(s):
    first = s.find('#')
    last = s.rfind('#')
    if first == -1 or last == -1:
        return s  
    return '?' * first + s[first:last + 1] + '?' * (len(s) - last - 1)

def taboo_cells(warehouse):
    '''  
    [Docstring omitted for brevity: It generates a map of taboo cells using Rule 1 and Rule 2.]
    '''
    lines = str(warehouse).split('\n')
    wall_cells = set(warehouse.walls)
    taboo_row_nullifier = set(warehouse.targets) | set(find_2D_iterator(lines, '*')) | set(find_2D_iterator(lines, '#'))
    lines = [mark_outside_walls(line) for line in lines]
    candidate_taboo_cells = set(find_2D_iterator_exclude(lines, '.', '#', '*', '?'))
    corner_taboo_cells = get_corner_taboo_cells(candidate_taboo_cells, wall_cells)
    wall_taboo_cells = get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells)
    taboo_set = corner_taboo_cells | wall_taboo_cells
    return get_taboo_cell_map(warehouse, taboo_set)

def get_reachable_positions(worker_pos, walls, boxes):
    visited = set()
    frontier = deque([worker_pos])
    while frontier:
        x, y = frontier.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in MOVES.values():
            nx, ny = x + dx, y + dy
            if (nx, ny) not in walls and (nx, ny) not in boxes and (nx, ny) not in visited:
                frontier.append((nx, ny))
    return visited

# -----------------------------------------------------------------------------

class SokobanPuzzle(search.Problem):
    '''
    An instance of SokobanPuzzle represents a Sokoban puzzle.
    [Rest of docstring omitted for brevity]
    '''

    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.walls = set(warehouse.walls)
        self.targets = set(warehouse.targets)
        self.visited_box_states = set()
        self.deadlock_cache = {}

        # each box is represented as (x, y, weight) tuple
        boxes_with_weights = [(b[0], b[1], w) for b, w in zip(warehouse.boxes, warehouse.weights)]
        boxes_with_weights.sort(key=lambda b: (b[1], b[0]))
        self.initial = (warehouse.worker, tuple(boxes_with_weights))
        
        self._seen_box_configs = set()
        self._reachable_cache = {}    # For caching reachable positions during search
        self._manhattan_cache = {}    # For caching Manhattan distances from boxes to nearest target

        # Precompute taboo cells and build a lookup set
        taboo_map = taboo_cells(warehouse)
        self.taboo_set = {(j, i)
                          for i, line in enumerate(taboo_map.splitlines())
                          for j, ch in enumerate(line) if ch == 'X'}

    def __eq__(self, other):
        return isinstance(other, SokobanPuzzle) and self.initial == other.initial

    def __hash__(self):
        return hash(self.initial)  # hash is based only on box positions

    def is_box_blocked(self, box_positions, box):
        x, y = box
        obstacles = self.walls.union(box_positions - {(x, y)})
        if ((x - 1, y) in obstacles and (x, y - 1) in obstacles): 
            return True
        if ((x + 1, y) in obstacles and (x, y - 1) in obstacles): 
            return True
        if ((x - 1, y) in obstacles and (x, y + 1) in obstacles): 
            return True
        if ((x + 1, y) in obstacles and (x, y + 1) in obstacles): 
            return True
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

        # Soft deadlocks (might be reversible)
        if any(self.is_box_blocked(box_positions, (bx, by)) for bx, by, _ in boxes):
            return True

        if self.has_frozen_clusters(box_positions):
            return True

        return False

    def get_reachable_cached(self, worker, boxes):
        """
        Compute (or retrieve from cache) the set of reachable positions for the worker given current boxes.
        """
        key = (worker, frozenset(boxes))
        if key not in self._reachable_cache:
            self._reachable_cache[key] = get_reachable_positions(worker, self.walls, set(boxes))
        return self._reachable_cache[key]

    def actions(self, state):
        # Do not generate actions if the state is in a taboo deadlock (unless it is the initial state)
        if self.is_taboo_deadlock(state) and state != self.initial:
            return []
        
        directions = ['Up', 'Down', 'Left', 'Right']
        (wx, wy), boxes = state
        boxes_xy = {(b[0], b[1]) for b in boxes}
        # Use cached reachable positions for the worker to avoid repeated BFS computations
        reachable = self.get_reachable_cached((wx, wy), boxes_xy)
        moves = MOVES  # using the pre-made constant
        actions = []

        for action in directions:
            dx, dy = moves[action]
            nx, ny = wx + dx, wy + dy
            if (nx, ny) in self.walls:
                continue
            if (nx, ny) in boxes_xy:
                # Pushing a box: check if the cell beyond the box is free
                bnx, bny = nx + dx, ny + dy
                if (bnx, bny) in self.walls or (bnx, bny) in boxes_xy:
                    continue
                if (wx, wy) in reachable:  # ensure worker can reach the pushing position
                    actions.append(action)
            else:
                if (nx, ny) in reachable:
                    actions.append(action)
        return actions

    def result(self, state, action):
        (wx, wy), boxes = state
        boxes = list(boxes)
        dx, dy = MOVES[action]
        new_worker = (wx + dx, wy + dy)
        for i, (bx, by, w) in enumerate(boxes):
            if (bx, by) == new_worker:
                # move the box and maintain its weight
                boxes[i] = (bx + dx, by + dy, w)
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
        # Identify the box that moved by comparing positions
        for pos, box in b2_xy.items():
            if pos not in b1_xy:
                moved_box = box
                break
        if moved_box:
            # Add additional cost based on the box weight
            return c + 1 + moved_box[2]
        return c + 1

    def h(self, node):
        state = node.state
        box_pos = frozenset((b[0], b[1]) for b in state[1])

        # Heavy penalty if the box configuration has already been seen
        penalty = 100 if box_pos in self._seen_box_configs else 0
        if penalty == 0:
            self._seen_box_configs.add(box_pos)

        if self.is_deadlock(node.state):
            return 10**6

        worker, boxes = node.state
        box_cost = 0

        # For each box, add weighted Manhattan distance to the closest target.
        # Cache distances so that repeated calls are fast.
        for bx, by, weight in boxes:
            if (bx, by) in self.targets:
                continue
            if (bx, by) not in self._manhattan_cache:
                self._manhattan_cache[(bx, by)] = min(abs(bx - tx) + abs(by - ty) for (tx, ty) in self.targets)
            d = self._manhattan_cache[(bx, by)]
            box_cost += d * (1 + weight * 0.5)

        return box_cost + penalty

# -----------------------------------------------------------------------------

def check_elem_action_seq(warehouse, action_seq):
    '''
    [Docstring omitted for brevity]
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

def solve_weighted_sokoban(warehouse):
    '''
    [Docstring omitted for brevity]
    '''
    problem = SokobanPuzzle(warehouse)

    # Quick check: if the puzzle is already solved.
    if all((b[0], b[1]) in warehouse.targets for b in warehouse.boxes):
        return [], 0

    result = search.astar_graph_search(problem)
    if result is None:
        return ['Impossible'], None
    return result.solution(), result.path_cost

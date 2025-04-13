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
from itertools import combinations
from collections import deque

# -----------------------------------------------------------------------------
# Return team members as specified
# -----------------------------------------------------------------------------
def my_team():
    '''
    Return the list of the team members for this assignment submission.
    Each team member is represented as a triplet (student_number, first_name, last_name)
    '''
    return [
        (11592931, 'Zackariya', 'Taylor'),
        (11220139, 'Isobel', 'Jones'),
        (1124744, 'Sophia', 'Sweet')
    ]

# -----------------------------------------------------------------------------
# Utility iterator functions to exclude characters from a line or grid
# -----------------------------------------------------------------------------
def find_1D_iterator_exclude(line, *exclude_chars):
    """
    Yield the index of every character in the provided line that is not among exclude_chars.
    """
    for pos, char in enumerate(line):
        if char not in exclude_chars:
            yield pos

def find_2D_iterator_exclude(lines, *exclude_chars):
    """
    Yield (x,y) positions for each cell in lines where the cell is not one of exclude_chars.
    """
    for y, line in enumerate(lines):
        for x in find_1D_iterator_exclude(line, *exclude_chars):
            yield (x, y)

# -----------------------------------------------------------------------------
# Functions for calculating taboo cells (cells which if occupied by a box make the puzzle unsolvable)
# -----------------------------------------------------------------------------
def get_corner_taboo_cells(candidate_taboo_cells, wall_cells):
    """
    Determine the taboo cells that are corners.
    A candidate cell is taboo if two adjacent (orthogonal) neighbours are both walls.
    """
    corner_taboo_cells = set()
    for candidate in candidate_taboo_cells:
        x, y = candidate
        # Check the four adjacent pairs for walls
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
    """
    Determine additional taboo cells that lie along wall segments between two corners.
    A wall segment is taboo if all cells between two taboo corners (horizontally or vertically) are not targets
    and there are walls on the external sides of that segment.
    """
    wall_taboo_cells = set()
    # Use combinations to iterate over each distinct pair of corner taboo cells.
    for corner1, corner2 in combinations(corner_taboo_cells, 2):
        x1, y1 = corner1
        x2, y2 = corner2

        # Vertical alignment: same column
        if x1 == x2:
            # Ensure walls beyond both ends vertically
            if ((x1, y1 - 1) in wall_cells and (x1, y2 + 1) in wall_cells):
                min_y, max_y = min(y1, y2), max(y1, y2)
                is_valid = True
                # Check that no cell along the vertical line is a target or has a gap (no walls on either side)
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

        # Horizontal alignment: same row
        elif y1 == y2:
            # Ensure walls exist on the left and right ends
            if ((x1 - 1, y1) in wall_cells and (x2 + 1, y1) in wall_cells):
                min_x, max_x = min(x1, x2), max(x1, x2)
                is_valid = True
                # Check that no cell along the horizontal line is a target or has a gap (no walls above or below)
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
    """
    Create a visual map (a string) of the warehouse indicating taboo cells.
    Mark taboo cells with an 'X' while preserving the wall ('#') and empty (' ') cells.
    """
    lines = [list(line) for line in str(warehouse).split('\n')]
    for i, line in enumerate(lines):
        for j in range(len(line)):
            if (j, i) in taboo_cells:
                line[j] = 'X'
            # Remove any other marks (worker, targets, boxes) leaving only walls and taboo markers
            elif line[j] not in {'#', ' '}:
                line[j] = ' '
    return "\n".join("".join(line) for line in lines)

def mark_outside_walls(s):
    """
    Replace characters outside the first and last wall with '?'.
    This ensures only the central wall segment is analysed.
    """
    first = s.find('#')
    last = s.rfind('#')
    if first == -1 or last == -1:
        return s  
    return '?' * first + s[first:last + 1] + '?' * (len(s) - last - 1)

def taboo_cells(warehouse):
    '''
    Identify the taboo cells of a warehouse.
    A taboo cell is defined as a cell that, if occupied by a box, makes the puzzle unsolvable.
    The algorithm only considers wall and target positions and applies two rules:
      Rule 1: A non-target corner cell is taboo.
      Rule 2: All non-target cells between two corners along a wall are taboo.
      
    @param warehouse: a Warehouse object.
    @return: A string representing the puzzle layout with wall cells marked as '#' and taboo cells as 'X'.
             The worker, target, and box marks are removed.
    '''
    # Convert warehouse layout into lines
    lines = str(warehouse).split('\n')
    wall_cells = set(warehouse.walls)
    # Cells that nullify potential taboo rows are targets or any cell marked as '*' or '#' in original layout.
    taboo_row_nullifier = (set(warehouse.targets) |
                           set(sokoban.find_2D_iterator(lines, '*')) |
                           set(sokoban.find_2D_iterator(lines, '#')))
    # Extend wall segments in each line to ensure we only examine the inner part.
    lines = [mark_outside_walls(line) for line in lines]
    # Candidate positions for taboo cells are those that are not '.', '#', '*', or '?'.
    candidate_taboo_cells = set(find_2D_iterator_exclude(lines, '.', '#', '*', '?'))
    
    # Determine taboo cells using both corner and wall-based rules.
    corner_taboo_cells = get_corner_taboo_cells(candidate_taboo_cells, wall_cells)
    wall_taboo_cells = get_wall_taboo_cells(corner_taboo_cells, taboo_row_nullifier, wall_cells)
    all_taboo_cells = corner_taboo_cells | wall_taboo_cells

    return get_taboo_cell_map(warehouse, all_taboo_cells)

# -----------------------------------------------------------------------------
# Function to compute all reachable positions for the worker using an optimized BFS.
# -----------------------------------------------------------------------------
def get_reachable_positions(worker_pos, walls, boxes):
    """
    Computes the set of positions reachable by the worker from the starting position.
    The worker cannot pass through walls or boxes.
    
    @param worker_pos: Starting (x, y) position of the worker.
    @param walls: A set containing wall positions.
    @param boxes: A set containing box positions.
    @return: A set of reachable (x, y) positions.
    """
    visited = {worker_pos}
    frontier = deque([worker_pos])
    
    while frontier:
        x, y = frontier.popleft()
        # Check adjacent positions (left, right, up, down)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in walls and (nx, ny) not in boxes and (nx, ny) not in visited:
                visited.add((nx, ny))
                frontier.append((nx, ny))
    return visited

# -----------------------------------------------------------------------------
# SokobanPuzzle class definition, compatible with search.Problem interface.
# -----------------------------------------------------------------------------
class SokobanPuzzle(search.Problem):
    '''
    Represents a weighted Sokoban puzzle. The puzzle includes information about walls, 
    targets, boxes with weights, and the worker position.
    
    The class is designed to work with the provided search module and includes functions 
    to generate legal moves, compute the result of a move, test for goal state, and estimate 
    the cost to reach a goal.
    '''

    def __init__(self, warehouse):
        """
        Initialize the puzzle with the given warehouse.
        Boxes are stored with their weight and sorted to ensure a unique state representation.
        Additionally, taboo cell positions are computed for deadlock detection.
        """
        self.warehouse = warehouse
        
        self.walls = set(warehouse.walls)
        self.targets = set(warehouse.targets)
        self.visited_box_states = set()
        self.deadlock_cache = {}
        
        # Represent each box as a tuple: (x, y, weight) and sort by (row, column)
        boxes_with_weights = [(box[0], box[1], weight) 
                              for box, weight in zip(warehouse.boxes, warehouse.weights)]
        boxes_with_weights.sort(key=lambda b: (b[1], b[0]))
        self.initial = (warehouse.worker, tuple(boxes_with_weights))

        # Cache to track visited box configurations in the heuristic calculation.
        if not hasattr(self, '_seen_box_configs'):
            self._seen_box_configs = set()

        # Compute the taboo cell set using the previously defined function.
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
        # Hash only based on the initial state (worker position and boxes configuration)
        return hash(self.initial)

    def is_box_blocked(self, box_positions, box):
        """
        Check if a specific box is blocked (cannot be moved) by having obstacles on two adjacent sides.
        Obstacles are either walls or other boxes.
        """
        x, y = box
        # Exclude the box itself from the set of obstacles.
        obstacles = self.walls.union(box_positions - {(x, y)})

        # Check all four combinations of adjacent positions.
        if ((x - 1, y) in obstacles and (x, y - 1) in obstacles): return True
        if ((x + 1, y) in obstacles and (x, y - 1) in obstacles): return True
        if ((x - 1, y) in obstacles and (x, y + 1) in obstacles): return True
        if ((x + 1, y) in obstacles and (x, y + 1) in obstacles): return True

        return False

    def has_frozen_clusters(self, box_positions):
        """
        Check for a frozen cluster: if any two adjacent boxes are both blocked, 
        then the puzzle is in a deadlock.
        """
        for b1, b2 in combinations(box_positions, 2):
            if abs(b1[0] - b2[0]) + abs(b1[1] - b2[1]) == 1:
                if self.is_box_blocked(box_positions, b1) and self.is_box_blocked(box_positions, b2):
                    return True
        return False

    def is_taboo_deadlock(self, state):
        """
        A state is in a taboo deadlock if any box sits on a taboo cell that is not a target.
        """
        _, boxes = state
        for bx, by, _ in boxes:
            if (bx, by) in self.taboo_set and (bx, by) not in self.targets:
                return True
        return False

    def is_deadlock(self, state):
        """
        Check the state for deadlocks. Uses caching for states that have been computed before.
        The function checks:
          1. Taboo deadlock: a box is on a taboo cell (if not target).
          2. Soft deadlocks: a box being blocked by obstacles.
          3. Frozen clusters: clusters of boxes that are mutually blocked.
        """
        _, boxes = state
        box_positions = frozenset((b[0], b[1]) for b in boxes)

        if box_positions in self.deadlock_cache:
            return self.deadlock_cache[box_positions]

        # Taboo cell deadlock takes precedence.
        if any((bx, by) in self.taboo_set and (bx, by) not in self.targets for bx, by, _ in boxes):
            self.deadlock_cache[box_positions] = True
            return True

        # Soft deadlocks (not cached because they might resolve later).
        if any(self.is_box_blocked(box_positions, (bx, by)) for bx, by, _ in boxes):
            return True

        if self.has_frozen_clusters(box_positions):
            return True

        return False

    def actions(self, state):
        """
        Generate all legal actions for the given state based on:
          - Whether pushing a box is allowed.
          - Whether the worker can reach the required pushing position.
          - Avoiding moves that result in deadlocks.
        """
        # Early exit if the state is already in a taboo deadlock (unless it is the initial state)
        if self.is_taboo_deadlock(state) and state != self.initial:
            return []
        
        directions = ['Up', 'Down', 'Left', 'Right']
        (wx, wy), boxes = state
        boxes_xy = {(b[0], b[1]) for b in boxes}
        # Compute reachable positions from worker's position using BFS.
        reachable = get_reachable_positions((wx, wy), self.walls, boxes_xy)
        # Cache reachable positions (if needed by heuristic later)
        self.last_reachable_cache = reachable
        
        # Map each action to its corresponding vector movement.
        moves = {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1)}
        legal_actions = []

        for action in directions:
            dx, dy = moves[action]
            nx, ny = wx + dx, wy + dy
            # If the next cell is a wall, skip this move.
            if (nx, ny) in self.walls:
                continue
            # If the next cell contains a box, check the possibility of pushing it.
            if (nx, ny) in boxes_xy:
                bnx, bny = nx + dx, ny + dy
                # Cannot push if the cell beyond the box is a wall or another box.
                if (bnx, bny) in self.walls or (bnx, bny) in boxes_xy:
                    continue
                # Ensure the worker can reach the current cell to push the box.
                if (wx, wy) in reachable:
                    legal_actions.append(action)
            else:
                # Moving into an empty/reachable cell
                if (nx, ny) in reachable:
                    legal_actions.append(action)
        return legal_actions

    def result(self, state, action):
        """
        Given a state and an action, compute the resulting state.
        If the action involves pushing a box, update the box position.
        The result maintains the sorted order of boxes.
        """
        (wx, wy), boxes = state
        boxes = list(boxes)
        # Map actions to directional vectors.
        moves = {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1)}
        dx, dy = moves[action]
        new_worker = (wx + dx, wy + dy)
        # If the new worker position matches a box, push it.
        for i, (bx, by, weight) in enumerate(boxes):
            if (bx, by) == new_worker:
                new_box = (bx + dx, by + dy, weight)
                boxes[i] = new_box
                break
        # Return new state with updated worker and sorted box positions.
        return (new_worker, tuple(sorted(boxes, key=lambda b: (b[1], b[0]))))

    def goal_test(self, state):
        """
        Test if the puzzle is solved.
        The goal is reached if every box is on a target cell.
        """
        _, boxes = state
        return all((b[0], b[1]) in self.targets for b in boxes)

    def path_cost(self, c, state1, action, state2):
        """
        Compute the cost of a path step.
        The cost includes the base move cost (1) and an additional cost based on the weight of any moved box.
        """
        _, b1 = state1
        _, b2 = state2
        
        moved_box = None
        # Build dictionaries mapping positions to the box for both states.
        b1_xy = {(b[0], b[1]): b for b in b1}
        b2_xy = {(b[0], b[1]): b for b in b2}
        # Identify the box that moved by comparing positions between states.
        for pos, box in b2_xy.items():
            if pos not in b1_xy:
                moved_box = box
                break
        if moved_box:
            # Add cost proportional to the box weight.
            return c + 1 + moved_box[2]
        return c + 1

    def h(self, node):
        """
        Heuristic function that estimates the cost to reach the goal from the current state.
        It computes a weighted Manhattan distance from boxes to their nearest targets.
        A penalty is added for repeated box configurations or unreachable box states.
        """
        state = node.state
        box_pos = frozenset((b[0], b[1]) for b in state[1])

        # Add a penalty if this box configuration has been seen before.
        if box_pos in self._seen_box_configs:
            penalty = 100  
        else:
            penalty = 0
            self._seen_box_configs.add(box_pos)

        # Immediately return a high cost if the state is in a deadlock.
        if self.is_deadlock(node.state):
            return 10**6

        worker, boxes = node.state
        box_cost = 0

        # Sum the weighted Manhattan distance from each box to its nearest target.
        for bx, by, weight in boxes:
            if (bx, by) in self.targets:
                continue  # No cost if already on target.
            # Compute the Manhattan distance to the nearest target.
            d = min(abs(bx - tx) + abs(by - ty) for (tx, ty) in self.targets)
            box_cost += d * (1 + weight * 0.5)

        # (Optional:) Further adjustments can be made based on worker-box distances
        # if desired, but are currently commented out.

        return box_cost + penalty

# -----------------------------------------------------------------------------
# Function to verify an action sequence on a warehouse.
# -----------------------------------------------------------------------------
def check_elem_action_seq(warehouse, action_seq):
    """
    Check whether a sequence of actions is legal in the given warehouse.
    If an action is illegal (e.g., pushing two boxes or into a wall), return "Impossible".
    Otherwise, return the resulting state as a string, which should match the output of Warehouse.__str__().
    """
    warehouse_copy = warehouse.copy()

    # Mapping actions to their move vectors.
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

        # If the worker moves into a wall, it is illegal.
        if (new_worker_x, new_worker_y) in walls:
            return "Impossible"

        # If the worker moves into a box, try to push it.
        if (new_worker_x, new_worker_y) in boxes:
            new_box_x, new_box_y = new_worker_x + dx, new_worker_y + dy

            # Cannot push if the destination has a wall or another box.
            if (new_box_x, new_box_y) in walls or (new_box_x, new_box_y) in boxes:
                return "Impossible"

            boxes.remove((new_worker_x, new_worker_y))
            boxes.add((new_box_x, new_box_y))

        worker_x, worker_y = new_worker_x, new_worker_y

    # Update the warehouse copy with new worker and box positions.
    warehouse_copy.worker = (worker_x, worker_y)
    warehouse_copy.boxes = tuple(boxes)

    return str(warehouse_copy)

# -----------------------------------------------------------------------------
# High-level function that solves the weighted sokoban puzzle.
# -----------------------------------------------------------------------------
def solve_weighted_sokoban(warehouse):
    """
    Analyze the given warehouse puzzle.
    
    @param warehouse: a valid Warehouse object.
    @return: A tuple (S, C) where S is the list of action steps that solve the puzzle
             and C is the total cost. If the puzzle cannot be solved, return ('Impossible', None).
    """
    # If all boxes are initially on targets, return the solved state immediately.
    if all((b[0], b[1]) in warehouse.targets for b in warehouse.boxes):
        return [], 0

    # Instantiate the SokobanPuzzle problem.
    problem = SokobanPuzzle(warehouse)
    # Use A* search from the search module to find a solution.
    result = search.astar_graph_search(problem)
    
    if result is None:
        return ['Impossible'], None
    
    return result.solution(), result.path_cost

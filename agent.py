# agent.py

from collections import deque
import heapq
import itertools
import math
import random


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    """Plans an entire route to the nearest food pellet offline, using an
    uninformed OR informed search algorithm, then executes that plan one
    action at a time. Re-plans whenever the current plan runs out.

    Position tracking: get_percept() never reports the agent's own (x, y),
    so this agent maintains its own belief of where it is, starting at the
    environment's known fixed start position (0, 0) and updating that
    belief after every action it takes. This is safe as long as the
    planned path only crosses cells the agent actually knows about (i.e.
    known walls) — toxic traps are NOT exposed to this agent and can
    silently desync it.
    """

    # Same axis-aligned deltas as VisualGridHuntGame.DIRECTIONS — movement
    # in this game is absolute (Up/Down/Left/Right), not relative to a
    # facing direction, so these are safe to reuse directly for planning.
    DIRECTIONS = {
        'Up': (0, 1),
        'Down': (0, -1),
        'Left': (-1, 0),
        'Right': (1, 0),
    }

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'          # 'BFS' | 'DFS' | 'UCS' | 'AStar'
        self.heuristic_type = 'manhattan' # 'manhattan' | 'euclidean' — used by A*
        self.position = (0, 0)            # believed current position


    # Shared helpers
    
    def _clamp_move(self, state, action, grid_size):
        """Applies one action to a state with the same boundary clamping
        execute_action() uses. Does NOT check walls — callers do that."""
        width, height = grid_size
        x, y = state
        dx, dy = self.DIRECTIONS[action]
        nx = max(0, min(width - 1, x + dx))
        ny = max(0, min(height - 1, y + dy))
        return (nx, ny)

    def _successors(self, state, walls, grid_size):
        """Yields (action, next_state) pairs for all four directions,
        skipping any move that's absorbed by a boundary clamp (no real
        movement) or that lands on a known wall. Reused by every search
        method below, including astar_search, so "valid neighbor" means
        exactly the same thing everywhere."""
        for action in self.DIRECTIONS:
            next_state = self._clamp_move(state, action, grid_size)
            if next_state == state:
                continue          # boundary clamp swallowed the move
            if next_state in walls:
                continue          # matches execute_action(): walls block movement
            yield action, next_state

    def _closest_food(self, position, all_food):
        if not all_food:
            return None
        return min(
            all_food,
            key=lambda f: abs(f[0] - position[0]) + abs(f[1] - position[1])
        )

    # Uninformed search (Week 3)

    def bfs_search(self, start, goal, walls, grid_size):
        """FIFO frontier -> explores shallowest nodes first."""
        frontier = deque([(start, [])])   # (state, action_path)
        reached = {start}

        while frontier:
            state, path = frontier.popleft()
            if state == goal:
                return path
            for action, next_state in self._successors(state, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []  # unreachable

    def dfs_search(self, start, goal, walls, grid_size):
        """LIFO frontier -> explores deepest nodes first (erratic paths)."""
        frontier = [(start, [])]          # stack: append/pop from the end
        reached = {start}

        while frontier:
            state, path = frontier.pop()
            if state == goal:
                return path
            for action, next_state in self._successors(state, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    def ucs_search(self, start, goal, walls, grid_size):
        """Priority queue ordered by path cost g(n)."""
        counter = itertools.count()  # tie-breaker so heapq never compares states/paths
        frontier = [(0, next(counter), start, [])]   # (cost, tiebreak, state, path)
        reached = {start: 0}

        while frontier:
            cost, _, state, path = heapq.heappop(frontier)
            if state == goal:
                return path
            for action, next_state in self._successors(state, walls, grid_size):
                new_cost = cost + 1
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    heapq.heappush(frontier, (new_cost, next(counter), next_state, path + [action]))
        return []

    # Step 1.1 (Week 4) — heuristic functions

    def manhattan_distance(self, pos, goal):
        """h(n) = |x1 - x2| + |y1 - y2|. Admissible for 4-way movement —
        see Part 2, Q2."""
        x1, y1 = pos
        x2, y2 = goal
        return abs(x1 - x2) + abs(y1 - y2)

    def euclidean_distance(self, pos, goal):
        """h(n) = sqrt((x1-x2)^2 + (y1-y2)^2) — straight-line distance."""
        x1, y1 = pos
        x2, y2 = goal
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def _heuristic(self, pos, goal, heuristic_type):
        """Thin dispatcher between the two heuristics above, keyed by
        self.heuristic_type so astar_search doesn't need its own if/else."""
        if heuristic_type == 'euclidean':
            return self.euclidean_distance(pos, goal)
        return self.manhattan_distance(pos, goal)

    # Step 1.2 (Week 4) — A* search

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        """f(n) = g(n) + h(n). Node expansion reuses _successors(), so
        "valid neighbor" (not a wall, in bounds) is identical to BFS/DFS/UCS —
        only the ordering of the frontier differs."""
        frontier = []
        reached_states = set()

        start_h = self._heuristic(start_pos, goal_pos, heuristic_type)
        heapq.heappush(frontier, (start_h, 0, start_pos, []))  # (f_cost, g_cost, current_pos, path_taken)

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos == goal_pos:
                return path_taken

            reached_states.add(current_pos)

            for action, next_pos in self._successors(current_pos, walls, grid_size):
                if next_pos not in reached_states:
                    g_new = g_cost + 1
                    h_new = self._heuristic(next_pos, goal_pos, heuristic_type)
                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, g_new, next_pos, path_taken + [action]))

        return []  # unreachable

    # Step 1.3 (Week 4) — plan once, execute step by step

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            goal = self._closest_food(self.position, percept['all_food'])
            if goal is None:
                return 'Up'  # no food left — nothing to plan toward

            walls = set(percept['walls'])
            grid_size = percept['grid_size']

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(self.position, goal, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(self.position, goal, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(self.position, goal, walls, grid_size)
            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(self.position, goal, walls, grid_size, self.heuristic_type)

            if not self.plan:
                return 'Up'  # goal unreachable given known walls

        action = self.plan.pop(0)
        self.position = self._clamp_move(self.position, action, percept['grid_size'])
        return action


if __name__ == "__main__":
    # --- Step 1.1 testing checkpoint ---
    _agent = SearchAgent()
    print("Manhattan(0,0 -> 3,4):", _agent.manhattan_distance((0, 0), (3, 4)))  # expect 7
    print("Euclidean(0,0 -> 3,4):", _agent.euclidean_distance((0, 0), (3, 4)))  # expect 5.0
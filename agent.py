# agent.py

from collections import deque
import heapq
import itertools

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
    uninformed search algorithm, then executes that plan one action at a
    time. Re-plans whenever the current plan runs out (i.e. after each
    food pellet is reached).

    Position tracking: get_percept() never reports the agent's own (x, y),
    so this agent maintains its own belief of where it is, starting at the
    environment's known fixed start position (0, 0) and updating that
    belief after every action it takes. This is safe as long as the
    planned path only crosses cells the agent actually knows about (i.e.
    known walls) — see the note in the lab writeup about toxic traps,
    which are NOT exposed to this agent and can silently desync it.
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
        self.active_algo = 'UCS'          # 'BFS' | 'DFS' | 'UCS'
        self.position = (0, 0)            # believed current position

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

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
        movement) or that lands on a known wall."""
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

    # ------------------------------------------------------------------
    # Step 1.2 — the three uninformed search strategies
    # ------------------------------------------------------------------

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
        """Priority queue ordered by path cost g(n). Every move costs 1
        here, so UCS ends up equivalent to BFS in this environment — but
        it's implemented as true cost-based search (reached tracks the
        cheapest known cost to each state, and re-relaxes on a cheaper
        find) so it generalizes if you ever add variable-cost terrain."""
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

    # ------------------------------------------------------------------
    # Step 1.3 — plan once, execute step by step
    # ------------------------------------------------------------------

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            goal = self._closest_food(self.position, percept['all_food'])
            if goal is None:
                return 'Up'  # no food left — nothing to plan toward

            walls = set(percept['walls'])
            grid_size = percept['grid_size']

            search_fn = {
                'BFS': self.bfs_search,
                'DFS': self.dfs_search,
                'UCS': self.ucs_search,
            }[self.active_algo]

            self.plan = search_fn(self.position, goal, walls, grid_size)
            if not self.plan:
                return 'Up'  # goal unreachable given known walls

        action = self.plan.pop(0)
        self.position = self._clamp_move(self.position, action, percept['grid_size'])
        return action
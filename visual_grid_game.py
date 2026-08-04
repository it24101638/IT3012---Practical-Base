# # visual_grid_game.py
# import random
# import tkinter as tk


# class VisualGridHuntGame:
#     """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

#     # Maps a facing direction to the (dx, dy) offset of the cell "ahead" of the agent
#     DIRECTIONS = {
#         'Up': (0, 1),
#         'Down': (0, -1),
#         'Left': (-1, 0),
#         'Right': (1, 0),
#     }

#     def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
#         self.width = width
#         self.height = height
#         self.agent_pos = [0, 0]  # Starting position (x, y)
#         self.facing = 'Up'  # Agent's current heading; used to compute "ahead" percepts

#         if custom_walls is not None:
#             self.walls = set(custom_walls)
#         else:
#             # Generate some default scattered walls for a larger grid
#             self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

#         # Dynamically generate random food positions avoiding walls and agent start
#         self.food_positions = set()
#         while len(self.food_positions) < num_food:
#             fx = random.randint(0, self.width - 1)
#             fy = random.randint(0, self.height - 1)
#             pos_tuple = (fx, fy)
#             if pos_tuple != (0, 0) and pos_tuple not in self.walls:
#                 self.food_positions.add(pos_tuple)

#         # Generate adversarial opponents
#         self.opponents = []
#         while len(self.opponents) < num_opponents:
#             ox = random.randint(0, self.width - 1)
#             oy = random.randint(0, self.height - 1)
#             op_pos = [ox, oy]
#             if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
#                 self.opponents.append(op_pos)

#         # Generate toxic traps avoiding walls, food, opponents, and agent start
#         self.toxic_traps = set()
#         num_traps = max(1, num_food // 3)  # scale traps with food count, at least 1
#         while len(self.toxic_traps) < num_traps:
#             tx = random.randint(0, self.width - 1)
#             ty = random.randint(0, self.height - 1)
#             trap_tuple = (tx, ty)
#             if (trap_tuple != (0, 0)
#                 and trap_tuple not in self.walls
#                 and trap_tuple not in self.food_positions):
#                 self.toxic_traps.add(trap_tuple)

#         self.score = 0
#         self.steps = 0
#         self.collision = False

#     def _get_ahead_position(self) -> tuple:
#         """Cell directly ahead of the agent, based on facing. NOT clamped —
#         may be off-grid, which get_percept() treats as blocked, like a wall."""
#         dx, dy = self.DIRECTIONS[self.facing]
#         ax, ay = self.agent_pos
#         return (ax + dx, ay + dy)

#     def _in_bounds(self, pos: tuple) -> bool:
#         x, y = pos
#         return 0 <= x < self.width and 0 <= y < self.height

#     def get_percept(self) -> dict:
#         ahead_pos = self._get_ahead_position()
#         off_grid = not self._in_bounds(ahead_pos)
#         return {
#             'wall_ahead': off_grid or ahead_pos in self.walls,
#             'toxin_ahead': (not off_grid) and ahead_pos in self.toxic_traps,
#             'food_here': (not off_grid) and ahead_pos in self.food_positions,
#             'collision': self.collision,
#         }

#     def execute_action(self, action: str):
#         self.steps += 1

#         if action in self.DIRECTIONS:
#             self.facing = action
        
#         new_pos = list(self.agent_pos)

#         if action == 'Up':
#             new_pos[1] = min(self.height - 1, new_pos[1] + 1)
#         elif action == 'Down':
#             new_pos[1] = max(0, new_pos[1] - 1)
#         elif action == 'Left':
#             new_pos[0] = max(0, new_pos[0] - 1)
#         elif action == 'Right':
#             new_pos[0] = min(self.width - 1, new_pos[0] + 1)

#         if tuple(new_pos) in self.walls:
#             self.score -= 5
#         elif tuple(new_pos) in self.toxic_traps:
#             self.score -= 15
#         else:
#             self.agent_pos = new_pos





#         tuple_pos = tuple(self.agent_pos)
#         if tuple_pos in self.food_positions:
#             self.food_positions.remove(tuple_pos)
#             self.score += 20

#         for op in self.opponents:
#             move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
#             if move == 'Up' and op[1] < self.height - 1:
#                 op[1] += 1
#             elif move == 'Down' and op[1] > 0:
#                 op[1] -= 1
#             elif move == 'Left' and op[0] > 0:
#                 op[0] -= 1
#             elif move == 'Right' and op[0] < self.width - 1:
#                 op[0] += 1

#             if op == self.agent_pos:
#                 self.score -= 50
#                 self.collision = True

#     def is_done(self) -> bool:
#         return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


# class GridGameGUI:
#     """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

#     def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
#         self.root = root
#         self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

#         self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
#                                       custom_walls=walls)

#         self.agent = ModelBasedAgent()

#         # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
#         max_canvas_dim = 600
#         self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

#         canvas_w = self.env.width * self.cell_size
#         canvas_h = self.env.height * self.cell_size

#         self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
#         self.canvas.pack()

#         self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
#         self.label.pack(pady=10)

#         self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
#                              fg="white")
#         self.btn.pack(pady=5)

#         self.draw_grid()

#     def draw_grid(self):
#         self.canvas.delete("all")

#         for x in range(self.env.width):
#             for y in range(self.env.height):
#                 x1 = x * self.cell_size
#                 y1 = (self.env.height - 1 - y) * self.cell_size
#                 x2 = x1 + self.cell_size
#                 y2 = y1 + self.cell_size

#                 color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
#                 self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

#                 # Only draw text if cell is large enough
#                 if self.cell_size >= 40 and (x, y) in self.env.walls:
#                     self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
#                                             font=("Arial", 8, "bold"))

#         for fx, fy in self.env.food_positions:
#             offset = self.cell_size * 0.25
#             x1 = fx * self.cell_size + offset
#             y1 = (self.env.height - 1 - fy) * self.cell_size + offset
#             self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
#                                     outline="#d97706")

#         for ox, oy in self.env.opponents:
#             offset = self.cell_size * 0.2
#             x1 = ox * self.cell_size + offset
#             y1 = (self.env.height - 1 - oy) * self.cell_size + offset
#             self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000", outline="#7a0000")

#         for fx, fy in self.env.toxic_traps:
#             offset = self.cell_size * 0.25
#             x1 = fx * self.cell_size + offset
#             y1 = (self.env.height - 1 - fy) * self.cell_size + offset
#             self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#5f1fa4", outline="#5f1fa4")

#         ax, ay = self.env.agent_pos
#         offset = self.cell_size * 0.15
#         x1 = ax * self.cell_size + offset
#         y1 = (self.env.height - 1 - ay) * self.cell_size + offset
#         self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",outline="#1e3a8a")

#     def run_loop(self):
#         self.btn.config(state="disabled")

#         def step():
#             if not self.env.is_done():
#                 percept = self.env.get_percept()
#                 action = self.agent.sense_and_act(percept)
#                 self.env.execute_action(action)

#                 self.draw_grid()
#                 self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
#                 self.root.after(250, step)
#             else:
#                 end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
#                 self.label.config(text=end_text)
#                 self.btn.config(state="normal")

#         step()

# class SimpleReflexAgent:
#     def sense_and_act(self, percept):
#         if percept['wall_ahead'] or percept['toxin_ahead']:
#             return 'Left'
#         return 'Up'


# class ModelBasedAgent:
#     """Remembers which directions it has already tried since getting stuck,
#     so it can systematically work through the alternatives instead of
#     oscillating between the same two directions forever."""

#     def __init__(self):
#         self.last_action = None       # the action that produced this percept
#         self.tried_directions = set() # directions already attempted at this dead end

#     def sense_and_act(self, percept: dict) -> str:
#         blocked = percept['wall_ahead'] or percept['toxin_ahead']

#         # --- 1. Update the model (Transition & Sensor Model) ---
#         if blocked and self.last_action is not None:
#             # last_action led us into a wall/toxin — remember it failed
#             self.tried_directions.add(self.last_action)
#         elif not blocked:
#             # we're in the clear — forget the old dead-end history
#             self.tried_directions.clear()

#         # --- 2. Memory-augmented IF-THEN rules ---
#         if blocked:
#             for direction in ('Left', 'Right', 'Down', 'Up'):
#                 if direction not in self.tried_directions:
#                     action = direction
#                     break
#             else:
#                 # tried all 4 directions from here — reset and start over
#                 self.tried_directions.clear()
#                 action = 'Left'
#         else:
#             action = 'Up'

#         self.last_action = action
#         return action


# if __name__ == "__main__":
#     root = tk.Tk()
#     # Try a larger grid size like 12x12 with 15 food and 3 opponents!
#     app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=2)
#     root.mainloop()











# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    # Maps a facing direction to the (dx, dy) offset of the cell "ahead" of the agent
    DIRECTIONS = {
        'Up': (0, 1),
        'Down': (0, -1),
        'Left': (-1, 0),
        'Right': (1, 0),
    }

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.facing = 'Up'  # Agent's current heading; used to compute "ahead" percepts

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        # Generate toxic traps avoiding walls, food, opponents, and agent start
        self.toxic_traps = set()
        num_traps = max(1, num_food // 3)  # scale traps with food count, at least 1
        opponent_positions = {tuple(op) for op in self.opponents}
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap_tuple = (tx, ty)
            if (trap_tuple != (0, 0)
                and trap_tuple not in self.walls
                and trap_tuple not in self.food_positions
                and trap_tuple not in opponent_positions):
                self.toxic_traps.add(trap_tuple)

        self.score = 0
        self.steps = 0
        self.collision = False

    def _get_ahead_position(self) -> tuple:
        """Returns the (x, y) coordinate of the cell directly ahead of the agent,
        based on its current facing direction. NOT clamped to the grid — may be
        out of bounds, which get_percept() interprets as "blocked" (same as a wall)."""
        dx, dy = self.DIRECTIONS[self.facing]
        ax, ay = self.agent_pos
        return (ax + dx, ay + dy)

    def _in_bounds(self, pos: tuple) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def get_percept(self) -> dict:
        ahead_pos = self._get_ahead_position()
        off_grid = not self._in_bounds(ahead_pos)
        return {
            # off-grid counts as blocked, same as a wall — you can't move there either
            'wall_ahead': off_grid or ahead_pos in self.walls,
            'toxin_ahead': (not off_grid) and ahead_pos in self.toxic_traps,
            # food_here is checked against the CURRENT tile, but execute_action()
            # auto-consumes food the instant the agent lands on it, so this can
            # never be True by the time the next percept is read — kept for
            # compatibility with the example format, but functionally dead.
            'food_here': tuple(self.agent_pos) in self.food_positions,
            # food_ahead is a live equivalent: checks the NEXT tile, before
            # the agent has moved onto (and auto-consumed) it.
            'food_ahead': (not off_grid) and ahead_pos in self.food_positions,
            'collision': self.collision,
        }

    def execute_action(self, action: str):
        self.steps += 1

        # Update heading first — the agent "faces" the direction it attempts to move,
        # regardless of whether that move actually succeeds.
        if action in self.DIRECTIONS:
            self.facing = action

        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        elif tuple(new_pos) in self.toxic_traps:
            self.score -= 15
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            new_op = list(op)
            if move == 'Up' and op[1] < self.height - 1:
                new_op[1] += 1
            elif move == 'Down' and op[1] > 0:
                new_op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                new_op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                new_op[0] += 1

            if tuple(new_op) not in self.walls:
                op[0], op[1] = new_op[0], new_op[1]

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=9, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)
        self.agent = ModelBasedAgent()

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000", outline="#7a0000")

        for fx, fy in self.env.toxic_traps:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#5f1fa4", outline="#4c1a75")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()

class SimpleReflexAgent:
    """A purely reactive agent: chooses an action based ONLY on the current
    percept, with no memory of past states, positions, or actions.

    Note on adapting the classic vacuum-world logic to this engine:
    - There's no separate 'suck' action here — food is auto-collected by
      execute_action() the instant the agent steps onto it, so food_here
      doesn't need its own action, it's handled automatically.
    - There's no separate 'turn' action either — in this grid, picking a
      direction both turns AND moves the agent in one step. So "turn left"
      becomes "try a different hardcoded direction" instead of rotating
      in place.
    """

    def sense_and_act(self, percept: dict) -> str:
        if percept['wall_ahead'] or percept['toxin_ahead']:
            return 'Left'   # fixed fallback direction whenever blocked
        return 'Up'         # fixed default direction otherwise


class ModelBasedAgent:
    """Remembers which directions it has already tried since getting stuck,
    so it can systematically work through the alternatives instead of
    oscillating between the same two directions forever.

    Note: get_percept() never reveals the agent's absolute grid position
    (partial observability), so 'memory' here can't be a set of visited
    (x, y) coordinates. Instead it's a RELATIVE tracker: which directions
    have failed since the agent last successfully moved.
    """

    def __init__(self):
        self.last_action = None       # the action that produced this percept
        self.tried_directions = set() # directions already attempted at this dead end

    def sense_and_act(self, percept: dict) -> str:
        blocked = percept['wall_ahead'] or percept['toxin_ahead']

        # --- 1. Update the model (Transition & Sensor Model) ---
        if blocked and self.last_action is not None:
            # last_action led us into a wall/toxin — remember it failed
            self.tried_directions.add(self.last_action)
        elif not blocked:
            # we're in the clear — forget the old dead-end history
            self.tried_directions.clear()

        # --- 2. Memory-augmented IF-THEN rules ---
        if blocked:
            for direction in ('Left', 'Right', 'Down', 'Up'):
                if direction not in self.tried_directions:
                    action = direction
                    break
            else:
                # tried all 4 directions from here — reset and start over
                self.tried_directions.clear()
                action = 'Left'
        else:
            action = 'Up'

        self.last_action = action
        return action


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=9)
    root.mainloop()

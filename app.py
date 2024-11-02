"""Play Gomoku against the computer in a Tkinter window."""
import tkinter as tk
from tkinter import ttk

from gomoku import COMPUTER, HUMAN, SIZE, Game, a_star_search, computer_move

GRID = 33
MARGIN = 22
EDGE = 2 * MARGIN + (SIZE - 1) * GRID
MODES = {"Easy": (1, 1), "Standard": (68, 2), "Hard": (SIZE * SIZE, 3)}
BEST_FIRST = "A*-style"
MINIMAX = "Minimax"


class GomokuWindow:
    def __init__(self, root):
        self.root = root
        self.game = Game()
        self.pending_move = None
        self.difficulty = tk.StringVar(value="Standard")
        self.algorithm = tk.StringVar(value=BEST_FIRST)
        self.status = tk.StringVar()
        root.title("Gomoku")
        root.resizable(False, False)

        controls = ttk.Frame(root, padding=(12, 10))
        controls.pack(fill="x")
        ttk.Button(controls, text="New game", command=self.restart).pack(side="left")
        self.undo_button = ttk.Button(controls, text="Undo turn", command=self.undo)
        self.undo_button.pack(side="left", padx=(8, 0))
        ttk.Combobox(
            controls, textvariable=self.difficulty, values=list(MODES),
            state="readonly", width=10,
        ).pack(side="right")
        ttk.Label(controls, text="Difficulty").pack(side="right", padx=8)
        ttk.Combobox(
            controls, textvariable=self.algorithm, values=[BEST_FIRST, MINIMAX],
            state="readonly", width=10,
        ).pack(side="right")

        self.canvas = tk.Canvas(root, width=EDGE, height=EDGE, background="#dcb578",
                                borderwidth=0, highlightthickness=0)
        self.canvas.pack(padx=12)
        self.canvas.bind("<Button-1>", self.play_human)
        ttk.Label(root, textvariable=self.status, padding=12).pack(anchor="w")
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        first, last = MARGIN, EDGE - MARGIN
        for index in range(SIZE):
            coord = MARGIN + index * GRID
            self.canvas.create_line(first, coord, last, coord, fill="#715636")
            self.canvas.create_line(coord, first, coord, last, fill="#715636")

        for index_row, index_col in ((3, 3), (3, 11), (7, 7), (11, 3), (11, 11)):
            self.draw_dot(index_row, index_col, 3, "#715636", "#715636")

        for row, col, player in self.game.history:
            color = "#1f2225" if player == HUMAN else "#fff9eb"
            self.draw_dot(row, col, 13, color, "#534637")
        if self.game.history:
            row, col, _ = self.game.history[-1]
            self.draw_dot(row, col, 3, "#b34729", "#b34729")

        self.undo_button.configure(state="normal" if self.game.history else "disabled")
        if self.game.winner:
            self.status.set("You win." if self.game.winner == HUMAN else "Computer wins.")
        elif self.game.finished:
            self.status.set("Draw. The board is full.")
        elif self.game.turn == HUMAN:
            self.status.set("Your turn · Black")
        else:
            self.status.set("Computer thinking · White")

    def draw_dot(self, row, col, radius, fill, outline):
        x, y = MARGIN + col * GRID, MARGIN + row * GRID
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                fill=fill, outline=outline)

    def play_human(self, event):
        if self.game.turn != HUMAN:
            return
        col = round((event.x - MARGIN) / GRID)
        row = round((event.y - MARGIN) / GRID)
        x, y = MARGIN + col * GRID, MARGIN + row * GRID
        if (event.x - x) ** 2 + (event.y - y) ** 2 > (GRID / 2) ** 2:
            return
        if self.game.play(row, col):
            self.draw()
            if not self.game.finished:
                self.pending_move = self.root.after(80, self.play_computer)

    def play_computer(self):
        self.pending_move = None
        if self.game.turn == COMPUTER and not self.game.finished:
            expansions, depth = MODES[self.difficulty.get()]
            if self.algorithm.get() == BEST_FIRST:
                move = a_star_search(self.game, expansions)
            else:
                move = computer_move(self.game, depth)
            if move is not None:
                self.game.play(*move)
            self.draw()

    def cancel_pending_move(self):
        if self.pending_move is not None:
            self.root.after_cancel(self.pending_move)
            self.pending_move = None

    def restart(self):
        self.cancel_pending_move()
        self.game = Game()
        self.draw()

    def undo(self):
        self.cancel_pending_move()
        self.game.undo_turn()
        self.draw()


if __name__ == "__main__":
    window = tk.Tk()
    app = GomokuWindow(window)
    window.mainloop()

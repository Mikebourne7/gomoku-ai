# Gomoku AI

Play five-in-a-row against a computer on a 15×15 board. Black moves first. Five or more stones in a row wins in any direction. A full board with no winner is a draw.

## Run

Use Python 3 with Tkinter on a graphical desktop. Run `python3 -m tkinter` to check that Tkinter can open a window.

```bash
python3 app.py
```

Click an intersection to play. The default **A*-style** opponent uses a priority queue to decide where to move. Choose **Minimax** to try the alternative opponent. **Undo turn** takes back your most recent move and the computer's reply, when present.

| Difficulty | A*-style candidate budget | Minimax lookahead |
| --- | ---: | ---: |
| Easy | 1 | 1 ply |
| Standard | 68 | 2 plies |
| Hard | Up to the whole board | 3 plies |

## A*-style move selection

The archived desktop version called its move selector `a_star_search()`. It seeded an open list with empty intersections touching existing stones in any of eight directions. It scored each intersection as a potential move for both sides, ranked it by `own score + 0.1 × opponent score`, and expanded the highest-scoring point by adding its unvisited neighbors. The method returned the best point encountered within the difficulty setting's visit budget. The original scoring compared five- and six-cell patterns across four axes, including split patterns and bonuses for overlapping threats.

The current [move selector](gomoku.py) follows that priority-queue approach:

1. Seed the queue with unoccupied neighbors of the existing stones. Score and enqueue each intersection once.
2. Before positional scoring, give first priority to a move that completes the computer's five-in-a-row, and second priority to a square that would complete the opponent's five-in-a-row. A square in the second group can block an immediate loss.
3. For the remaining moves, evaluate the lines through the candidate horizontally, vertically, and along both diagonals. The heuristic rewards longer runs and open ends. The integer priority `10 × attack + defense` keeps the original 1-to-0.1 weighting, with ties resolved by distance to the center, then by row and column.
4. Pop the strongest candidate from the heap. Add its empty neighbors and repeat within the visit budget. Return the highest-ranked point popped. The candidate's location changes during the search while the board position stays fixed.

For example, if white already occupies four consecutive squares and has an open end, completing the line takes precedence over blocking black. If white has no immediate win and black can complete a line at one square, that square takes precedence over quieter positional moves.

### Relationship to standard A*

Standard A* ranks paths by `f(n) = g(n) + h(n)`, combining the cost already paid with an estimate of the remaining cost to a goal. Here the queue ranks individual intersections by their tactical and positional scores. There is no cumulative path cost or goal state, so the original method is more precisely a heuristic best-first search. The candidate visit budget controls how far the search explores the board. It does not count future turns. See the [original A* paper](https://doi.org/10.1109/TSSC.1968.300136).

### Minimax alternative

Minimax simulates alternating moves and evaluates the resulting board positions. It uses alpha-beta pruning and limits ordinary branches to eight ranked candidates per position. Its difficulty measures how many half-moves it looks ahead. This approach was explored in a separate prototype in the project archive.

## Project history

This edition revisits Gomoku files dated 2024 and reimplements the interface directly with Tkinter. The desktop project's A*-style selector is the default, with minimax available as a second mode.

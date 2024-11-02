# Gomoku AI

Play five-in-a-row against a computer on a 15×15 board. Black moves first. A line of at least five stones wins in any direction, and a full board with no winner is a draw.

## Run

Use Python 3 with Tkinter. Run `python3 -m tkinter` to check that the graphical environment is available.

```bash
python3 app.py
```

Click a board intersection to play. Choose Easy, Standard, or Hard to change the search depth. **Undo turn** removes your most recent move and the computer's reply, when present.

## Opponent

The opponent searches nearby intersections and prioritizes immediate wins and blocks. Alpha-beta pruning limits the search, and a board heuristic scores lines by length and open ends. The three difficulty levels search one, two, or three plies.

## Project history

This version revisits an archived Gomoku project with files dated 2024. It keeps the human-versus-computer format and the minimax approach explored in the archived prototype. The interface was reimplemented directly with Tkinter.

# Managing players

Administrative player edits are done with `player_edits.py` from the repository root. All commands take an optional `--game <name>` (a name from `rankings/games.py`); it can be omitted when only one game is registered.

## Retiring a player

When a colleague leaves the company, retire them instead of deleting them:

```bash
python3 player_edits.py --retire "Player Name"
```

This writes `RETIRED` in the status column (column D) of the `Players` tab and refreshes the leaderboards. A retired player:

- keeps all ratings and match history;
- is removed from every regular leaderboard;
- still appears on the full leaderboard (if configured, see below) with a `(retired)` suffix;
- is removed from the form dropdowns by the Apps Script — run the script manually or wait for the next form submission to trigger it.

Undo it at any time; the player returns to the leaderboards with their ratings intact:

```bash
python3 player_edits.py --unretire "Player Name"
```

## Full leaderboard including retired players

Set `full_leaderboard_range` on the game's `SheetLayout` (default: disabled) to also write an overall leaderboard that keeps retired players, marked with a `(retired)` suffix:

```python
layout=SheetLayout(full_leaderboard_range="Leaderboard!M3:N")
```

## Renaming a player

```bash
python3 player_edits.py --rename "Old Name" "New Name"
```

This replaces the name on the `Players` tab, in every rating category on the `Ratings` tab, and in the historical `Matches` and `Balancing` rows, then refreshes the leaderboards. The rename is rejected if the new name is already taken.

The form dropdowns update on the next Apps Script run. Any match submitted with the old name after the rename cannot be matched to a rating and will block processing — do renames at a quiet moment and make sure the dropdowns are updated before the next match is played.

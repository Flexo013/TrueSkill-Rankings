# Registering games

Games are registered in code: `rankings/games.py` holds one `GameConfig` per game, and the process runs everything in its `GAMES` list. Game names must be unique — the watcher refuses to start otherwise.

## A new game

```python
AIR_HOCKEY = GameConfig(
    name="air-hockey",
    spreadsheet_id="...",       # from the spreadsheet URL
    gmail_label_id="Label_...", # from list_labels.py
    track_positions=False,      # air hockey has no offense/defense roles
)

GAMES = [FOOSBALL, AIR_HOCKEY]
```

## A second league of an existing game

Rules are shared; only the identity (name, spreadsheet, label) changes:

```python
FOOSBALL_SALES = dataclasses.replace(
    FOOSBALL,
    name="foosball-sales",
    spreadsheet_id="...",
    gmail_label_id="...",
)

GAMES = [FOOSBALL, FOOSBALL_SALES]
```

## Available options

All options live in `rankings/config.py`:

| Option | Default | Meaning |
|---|---|---|
| `track_positions` | `True` | Keep separate offense/defense ratings for full 2v2 matches |
| `track_solo` | `True` | Keep a separate rating for 1v1/1v2/2v1 matches |
| `trueskill` | mu 1000, sigma 333, beta 166, tau 3.3333, draw probability 0.001 | `TrueSkillSettings` for the game's rating environment |
| `score_impact` | target score 10, factor caps 0.75–1.25 | `ScoreImpactSettings`: how score margin, match quality, and match length scale rating updates |
| `layout` | template layout | `SheetLayout`: A1 ranges of all tabs, for spreadsheets that deviate from the template |

After editing `rankings/games.py`, restart the process to pick up the change — see [Running the software](running.md).

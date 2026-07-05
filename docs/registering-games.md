# Registering games

Games are registered in code: `rankings/games.py` holds one `GameConfig` per game, and the process runs everything in its `GAMES` list. Game names must be unique — the watcher refuses to start otherwise.

A `GameConfig` is identity (name, spreadsheet, Gmail label) plus a **game type**: the rule preset from `rankings/game_types.py` that describes the kind of game. Game-specific tuning like the draw chance and the score an even match is played to lives on the game type, so every kind of game states its own values.

## Available game types

| Game type | Format | Rating categories | Notes |
|---|---|---|---|
| `game_types.FOOSBALL` | Team (1v1–2v2 with scores) | overall, offense, defense, solo | No draws; even match is played to 10 |
| `game_types.AIR_HOCKEY` | Team (1v1–2v2 with scores) | overall, solo | No fixed positions; no draws; first to 10 |
| `game_types.TRACKMANIA` | Free-for-all (2–8 players in finish order) | overall | No scores — TrueSkill rates the finish order directly |

A new kind of game gets a new `GameType` in `rankings/game_types.py`; see `rankings/config.py` for all fields (match format, `TrueSkillSettings`, `ScoreImpactSettings`, tracked categories).

## A new game

```python
AIR_HOCKEY = GameConfig(
    name="air-hockey",
    spreadsheet_id="...",       # from the spreadsheet URL
    gmail_label_id="Label_...", # from list_labels.py
    game_type=game_types.AIR_HOCKEY,
)

TRACKMANIA = GameConfig(
    name="trackmania",
    spreadsheet_id="...",
    gmail_label_id="Label_...",
    game_type=game_types.TRACKMANIA,
    layout=FFA_SHEET_LAYOUT,    # free-for-all Matches tab layout
)

GAMES = [FOOSBALL, AIR_HOCKEY, TRACKMANIA]
```

## A second league of an existing game

The game type is shared; only the identity (name, spreadsheet, label) changes:

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

| Option | Where | Meaning |
|---|---|---|
| `match_format` | `GameType` | `TEAM` (scored 1v1–2v2 matches) or `FREE_FOR_ALL` (2–8 players in finish order, no scores) |
| `trueskill` | `GameType` | `TrueSkillSettings` for the game's rating environment (mu 1000, sigma 333, beta 166, tau 3.3333 by default; each game type sets its own draw probability) |
| `score_impact` | `GameType` | `ScoreImpactSettings`: how score margin, match quality, and match length scale rating updates; `None` for free-for-all games |
| `track_positions` | `GameType` | Keep separate offense/defense ratings for full 2v2 matches |
| `track_solo` | `GameType` | Keep a separate rating for 1v1/1v2/2v1 matches |
| `ffa_max_players` | `GameType` | Free-for-all only: how many player slots the match form offers (default 8) |
| `layout` | `GameConfig` | `SheetLayout`: A1 ranges of all tabs. Use `FFA_SHEET_LAYOUT` for free-for-all games, or override for spreadsheets that deviate from the template |

After editing `rankings/games.py`, restart the process to pick up the change — see [Running the software](running.md).

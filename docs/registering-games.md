# Registering games

Games are registered in code: `rankings/games.py` holds one `GameConfig` per game, and the process runs everything in its `GAMES` list. Game names must be unique; the watcher refuses to start otherwise.

The examples below only set the options they need; see [Full example](#full-example) for a `GameConfig` spelling out every available option.

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
| `match_format` | `MatchFormat.TEAM` | How matches are entered and rated; `FFA` is scaffolding, see [Future work](#future-work) |
| `allow_draws` | `False` | Whether matches can end in equal scores; `True` is scaffolding, see [Future work](#future-work) |
| `max_players_per_match` | `4` | Player slots on the match form; values other than 4 are scaffolding, see [Future work](#future-work) |
| `enable_balancing` | `True` | Whether the game has a balancing form and sheet |
| `trueskill` | mu 1000, sigma 333, beta 166, tau 3.3333, draw probability 0.001 | `TrueSkillSettings` for the game's rating environment |
| `score_impact` | target score 10, factor caps 0.75–1.25 | `ScoreImpactSettings`: how score margin, match quality, and match length scale rating updates |
| `layout` | template layout | `SheetLayout`: A1 ranges of all tabs, for spreadsheets that deviate from the template |

## Full example

A `GameConfig` with every option written out, set to its default value:

```python
GameConfig(
    name="example",
    spreadsheet_id="...",
    gmail_label_id="Label_...",
    track_positions=True,
    track_solo=True,
    match_format=MatchFormat.TEAM,
    allow_draws=False,
    max_players_per_match=4,
    enable_balancing=True,
    trueskill=TrueSkillSettings(
        mu=1000.0,
        sigma=333.0,
        beta=166.0,
        tau=3.3333,
        draw_probability=0.001,
    ),
    score_impact=ScoreImpactSettings(
        min_score_factor=0.75,
        max_score_factor=1.25,
        quality_min_factor=0.85,
        quality_factor_span=0.3,
        standard_target_score=10,
    ),
    layout=SheetLayout(
        players_range="Players!B3:C",
        players_processed_col=3,
        matches_range="Matches!B2:H",
        matches_processed_col=8,
        balancing_range="Balancing!B2:G",
        balancing_team_cols=(6, 7),
        ratings_first_row=3,
        categories=DEFAULT_CATEGORY_LAYOUTS,  # per-category ranges, see config.py
    ),
)
```

After editing `rankings/games.py`, restart the process to pick up the change; see [Running the software](running.md).

## Future work

`match_format=MatchFormat.FFA`, `allow_draws=True`, and `max_players_per_match` values other than 4 are scaffolding: the options exist on `GameConfig` but raise `NotImplementedError` at registration time until the processor supports them. See the future-work notes in [Forms and spreadsheet](forms.md) and [Apps Script](apps-script.md).

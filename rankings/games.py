"""The registry of games this process runs.

All games are managed by a single host Google account that owns the
spreadsheets, forms, and Gmail labels. One process runs every registered
game, including multiple leagues of the same game for different groups of
colleagues: game rules (TrueSkill settings, position/solo tracking, score
impact) live on GameConfig defaults or a shared base config, while each
league gets its own name, spreadsheet, and Gmail label.

See rankings.config for all available options.
"""

import dataclasses

from rankings.config import GameConfig

FOOSBALL = GameConfig(
    name="foosball",
    spreadsheet_id="1ij0SE4S9ZPYfDm8_JW4PFMnbDvhp6hmlIckQN1fKUQ8",
    gmail_label_id="Label_6763635978072909105",
)

# A second league of the same game reuses the rules and overrides identity:
# FOOSBALL_SALES = dataclasses.replace(
#     FOOSBALL,
#     name="foosball-sales",
#     spreadsheet_id="...",
#     gmail_label_id="...",
# )

# A different game type overrides the rules it needs, e.g. no
# offense/defense positions for air hockey:
# AIR_HOCKEY = GameConfig(
#     name="air-hockey",
#     spreadsheet_id="...",
#     gmail_label_id="...",
#     track_positions=False,
# )

GAMES = [FOOSBALL]

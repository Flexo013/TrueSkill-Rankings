"""The registry of games this process runs.

All games are managed by a single host Google account that owns the
spreadsheets, forms, and Gmail labels. One process runs every registered
game, including multiple leagues of the same game for different groups of
colleagues: the rules live on a shared ``GameType`` preset from
``rankings.game_types``, while each league gets its own name, spreadsheet,
and Gmail label.

See rankings.config for all available options.
"""

import dataclasses

from rankings import game_types
from rankings.config import FFA_SHEET_LAYOUT, GameConfig

FOOSBALL = GameConfig(
    name="foosball",
    spreadsheet_id="1ij0SE4S9ZPYfDm8_JW4PFMnbDvhp6hmlIckQN1fKUQ8",
    gmail_label_id="Label_6763635978072909105",
    game_type=game_types.FOOSBALL,
)

# A second league of the same game reuses the game type and overrides identity:
# FOOSBALL_SALES = dataclasses.replace(
#     FOOSBALL,
#     name="foosball-sales",
#     spreadsheet_id="...",
#     gmail_label_id="...",
# )

# A different game picks its own game type (and, for free-for-all games,
# the free-for-all sheet layout):
# AIR_HOCKEY = GameConfig(
#     name="air-hockey",
#     spreadsheet_id="...",
#     gmail_label_id="...",
#     game_type=game_types.AIR_HOCKEY,
# )
# TRACKMANIA = GameConfig(
#     name="trackmania",
#     spreadsheet_id="...",
#     gmail_label_id="...",
#     game_type=game_types.TRACKMANIA,
#     layout=FFA_SHEET_LAYOUT,
# )

GAMES = [FOOSBALL]

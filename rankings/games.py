"""The registry of games this process runs.

To add a game (e.g. air hockey), create its spreadsheet from the same template,
set up a Gmail label + filter for its form notifications, and add a GameConfig
here. Options like track_positions/track_solo, TrueSkill settings, and score
impact tuning can differ per game; see rankings.config for all knobs.
"""

from rankings.config import GameConfig

FOOSBALL = GameConfig(
    name="foosball",
    spreadsheet_id="1ij0SE4S9ZPYfDm8_JW4PFMnbDvhp6hmlIckQN1fKUQ8",
    gmail_label_id="Label_6763635978072909105",
)

# Example of a second game without offense/defense positions:
# AIR_HOCKEY = GameConfig(
#     name="air-hockey",
#     spreadsheet_id="...",
#     gmail_label_id="...",
#     track_positions=False,
#     score_impact=ScoreImpactSettings(standard_target_score=10),
# )

GAMES = [FOOSBALL]

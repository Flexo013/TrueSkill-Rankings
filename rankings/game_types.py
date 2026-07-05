"""Known game types: the rule presets that games in ``rankings.games`` use.

A game type bundles the rules of one kind of game — match format, TrueSkill
tuning, and which rating categories are tracked. Every league of the same
game shares its game type; identity (name, spreadsheet, Gmail label) lives on
the ``GameConfig`` in ``rankings.games``.
"""

from rankings.config import (
    GameType,
    MatchFormat,
    ScoreImpactSettings,
    TrueSkillSettings,
)

# Team matches with fixed offense/defense positions and a separate solo
# rating. The form cannot submit a draw, and an even match is played to 10.
FOOSBALL = GameType(
    match_format=MatchFormat.TEAM,
    trueskill=TrueSkillSettings(draw_probability=0.001),
    score_impact=ScoreImpactSettings(standard_target_score=10),
    track_positions=True,
    track_solo=True,
)

# Team play without fixed positions (players switch freely at the table);
# otherwise scored like foosball: no draws, first to 10.
AIR_HOCKEY = GameType(
    match_format=MatchFormat.TEAM,
    trueskill=TrueSkillSettings(draw_probability=0.001),
    score_impact=ScoreImpactSettings(standard_target_score=10),
    track_positions=False,
    track_solo=True,
)

# Free-for-all races of 2-8 players. The match row lists players in finish
# order and TrueSkill rates the whole field from that order directly, so
# there are no scores and no score impact tuning. The form cannot express a
# tie, hence the near-zero draw probability.
TRACKMANIA = GameType(
    match_format=MatchFormat.FREE_FOR_ALL,
    trueskill=TrueSkillSettings(draw_probability=0.001),
    score_impact=None,
    ffa_max_players=8,
)

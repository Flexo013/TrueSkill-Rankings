"""Pure TrueSkill rating calculations, independent of any storage backend.

All functions take an explicit ``trueskill.TrueSkill`` environment so that
multiple games with different TrueSkill settings can run in one process.
"""

from typing import List, Optional

import trueskill

from rankings.config import ScoreImpactSettings


def rate_flexible_match(
    env: trueskill.TrueSkill, ratings: List[Optional[trueskill.Rating]]
) -> List[trueskill.Rating]:
    """Rate a 1v1, 1v2, 2v1, or 2v2 match.

    ``ratings`` holds four entries in the order [winner, winner, loser, loser];
    the 2nd and 4th entry are None when that team only had one player. Returns
    the new ratings of the actual players, winners first.
    """
    winning_team = [ratings[0]]
    losing_team = [ratings[2]]
    if ratings[1] is not None:
        winning_team.append(ratings[1])
    if ratings[3] is not None:
        losing_team.append(ratings[3])

    new_ratings = env.rate([winning_team, losing_team], ranks=[0, 1])
    return [rating for team in new_ratings for rating in team]


def rate_free_for_all(
    env: trueskill.TrueSkill, ratings: List[trueskill.Rating]
) -> List[trueskill.Rating]:
    """Rate a free-for-all match, given ratings in finish order (winner first).

    Every player is their own rating group and the finish position is the
    rank — TrueSkill's native model for N-player free-for-all matches, so no
    scores are involved. Returns the new ratings in the same order.
    """
    groups = [[rating] for rating in ratings]
    new_ratings = env.rate(groups, ranks=list(range(len(groups))))
    return [group[0] for group in new_ratings]


def scale_rating_update(
    env: trueskill.TrueSkill,
    old_rating: trueskill.Rating,
    new_rating: trueskill.Rating,
    factor: float,
) -> trueskill.Rating:
    """Interpolate between the old and new rating by ``factor``."""
    return env.create_rating(
        mu=old_rating.mu + (new_rating.mu - old_rating.mu) * factor,
        sigma=old_rating.sigma + (new_rating.sigma - old_rating.sigma) * factor,
    )


def calculate_match_length_factor(target_score: int, standard_target_score: int) -> float:
    return 0.5 + 0.5 * (target_score / standard_target_score)


def calculate_score_factor(
    env: trueskill.TrueSkill,
    settings: ScoreImpactSettings,
    blue_team: List[trueskill.Rating],
    red_team: List[trueskill.Rating],
    score_blue: int,
    score_red: int,
) -> float:
    """How strongly this match result should move the ratings."""
    margin = abs(score_blue - score_red)
    target_score = max(score_blue, score_red)

    # Score Factor: Linear margin scaling, capped at the configured maximum.
    scaled_margin = settings.min_score_factor + margin / 20.0
    score_factor = min(settings.max_score_factor, scaled_margin)

    # Quality Factor: Damp score impact for uneven matchups and boost it
    # slightly for balanced ones.
    quality_factor = (
        settings.quality_min_factor
        + settings.quality_factor_span * env.quality([blue_team, red_team])
    )

    match_length_factor = calculate_match_length_factor(
        target_score, settings.standard_target_score
    )

    return score_factor * quality_factor * match_length_factor

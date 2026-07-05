"""Configuration dataclasses describing a game and its spreadsheet layout.

Every game (foosball, air hockey, ...) is a single ``GameConfig`` instance.
The processor and mail watcher only ever look at the config they are given,
so multiple games can run side by side in the same process without sharing
any state. Concrete game instances live in ``rankings.games``.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Tuple


class RatingCategory(Enum):
    OVERALL = "overall"
    OFFENSE = "offense"
    DEFENSE = "defense"
    SOLO = "solo"


@dataclass(frozen=True)
class CategoryLayout:
    """Where one rating category lives inside the spreadsheet."""

    rating_range: str
    leaderboard_range: str
    rating_start_col: int


DEFAULT_CATEGORY_LAYOUTS: Mapping[RatingCategory, CategoryLayout] = {
    RatingCategory.OVERALL: CategoryLayout(
        rating_range="Ratings!A3:C",
        leaderboard_range="Leaderboard!A3:B",
        rating_start_col=2,
    ),
    RatingCategory.OFFENSE: CategoryLayout(
        rating_range="Ratings!E3:G",
        leaderboard_range="Leaderboard!D3:E",
        rating_start_col=6,
    ),
    RatingCategory.DEFENSE: CategoryLayout(
        rating_range="Ratings!I3:K",
        leaderboard_range="Leaderboard!G3:H",
        rating_start_col=10,
    ),
    RatingCategory.SOLO: CategoryLayout(
        rating_range="Ratings!M3:O",
        leaderboard_range="Leaderboard!J3:K",
        rating_start_col=14,
    ),
}


@dataclass(frozen=True)
class SheetLayout:
    """A1 ranges and column positions of the input/output areas of a game sheet.

    The ``*_processed_col`` values are 1-based spreadsheet column numbers of
    the checkbox column that marks a row as already handled.
    """

    players_range: str = "Players!B3:C"
    players_processed_col: int = 3
    matches_range: str = "Matches!B2:H"
    matches_processed_col: int = 8
    balancing_range: str = "Balancing!B2:G"
    balancing_team_cols: Tuple[int, int] = (6, 7)
    ratings_first_row: int = 3
    categories: Mapping[RatingCategory, CategoryLayout] = field(
        default_factory=lambda: DEFAULT_CATEGORY_LAYOUTS
    )


@dataclass(frozen=True)
class TrueSkillSettings:
    mu: float = 1000.0
    sigma: float = 333.0
    beta: float = 166.0
    tau: float = 3.3333
    draw_probability: float = 0.001


@dataclass(frozen=True)
class ScoreImpactSettings:
    """Tuning knobs for how the match score scales the TrueSkill update."""

    min_score_factor: float = 0.75
    max_score_factor: float = 1.25
    quality_min_factor: float = 0.85
    quality_factor_span: float = 0.3
    standard_target_score: int = 10


@dataclass(frozen=True)
class GameConfig:
    """Everything needed to run one game: identity, options, and sheet layout."""

    name: str
    spreadsheet_id: str
    gmail_label_id: str
    trueskill: TrueSkillSettings = TrueSkillSettings()
    score_impact: ScoreImpactSettings = ScoreImpactSettings()
    # Track separate offense/defense ratings for full 2v2 matches.
    track_positions: bool = True
    # Track a separate "solo" rating for 1v1/1v2/2v1 matches.
    track_solo: bool = True
    layout: SheetLayout = SheetLayout()

    @property
    def rating_categories(self) -> Tuple[RatingCategory, ...]:
        categories = [RatingCategory.OVERALL]
        if self.track_positions:
            categories += [RatingCategory.OFFENSE, RatingCategory.DEFENSE]
        if self.track_solo:
            categories.append(RatingCategory.SOLO)
        return tuple(categories)

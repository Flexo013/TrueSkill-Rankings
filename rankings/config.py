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


class MatchFormat(Enum):
    # Two teams of one or two players, each with a score.
    TEAM = "team"
    # Free-for-all: players entered in finish order, scores optional.
    # Scaffolding only; selecting it raises NotImplementedError.
    FFA = "ffa"


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
    # How matches are entered and rated. Scaffolding: only TEAM is implemented.
    match_format: MatchFormat = MatchFormat.TEAM
    # Allow matches with equal scores, for games played on time.
    # Scaffolding: rating a draw is not implemented, equal scores are skipped.
    allow_draws: bool = False
    # Number of player slots on the match form. Scaffolding: the processor
    # only supports 4 (two teams of one or two players). Must match the
    # MAX_PLAYERS_PER_MATCH constant of the game's Apps Script.
    max_players_per_match: int = 4
    # Whether the game has a balancing form and sheet. Disable for game
    # types where team balancing makes no sense (e.g. FFA).
    enable_balancing: bool = True
    layout: SheetLayout = SheetLayout()

    def __post_init__(self):
        # Fail at registration time for scaffolded options that the
        # processor cannot honor yet, rather than misprocessing matches.
        if self.match_format is not MatchFormat.TEAM:
            raise NotImplementedError(
                f"{self.name}: match_format={self.match_format.value!r}"
                " is not implemented yet"
            )
        if self.allow_draws:
            raise NotImplementedError(
                f"{self.name}: allow_draws is not implemented yet"
            )
        if self.max_players_per_match != 4:
            raise NotImplementedError(
                f"{self.name}: max_players_per_match="
                f"{self.max_players_per_match} is not implemented yet"
            )

    @property
    def rating_categories(self) -> Tuple[RatingCategory, ...]:
        categories = [RatingCategory.OVERALL]
        if self.track_positions:
            categories += [RatingCategory.OFFENSE, RatingCategory.DEFENSE]
        if self.track_solo:
            categories.append(RatingCategory.SOLO)
        return tuple(categories)

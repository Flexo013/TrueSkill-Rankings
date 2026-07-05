"""Processes one game's spreadsheet: new players, matches, balancing, leaderboards."""

import math
from typing import List, Optional, Sequence, Tuple

import trueskill

from rankings import rating_math
from rankings.config import GameConfig, RatingCategory
from rankings.sheets import SheetsClient, parse_range_start


class RatingTable:
    """In-memory snapshot of one rating category's columns on the Ratings sheet."""

    def __init__(self, category: RatingCategory, rows: list, first_row: int,
                 env: trueskill.TrueSkill):
        self.category = category
        self._first_row = first_row
        self._env = env
        self._names: List[str] = []
        self._values = {}
        for name, mu, sigma in rows:
            self._names.append(name)
            self._values[name] = (float(mu), float(sigma))

    def get_rating(self, player_name: str) -> trueskill.Rating:
        mu, sigma = self._values[player_name]
        return self._env.create_rating(mu=mu, sigma=sigma)

    def row_number(self, player_name: str) -> int:
        return self._names.index(player_name) + self._first_row

    def items(self):
        return ((name, self.get_rating(name)) for name in self._names)


class GameProcessor:
    """Runs a full processing pass for a single game."""

    def __init__(self, config: GameConfig, sheets: Optional[SheetsClient] = None,
                 credentials=None):
        self.config = config
        self.layout = config.layout
        self.sheets = sheets or SheetsClient(config.spreadsheet_id, credentials=credentials)
        ts = config.trueskill
        self.env = trueskill.TrueSkill(
            mu=ts.mu,
            sigma=ts.sigma,
            beta=ts.beta,
            tau=ts.tau,
            draw_probability=ts.draw_probability,
        )

    def run(self) -> None:
        if not self.init_players():
            return
        self.suggest_balanced_teams()
        self.process_matches()
        self.update_leaderboards()

    # --- Players ---

    def init_players(self) -> bool:
        """Give newly registered players a default rating in every category.

        Returns False when the player list contains duplicates, in which case
        the whole run is aborted so ratings cannot be attributed ambiguously.
        """
        rows = self.sheets.read(self.layout.players_range)
        player_names = [str(row[0]).strip() for row in rows if row and str(row[0]).strip()]
        if len(set(player_names)) != len(player_names):
            print(f"[{self.config.name}] Found duplicate player, aborting this run.")
            return False

        sheet, start_col, start_row = parse_range_start(self.layout.players_range)
        processed_offset = self.layout.players_processed_col - start_col
        for i, row in enumerate(rows):
            if len(row) > processed_offset:
                continue
            row_number = start_row + i
            processed_cell = f"{sheet}!R{row_number}C{self.layout.players_processed_col}"
            if self.sheets.read(processed_cell):
                continue

            new_rating = self.env.create_rating()
            for category in self.config.rating_categories:
                self._write_rating(category, row_number, new_rating)
            self.sheets.write(processed_cell, [["TRUE"]])
        return True

    # --- Matches ---

    def process_matches(self) -> None:
        sheet, start_col, start_row = parse_range_start(self.layout.matches_range)
        processed_offset = self.layout.matches_processed_col - start_col
        rows = self.sheets.read(self.layout.matches_range)
        for i, row in enumerate(rows):
            if len(row) > processed_offset:
                continue
            row_number = start_row + i
            processed_cell = f"{sheet}!R{row_number}C{self.layout.matches_processed_col}"
            if self.sheets.read(processed_cell):
                continue
            self._process_match(row)
            self.sheets.write(processed_cell, [["TRUE"]])

    def _process_match(self, match_row: list) -> None:
        red_off, red_def, blue_off, blue_def, score_red, score_blue = match_row
        score_red = int(score_red)
        score_blue = int(score_blue)
        if score_red == score_blue:
            # Draws are not supported.
            return

        if score_red > score_blue:
            result = (red_off, red_def, blue_off, blue_def)
        else:
            result = (blue_off, blue_def, red_off, red_def)

        names = [name for name in result if name]
        if len(set(names)) != len(names):
            # Bogus input where a player occurs multiple times.
            return

        if "" in result:
            self._process_partial_match(result)
        else:
            self._process_full_match(red_off, red_def, blue_off, blue_def,
                                     score_blue, score_red)

    def _process_partial_match(self, result: Tuple[str, str, str, str]) -> None:
        """Process a 1v1, 1v2, or 2v1 match, given winner-first player names."""
        categories = [RatingCategory.OVERALL]
        if self.config.track_solo:
            categories.append(RatingCategory.SOLO)

        for category in categories:
            table = self._read_ratings(category)
            old_ratings = [table.get_rating(name) if name else None for name in result]
            new_ratings = rating_math.rate_flexible_match(self.env, old_ratings)
            players = [name for name in result if name]
            for name, rating in zip(players, new_ratings):
                self._write_rating(category, table.row_number(name), rating)

    def _process_full_match(self, red_off: str, red_def: str, blue_off: str,
                            blue_def: str, score_blue: int, score_red: int) -> None:
        """Process a full 2v2 match: overall ratings, plus positional if enabled."""
        overall = self._read_ratings(RatingCategory.OVERALL)
        self._rate_teams(
            blue_slots=[(overall, blue_off), (overall, blue_def)],
            red_slots=[(overall, red_off), (overall, red_def)],
            score_blue=score_blue,
            score_red=score_red,
        )

        if self.config.track_positions:
            offense = self._read_ratings(RatingCategory.OFFENSE)
            defense = self._read_ratings(RatingCategory.DEFENSE)
            self._rate_teams(
                blue_slots=[(offense, blue_off), (defense, blue_def)],
                red_slots=[(offense, red_off), (defense, red_def)],
                score_blue=score_blue,
                score_red=score_red,
            )

    def _rate_teams(self, blue_slots: Sequence[Tuple[RatingTable, str]],
                    red_slots: Sequence[Tuple[RatingTable, str]],
                    score_blue: int, score_red: int) -> None:
        """Rate blue vs red, scale the update by the score factor, and store it.

        Each slot pairs a player name with the rating table (category) that
        player is rated against in this position.
        """
        blue_team = [table.get_rating(name) for table, name in blue_slots]
        red_team = [table.get_rating(name) for table, name in red_slots]

        factor = rating_math.calculate_score_factor(
            self.env, self.config.score_impact, blue_team, red_team,
            score_blue, score_red,
        )

        # Raw scores do not affect the TrueSkill update directly; only
        # winner/loser order does.
        team_ranks = [0, 1] if score_blue > score_red else [1, 0]
        new_blue, new_red = self.env.rate([blue_team, red_team], ranks=team_ranks)

        all_slots = list(blue_slots) + list(red_slots)
        old_ratings = blue_team + red_team
        new_ratings = list(new_blue) + list(new_red)
        for (table, name), old, new in zip(all_slots, old_ratings, new_ratings):
            scaled = rating_math.scale_rating_update(self.env, old, new, factor)
            self._write_rating(table.category, table.row_number(name), scaled)

    # --- Balancing ---

    def suggest_balanced_teams(self) -> None:
        """Fill in the suggested team split for new rows on the Balancing sheet."""
        sheet, start_col, start_row = parse_range_start(self.layout.balancing_range)
        first_team_col, second_team_col = self.layout.balancing_team_cols
        processed_offset = first_team_col - start_col
        rows = self.sheets.read(self.layout.balancing_range)
        for i, row in enumerate(rows):
            if len(row) > processed_offset:
                continue
            row_number = start_row + i
            team_1, team_2 = self._best_team_split(row[:4])
            self.sheets.write(f"{sheet}!R{row_number}C{first_team_col}", [[team_1]])
            self.sheets.write(f"{sheet}!R{row_number}C{second_team_col}", [[team_2]])

    def _best_team_split(self, players: Sequence[str]) -> Tuple[str, str]:
        p1, p2, p3, p4 = players
        overall = self._read_ratings(RatingCategory.OVERALL)
        ratings = {name: overall.get_rating(name) for name in players}

        pairings = [
            ((p1, p2), (p3, p4)),
            ((p1, p3), (p2, p4)),
            ((p1, p4), (p2, p3)),
        ]

        def draw_chance_offset(pairing):
            (a1, a2), (b1, b2) = pairing
            quality = self.env.quality(
                [[ratings[a1], ratings[a2]], [ratings[b1], ratings[b2]]]
            )
            return abs(quality - 0.5)

        (t1a, t1b), (t2a, t2b) = min(pairings, key=draw_chance_offset)
        return f"{t1a} {t1b}", f"{t2a} {t2b}"

    # --- Leaderboards ---

    def update_leaderboards(self) -> None:
        for category in self.config.rating_categories:
            table = self._read_ratings(category)
            rated_players = [
                (name, rating)
                for name, rating in table.items()
                if not self._is_default_rating(rating)
            ]
            rated_players.sort(key=lambda item: self.env.expose(item[1]), reverse=True)

            values = [[rank + 1, name] for rank, (name, _) in enumerate(rated_players)]
            self.sheets.write(self.layout.categories[category].leaderboard_range, values)

    def _is_default_rating(self, rating: trueskill.Rating) -> bool:
        return math.isclose(rating.mu, self.env.mu) and math.isclose(
            rating.sigma, self.env.sigma
        )

    # --- Shared helpers ---

    def _read_ratings(self, category: RatingCategory) -> RatingTable:
        rows = self.sheets.read(self.layout.categories[category].rating_range)
        return RatingTable(category, rows, self.layout.ratings_first_row, self.env)

    def _write_rating(self, category: RatingCategory, row_number: int,
                      rating: trueskill.Rating) -> None:
        layout = self.layout.categories[category]
        sheet, _, _ = parse_range_start(layout.rating_range)
        col = layout.rating_start_col
        self.sheets.write(
            f"{sheet}!R{row_number}C{col}:R{row_number}C{col + 1}",
            [[rating.mu, rating.sigma]],
        )

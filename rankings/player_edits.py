"""Player management operations: retiring, unretiring, and renaming.

These are one-off administrative edits, driven by the ``player_edits.py``
command at the repository root. Retiring only flips the status column on the
Players sheet: ratings and match history are kept, so a retired player can be
unretired later without losing anything. The Apps Script reads the same status
column to drop retired players from the form dropdowns.
"""

from typing import Optional

from rankings.config import GameConfig, MatchFormat, RETIRED_STATUS
from rankings.processor import GameProcessor
from rankings.sheets import SheetsClient, parse_range_start


class PlayerEditor:
    """Applies player edits to one game's spreadsheet."""

    def __init__(self, config: GameConfig, sheets: Optional[SheetsClient] = None):
        self.config = config
        self.layout = config.layout
        self.sheets = sheets or SheetsClient(config.spreadsheet_id)
        self._processor = GameProcessor(config, sheets=self.sheets)

    def retire(self, name: str) -> None:
        self._set_status(name, RETIRED_STATUS)
        self._processor.update_leaderboards()

    def unretire(self, name: str) -> None:
        self._set_status(name, "")
        self._processor.update_leaderboards()

    def rename(self, old_name: str, new_name: str) -> None:
        """Rename a player everywhere: Players, Ratings, Matches, and Balancing.

        Match history is rewritten too, so replays and audits stay consistent
        with the new name.
        """
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("The new name must not be empty.")
        existing = self._player_names()
        if new_name in existing:
            raise ValueError(f"Player {new_name!r} already exists.")
        if old_name not in existing:
            raise ValueError(f"Player {old_name!r} not found on the Players sheet.")

        sheet, row = self._find_player_row(old_name)
        name_col = parse_range_start(self.layout.players_range)[1]
        self.sheets.write(f"{sheet}!R{row}C{name_col}", [[new_name]])

        for category in self.config.rating_categories:
            self._rename_in_ratings(category, old_name, new_name)
        game_type = self.config.game_type
        match_player_cols = (
            game_type.ffa_max_players
            if game_type.match_format is MatchFormat.FREE_FOR_ALL else 4
        )
        self._rename_in_columns(self.layout.matches_range, match_player_cols,
                                old_name, new_name)
        if game_type.has_balancing:
            self._rename_in_columns(self.layout.balancing_range, 4, old_name, new_name)

        self._processor.update_leaderboards()

    # --- Helpers ---

    def _player_names(self) -> list:
        rows = self.sheets.read(self.layout.players_range)
        return [str(row[0]).strip() for row in rows if row and str(row[0]).strip()]

    def _find_player_row(self, name: str):
        sheet, _, start_row = parse_range_start(self.layout.players_range)
        rows = self.sheets.read(self.layout.players_range)
        for i, row in enumerate(rows):
            if row and str(row[0]).strip() == name:
                return sheet, start_row + i
        raise ValueError(f"Player {name!r} not found on the Players sheet.")

    def _set_status(self, name: str, status: str) -> None:
        sheet, row = self._find_player_row(name)
        cell = f"{sheet}!R{row}C{self.layout.players_status_col}"
        self.sheets.write(cell, [[status]])

    def _rename_in_ratings(self, category, old_name: str, new_name: str) -> None:
        layout = self.layout.categories[category]
        sheet, name_col, start_row = parse_range_start(layout.rating_range)
        rows = self.sheets.read(layout.rating_range)
        for i, row in enumerate(rows):
            if row and str(row[0]).strip() == old_name:
                self.sheets.write(
                    f"{sheet}!R{start_row + i}C{name_col}", [[new_name]]
                )

    def _rename_in_columns(self, sheet_range: str, player_col_count: int,
                           old_name: str, new_name: str) -> None:
        """Replace the name in the first ``player_col_count`` columns of a range."""
        sheet, start_col, start_row = parse_range_start(sheet_range)
        rows = self.sheets.read(sheet_range)
        for i, row in enumerate(rows):
            for j in range(min(player_col_count, len(row))):
                if str(row[j]).strip() == old_name:
                    self.sheets.write(
                        f"{sheet}!R{start_row + i}C{start_col + j}", [[new_name]]
                    )

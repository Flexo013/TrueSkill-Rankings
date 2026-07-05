"""One-time Google OAuth setup.

Runs the interactive login flow, stores token.json, and verifies spreadsheet
access for every configured game.
"""

from googleapiclient.errors import HttpError

from rankings.auth import create_or_refresh_credentials
from rankings.games import GAMES
from rankings.sheets import SheetsClient


def main():
    credentials = create_or_refresh_credentials()
    for game in GAMES:
        try:
            client = SheetsClient(game.spreadsheet_id, credentials=credentials)
            players = client.read(game.layout.players_range)
            print(f"[{game.name}] Sheets access OK ({len(players)} player rows).")
        except HttpError as error:
            print(f"[{game.name}] Sheets access failed: {error}")


if __name__ == "__main__":
    main()

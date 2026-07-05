"""Command-line player management: retire, unretire, or rename a player.

Examples:
    python3 player_edits.py --retire "Player Name"
    python3 player_edits.py --unretire "Player Name"
    python3 player_edits.py --rename "Old Name" "New Name"
    python3 player_edits.py --game foosball --retire "Player Name"

Retiring keeps a player's ratings and match history but removes them from the
regular leaderboards and (via the Apps Script) from the form dropdowns.
"""

import argparse
import sys

from rankings.games import GAMES
from rankings.player_edits import PlayerEditor


def select_game(game_name):
    games = {game.name: game for game in GAMES}
    if game_name:
        if game_name not in games:
            sys.exit(f"Unknown game {game_name!r}. Registered: {', '.join(games)}.")
        return games[game_name]
    if len(games) == 1:
        return next(iter(games.values()))
    sys.exit(f"Multiple games registered ({', '.join(games)}); pass --game.")


def main():
    parser = argparse.ArgumentParser(
        description="Retire, unretire, or rename a player of one game."
    )
    parser.add_argument("--game", help="game name from rankings/games.py "
                                       "(optional when only one game is registered)")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--retire", metavar="NAME", help="mark a player as retired")
    action.add_argument("--unretire", metavar="NAME", help="clear a player's retired status")
    action.add_argument("--rename", nargs=2, metavar=("OLD", "NEW"),
                        help="rename a player everywhere on the spreadsheet")
    args = parser.parse_args()

    config = select_game(args.game)
    editor = PlayerEditor(config)
    if args.retire:
        editor.retire(args.retire)
        print(f"[{config.name}] Retired {args.retire!r} and refreshed the leaderboards.")
        print("Run the spreadsheet's Apps Script (or wait for the next form "
              "submission) to remove them from the form dropdowns.")
    elif args.unretire:
        editor.unretire(args.unretire)
        print(f"[{config.name}] Unretired {args.unretire!r} and refreshed the leaderboards.")
    else:
        old_name, new_name = args.rename
        editor.rename(old_name, new_name)
        print(f"[{config.name}] Renamed {old_name!r} to {new_name!r} everywhere.")
        print("Run the spreadsheet's Apps Script (or wait for the next form "
              "submission) to update the form dropdowns.")


if __name__ == "__main__":
    main()

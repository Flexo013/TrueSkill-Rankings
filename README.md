# TrueSkill Rankings

A Python implementation of the [TrueSkill](https://trueskill.org/) ranking system. Used for modelling the skill level of players in a mix of 1v1, 1v2, 2v1, and 2v2 matches. Data storage is handled by Google Sheets, and data collection by Google Forms. Google Apps Script is used for syncing data between the input forms.

All games are managed by a single host Google account running a single process, so people who want their own game (air hockey, table tennis, a separate foosball league for their team, ...) don't need to run anything themselves. Each game gets its own spreadsheet, forms, Gmail label, and rating options.

## Foosball

The current foosball rankings and leaderboard are managed by this repository's code. The [create player](https://docs.google.com/forms/d/e/1FAIpQLSe6t1b2XdOFceT9-mOzIVnFznLl1ZtgOAoBt6j9D5ipek-fcQ/viewform) and [submit match](https://docs.google.com/forms/u/0/d/e/1FAIpQLSeflIJn3-6S0LcnKtBoi0NXz4P_MIzsPnrvgv_zNzMMDRTzEQ/viewform) forms are the main way of interacting with the system. Leaderboard can be found at this [Google Sheet](https://docs.google.com/spreadsheets/d/1ij0SE4S9ZPYfDm8_JW4PFMnbDvhp6hmlIckQN1fKUQ8/edit?resourcekey=&gid=1829137064#gid=1829137064).

# Documentation

Setup and operation are documented in [docs/index.md](docs/index.md).

# Quick start

1. `pip3 install -r requirements.txt`
2. `python3 authenticate.py`: authenticate as the host account (creates `token.json`; delete any old token first).
3. `python3 mail_checker.py`: run the watcher.

# Code layout

- `mail_checker.py`: entry point; watches Gmail and processes each configured game.
- `authenticate.py`: one-time OAuth setup; creates `token.json` and verifies Sheets access.
- `list_labels.py`: prints Gmail label IDs, for configuring a new game.
- `rankings/games.py`: the registry of games this process runs. Add a `GameConfig` here to add a game.
- `rankings/config.py`: configuration dataclasses for game options (1v1/positions/solo tracking), TrueSkill settings, score impact tuning, and spreadsheet layout.
- `rankings/processor.py`: `GameProcessor`, which initializes new players, processes matches, suggests balanced teams, and updates leaderboards for one game.
- `rankings/rating_math.py`: pure TrueSkill calculations (no Google API dependencies).
- `rankings/watcher.py`: `MailWatcher`, which polls one Gmail label per game and triggers processing on new mail.
- `rankings/sheets.py`: Google Sheets client with rate-limit backoff.
- `rankings/auth.py`: shared OAuth credential handling.
- `apps_script/`: reference copy of the Apps Script bound to each game spreadsheet.

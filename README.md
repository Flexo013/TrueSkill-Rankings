# TrueSkill Rankings

A Python implementation of the [TrueSkill](https://trueskill.org/) ranking system. Used for modelling the skill level of players in a mix of 1v1, 1v2, 2v1, and 2v2 matches. Data storage is handled by Google Sheets, and data collection by Google Forms. Google Apps Script is used for syncing data between the input forms.

The process supports running multiple games at once (e.g. foosball and air hockey), each with its own spreadsheet, Gmail label, and rating options.

## Foosball

The current foosball rankings and leaderboard are managed by this repository's code. The [create player](https://docs.google.com/forms/d/e/1FAIpQLSe6t1b2XdOFceT9-mOzIVnFznLl1ZtgOAoBt6j9D5ipek-fcQ/viewform) and [submit match](https://docs.google.com/forms/u/0/d/e/1FAIpQLSeflIJn3-6S0LcnKtBoi0NXz4P_MIzsPnrvgv_zNzMMDRTzEQ/viewform) forms are the main way of interacting with the system. Leaderboard can be found at this [Google Sheet](https://docs.google.com/spreadsheets/d/1ij0SE4S9ZPYfDm8_JW4PFMnbDvhp6hmlIckQN1fKUQ8/edit?resourcekey=&gid=1829137064#gid=1829137064).

# Setup

1. Install the necessary python packages with `pip3 install -r requirements.txt`.
2. Run `python3 authenticate.py` to authenticate with Google and create a `token.json`. This will fail if you have an old `token.json` file, delete it and reauthenticate.
3. Run `python3 mail_checker.py` to run the project

# Code layout

- `mail_checker.py` — entry point; watches Gmail and processes each configured game.
- `authenticate.py` — one-time OAuth setup; creates `token.json` and verifies Sheets access.
- `rankings/games.py` — the registry of games this process runs. Add a `GameConfig` here to add a game.
- `rankings/config.py` — configuration dataclasses: game options (1v1/positions/solo tracking), TrueSkill settings, score impact tuning, and spreadsheet layout.
- `rankings/processor.py` — `GameProcessor`: initializes new players, processes matches, suggests balanced teams, and updates leaderboards for one game.
- `rankings/rating_math.py` — pure TrueSkill calculations (no Google API dependencies).
- `rankings/watcher.py` — `MailWatcher`: polls one Gmail label per game and triggers processing on new mail.
- `rankings/sheets.py` — Google Sheets client with rate-limit backoff.
- `rankings/auth.py` — shared OAuth credential handling.

# Adding a game

All games are managed by a single host Google account running a single `mail_checker.py` process, so people who want their own game (air hockey, table tennis, a separate foosball league for their team, ...) don't need to run anything themselves. The host account owns every game's spreadsheet, forms, and Gmail labels.

1. From the host account, copy the existing spreadsheet as a template and create the matching Google Forms.
2. Enable "Email notifications for new responses" on the new forms.
3. In the host account's Gmail, create a filter that applies a dedicated label to the new game's notification emails. Run `python3 list_labels.py` to find the label's ID.
4. Add a `GameConfig` to `rankings/games.py` with the new spreadsheet ID and label ID. Per-game options include `track_positions` (offense/defense ratings), `track_solo` (separate 1v1 rating), TrueSkill parameters, and score impact tuning. Running the same game twice for different groups of colleagues is just two configs with the same rules but their own name, spreadsheet, and label — see the examples in `rankings/games.py`.

A failure while processing one game (bad input data, API errors) is logged and does not affect the other games in the process; the failed game's rows stay unprocessed and are retried when its next email arrives.

It is also possible to run your own instance of this software with your own Google account and game registry, but the single shared host is the main setup.

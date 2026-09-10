# Forms and spreadsheet

Each game has one spreadsheet and its own set of Google Forms, all owned by the host account.

## Spreadsheet

Copy the [game spreadsheet template](https://docs.google.com/spreadsheets/d/1dTYNrOF8uSul85hZzxYDwFGW5WCF4oBNRvM92DUFftA/edit?usp=sharing). The processor expects these tabs (exact ranges are configured in `rankings/config.py` under `SheetLayout` and can be overridden per game):

| Tab | Purpose | Layout |
|---|---|---|
| `Players` | Registered player names | Names in column B from row 3; column C marks a player as initialized |
| `Matches` | Submitted match results | Columns B–G from row 2: red offense, red defense, blue offense, blue defense, red score, blue score; column H marks a row as processed |
| `Ratings` | TrueSkill ratings per category | Four column blocks (overall, offense, defense, solo) from row 3, each holding name, mu, sigma |
| `Leaderboard` | Ranked output per category | Written by the processor; rank and name per category block |

This layout reflects the only match format supported today: two teams of one or two players, each with a score. It should eventually depend on the game type; an FFA format, for example, would take player names in finish order, with scores optional. See [Future work](#future-work).

## Forms

Create the forms and link their responses to the game spreadsheet tabs so submissions land on the tabs above:

- **Create player** ([template](https://forms.gle/6jN3NTBp1Aqpatzv7)): a single name field; new names are appended to the `Players` tab.
- **Submit match** ([template](https://forms.gle/hmQ687XhT3njrxy79)): four player dropdowns (red offense, red defense, blue offense, blue defense) and the two team scores. The second player of a team should be optional while all other fields are required.

The player dropdowns in the match form are kept in sync with the `Players` tab by an Apps Script; see [Apps Script](apps-script.md).

## Input rules enforced by the processor

- Draws are not supported; a match with equal scores is ignored.
- A match naming the same player twice is ignored.
- A duplicate name on the `Players` tab aborts processing for that game until fixed (the Apps Script also deletes duplicate registrations on submission).

## Future work

`GameConfig` already scaffolds the options below, but selecting them raises `NotImplementedError` until the processor supports them:

- `allow_draws`: draw support should become configurable per game, since a game played on time can legitimately end in a draw.
- `match_format=MatchFormat.FFA`: an FFA format with players entered in finish order and optional scores, which also changes the `Matches` layout and the match form.
- `max_players_per_match`: values other than 4 require the processor to handle a variable number of player columns.

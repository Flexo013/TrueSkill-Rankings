# Forms and spreadsheet

Each game has one spreadsheet and its own set of Google Forms, all owned by the host account.

## Spreadsheet

Copy the existing game spreadsheet as a template. The processor expects these tabs (exact ranges are configured in `rankings/config.py` under `SheetLayout` and can be overridden per game):

| Tab | Purpose | Layout |
|---|---|---|
| `Players` | Registered player names | Names in column B from row 3; column C marks a player as initialized; column D holds the status (`RETIRED` for retired players, see [Managing players](managing-players.md)) |
| `Matches` | Submitted match results | Columns B–G from row 2: red offense, red defense, blue offense, blue defense, red score, blue score; column H marks a row as processed |
| `Balancing` | Team-balancing requests | Columns B–E from row 2: four player names; columns F–G receive the suggested teams |
| `Ratings` | TrueSkill ratings per category | Four column blocks (overall, offense, defense, solo) from row 3, each holding name, mu, sigma |
| `Leaderboard` | Ranked output per category | Written by the processor; rank and name per category block |

## Forms

Create three forms and link their responses to the game spreadsheet so submissions land on the tabs above:

- **Create player** — a single name field; new names are appended to the `Players` tab.
- **Submit match** — four player dropdowns (red offense, red defense, blue offense, blue defense) and the two team scores. For 1v1, 1v2, or 2v1 matches the second player of a team is left empty.
- **Balance teams** — four player dropdowns; the processor writes the fairest team split back to the sheet.

The player dropdowns in the match and balancing forms are kept in sync with the `Players` tab by an Apps Script — see [Apps Script](apps-script.md).

## Input rules enforced by the processor

- Draws are not supported; a match with equal scores is ignored.
- A match naming the same player twice is ignored.
- A duplicate name on the `Players` tab aborts processing for that game until fixed (the Apps Script also deletes duplicate registrations on submission).
- Retired players keep their ratings but are excluded from the dropdowns and the regular leaderboards — see [Managing players](managing-players.md).

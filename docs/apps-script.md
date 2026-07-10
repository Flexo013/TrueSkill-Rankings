# Apps Script

Google Apps Script keeps the player dropdowns in the match and balancing forms in sync with the `Players` tab: it is triggered by a submission on the create-player form and updates the dropdowns of the other forms. The script lives in this repository at `apps_script/update_player_dropdowns.gs` for reference; the live copy runs bound to each game's spreadsheet, where the code is leading.

## Installing it for a new game

1. Open the new game's spreadsheet and go to **Extensions → Apps Script**.
2. Paste the contents of `apps_script/update_player_dropdowns.gs`.
3. Replace the two form IDs at the top with the new game's **match form** and **balancing form** IDs (the long ID in each form's edit URL).
4. Add an installable trigger: **Triggers → Add trigger**, function `updateDropdown`, event source *From spreadsheet*, event type *On form submit*.
5. Submit a test player through the create-player form and check that both forms' dropdowns update.

The script assumes the first four `LIST` items of each form are the player dropdowns, so keep any additional dropdown questions after them.

## Future work

- The number of player dropdowns is hardcoded to four; it should become configurable per game type as a max-players-per-match setting.
- The balancing form should become optional — in always-FFA games a team-balancing form makes no sense.

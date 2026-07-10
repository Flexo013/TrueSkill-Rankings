# Apps Script

Google Apps Script keeps the player dropdowns in the match and balancing forms in sync with the `Players` tab: it is triggered by a submission on the create-player form and updates the dropdowns of the other forms. The script lives in this repository at `apps_script/update_player_dropdowns.gs` for reference; the live copy runs bound to each game's spreadsheet, where the code is leading.

## Installing it for a new game

1. Open the new game's spreadsheet and go to **Extensions → Apps Script**.
2. Paste the contents of `apps_script/update_player_dropdowns.gs`.
3. Set the per-game constants at the top of the script:
   - `MATCH_FORM_ID`: the new game's match form ID (the long ID in the form's edit URL).
   - `BALANCE_FORM_ID`: the balancing form ID, or empty (`''`) for games without a balancing form.
   - `MAX_PLAYERS_PER_MATCH`: the number of player dropdowns, matching the `max_players_per_match` of the game's `GameConfig`.
4. Add an installable trigger: **Triggers → Add trigger**, function `updateDropdown`, event source *From spreadsheet*, event type *On form submit*.
5. Submit a test player through the create-player form and check that the forms' dropdowns update.

The script assumes the first `MAX_PLAYERS_PER_MATCH` dropdown (`LIST`) items of each form are the player dropdowns, so keep any additional dropdown questions after them.

## Future work

The script constants duplicate settings that live on the game's `GameConfig` (`max_players_per_match`, `enable_balancing`). Eventually the script should be generated or driven from the config so a game is only configured once.

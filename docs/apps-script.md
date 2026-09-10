# Apps Script

Google Apps Script keeps the player dropdowns in the match form in sync with the `Players` tab: it is triggered by a submission on the create-player form and updates the dropdowns of the match form. The script lives in this repository at `apps_script/update_player_dropdowns.gs` for reference; the live copy runs bound to each game's spreadsheet, where the code is leading.

## Installing it for a new game

1. Open the new game's 'Create Player' spreadsheet and go via the kebab-menu on the top right to 'Apps Script'.
2. Create a new project based on the game name, for example 'Foosball'.
3. Paste the contents of `apps_script/update_player_dropdowns.gs`.
    - Rename the file.
4. Set the per-game constants at the top of the script:
    - `MATCH_FORM_ID`: the new game's match form ID (the long ID in the form's edit URL).
    - `MAX_PLAYERS_PER_MATCH`: the number of player dropdowns, matching the `max_players_per_match` of the game's `GameConfig`.
    - Save your changes
5. Navigate to 'Triggers' using the sidebar on the left.
6. Add a new trigger using the bottom right button:
    - Function: `updateDropdown`
    - Deployment: `Head` (default)
    - Source: `From form` (default)
    - Event type: `On form submit`
    - Save and accept risk via 'Advanced'.
---
6. Submit a test player through the create-player form and check that the form's dropdowns update.

The script assumes the first `MAX_PLAYERS_PER_MATCH` dropdown (`LIST`) items of the form are the player dropdowns, so keep any additional dropdown questions after them.

## Future work

The script constants duplicate settings that live on the game's `GameConfig` (`max_players_per_match`). Eventually the script should be generated or driven from the config so a game is only configured once.

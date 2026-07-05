# Apps Script

Google Apps Script keeps the player dropdowns in the match and balancing forms in sync with the `Players` tab. The script lives in this repository at `apps_script/update_player_dropdowns.gs` for reference; the live copy runs bound to each game's spreadsheet.

## What it does

On every new player registration, `updateDropdown`:

1. Reads all player names from `Players!B2:B`.
2. Trims the latest entry and deletes the row again if the name already exists (duplicate registration).
3. Sorts the names and sets them as the choices of the first four dropdown (`LIST`) items of both the match form and the balancing form.

## Installing it for a new game

1. Open the new game's spreadsheet and go to **Extensions → Apps Script**.
2. Paste the contents of `apps_script/update_player_dropdowns.gs`.
3. Replace the two form IDs at the top with the new game's **match form** and **balancing form** IDs (the long ID in each form's edit URL).
4. Add an installable trigger: **Triggers → Add trigger**, function `updateDropdown`, event source *From spreadsheet*, event type *On form submit*.
5. Submit a test player through the create-player form and check that both forms' dropdowns update.

The script assumes the first four `LIST` items of each form are the player dropdowns, so keep any additional dropdown questions after them.
